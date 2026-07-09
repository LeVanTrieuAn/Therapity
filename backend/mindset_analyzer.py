"""
mindset_analyzer.py
Module AI chuyên phân tích tư duy người dùng Thapsang.

Nguồn dữ liệu phân tích:
  - Bài đăng AOA (aoa_db.json): phong cách viết, mindmap, hashtag, nội dung
  - Lịch sử hội thoại Coach (thapsang_db.json): cách giao tiếp, chủ đề băn khoăn, ngôn ngữ cảm xúc

Đầu ra:
  - radar_stats: 6 chỉ số tư duy (0-100)
  - keywords: các thế mạnh nổi bật của người dùng
  - analysis_text: đoạn đánh giá tổng quan
  - mbti_suggestions: top 3 MBTI phù hợp kèm tỉ lệ và lý do
"""

import json
import re
import hashlib
import os
import math
from openai import OpenAI
from dotenv import load_dotenv
import cms_helper

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

DATABASE_DIR = os.path.join(os.path.dirname(BASE_DIR), "database")
THAPSANG_DB  = os.path.join(DATABASE_DIR, "thapsang_db.json")
AOA_DB       = os.path.join(DATABASE_DIR, "aoa_db.json")

DEFAULT_MODEL = os.getenv("LLM_MODEL", "thapsang").split(",")[0].strip()

_ai_client = None

def get_client() -> OpenAI:
    global _ai_client
    if _ai_client is None:
        _ai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
        )
    return _ai_client


# ─── Từ điển từ khoá định tính (keyword-based baseline) ───────────────────────
KEYWORD_DIMS = {
    "Khách quan": ["số liệu", "thông tin", "bằng chứng", "nguồn", "dữ liệu",
                   "chi tiết", "cụ thể", "thực tế", "phân tích", "con số"],
    "Cảm xúc":   ["cảm thấy", "buồn", "vui", "lo lắng", "hạnh phúc", "tâm trạng",
                   "sợ", "thương", "yêu", "ghét", "nhạy cảm", "tình cảm"],
    "Tiêu cực":  ["lưu ý", "cẩn thận", "rủi ro", "nguy cơ", "kiểm tra",
                   "xác thực", "đề phòng", "nghi ngờ", "chậm", "chắc", "an toàn"],
    "Tích cực":  ["hy vọng", "tốt đẹp", "tiềm năng", "cơ hội", "phát triển",
                   "tin tưởng", "vượt qua", "thành công", "tích cực", "niềm tin"],
    "Sáng tạo":  ["ý tưởng", "mới", "sáng tạo", "khác biệt", "thử nghiệm",
                   "độc đáo", "phát minh", "cải tiến", "giải pháp", "tưởng tượng"],
    "Tổng quan": ["tóm lại", "khái quát", "nhìn chung", "hệ thống", "tổng thể",
                   "bức tranh", "kết luận", "cấu trúc", "toàn diện"],
}

DIMS = list(KEYWORD_DIMS.keys())   # thứ tự cố định


# ─── Thu thập corpus ──────────────────────────────────────────────────────────
def _collect_corpus(username: str) -> tuple[str, str, str]:
    """Trả về (aoa_text, coach_text, onboarding_context) — toàn bộ văn bản và bối cảnh của người dùng."""
    import cms_helper
    aoa_text   = ""
    coach_text = ""
    onboarding_context = ""
    
    try:
        user_info = cms_helper.get_user_by_username(username)
        if user_info and isinstance(user_info.get("onboarding"), dict):
            onboarding_context = user_info["onboarding"].get("_core_context", "")
    except Exception as e:
        print(f"[mindset_analyzer] Lỗi đọc onboarding: {e}")

    # 1. AOA posts + comments
    try:
        posts = cms_helper.get_aoa_posts()
        for post in posts:
            if post.get("author_name") == username:
                aoa_text += " " + post.get("content", "")
                # Gộp thêm nhãn mindmap nodes
                for node in post.get("graph_data", {}).get("nodes", []):
                    aoa_text += " " + node.get("label", "")
            for cmt in post.get("comments", []):
                if cmt.get("author_name") == username:
                    aoa_text += " " + cmt.get("content", "")
    except Exception as e:
        print(f"[mindset_analyzer] Lỗi đọc aoa từ CMS: {e}")

    # 2. Coach conversations
    try:
        chats = cms_helper.get_chat_sessions(username)
        for key, val in chats.items():
            if "chat_history" in val:
                for msg in val["chat_history"]:
                    if msg.get("role") == "user":
                        coach_text += " " + msg.get("content", "")
    except Exception as e:
        print(f"[mindset_analyzer] Lỗi đọc chats từ CMS: {e}")

    return aoa_text.strip(), coach_text.strip(), onboarding_context.strip()


# ─── Tính điểm baseline bằng keyword matching ─────────────────────────────────
def _keyword_stats(username: str, full_text: str) -> list[int]:
    """Baseline score 50-70 dựa trên hash + keyword bonus."""
    h = hashlib.md5(username.encode()).hexdigest()
    scores = []
    for i, dim in enumerate(DIMS):
        base = 50 + (int(h[i*2:i*2+2], 16) % 21)       # 50–70
        hits  = sum(full_text.lower().count(kw) for kw in KEYWORD_DIMS[dim])
        bonus = min(hits * 3, 28)
        scores.append(min(base + bonus, 98))
    return scores


# ─── Gọi AI phân tích toàn diện ──────────────────────────────────────────────
def _ai_analyze(username: str, aoa_text: str, coach_text: str, onboarding_context: str) -> dict | None:
    """
    Gọi LLM. Nếu corpus quá ngắn, trả về None để dùng logic fallback.
    """
    if len(aoa_text) < 50 and len(coach_text) < 50:
        return None  # Không đủ dữ liệu cho AI

    corpus = f"[BỐI CẢNH NGƯỜI DÙNG]\n{onboarding_context}\n\n[AOA POSTS]\n{aoa_text[:4000]}\n\n[COACH CONVERSATIONS]\n{coach_text[:4000]}"

    system_prompt = (
        "Bạn là chuyên gia phân tích tâm lý, hành vi và tư duy AI của nền tảng Thapsang. "
        "Nhiệm vụ của bạn là đọc hiểu sâu sắc bối cảnh người dùng (context) và ngôn từ thực tế của họ "
        "để phân loại tính cách (MBTI) và tư duy một cách cá nhân hóa và chính xác nhất. "
        "Kết luận phải bám sát vào những gì họ thực sự đã viết. "
        "Hãy phân tích và trả về JSON THUẦN TÚY (không có markdown)."
    )

    user_prompt = f"""Phân tích tư duy của người dùng '{username}' từ dữ liệu sau:

{corpus}

Trả về JSON với CÁC TRƯỜNG SAU (không có key thừa):
{{
  "radar_stats": {{
    "Khách quan": <số 0-100>,
    "Cảm xúc": <số 0-100>,
    "Tiêu cực": <số 0-100>,
    "Tích cực": <số 0-100>,
    "Sáng tạo": <số 0-100>,
    "Tổng quan": <số 0-100>
  }},
  "keywords": [
    {{"vi": "<từ khoá tiếng Việt>", "en": "<từ khoá tiếng Anh>"}}
  ],
  "analysis_text": {{
    "vi": "<2-4 câu nhận xét tư duy tiếng Việt>",
    "en": "<2-4 câu nhận xét tư duy tiếng Anh>"
  }},
  "mbti_suggestions": [
    {{
      "type": "<VD: INTJ>",
      "score": <phần trăm 0-100>,
      "reason": {{
        "vi": "<1-2 câu lý do tiếng Việt>",
        "en": "<1-2 câu lý do tiếng Anh>"
      }}
    }}
  ]
}}"""

    try:
        client = get_client()
        resp = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.2,
            top_p=0.9,
        )
        raw = resp.choices[0].message.content or ""
        # Cố gắng trích xuất JSON
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"[mindset_analyzer] AI call failed: {e}")

    return None


# ─── PUBLIC API ───────────────────────────────────────────────────────────────
def analyze_mindset(username: str) -> dict:
    """
    Hàm chính — trả về toàn bộ phân tích tư duy của người dùng.

    Returns:
    {
      "radar_stats": [int, ...],          # 6 giá trị theo thứ tự DIMS
      "dims": ["Khách quan", ...],           # 6 tên chiều
      "keywords": ["...", ...],
      "analysis_text": "...",
      "mbti_suggestions": [{type, score, reason}, ...]
    }
    """
    aoa_text, coach_text, onboarding_context = _collect_corpus(username)
    full_text = aoa_text + " " + coach_text

    # Tạo hash để kiểm tra xem dữ liệu có thay đổi hay không
    corpus_hash = hashlib.md5(full_text.encode("utf-8")).hexdigest()
    
    # Kiểm tra Cache từ CMS Server
    user_info = cms_helper.get_user_by_username(username)
    if user_info and isinstance(user_info.get("onboarding"), dict):
        onboarding_data = user_info["onboarding"]
        user_cache = onboarding_data.get("_mindset_cache", {})
        # Nếu hash không đổi -> trả về dữ liệu đã tính toán (rất nhanh)
        if user_cache.get("hash") == corpus_hash and "data" in user_cache:
            return user_cache["data"]
    else:
        onboarding_data = {}

    # 1. Baseline từ keyword
    baseline = _keyword_stats(username, full_text)

    # 2. Thử gọi AI để tinh chỉnh
    ai_result = _ai_analyze(username, aoa_text, coach_text, onboarding_context)

    if ai_result:
        # Merge radar_stats từ AI (ưu tiên AI nếu parse được)
        raw_radar = ai_result.get("radar_stats", {})
        radar = []
        for dim in DIMS:
            ai_val = raw_radar.get(dim)
            if isinstance(ai_val, (int, float)) and 0 <= ai_val <= 100:
                radar.append(int(ai_val))
            else:
                radar.append(baseline[DIMS.index(dim)])

        keywords = ai_result.get("keywords") or []
        analysis_text = ai_result.get("analysis_text") or _default_analysis(username)
        mbti = ai_result.get("mbti_suggestions") or _default_mbti()
    else:
        # Fallback hoàn toàn keyword-based
        radar = baseline
        keywords = _keyword_keywords(full_text)
        analysis_text = _default_analysis(username)
        mbti = _default_mbti()

    final_result = {
        "radar_stats": radar,
        "dims": DIMS,
        "keywords": keywords[:8],
        "analysis_text": analysis_text,
        "mbti_suggestions": mbti[:3],
    }

    # Lưu kết quả mới tính vào cache trên CMS Server
    if user_info:
        try:
            onboarding_data["_mindset_cache"] = {
                "hash": corpus_hash,
                "data": final_result
            }
            cms_helper.update_user(user_info["id"], {"onboarding": onboarding_data})
        except Exception as e:
            print(f"[mindset_analyzer] Lỗi đồng bộ cache lên CMS server: {e}")

    return final_result


# ─── Fallback helpers ─────────────────────────────────────────────────────────
def _keyword_keywords(text: str) -> list[dict]:
    """Trích xuất top keywords thế mạnh dựa trên tần suất."""
    candidates = {
        "Khủng hoảng tuổi 25": (["khủng hoảng", "tuổi 25", "định hướng", "áp lực", "chênh vênh"], "Quarter-life Crisis"),
        "Tư duy logic": (["logic", "lý luận", "phân tích", "suy nghĩ"], "Logical Thinking"),
        "Lập kế hoạch": (["kế hoạch", "mục tiêu", "lộ trình", "chiến lược"], "Planning"),
        "Cân bằng cảm xúc": (["cảm xúc", "cân bằng", "bình tĩnh", "tâm lý"], "Emotional Balance"),
        "Sáng tạo": (["sáng tạo", "ý tưởng", "mới", "khác biệt"], "Creativity"),
        "Đồng cảm": (["đồng cảm", "hiểu", "chia sẻ", "hỗ trợ"], "Empathy"),
        "Kiên trì": (["kiên trì", "nỗ lực", "cố gắng", "không từ bỏ"], "Persistence"),
        "Tự nhận thức": (["tự nhận", "bản thân", "nhận ra", "thay đổi"], "Self-Awareness"),
        "Tư duy hệ thống": (["hệ thống", "tổng thể", "cấu trúc", "toàn diện"], "Systems Thinking"),
    }
    t = text.lower()
    scored = {k: sum(t.count(w) for w in ws[0]) for k, ws in candidates.items()}
    sorted_keys = [k for k, _ in sorted(scored.items(), key=lambda x: -x[1]) if _ > 0] or list(candidates.keys())[:5]
    return [{"vi": k, "en": candidates[k][1]} for k in sorted_keys]


def _default_analysis(username: str) -> dict:
    return {
        "vi": f"Dữ liệu ban đầu cho thấy {username} có phong cách tư duy cân bằng giữa cảm xúc và lý trí. Hãy tiếp tục chia sẻ thêm trên AOA và trò chuyện với Coach để AI phân tích sâu hơn.",
        "en": f"Initial data suggests {username} has a balanced mindset between emotion and logic. Continue sharing on AOA and chatting with Coach for a deeper AI analysis."
    }


def _default_mbti() -> list[dict]:
    return [
        {"type": "INFJ", "score": 75, "reason": {"vi": "Có bản lĩnh nội tâm mạnh, tiêu chuẩn đạo đức cao dẫn đến kiệt sức, và xu hướng tìm kiếm ý nghĩa sâu sắc thay vì chỉ giải quyết bề nổi.", "en": "Strong inner fortitude and high moral standards leading to burnout, with a tendency to seek profound meaning rather than surface-level solutions."}},
        {"type": "INTJ", "score": 18, "reason": {"vi": "Xu hướng lập kế hoạch chiến lược và tư duy hệ thống rõ ràng trong cách tiếp cận vấn đề.", "en": "Strategic planning and systems thinking tendency evident in problem-solving."}},
        {"type": "INFP", "score": 10, "reason": {"vi": "Sự nhạy cảm và khả năng biểu đạt cảm xúc tinh tế cũng gợi lên đặc điểm INFP.", "en": "Sensitivity and delicate emotional expression also suggest INFP traits."}},
    ]
