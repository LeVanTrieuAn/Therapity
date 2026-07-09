import os
import sys
import json

# Fix cho Windows console in tiếng Việt
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load môi trường từ file .env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("Missing OPENAI_API_KEY in environment variables (.env)")

client = OpenAI(
    api_key=api_key,
    base_url=os.getenv("LLM_BASE_URL", "https://llmapi.digiforce.vn/v1")
)
model_name = os.getenv("LLM_MODEL", "thapsang").split(",")[0].strip()

# 2. Định vị file database
DATABASE_DIR = os.path.join(os.path.dirname(BASE_DIR), "database")
THAPSANG_DB_PATH = os.path.join(DATABASE_DIR, "thapsang_db.json")

import cms_helper

def load_db():
    # Deprecated for file operations - returns empty dict
    return {}

def save_db(data):
    # Deprecated
    pass

def learn_contexts():
    print(f"Bắt đầu học ngữ cảnh từ Diary cho các người dùng trên CMS...")
    # Fetch all users
    # For each user, fetch their diary entries and generate context
    # Since CMS doesn't support get_all_users directly, we can fetch all diary entries and learn contexts for all unique authors!
    try:
        # Fetch AOA posts to find active usernames or use a predefined set
        posts = cms_helper.get_aoa_posts()
        usernames = set(p.get("author_name") for p in posts if p.get("author_name"))
        # Also add default user
        usernames.add("user")
        
        for username in usernames:
            entries = cms_helper.get_diary_entries(username)
            if not entries:
                continue
                
            print(f"Đang phân tích ngữ cảnh cho user: {username} ({len(entries)} bài viết)...")
            combined_text = ""
            for idx, entry in enumerate(entries):
                combined_text += f"\n--- Bài {idx + 1} ({entry.get('date', '')}) ---\n"
                combined_text += f"Tiêu đề: {entry.get('title', '')}\n"
                combined_text += f"Tâm trạng: {entry.get('mood', '')}\n"
                combined_text += f"Nội dung: {entry.get('content', '')}\n"
                
            if not combined_text.strip():
                continue

            system_prompt = (
                "Bạn là một chuyên gia phân tích tâm lý học và quản lý tri thức. "
                "Nhiệm vụ của bạn là đọc các đoạn Nhật ký (Diary) của người dùng và tóm tắt lại thành một "
                "'Ngữ cảnh cốt lõi' (Core Context) ngắn gọn (dưới 150 từ). "
                "Mục đích của đoạn tóm tắt này là để lưu trữ vào bộ nhớ dài hạn, giúp AI hiểu được ngay: "
                "tính cách, những vấn đề bận tâm chính, thói quen và cảm xúc chủ đạo của người dùng. "
                "Tuyệt đối không đưa ra lời khuyên, chỉ đúc kết sự thật khách quan về người dùng."
            )

            user_prompt = f"Đây là các đoạn nhật ký của người dùng '{username}':\n{combined_text}\n\nHãy tạo đoạn tóm tắt ngữ cảnh cốt lõi:"

            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=300,
                    temperature=0.2,
                    top_p=0.9,
                )
                core_context = response.choices[0].message.content.strip()
                
                # Save core context inside onboardingData['_core_context'] in CMS
                user_info = cms_helper.get_user_by_username(username)
                if user_info:
                    onboarding = user_info.get("onboarding") or {}
                    if isinstance(onboarding, dict):
                        onboarding["_core_context"] = core_context
                        cms_helper.update_user(user_info["id"], {"onboarding": onboarding})
                print(f"-> Đã học xong cho {username}: {core_context[:80]}...\n")
                
            except Exception as e:
                print(f"Lỗi khi học ngữ cảnh cho {username}: {e}")
    except Exception as ex:
        print(f"Lỗi khi quét người dùng từ CMS: {ex}")


def generate_context_from_onboarding(username: str, onboarding: dict):
    """Tạo một Core Context ngắn gọn từ dữ liệu onboarding và lưu vào onboardingData._core_context trên CMS."""
    if not onboarding:
        return None

    # Build a concise description of user's onboarding choices
    parts = []
    day_of_birth = onboarding.get("day_of_birth")
    month_of_birth = onboarding.get("month_of_birth")
    year_of_birth = onboarding.get("year_of_birth")
    age = onboarding.get("age")
    gender = onboarding.get("gender")
    interests = onboarding.get("interests", [])
    problems = onboarding.get("problems", [])
    goals = onboarding.get("goals", [])
    source = onboarding.get("source")

    if day_of_birth and month_of_birth and year_of_birth:
        parts.append(f"Ngày sinh: {day_of_birth}/{month_of_birth}/{year_of_birth}")
    elif age:
        parts.append(f"Độ tuổi: {age}")
    if gender:
        parts.append(f"Giới tính: {gender}")
    if interests:
        parts.append("Sở thích: " + ", ".join(interests))
    if problems:
        parts.append("Vấn đề chính: " + ", ".join(problems))
    if goals:
        parts.append("Mục tiêu: " + ", ".join(goals))
    if source:
        parts.append(f"Nguồn biết đến: {source}")

    combined = "\n".join(parts)

    system_prompt = (
        "Bạn là một chuyên gia phân tích tâm lý học và quản lý tri thức. "
        "Nhiệm vụ của bạn là đọc tóm tắt lựa chọn onboarding của người dùng và tạo một 'Ngữ cảnh cốt lõi' (Core Context) ngắn gọn dưới 150 từ. "
        "Đoạn này phải nêu rõ tính cách sơ bộ, những bận tâm chính, ưu tiên mục tiêu, và các điều kiện nhạy cảm nếu có. "
        "Tuyệt đối không đưa lời khuyên, chỉ tóm tắt các thông tin khách quan."
    )

    user_prompt = f"Dưới đây là dữ liệu onboarding của người dùng '{username}':\n{combined}\n\nHãy tạo đoạn tóm tắt ngữ cảnh cốt lõi:"

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=250,
            temperature=0.1,
            top_p=0.9,
        )
        core_context = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Onboarding context LLM error for {username}: {e}")
        # Fallback: build deterministic summary
        summary_lines = []
        if day_of_birth and month_of_birth and year_of_birth:
            summary_lines.append(f"Sinh ngày: {day_of_birth}/{month_of_birth}/{year_of_birth}")
        elif age:
            summary_lines.append(f"{age}")
        if gender: summary_lines.append(f"{gender}")
        if interests: summary_lines.append("Sở thích: " + ", ".join(interests[:5]))
        if problems: summary_lines.append("Vấn đề: " + ", ".join(problems[:5]))
        if goals: summary_lines.append("Mục tiêu: " + ", ".join(goals[:5]))
        core_context = "; ".join(summary_lines)

    user_info = cms_helper.get_user_by_username(username)
    if user_info:
        onboarding_payload = onboarding or {}
        onboarding_payload["_core_context"] = core_context
        cms_helper.update_user(user_info["id"], {"onboarding": onboarding_payload, "onboarded": True})
        
    print(f"-> Đã sinh Core Context từ onboarding cho {username}: {core_context[:100]}...")
    return core_context

if __name__ == "__main__":
    learn_contexts()
