import os
import json
import datetime
from datetime import datetime
from typing import List, Dict, Any, Optional

# Note: CMS variables commented out and marked with //
# CMS_BASE_URL = os.getenv("CMS_BASE_URL", "http://localhost:13000/api")  # //
# CMS_API_KEY = os.getenv("CMS_API_KEY")  # //

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "..", "database")
THAPSANG_DB = os.path.join(DATABASE_DIR, "thapsang_db.json")
AOA_DB = os.path.join(DATABASE_DIR, "aoa_db.json")
COHORT_DB = os.path.join(DATABASE_DIR, "cohort_db.json")

def load_json_db(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return default
    return default

def save_json_db(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_thapsang_db():
    return load_json_db(THAPSANG_DB, {"_folders": {}, "_diaries": {}, "_profiles": {}, "_contexts": {}, "_accounts": {}})

def save_thapsang_db(data):
    save_json_db(THAPSANG_DB, data)

def load_aoa_db():
    return load_json_db(AOA_DB, {"posts": []})

def save_aoa_db(data):
    save_json_db(AOA_DB, data)

def load_cohort_db():
    return load_json_db(COHORT_DB, {"members": [], "syllabus": []})

def save_cohort_db(data):
    save_json_db(COHORT_DB, data)


def get_active_llm_config() -> Dict[str, Any]:
    return {
        "model": os.getenv("LLM_MODEL", "llama3"),
        "temperature": 0.7,
        "max_tokens": 2048,
        "stream": False
    }

def sync_active_model_to_cms(active_model: str):
    pass

def count_tokens(text: str, model_name: Optional[str] = None) -> int:
    if not text:
        return 0
    try:
        import tiktoken
        encoding_name = "cl100k_base"
        if model_name:
            model_lower = model_name.lower()
            if "gpt-4o" in model_lower:
                encoding_name = "o200k_base"
            elif "gpt-4" in model_lower or "gpt-3.5" in model_lower:
                encoding_name = "cl100k_base"
            elif "text-embedding" in model_lower:
                encoding_name = "cl100k_base"
        try:
            encoding = tiktoken.get_encoding(encoding_name)
        except Exception:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        return len(text) // 4

def authenticate_user(email: str, password: str) -> tuple[bool, str]:
    db = load_thapsang_db()
    accounts = db.setdefault("_accounts", {})
    if email in accounts:
        if accounts[email] == password:
            return True, ""
    for username, prof in db.setdefault("_profiles", {}).items():
        if prof.get("email") == email:
            if accounts.get(username) == password:
                return True, ""
    return False, "Tài khoản hoặc mật khẩu không chính xác"

def onboarding_text_to_dict(val: Any) -> Dict[str, Any]:
    if isinstance(val, dict):
        return val
    if not isinstance(val, str) or not val.strip():
        return {}
    try:
        parsed = json.loads(val)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
        
    res = {
        "day_of_birth": "",
        "month_of_birth": "",
        "year_of_birth": "",
        "gender": "",
        "interests": [],
        "problems": [],
        "goals": [],
        "source": "",
        "_core_context": ""
    }
    
    lines = val.split("\n")
    for line in lines:
        line = line.strip()
        if not line or ":" not in line:
            continue
        key_part, val_part = line.split(":", 1)
        key_part = key_part.strip().lower()
        val_part = val_part.strip()
        
        if "ngày sinh" in key_part or "birth" in key_part:
            parts = val_part.split("/")
            if len(parts) == 3:
                res["day_of_birth"] = parts[0].strip()
                res["month_of_birth"] = parts[1].strip()
                res["year_of_birth"] = parts[2].strip()
        elif "giới tính" in key_part or "gender" in key_part:
            res["gender"] = val_part
        elif "sở thích" in key_part or "interests" in key_part:
            res["interests"] = [x.strip() for x in val_part.split(",") if x.strip()]
        elif "khó khăn" in key_part or "vấn đề" in key_part or "problems" in key_part:
            res["problems"] = [x.strip() for x in val_part.split(",") if x.strip()]
        elif "mục tiêu" in key_part or "goals" in key_part:
            res["goals"] = [x.strip() for x in val_part.split(",") if x.strip()]
        elif "nguồn" in key_part or "source" in key_part:
            res["source"] = val_part
        elif "bối cảnh" in key_part or "ngữ cảnh" in key_part or "context" in key_part:
            res["_core_context"] = val_part
        elif "mindset cache" in key_part:
            try:
                res["_mindset_cache"] = json.loads(val_part)
            except Exception:
                pass
    return res

def dict_to_onboarding_text(data: Dict[str, Any]) -> str:
    if not isinstance(data, dict) or not data:
        return ""
    lines = []
    day = data.get("day_of_birth", "")
    month = data.get("month_of_birth", "")
    year = data.get("year_of_birth", "")
    if day or month or year:
        lines.append(f"Ngày sinh: {day}/{month}/{year}")
    elif data.get("age"):
        lines.append(f"Độ tuổi: {data.get('age')}")
    if data.get("gender"):
        lines.append(f"Giới tính: {data.get('gender')}")
        
    def format_list(val):
        if isinstance(val, list):
            return ", ".join(val)
        return str(val) if val else ""
        
    if data.get("interests"):
        lines.append(f"Sở thích: {format_list(data.get('interests'))}")
    if data.get("problems"):
        lines.append(f"Khó khăn: {format_list(data.get('problems'))}")
    if data.get("goals"):
        lines.append(f"Mục tiêu: {format_list(data.get('goals'))}")
    if data.get("source"):
        lines.append(f"Nguồn biết đến: {data.get('source')}")
    if data.get("_core_context"):
        lines.append(f"Bối cảnh AI: {data.get('_core_context')}")
    if data.get("_mindset_cache"):
        cache_str = json.dumps(data.get("_mindset_cache"), ensure_ascii=False)
        lines.append(f"Mindset cache: {cache_str}")
    return "\n".join(lines)

def extract_attachment_url(val: Any) -> str:
    if not val:
        return ""
    if isinstance(val, str):
        val = val.strip()
        if val.startswith("[") or val.startswith("{"):
            try:
                val = json.loads(val)
            except Exception:
                pass
    if isinstance(val, list):
        if len(val) > 0:
            first = val[0]
            if isinstance(first, dict):
                return first.get("url") or first.get("path") or ""
            elif isinstance(first, str):
                return first
        return ""
    if isinstance(val, dict):
        return val.get("url") or val.get("path") or ""
    return str(val) if isinstance(val, str) else ""

def upload_attachment(base64_str: str) -> Optional[Dict[str, Any]]:
    if not base64_str or not isinstance(base64_str, str) or not base64_str.startswith("data:image/"):
        return None
    try:
        import base64
        import re
        import uuid
        meta, data = base64_str.split(",", 1)
        match = re.search(r"data:image/(\w+);base64", meta)
        ext = match.group(1) if match else "png"
        image_data = base64.b64decode(data)
        filename = f"upload_{uuid.uuid4().hex}.{ext}"
        local_path = os.path.join(BASE_DIR, "..", "frontend", "assets", "voices", filename)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(image_data)
        return {"url": f"/assets/voices/{filename}", "path": f"/assets/voices/{filename}"}
    except Exception as e:
        print(f"[LOCAL UPLOAD ERROR] Failed to save attachment: {e}")
    return None

def upload_base64_image(base64_str: str) -> str:
    res = upload_attachment(base64_str)
    if res:
        return res.get("url", base64_str)
    return base64_str

def sanitize_display_name(displayname: Optional[str], username: Optional[str]) -> str:
    name_to_clean = displayname or username or ""
    if name_to_clean and "@" in name_to_clean:
        return name_to_clean.split("@")[0]
    return name_to_clean or "Người dùng Thapsang"

def parse_following_list(val: Any) -> List[str]:
    if not val:
        return []
    if isinstance(val, list):
        return [str(x) for x in val if x]
    if isinstance(val, str):
        val = val.strip()
        if not val:
            return []
        if val.startswith("[") and val.endswith("]"):
            try:
                parsed = json.loads(val)
                if isinstance(parsed, list):
                    return [str(x) for x in parsed if x]
            except:
                pass
        return [x.strip() for x in val.split(",") if x.strip()]
    return []

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    db = load_thapsang_db()
    profiles = db.setdefault("_profiles", {})
    if username not in profiles:
        return None
    prof = profiles[username]
    return {
        "id": username,
        "username": username,
        "displayName": prof.get("displayName", username),
        "bio": prof.get("bio", ""),
        "following_list": prof.get("following_list", []),
        "onboarding": prof.get("onboarding", {}),
        "avatar_url": prof.get("avatar_url", ""),
        "banner_url": prof.get("banner_url", ""),
        "email": prof.get("email", "")
    }

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    db = load_thapsang_db()
    profiles = db.setdefault("_profiles", {})
    for username, prof in profiles.items():
        if prof.get("email") == email:
            return get_user_by_username(username)
    return None

def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    db = load_thapsang_db()
    username = user_data["username"]
    password = user_data.get("password", "password123")
    db.setdefault("_accounts", {})[username] = password
    
    profiles = db.setdefault("_profiles", {})
    profiles[username] = {
        "displayName": user_data.get("displayName", username),
        "bio": user_data.get("bio", ""),
        "email": user_data.get("email", ""),
        "following_list": user_data.get("following_list", []),
        "onboarding": user_data.get("onboarding", {}),
        "avatar_url": user_data.get("avatar_url", ""),
        "banner_url": user_data.get("banner_url", "")
    }
    save_thapsang_db(db)
    return get_user_by_username(username)

def update_user(user_id: Any, user_data: Dict[str, Any]) -> Dict[str, Any]:
    db = load_thapsang_db()
    profiles = db.setdefault("_profiles", {})
    username = str(user_id)
    if username not in profiles:
        # try search by email
        for uname, prof in profiles.items():
            if prof.get("email") == user_id:
                username = uname
                break
    if username not in profiles:
        profiles[username] = {}
        
    prof = profiles[username]
    for k, v in user_data.items():
        if k == "password":
            db.setdefault("_accounts", {})[username] = v
        else:
            prof[k] = v
    save_thapsang_db(db)
    return get_user_by_username(username)

def delete_user(user_id: Any) -> bool:
    db = load_thapsang_db()
    profiles = db.setdefault("_profiles", {})
    accounts = db.setdefault("_accounts", {})
    username = str(user_id)
    deleted = False
    if username in profiles:
        del profiles[username]
        deleted = True
    if username in accounts:
        del accounts[username]
        deleted = True
    if deleted:
        save_thapsang_db(db)
    return deleted

def get_chat_sessions(username: Optional[str] = None) -> Dict[str, Any]:
    db = load_thapsang_db()
    result = {}
    for key, s in db.items():
        if key.startswith("_"):
            continue
        if not isinstance(s, dict) or "username" not in s:
            continue
        s_username = s.get("username")
        if username and s_username != username:
            continue
        chat_history = s.get("chat_history", [])
        graph_data = s.get("graph_data", {"nodes": [], "edges": []})
        result[key] = {
            "id": key,
            "username": s_username,
            "chat_history": chat_history,
            "graph_data": graph_data,
            "tasks": s.get("tasks", []),
            "has_new_task": s.get("has_new_task", False),
            "custom_title": s.get("custom_title", s.get("customTitle", "")),
            "token_used": s.get("token_used", 0),
            "model_used": s.get("model_used", ""),
            "created_at": s.get("created_at", s.get("createdAt")),
            "voice": s.get("voice", ""),
            "suggested_replies": s.get("suggested_replies", [])
        }
    return result

def save_chat_session(session_id: str, username: str, chat_data: Dict[str, Any]) -> Dict[str, Any]:
    db = load_thapsang_db()
    if not session_id or session_id.startswith("temp_"):
        import time
        session_id = str(int(time.time() * 1000))
    session = db.setdefault(session_id, {})
    session["username"] = username
    session["chat_history"] = chat_data.get("chat_history", [])
    session["graph_data"] = chat_data.get("graph_data", {"nodes": [], "edges": []})
    session["tasks"] = chat_data.get("tasks", [])
    session["has_new_task"] = chat_data.get("has_new_task", False)
    session["custom_title"] = chat_data.get("custom_title", chat_data.get("customTitle", ""))
    session["token_used"] = chat_data.get("token_used", 0)
    session["model_used"] = chat_data.get("model_used", "")
    session["created_at"] = chat_data.get("created_at", session.get("created_at", datetime.now().isoformat() + "Z"))
    session["voice"] = chat_data.get("voice", "")
    session["suggested_replies"] = chat_data.get("suggested_replies", [])
    save_thapsang_db(db)
    return session

def delete_chat_session(session_id: str) -> bool:
    db = load_thapsang_db()
    if session_id in db:
        del db[session_id]
        save_thapsang_db(db)
        return True
    return False

def get_diary_entries(username: str) -> List[Dict[str, Any]]:
    db = load_thapsang_db()
    diaries = db.setdefault("_diaries", {}).setdefault(username, [])
    diaries.sort(key=lambda x: x.get("date", ""), reverse=True)
    return diaries

def save_diary_entry(entry_id: str, username: str, entry_data: Dict[str, Any]) -> Dict[str, Any]:
    db = load_thapsang_db()
    diaries = db.setdefault("_diaries", {}).setdefault(username, [])
    existing = None
    if entry_id:
        for entry in diaries:
            if str(entry.get("id")) == str(entry_id):
                existing = entry
                break
    date_val = entry_data.get("date", "")
    if not date_val:
        date_val = datetime.now().isoformat() + "Z"
    if existing:
        existing["title"] = entry_data.get("title", "")
        existing["content"] = entry_data.get("content", "")
        existing["folder"] = entry_data.get("folder", "")
        existing["ai_insight"] = entry_data.get("ai_insight", "")
        existing["date"] = date_val
        ret = existing
    else:
        if not entry_id or entry_id.startswith("temp_"):
            import time
            entry_id = f"diary_{int(time.time())}"
        new_entry = {
            "id": entry_id,
            "title": entry_data.get("title", ""),
            "content": entry_data.get("content", ""),
            "mood": entry_data.get("mood", "Calm"),
            "folder": entry_data.get("folder", ""),
            "date": date_val,
            "ai_insight": entry_data.get("ai_insight", "")
        }
        diaries.append(new_entry)
        ret = new_entry
    save_thapsang_db(db)
    return ret

def delete_diary_entry(entry_id: str) -> bool:
    db = load_thapsang_db()
    diaries_dict = db.setdefault("_diaries", {})
    deleted = False
    for username, diaries in diaries_dict.items():
        for i, entry in enumerate(diaries):
            if str(entry.get("id")) == str(entry_id):
                diaries.pop(i)
                deleted = True
                break
        if deleted:
            break
    if deleted:
        save_thapsang_db(db)
    return deleted

def get_diary_folders(username: str) -> List[str]:
    db = load_thapsang_db()
    return db.setdefault("_folders", {}).setdefault(username, [])

def create_diary_folder(username: str, folder_name: str) -> bool:
    db = load_thapsang_db()
    folders = db.setdefault("_folders", {}).setdefault(username, [])
    if folder_name not in folders:
        folders.append(folder_name)
        save_thapsang_db(db)
        return True
    return False

def delete_diary_folder(username: str, folder_name: str) -> bool:
    db = load_thapsang_db()
    folders = db.setdefault("_folders", {}).setdefault(username, [])
    if folder_name in folders:
        folders.remove(folder_name)
        diaries = db.setdefault("_diaries", {}).setdefault(username, [])
        db["_diaries"][username] = [d for d in diaries if d.get("folder") != folder_name]
        save_thapsang_db(db)
        return True
    return False

def translate_aoa_text(text: str) -> str:
    if not text:
        return ""
    en_text = text
    mapping = {
        'Đã hoàn thành:': 'Completed:',
        'Viết ra 3 kỳ vọng cụ thể đang gây áp lực và thay thế bằng thực tế': 'Write down 3 specific expectations causing pressure and replace them with reality',
        'Insight & Bài học:': 'Insight & Lessons:',
        'Xây dựng Routine buổi sáng (Morning Protocol)': 'Build Morning Routine (Morning Protocol)',
        'Nghe Podcast: Quản trị Năng lượng - Andrew Huberman': 'Listen to Podcast: Energy Management - Andrew Huberman',
        'Góc nhìn của mình về vấn đề:': 'My perspective on the issue:',
        'Mọi người nghĩ sao?': 'What does everyone think?',
        'Rất đồng tình với góc nhìn của bạn! Mình cũng từng trải qua điều tương tự.': 'Totally agree with your perspective! I have experienced something similar.',
        'Khủng hoảng tuổi 25, mất định hướng': 'Quarter-life crisis, feeling lost',
        'Áp lực đồng trang lứa khi bạn bè thành công': 'Peer pressure when friends succeed',
        'Cảm giác trì hoãn không thể kiểm soát': 'Uncontrollable feeling of procrastination',
        'Sợ thất bại khi bắt đầu một dự án mới': 'Fear of failure when starting a new project',
        'Mất cân bằng giữa công việc và gia đình': 'Imbalance between work and family',
        'Thiếu tự tin trong giao tiếp đám đông': 'Lack of confidence in public speaking',
        'Làm sao để tìm thấy đam mê thực sự?': 'How to find true passion?',
        'Ám ảnh sự hoàn hảo dẫn đến kiệt sức': 'Obsession with perfection leading to burnout',
        'Sợ bị đánh giá bởi người khác': 'Fear of being judged by others',
        'Muốn thay đổi nhưng luôn quay lại thói quen cũ': 'Want to change but always revert to old habits',
        'Áp lực từ bản thân': 'Pressure from self',
        'Công việc không phải vấn đề': 'Work is not the problem',
        "Cam kết với từ 'cố gắng'": "Commitment to the word 'try'",
        'Kỳ vọng bản thân': 'Self expectations'
    }
    for k, v in mapping.items():
        en_text = en_text.replace(k, v)
    if en_text == text and len(text.strip()) > 0:
        import requests
        import urllib.parse
        try:
            url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=vi&tl=en&dt=t&q=" + urllib.parse.quote(text)
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                return "".join([d[0] for d in res.json()[0]])
        except:
            pass
    return en_text

def serialize_aoa_content(content: Any) -> str:
    if isinstance(content, dict):
        return content.get("vi", "").strip() or content.get("en", "").strip()
    return str(content).strip()

def deserialize_aoa_content(content_str: str) -> str:
    if not content_str:
        return ""
    content_str = content_str.strip()
    if content_str.startswith("{"):
        try:
            parsed = json.loads(content_str)
            if isinstance(parsed, dict):
                return parsed.get("vi", parsed.get("en", "")).strip()
        except:
            pass
    lower_str = content_str.lower()
    vi_marker = "tiếng việt:"
    en_marker = "tiếng anh:"
    vi_pos = lower_str.find(vi_marker)
    en_pos = lower_str.find(en_marker)
    if vi_pos != -1 and en_pos != -1:
        if vi_pos < en_pos:
            vi_start = vi_pos + len(vi_marker)
            return content_str[vi_start:en_pos].strip()
        else:
            vi_start = vi_pos + len(vi_marker)
            return content_str[vi_start:].strip()
    if vi_pos != -1:
        vi_start = vi_pos + len(vi_marker)
        return content_str[vi_start:].strip()
    return content_str

def get_aoa_posts() -> List[Dict[str, Any]]:
    db = load_aoa_db()
    posts = db.setdefault("posts", [])
    posts.sort(key=lambda x: x.get("id", ""), reverse=True)
    return posts

def create_aoa_post(author_name: str, author_avatar: str, content: Any, graph_data: Dict[str, Any], post_privacy: str = "public") -> Dict[str, Any]:
    db = load_aoa_db()
    import time
    post_id = str(time.time())
    uploaded_avatar = upload_base64_image(author_avatar)
    post = {
        "id": post_id,
        "author_name": author_name,
        "author_avatar": uploaded_avatar,
        "content": serialize_aoa_content(content),
        "graph_data": graph_data,
        "timestamp": datetime.now().strftime("%H:%M %d/%m/%Y"),
        "likes": 0,
        "shares": 0,
        "post_status": "active",
        "post_privacy": post_privacy,
        "liked_by": [],
        "comments": []
    }
    db["posts"].append(post)
    save_aoa_db(db)
    return post

def update_aoa_post(post_id: str, post_data: Dict[str, Any]) -> Dict[str, Any]:
    db = load_aoa_db()
    posts = db.setdefault("posts", [])
    for p in posts:
        if str(p.get("id")) == str(post_id):
            for k, v in post_data.items():
                if k == "content":
                    p["content"] = serialize_aoa_content(v)
                else:
                    p[k] = v
            save_aoa_db(db)
            return p
    return {}

def delete_aoa_post(post_id: str) -> bool:
    db = load_aoa_db()
    posts = db.setdefault("posts", [])
    for i, p in enumerate(posts):
        if str(p.get("id")) == str(post_id):
            posts.pop(i)
            save_aoa_db(db)
            return True
    return False

def add_aoa_comment(post_id: str, author_name: str, author_avatar: str, content: Any) -> Dict[str, Any]:
    db = load_aoa_db()
    posts = db.setdefault("posts", [])
    uploaded_avatar = upload_base64_image(author_avatar)
    comment = {
        "author_name": author_name,
        "author_avatar": uploaded_avatar,
        "content": serialize_aoa_content(content),
        "timestamp": datetime.now().strftime("%H:%M %d/%m/%Y")
    }
    for p in posts:
        if str(p.get("id")) == str(post_id):
            p.setdefault("comments", []).append(comment)
            save_aoa_db(db)
            return comment
    return {}

def serialize_subtasks(subtasks_list: list) -> str:
    if not isinstance(subtasks_list, list):
        res = str(subtasks_list) if subtasks_list else ""
        return res[:255]
    lines = ["Micro-steps:"]
    for sub in subtasks_list:
        title = sub.get("title", "")
        completed = sub.get("completed", False)
        status_marker = "[x]" if completed else "[ ]"
        lines.append(f"- {status_marker} {title}")
    res = "\n".join(lines)
    if len(res) > 255:
        return res[:252] + "..."
    return res

def deserialize_subtasks(val: Any) -> list:
    if not val:
        return []
    if isinstance(val, list):
        return val
    if not isinstance(val, str):
        return []
    val_stripped = val.strip()
    if val_stripped.startswith("[") and val_stripped.endswith("]"):
        try:
            parsed = json.loads(val_stripped)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass
    res = []
    lines = val.split("\n")
    for line in lines:
        line = line.strip()
        if not line or line.startswith("Micro-steps:"):
            continue
        if line.startswith("- [ ]") or line.startswith("- [x]"):
            title = line[5:].strip()
            completed = line.startswith("- [x]")
            res.append({"title": title, "completed": completed})
    return res

def get_tasks(username: str) -> List[Dict[str, Any]]:
    db = load_thapsang_db()
    profiles = db.setdefault("_profiles", {})
    if username not in profiles:
        return []
    return profiles[username].setdefault("tasks", [])

def create_task(username: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    db = load_thapsang_db()
    profiles = db.setdefault("_profiles", {})
    if username not in profiles:
        profiles[username] = {}
    tasks = profiles[username].setdefault("tasks", [])
    import time
    task_id = str(int(time.time() * 1000))
    task = {
        "id": task_id,
        "title": task_data.get("title", ""),
        "goal": task_data.get("goal") or task_data.get("description") or "",
        "status": task_data.get("status", "backlog"),
        "deadline": task_data.get("deadline") or "",
        "effort": task_data.get("effort") or 1,
        "subtasks": task_data.get("subtasks") or [],
        "contextLink": task_data.get("contextLink") or ""
    }
    tasks.append(task)
    save_thapsang_db(db)
    return task

def update_task(task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    db = load_thapsang_db()
    profiles = db.setdefault("_profiles", {})
    for username, prof in profiles.items():
        tasks = prof.setdefault("tasks", [])
        for t in tasks:
            if str(t.get("id")) == str(task_id):
                for k, v in task_data.items():
                    if k == "description":
                        t["goal"] = v
                    else:
                        t[k] = v
                save_thapsang_db(db)
                return t
    return {}

def delete_task(task_id: str) -> bool:
    db = load_thapsang_db()
    profiles = db.setdefault("_profiles", {})
    deleted = False
    for username, prof in profiles.items():
        tasks = prof.setdefault("tasks", [])
        for i, t in enumerate(tasks):
            if str(t.get("id")) == str(task_id):
                tasks.pop(i)
                deleted = True
                break
        if deleted:
            break
    if deleted:
        save_thapsang_db(db)
    return deleted

def recalculate_roadmap_progress(roadmap_id: int):
    pass

def get_cohort_members() -> List[Dict[str, Any]]:
    db = load_cohort_db()
    return db.setdefault("members", [])

def add_cohort_member(username: str, display_name: str, buddy_name: str = "Gia Cát AI", is_self: bool = True, week_progress: int = 0) -> Dict[str, Any]:
    db = load_cohort_db()
    members = db.setdefault("members", [])
    for m in members:
        if m.get("username") == username:
            m["display_name"] = display_name
            m["buddy"] = buddy_name
            m["is_self"] = is_self
            m["week_progress"] = week_progress
            save_cohort_db(db)
            return m
    m = {
        "username": username,
        "display_name": display_name,
        "week_progress": week_progress,
        "buddy": buddy_name,
        "joined": datetime.now().strftime("%Y-%m-%d"),
        "is_self": is_self
    }
    members.append(m)
    save_cohort_db(db)
    return m

def update_cohort_member_progress(member_id: str, username: str, progress: int) -> bool:
    db = load_cohort_db()
    members = db.setdefault("members", [])
    updated = False
    for m in members:
        if m.get("username") == username:
            m["week_progress"] = progress
            updated = True
            break
    if updated:
        save_cohort_db(db)
    return updated

def clear_cohort_members(cohort_id: str = "cohort_04", username: Optional[str] = None) -> bool:
    db = load_cohort_db()
    members = db.setdefault("members", [])
    db["members"] = [m for m in members if m.get("is_self") or (username and m.get("username") == username)]
    save_cohort_db(db)
    return True

def get_personal_roadmap_tasks(username: str) -> List[Dict[str, Any]]:
    db = load_thapsang_db()
    profiles = db.setdefault("_profiles", {})
    if username not in profiles:
        return []
    return profiles[username].setdefault("personal_roadmap_tasks", [])

def create_personal_roadmap_task(username: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    db = load_thapsang_db()
    profiles = db.setdefault("_profiles", {})
    if username not in profiles:
        profiles[username] = {}
    tasks = profiles[username].setdefault("personal_roadmap_tasks", [])
    import time
    task_id = str(int(time.time() * 1000))
    task = {
        "id": task_id,
        "title": task_data.get("title", ""),
        "goal": task_data.get("goal") or task_data.get("description") or "",
        "status": task_data.get("status", "backlog"),
        "deadline": "",
        "effort": task_data.get("effort", 2),
        "subtasks": task_data.get("subtasks") or [
            {"title": "Phân tích yêu cầu bài học", "done": False},
            {"title": "Hoàn thành chiêm nghiệm Socratic", "done": False}
        ],
        "contextLink": task_data.get("contextLink", "Lộ trình cá nhân - The Great Rebuild"),
        "week": int(task_data.get("week") or 1),
        "type": task_data.get("type", "core"),
        "description": task_data.get("description", ""),
        "essay": task_data.get("essay", ""),
        "quiz": task_data.get("quiz")
    }
    tasks.append(task)
    save_thapsang_db(db)
    return task

def update_personal_roadmap_task(task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    db = load_thapsang_db()
    profiles = db.setdefault("_profiles", {})
    for username, prof in profiles.items():
        tasks = prof.setdefault("personal_roadmap_tasks", [])
        for t in tasks:
            if str(t.get("id")) == str(task_id):
                for k, v in task_data.items():
                    if k == "task_title":
                        t["title"] = v
                    elif k == "task_description" or k == "description":
                        t["goal"] = v
                        t["description"] = v
                    elif k == "user_answer":
                        t["essay"] = v
                    else:
                        t[k] = v
                save_thapsang_db(db)
                return t
    return {}

def delete_personal_roadmap_task(task_id: str) -> bool:
    db = load_thapsang_db()
    profiles = db.setdefault("_profiles", {})
    deleted = False
    for username, prof in profiles.items():
        tasks = prof.setdefault("personal_roadmap_tasks", [])
        for i, t in enumerate(tasks):
            if str(t.get("id")) == str(task_id):
                tasks.pop(i)
                deleted = True
                break
        if deleted:
            break
    if deleted:
        save_thapsang_db(db)
    return deleted

def get_cohort_syllabus(cohort_id: Optional[str] = None) -> List[Dict[str, Any]]:
    db = load_cohort_db()
    syllabus = db.get("syllabus")
    if syllabus:
        return syllabus
    
    fallback_syllabus = [
        {
            "id": "w1",
            "cohort_id": "cohort_04",
            "week": 1,
            "phase": "unlearn",
            "title": "Nhận diện & Gỡ bỏ Định kiến cũ | Cognitive Unlearning",
            "description": "Nhận diện những mô thức tư duy cũ kỹ và rào cản nhận thức đang kìm hãm sự phát triển của bạn.",
            "status": "active",
            "tasks": [
                {"title": "Liệt kê 3 định kiến giới hạn bản thân trong quá khứ", "type": "core"},
                {"title": "Đọc tài liệu về phương pháp 'Mental Model Unlearning'", "type": "supplementary"}
            ]
        },
        {
            "id": "w2",
            "cohort_id": "cohort_04",
            "week": 2,
            "phase": "relearn",
            "title": "Thiết lập Tư duy Tăng trưởng | Establishing Growth Mindset",
            "description": "Kiến tạo các thói quen học tập và hành động theo phương pháp Socratic.",
            "status": "upcoming",
            "tasks": [
                {"title": "Thiết lập mục tiêu 6 tháng tới theo mô hình OKR", "type": "core"},
                {"title": "Nghe podcast Quản trị Năng lượng của Andrew Huberman", "type": "supplementary"}
            ]
        }
    ]
    for w in range(3, 13):
        phase = "relearn" if w <= 6 else "execute"
        fallback_syllabus.append({
            "id": f"w{w}",
            "cohort_id": "cohort_04",
            "week": w,
            "phase": phase,
            "title": f"Chặng {w}: Vận hành thực chiến | Execution Cycle {w}" if phase == "execute" else f"Chặng {w}: Tích hợp Kiến thức | Cognitive Integration {w}",
            "description": f"Vận hành chu trình thực tế, tối ưu hóa hiệu suất và nhận phản hồi Socratic từ Coach ở tuần thứ {w}.",
            "status": "upcoming",
            "tasks": [
                {"title": f"Thực hiện chu trình PDCA tuần thứ {w}", "type": "core"},
                {"title": f"Ghi nhật ký chiêm nghiệm sâu sắc tuần {w}", "type": "supplementary"}
            ]
        })
    return fallback_syllabus

def update_cohort_syllabus_week(cohort_id: str, week: int, week_data: Dict[str, Any]) -> bool:
    db = load_cohort_db()
    syllabus = db.setdefault("syllabus", [])
    updated = False
    for s in syllabus:
        if s.get("cohort_id") == cohort_id and s.get("week") == week:
            for k, v in week_data.items():
                s[k] = v
            updated = True
            break
    if not updated:
        payload = week_data.copy()
        payload["cohort_id"] = cohort_id
        payload["week"] = week
        payload["phase"] = "relearn" if week > 1 else "unlearn"
        payload["status"] = "upcoming"
        syllabus.append(payload)
    save_cohort_db(db)
    return True

def get_analytics_assessments(username: str) -> List[Dict[str, Any]]:
    return []

def submit_analytics_assessment(username: str, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
    return {}

def reset_analytics_assessments(username: str) -> bool:
    return True
