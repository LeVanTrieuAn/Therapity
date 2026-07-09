import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

CMS_BASE_URL = os.getenv("CMS_BASE_URL", "http://localhost:13000/api")
CMS_API_KEY = os.getenv("CMS_API_KEY")

headers = {
    "Authorization": f"Bearer {CMS_API_KEY}",
    "Content-Type": "application/json"
}

def get_active_llm_config() -> Dict[str, Any]:
    """
    Fetches the active LLM Provider from the CMS where ai_provider is true.
    Returns a dictionary of configuration to pass to the AI functions.
    Does NOT cache the result as requested by the user.
    """
    try:
        import json
        res = request_cms("GET", "/llm_provider", params={
            "filter": json.dumps({"ai_provider": True}),
            "limit": 1
        })
        providers = res.get("data", [])
        if providers:
            provider = providers[0]
            config = {}
            if provider.get("name_model"):
                config["model"] = provider["name_model"]
            if provider.get("max_token") is not None:
                config["max_tokens"] = provider["max_token"]
            if provider.get("temperature") is not None:
                config["temperature"] = provider["temperature"]
            if provider.get("top_p") is not None:
                config["top_p"] = provider["top_p"]
            if provider.get("top_k"):
                config["top_k"] = provider["top_k"]
            if provider.get("stream") is not None:
                config["stream"] = provider["stream"]
            return config
    except Exception as e:
        print(f"[CMS HELPER] Failed to fetch LLM config: {e}")
    return {}

def sync_active_model_to_cms(active_model: str):
    """
    Tự động cập nhật cột ai_provider trên CMS dựa theo model đang chạy dưới code.
    """
    try:
        import json
        res = request_cms("GET", "/llm_provider", params={"limit": 50})
        providers = res.get("data", [])
        for p in providers:
            p_id = p.get("id")
            name_model = p.get("name_model")
            
            # Kiểm tra xem dòng này có phải model đang chạy không
            is_active = (name_model == active_model)
            
            # Trạng thái hiện tại trên CMS
            current_status = bool(p.get("ai_provider"))
            
            # Nếu trạng thái sai lệch thì cập nhật lại
            if is_active != current_status:
                payload = {"ai_provider": True if is_active else None}
                request_cms("PATCH", f"/llm_provider/{p_id}", params={"filterByTk": p_id}, json_data=payload)
    except Exception as e:
        print(f"[CMS HELPER] Failed to sync active model to CMS: {e}")

def count_tokens(text: str, model_name: Optional[str] = None) -> int:
    """
    Counts the number of tokens in a text using the tiktoken library.
    Falls back to len(text) // 4 if tiktoken is not available or fails.
    """
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
    url = f"{CMS_BASE_URL}/auth:signIn"
    payload = {"account": email, "password": password}
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            return True, ""
        else:
            err_msg = ""
            try:
                data = response.json()
                if "errors" in data and len(data["errors"]) > 0:
                    err_msg = data["errors"][0].get("message", "")
                import os
                debug_path = os.path.join(os.path.dirname(__file__), "..", "database", "debug_login.txt")
                with open(debug_path, "a", encoding="utf-8") as f:
                    f.write(f"Auth failed for {url} with {payload}. Status: {response.status_code}, Body: {response.text}\n")
            except:
                pass
            return False, err_msg
    except Exception as e:
        try:
            import os
            debug_path = os.path.join(os.path.dirname(__file__), "..", "database", "debug_login.txt")
            with open(debug_path, "a", encoding="utf-8") as f:
                f.write(f"Exception during auth try at {url}: {e}\n")
        except:
            pass
        return False, str(e)

def request_cms(method: str, endpoint: str, json_data: Any = None, params: Any = None) -> Any:
    # Map REST endpoints dynamically to Digiforce/NocoBase specific actions according to api.md
    mapped_endpoint = endpoint
    
    # Strip leading/trailing slashes for parsing
    clean_path = endpoint.strip("/")
    parts = clean_path.split("/")
    
    # Check if this is a collection-level or record-level URL
    if len(parts) == 1:
        # e.g. GET /users -> GET /users:list
        # e.g. POST /users -> POST /users:create
        collection = parts[0]
        if method.upper() == "GET":
            mapped_endpoint = f"/{collection}:list"
        elif method.upper() == "POST":
            mapped_endpoint = f"/{collection}:create"
    elif len(parts) == 2:
        # e.g. GET /users/123 -> GET /users:get (using query params filterByTk=123)
        # e.g. PATCH /users/123 -> POST /users:update (using query params filterByTk=123)
        # e.g. DELETE /users/123 -> POST /users:destroy (using query params filterByTk=123)
        collection, record_id = parts[0], parts[1]
        
        # Don't translate attachments:create
        if collection != "attachments":
            if params is None:
                params = {}
            params["filterByTk"] = record_id
            
            if method.upper() == "GET":
                mapped_endpoint = f"/{collection}"
                import json
                params.pop("filterByTk", None) # Remove filterByTk for GET
                
                # If there's an existing filter string, we could try to merge, but simple cases just overwrite or use id
                existing_filter = params.get("filter", "{}")
                
                parsed_id = int(record_id) if record_id.isdigit() else record_id
                
                try:
                    f_dict = json.loads(existing_filter) if isinstance(existing_filter, str) else existing_filter
                    f_dict["id"] = parsed_id
                    params["filter"] = json.dumps(f_dict)
                except Exception:
                    params["filter"] = json.dumps({"id": parsed_id})
                    
            elif method.upper() in ["PATCH", "PUT", "POST"]:
                mapped_endpoint = f"/{collection}:update"
                method = "POST" # NocoBase :update action expects POST
            elif method.upper() == "DELETE":
                mapped_endpoint = f"/{collection}:destroy"
                method = "POST" # NocoBase :destroy action expects POST

    if mapped_endpoint and (mapped_endpoint.endswith(":update") or mapped_endpoint.endswith(":destroy")) and params and "filterByTk" in params:
        params["filterByTargetKey"] = params.pop("filterByTk")

    url = f"{CMS_BASE_URL}{mapped_endpoint}"
    
    # Add cache-busting timestamp for GET requests to bypass Nginx cache
    if method.upper() == "GET":
        import time
        if params is None:
            params = {}
        params["_t"] = int(time.time() * 1000)

    try:
        response = requests.request(method, url, headers=headers, json=json_data, params=params, timeout=30)
        if response.status_code in [204, 205]:
            return None
        response.raise_for_status()
        return response.json()
    except Exception as e:
        if 'response' in locals() and response is not None:
            print(f"[CMS ERROR DETAILS] Status: {response.status_code}, Body: {response.text}")
        print(f"[CMS ERROR] {method} {url} failed: {e}")
        raise e

def onboarding_text_to_dict(val: Any) -> Dict[str, Any]:
    if isinstance(val, dict):
        return val
    if not isinstance(val, str) or not val.strip():
        return {}
    
    # Try if it's actually valid JSON string (legacy or fallback support)
    try:
        import json
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
        if not line:
            continue
        if ":" not in line:
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
                import json
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
        import json
        cache_str = json.dumps(data.get("_mindset_cache"), ensure_ascii=False)
        lines.append(f"Mindset cache: {cache_str}")
        
    return "\n".join(lines)

# --- USERS METHODS ---

def extract_attachment_url(val: Any) -> str:
    if not val:
        return ""
    # If it is a string and represents a JSON list or object
    if isinstance(val, str):
        val = val.strip()
        if val.startswith("[") or val.startswith("{"):
            try:
                import json
                val = json.loads(val)
            except Exception:
                pass

    # If it is a list of attachments
    if isinstance(val, list):
        if len(val) > 0:
            first = val[0]
            if isinstance(first, dict):
                url = first.get("url") or first.get("path") or ""
                # Resolve relative URL
                if url and not url.startswith("http"):
                    from urllib.parse import urlparse
                    parsed_url = urlparse(CMS_BASE_URL)
                    cms_origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    if url.startswith("/"):
                        return f"{cms_origin}{url}"
                    else:
                        return f"{cms_origin}/{url}"
                return url or ""
            elif isinstance(first, str):
                return first
        return ""

    # If it is a dictionary representing a single attachment
    if isinstance(val, dict):
        url = val.get("url") or val.get("path") or ""
        if url and not url.startswith("http"):
            from urllib.parse import urlparse
            parsed_url = urlparse(CMS_BASE_URL)
            cms_origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
            if url.startswith("/"):
                return f"{cms_origin}{url}"
            else:
                return f"{cms_origin}/{url}"
        return url or ""

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
        
        files = {
            "file": (filename, image_data, f"image/{ext}")
        }
        
        url = f"{CMS_BASE_URL}/attachments:create"
        response = requests.post(url, headers={"Authorization": f"Bearer {CMS_API_KEY}"}, files=files, timeout=15)
        response.raise_for_status()
        
        res_data = response.json().get("data", {})
        return res_data
    except Exception as e:
        print(f"[UPLOAD ATTACHMENT ERROR] Failed to upload attachment: {e}")
        
    return None

def upload_base64_image(base64_str: str) -> str:
    if not base64_str or not isinstance(base64_str, str) or not base64_str.startswith("data:image/"):
        return base64_str
        
    try:
        import base64
        import re
        import uuid
        from urllib.parse import urlparse
        
        meta, data = base64_str.split(",", 1)
        match = re.search(r"data:image/(\w+);base64", meta)
        ext = match.group(1) if match else "png"
        
        image_data = base64.b64decode(data)
        filename = f"upload_{uuid.uuid4().hex}.{ext}"
        
        parsed_url = urlparse(CMS_BASE_URL)
        cms_origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        files = {
            "file": (filename, image_data, f"image/{ext}")
        }
        
        url = f"{CMS_BASE_URL}/attachments:create"
        response = requests.post(url, headers={"Authorization": f"Bearer {CMS_API_KEY}"}, files=files, timeout=15)
        response.raise_for_status()
        
        res_data = response.json().get("data", {})
        relative_path = res_data.get("url", "")
        if relative_path:
            return f"{cms_origin}{relative_path}"
    except Exception as e:
        print(f"[UPLOAD BASE64 ERROR] Failed to upload image to CMS: {e}")
        
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
                import json
                parsed = json.loads(val)
                if isinstance(parsed, list):
                    return [str(x) for x in parsed if x]
            except:
                pass
        return [x.strip() for x in val.split(",") if x.strip()]
    return []

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    try:
        import json
        res = request_cms("GET", f"/users", params={
            "filter": json.dumps({"username": username}),
            "appends": ["user_avatar", "user_banner"]
        })
        users = res.get("data", [])
        if not users and "@" in username:
            res = request_cms("GET", f"/users", params={
                "filter": json.dumps({"email": username}),
                "appends": ["user_avatar", "user_banner"]
            })
            users = res.get("data", [])
        if users:
            user = users[0]
            # Map CMS camelCase back to frontend expected snake_case/boolean
            return {
                "id": user.get("id"),
                "username": user.get("username"),
                "email": user.get("email"),
                "phone": user.get("phone"),
                "password": user.get("password"),
                "displayName": sanitize_display_name(user.get("displayname"), user.get("username")),
                "bio": user.get("bio", ""),
                "avatar": extract_attachment_url(user.get("user_avatar")),
                "banner": extract_attachment_url(user.get("user_banner")),
                "following_list": parse_following_list(user.get("followingList")),
                "onboarded": user.get("onboarded") == "true",
                "onboarding": onboarding_text_to_dict(user.get("onboardingData"))
            }
    except Exception:
        pass
    return None

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    try:
        import json
        res = request_cms("GET", f"/users", params={
            "filter": json.dumps({"email": email}),
            "appends": ["user_avatar", "user_banner"]
        })
        users = res.get("data", [])
        if users:
            user = users[0]
            return {
                "id": user.get("id"),
                "username": user.get("username"),
                "email": user.get("email"),
                "phone": user.get("phone"),
                "password": user.get("password"),
                "displayName": sanitize_display_name(user.get("displayname"), user.get("username")),
                "bio": user.get("bio", ""),
                "avatar": extract_attachment_url(user.get("user_avatar")),
                "banner": extract_attachment_url(user.get("user_banner")),
                "following_list": parse_following_list(user.get("followingList")),
                "onboarded": user.get("onboarded") == "true",
                "onboarding": onboarding_text_to_dict(user.get("onboardingData"))
            }
    except Exception:
        pass
    return None

def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    payload = {
        "username": user_data.get("username"),
        "password": user_data.get("password"),
        "email": user_data.get("email"),
        "displayname": user_data.get("displayName", user_data.get("username")),
        "bio": user_data.get("bio", ""),
        "followingList": user_data.get("following_list", []),
        "onboardingData": dict_to_onboarding_text(user_data.get("onboarding")),
        "onboarded": "true" if user_data.get("onboarded") else "false"
    }
    if "phone" in user_data:
        payload["phone"] = user_data["phone"]
        
    avatar_attachment = upload_attachment(user_data.get("avatar", ""))
    if avatar_attachment:
        payload["user_avatar"] = [avatar_attachment]
    else:
        payload["user_avatar"] = []
        
    banner_attachment = upload_attachment(user_data.get("banner", ""))
    if banner_attachment:
        payload["user_banner"] = [banner_attachment]
    else:
        payload["user_banner"] = []
        
    res = request_cms("POST", "/users", json_data=payload)
    return res.get("data", {})

def update_user(user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
    payload = {}
    if "username" in user_data:
        payload["username"] = user_data["username"]
    if "password" in user_data:
        payload["password"] = user_data["password"]
    if "email" in user_data:
        payload["email"] = user_data["email"]
    if "phone" in user_data:
        payload["phone"] = user_data["phone"]
    if "displayName" in user_data:
        payload["displayname"] = user_data["displayName"]
    if "bio" in user_data:
        payload["bio"] = user_data["bio"]
    if "following_list" in user_data:
        payload["followingList"] = user_data["following_list"]
    if "onboarding" in user_data:
        payload["onboardingData"] = dict_to_onboarding_text(user_data["onboarding"])
        payload["onboarded"] = "true" if user_data["onboarding"] else "false"
    if "onboarded" in user_data:
        payload["onboarded"] = "true" if user_data["onboarded"] else "false"
        
    if "avatar" in user_data:
        avatar_val = user_data["avatar"]
        if avatar_val == "":
            payload["user_avatar"] = []
        elif isinstance(avatar_val, str) and avatar_val.startswith("data:image/"):
            avatar_attachment = upload_attachment(avatar_val)
            if avatar_attachment:
                payload["user_avatar"] = [avatar_attachment]
                
    if "banner" in user_data:
        banner_val = user_data["banner"]
        if banner_val == "":
            payload["user_banner"] = []
        elif isinstance(banner_val, str) and banner_val.startswith("data:image/"):
            banner_attachment = upload_attachment(banner_val)
            if banner_attachment:
                payload["user_banner"] = [banner_attachment]
        
    res = request_cms("PATCH", f"/users/{user_id}", params={"filterByTk": user_id}, json_data=payload)
    return res.get("data", {})

def delete_user(user_id: int) -> bool:
    try:
        import json
        user_id_int = int(user_id)
        
        # 1. Cascade-delete personal_roadmaps first
        try:
            res = request_cms("GET", "/personal_roadmaps", params={"filter": json.dumps({"fk_user": user_id_int}), "limit": 100})
            roadmaps = res.get("data", [])
            for r in roadmaps:
                rid = r.get("id")
                if rid:
                    request_cms("DELETE", f"/personal_roadmaps/{rid}", params={"filterByTk": rid})
        except Exception as e:
            print(f"[CASCADE DELETE] Failed to delete personal roadmaps for user {user_id}: {e}")
            
        # 2. Cascade-delete diary_entries
        try:
            res = request_cms("GET", "/diary_entries", params={"filter": json.dumps({"fk_user": user_id_int}), "limit": 200})
            entries = res.get("data", [])
            for entry in entries:
                eid = entry.get("id")
                if eid:
                    request_cms("DELETE", f"/diary_entries/{eid}", params={"filterByTk": eid})
        except Exception as e:
            print(f"[CASCADE DELETE] Failed to delete diary entries for user {user_id}: {e}")
            
        # 3. Cascade-delete tasks
        try:
            res = request_cms("GET", "/tasks", params={"filter": json.dumps({"fk_user": user_id_int}), "limit": 200})
            tasks = res.get("data", [])
            for t in tasks:
                tid = t.get("id")
                if tid:
                    request_cms("DELETE", f"/tasks/{tid}", params={"filterByTk": tid})
        except Exception as e:
            print(f"[CASCADE DELETE] Failed to delete tasks for user {user_id}: {e}")

        # 4. Cascade-delete chat_sessions (which also cascade deletes chat_logs!)
        try:
            res = request_cms("GET", "/chat_sessions", params={"filter": json.dumps({"fk_user": user_id_int}), "limit": 500})
            sessions = res.get("data", [])
            for s in sessions:
                sid = s.get("id")
                if sid:
                    delete_chat_session(str(sid))
        except Exception as e:
            print(f"[CASCADE DELETE] Failed to delete chat sessions for user {user_id}: {e}")

        # 5. Cascade-delete aoa_comments created by user
        try:
            res = request_cms("GET", "/aoa_comments", params={"filter": json.dumps({"fk_author": user_id_int}), "limit": 500})
            comments = res.get("data", [])
            for c in comments:
                cid = c.get("id")
                if cid:
                    request_cms("DELETE", f"/aoa_comments/{cid}", params={"filterByTk": cid})
        except Exception as e:
            print(f"[CASCADE DELETE] Failed to delete AOA comments for user {user_id}: {e}")

        # 6. Cascade-delete aoa_posts (which also deletes comments on those posts!)
        try:
            res = request_cms("GET", "/aoa_posts", params={"filter": json.dumps({"fk_author": user_id_int}), "limit": 200})
            posts = res.get("data", [])
            for p in posts:
                pid = p.get("id")
                if pid:
                    delete_aoa_post(str(pid))
        except Exception as e:
            print(f"[CASCADE DELETE] Failed to delete AOA posts for user {user_id}: {e}")

        # 7. Finally delete the user
        request_cms("DELETE", f"/users/{user_id}", params={"filterByTk": user_id})
        return True
    except Exception as e:
        print(f"Failed to delete user {user_id}: {e}")
        return False

# --- CHAT SESSIONS METHODS ---

def get_chat_sessions(username: Optional[str] = None) -> Dict[str, Any]:
    try:
        import json
        params = {"limit": 500}
        if username:
            user_info = get_user_by_username(username)
            if not user_info:
                return {}
            params["filter"] = json.dumps({
                "$or": [
                    {"fk_user": user_info["id"]},
                    {"relation_chat_sessions_users.id": user_info["id"]},
                    {"createdById": user_info["id"]}
                ]
            })
        res = request_cms("GET", f"/chat_sessions", params=params)
        sessions = res.get("data", [])
        
        # Build a map of user_id -> username to resolve s.relation_chat_sessions_users or fk_user
        user_map = {}
        user_ids = set()
        for s in sessions:
            rel = s.get("relation_chat_sessions_users")
            # Extract from relation dict if expanded
            if isinstance(rel, dict):
                r_id = rel.get("id")
                r_name = rel.get("username") or rel.get("email")
                if r_id and r_name:
                    user_map[int(r_id)] = r_name
            
            uid = s.get("fk_user") or s.get("createdById")
            if not uid and isinstance(rel, dict):
                uid = rel.get("id")
                
            if uid and isinstance(uid, (int, str)):
                try:
                    user_ids.add(int(uid))
                except:
                    pass
                    
        if user_ids:
            try:
                res_users = request_cms("GET", "/users", params={
                    "filter": json.dumps({"id": {"$in": list(user_ids)}}),
                    "limit": 100
                })
                users_data = res_users.get("data", [])
                for u in users_data:
                    u_id = u.get("id")
                    u_name = u.get("username") or u.get("email") or ""
                    if u_id and u_name:
                        user_map[int(u_id)] = u_name
            except Exception as ue:
                print(f"Failed to bulk fetch user profiles for chat sessions: {ue}")

        result = {}
        for s in sessions:
            s_id = str(s.get("id"))
            
            # Reconstruct username property
            resolved_username = ""
            rel = s.get("relation_chat_sessions_users")
            uid = s.get("fk_user") or s.get("createdById")
            if not uid and isinstance(rel, dict):
                uid = rel.get("id")
                
            if uid:
                try:
                    resolved_username = user_map.get(int(uid), "")
                except:
                    pass
            if not resolved_username and isinstance(rel, dict):
                resolved_username = rel.get("username") or rel.get("email") or ""
            if not resolved_username and username:
                resolved_username = username
            
            # Security explicit filter: Ensure session actually belongs to the requesting user
            if username and resolved_username != username and resolved_username != user_info.get("email", ""):
                continue
                
            # 1. Primary: Reconstruct chat_history from graph_data column
            chat_history = []
            
            raw_graph = s.get("graph_data")
            graph_data = {"nodes": [], "edges": []}
            if raw_graph:
                if isinstance(raw_graph, str) and raw_graph.strip().startswith("{"):
                    try:
                        graph_data = json.loads(raw_graph)
                    except Exception:
                        pass
                elif isinstance(raw_graph, dict):
                    graph_data = raw_graph
                    
            if isinstance(graph_data, dict):
                chat_history = graph_data.get("chat_history", [])
                suggested_replies = graph_data.get("suggested_replies", [])
                # Strip out chat_history and suggested_replies from graph_data so the frontend gets a clean mind map
                if "chat_history" in graph_data:
                    graph_data = {k: v for k, v in graph_data.items() if k != "chat_history"}
                if "suggested_replies" in graph_data:
                    graph_data = {k: v for k, v in graph_data.items() if k != "suggested_replies"}
            
            # 2. Fallback A: Reconstruct from message_content (legacy format or double line fallback)
            if not chat_history:
                msg_content = s.get("message_content")
                if msg_content:
                    if isinstance(msg_content, list):
                        chat_history = msg_content
                    elif isinstance(msg_content, str):
                        if "<!--JSON:" in msg_content:
                            try:
                                json_part = msg_content.split("<!--JSON:")[1].split("-->")[0].strip()
                                chat_history = json.loads(json_part)
                            except Exception:
                                pass
                        
                        if not chat_history and msg_content.strip().startswith("["):
                            try:
                                chat_history = json.loads(msg_content)
                            except Exception:
                                pass
                        
                        # Double fallback to parsing human-readable format line-by-line
                        if not chat_history:
                            try:
                                lines = msg_content.splitlines()
                                for line in lines:
                                    line = line.strip()
                                    if line.startswith("AI:"):
                                        content = line[3:].strip().strip('"')
                                        chat_history.append({"role": "model", "content": content})
                                    elif line.startswith("Người dùng:"):
                                        content = line[11:].strip().strip('"')
                                        chat_history.append({"role": "user", "content": content})
                            except Exception:
                                pass
            
            # 3. Fallback B: Fetch chat logs if message_content was empty or unparseable
            if not chat_history:
                try:
                    logs_res = request_cms("GET", "/chat_logs", params={
                        "filter": json.dumps({"session_id": s_id}),
                        "sort": "id",  # Snowflake ID is chronological
                        "limit": 500
                    })
                    logs_data = logs_res.get("data", [])
                    for log_item in logs_data:
                        chat_history.append({
                            "role": "user" if log_item.get("Role") == "user" else "model",
                            "content": log_item.get("message_content", ""),
                            "reasoning": log_item.get("reasoning", ""),
                            "token_used": log_item.get("token_used"),
                            "model_used": log_item.get("model_used")
                        })
                except Exception as log_err:
                    print(f"Failed to fetch fallback chat logs for session {s_id}: {log_err}")
                
            raw_tasks = s.get("tasks")
            parsed_legacy_tasks = json.loads(raw_tasks) if isinstance(raw_tasks, str) and raw_tasks.strip().startswith("[") else (raw_tasks if isinstance(raw_tasks, list) else [])
            
            result[s_id] = {
                "id": s_id,
                "username": resolved_username,
                "chat_history": chat_history,
                "graph_data": graph_data,
                "tasks": graph_data.get("tasks", parsed_legacy_tasks),
                "has_new_task": s.get("has_new_task") == "true",
                "custom_title": s.get("custom_title", s.get("customTitle", "")),
                "token_used": s.get("token_used") or 0,
                "model_used": s.get("model_used") or "",
                "created_at": s.get("createdAt"),
                "voice": s.get("voice", ""),
                "suggested_replies": suggested_replies
            }
        return result
    except Exception:
        return {}

def save_chat_session(session_id: str, username: str, chat_data: Dict[str, Any]) -> Dict[str, Any]:
    import json
    # Check if session already exists by querying ID
    existing = None
    if session_id and not session_id.startswith("temp_"):
        try:
            res = request_cms("GET", f"/chat_sessions/{session_id}")
            existing = res.get("data")
        except Exception:
            pass
            
    user_info = get_user_by_username(username)
    if not user_info:
        raise ValueError(f"User {username} not found")
    user_id = user_info["id"]
    # Format the human-readable text for users (excluding reasoning, title, isWelcome, isTyped)
    chat_history = chat_data.get("chat_history", [])
    
    formatted_lines = []
    for msg in chat_history:
        role_label = "AI" if msg.get("role") == "model" else "Người dùng"
        content = msg.get("content", "")
        formatted_lines.append(f'{role_label}: "{content}"')
        voice_url = msg.get("voiceUrl")
        if voice_url:
            formatted_lines.append(f'Âm thanh: "{voice_url}"')
    
    # Strictly clean! The HTML JSON comment is completely hidden/removed from message_content!
    message_content_str = "\n".join(formatted_lines)

    # Embed complete chat history inside graph_data to maintain perfect developer-fidelity invisibly!
    graph_data_val = chat_data.get("graph_data", {"nodes": [], "edges": []})
    if isinstance(graph_data_val, str) and graph_data_val.strip().startswith("{"):
        try:
            graph_data_val = json.loads(graph_data_val)
        except Exception:
            pass
    if not isinstance(graph_data_val, dict):
        graph_data_val = {"nodes": [], "edges": []}
    
    # Store complete chat history array, tasks and suggested replies inside graph_data JSON
    graph_data_val["chat_history"] = chat_history
    raw_tasks = chat_data.get("tasks", [])
    graph_data_val["tasks"] = raw_tasks
    suggested_replies = chat_data.get("suggested_replies", [])
    graph_data_val["suggested_replies"] = suggested_replies
    serialized_graph_data = json.dumps(graph_data_val, ensure_ascii=False)

    formatted_tasks = []
    if isinstance(raw_tasks, list):
        for idx, t in enumerate(raw_tasks):
            if not isinstance(t, dict): continue
            t_title = t.get("content_vi") or t.get("content_en") or t.get("content") or t.get("title") or ""
            t_desc = t.get("goal_vi") or t.get("goal_en") or t.get("goal") or ""
            if "|||" in str(t_title):
                t_title = str(t_title).split("|||")[0].strip()
            if "|||" in str(t_desc):
                t_desc = str(t_desc).split("|||")[0].strip()
                
            t_status = t.get("current_status", "done" if t.get("completed") else "backlog")
            t_deadline = t.get("deadline", "Không có")
            
            task_str = f"--- Nhiệm vụ {idx+1} ---\n"
            task_str += f"Title: {t_title}\n"
            task_str += f"Description: {t_desc}\n"
            task_str += f"Status: {t_status}\n"
            task_str += f"Deadline: {t_deadline}"
            
            subtasks = t.get("subtasks", [])
            if subtasks and isinstance(subtasks, list):
                task_str += "\nSubtask:\n"
                for s in subtasks:
                    s_title = s.get("title", "") if isinstance(s, dict) else str(s)
                    if "|||" in str(s_title):
                        s_title = str(s_title).split("|||")[0].strip()
                    is_completed = s.get("completed") if isinstance(s, dict) else False
                    checkbox = "[x]" if is_completed else "[ ]"
                    task_str += f"  {checkbox} {s_title}\n"
            
            formatted_tasks.append(task_str)
            
    tasks_text_payload = "\n\n".join(formatted_tasks) if formatted_tasks else ""


    # Extract custom_title from title if not set
    custom_title = chat_data.get("custom_title", chat_data.get("customTitle", ""))
    if not custom_title:
        for msg in chat_history:
            if isinstance(msg, dict) and msg.get("title"):
                custom_title = msg.get("title")
                break

    payload = {
        # REMOVED deprecated "username" column
        "chat_history": [],  # Kept empty in sessions column since we use chat_logs
        "graph_data": serialized_graph_data,
        "tasks": tasks_text_payload,
        "has_new_task": "true" if chat_data.get("has_new_task") else "false",
        "custom_title": custom_title,
        "message_content": message_content_str,
        "token_used": int(chat_data.get("token_used", 0)) if chat_data.get("token_used") is not None else 0,
        "model_used": str(chat_data.get("model_used", "")) if chat_data.get("model_used") is not None else "",
        "voice": str(chat_data.get("voice", "")) if chat_data.get("voice") is not None else "",
        "fk_user": user_id,
        "relation_chat_sessions_users": user_id
    }

    if existing:
        res = request_cms("PATCH", f"/chat_sessions/{session_id}", params={"filterByTk": session_id}, json_data=payload)
    else:
        # If it is a string session ID but not a snowflake, we let the CMS generate a snowflake ID
        if session_id and not session_id.startswith("temp_") and session_id.isdigit():
            payload["id"] = int(session_id)
        res = request_cms("POST", "/chat_sessions", json_data=payload)
        
    saved_session = res.get("data", {})
    if isinstance(saved_session, list):
        saved_session = saved_session[0] if saved_session else {}
    actual_session_id = str(saved_session.get("id", session_id))

    # --- SAVE FLAT MESSAGES TO CHAT_LOGS (Nice-to-have relational backup) ---
    # Disabled temporarily to prevent severe performance bottlenecks and API timeouts
    # where N messages cause 2N sequential HTTP requests to the CMS.
    # The full chat_history is already safely stored in graph_data JSON.
    pass
    return saved_session

def delete_chat_session(session_id: str) -> bool:
    if not session_id or str(session_id).startswith("temp_"):
        return True
    try:
        # Cascade-delete chat logs for this session first
        try:
            import json
            logs_res = request_cms("GET", "/chat_logs", params={"filter": json.dumps({"session_id": str(session_id)}), "limit": 1000})
            existing_logs = logs_res.get("data", [])
            for log_item in existing_logs:
                log_id = log_item.get("id")
                if log_id:
                    request_cms("DELETE", f"/chat_logs/{log_id}", params={"filterByTk": log_id})
        except Exception as e:
            print(f"[CASCADE ERROR] Failed to clean logs during session deletion: {e}")

        request_cms("DELETE", f"/chat_sessions/{session_id}", params={"filterByTk": session_id})
        return True
    except Exception as del_err:
        import traceback
        with open("delete_error.log", "a", encoding="utf-8") as f:
            f.write(f"Failed to delete {session_id}: {del_err}\n{traceback.format_exc()}\n")
        return False

# --- DIARY ENTRIES & FOLDERS METHODS ---

def get_diary_entries(username: str) -> List[Dict[str, Any]]:
    try:
        import json
        user_info = get_user_by_username(username)
        if not user_info:
            return []
        res = request_cms("GET", f"/diary_entries", params={
            "filter": json.dumps({"fk_user": user_info["id"]}),
            "sort": "-date",
            "limit": 500
        })
        entries = res.get("data", [])
        return [
            {
                "id": str(entry.get("id")),
                "title": entry.get("title", ""),
                "content": entry.get("content", ""),
                "mood": "Calm", # Mocked as it is not in the CMS schema
                "folder": entry.get("folder", ""),
                "date": entry.get("date", ""),
                "ai_insight": entry.get("aiInsight", "")
            }
            for entry in entries
        ]
    except Exception:
        return []

def save_diary_entry(entry_id: str, username: str, entry_data: Dict[str, Any]) -> Dict[str, Any]:
    existing = None
    if entry_id and not entry_id.startswith("temp_"):
        try:
            res = request_cms("GET", f"/diary_entries/{entry_id}")
            existing = res.get("data")
        except Exception:
            pass

    user_info = get_user_by_username(username)
    if not user_info:
        raise ValueError(f"User {username} not found")
    user_id = user_info["id"]

    date_val = entry_data.get("date", "")
    if date_val:
        if " " in date_val:
            date_val = date_val.replace(" ", "T")
        if not date_val.endswith("Z") and "+" not in date_val:
            date_val += "Z"
    else:
        import datetime
        date_val = datetime.datetime.now().isoformat() + "Z"

    payload = {
        # REMOVED deprecated "username" column
        "title": entry_data.get("title", ""),
        "content": entry_data.get("content", ""),
        "folder": entry_data.get("folder", ""),
        "aiInsight": entry_data.get("ai_insight", ""),
        "date": date_val,
        "fk_user": user_id,
        "Relation_Diary_Entries_Users": user_id
    }

    if existing:
        res = request_cms("PATCH", f"/diary_entries/{entry_id}", params={"filterByTk": entry_id}, json_data=payload)
    else:
        if entry_id and not entry_id.startswith("temp_") and entry_id.isdigit():
            payload["id"] = int(entry_id)
        res = request_cms("POST", "/diary_entries", json_data=payload)
        
    data = res.get("data", {})
    if isinstance(data, list):
        data = data[0] if data else {}
    return {
        "id": str(data.get("id")),
        "title": data.get("title", ""),
        "content": data.get("content", ""),
        "mood": "Calm",
        "folder": data.get("folder", ""),
        "date": data.get("date", ""),
        "ai_insight": data.get("aiInsight", "")
    }

def delete_diary_entry(entry_id: str) -> bool:
    try:
        request_cms("DELETE", f"/diary_entries/{entry_id}", params={"filterByTk": entry_id})
        return True
    except Exception:
        return False

def get_diary_folders(username: str) -> List[str]:
    try:
        import json
        user_info = get_user_by_username(username)
        if not user_info:
            return []
        res = request_cms("GET", f"/diary_folders", params={
            "filter": json.dumps({"fk_user": user_info["id"]}),
            "limit": 100
        })
        folders = res.get("data", [])
        return [f.get("name") for f in folders if f.get("name")]
    except Exception:
        return []

def create_diary_folder(username: str, folder_name: str) -> bool:
    existing_folders = get_diary_folders(username)
    if folder_name in existing_folders:
        return True
        
    user_info = get_user_by_username(username)
    if not user_info:
        return False
    user_id = user_info["id"]
        
    payload = {
        # REMOVED deprecated "username" column
        "name": folder_name,
        "fk_user": user_id,
        "Relation_Diary_Folders_User": user_id
    }
        
    try:
        request_cms("POST", "/diary_folders", json_data=payload)
        return True
    except Exception:
        return False

def delete_diary_folder(username: str, folder_name: str) -> bool:
    try:
        import json
        user_info = get_user_by_username(username)
        if not user_info:
            return False
        res = request_cms("GET", f"/diary_folders", params={
            "filter": json.dumps({"fk_user": user_info["id"], "name": folder_name})
        })
        folders = res.get("data", [])
        for f in folders:
            request_cms("DELETE", f"/diary_folders/{f['id']}", params={"filterByTk": f['id']})
        return True
    except Exception:
        return False

# --- AOA POSTS & COMMENTS METHODS ---

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
    """
    Converts a content dictionary or string into a clean plain text format for database storage.
    """
    if isinstance(content, dict):
        return content.get("vi", "").strip() or content.get("en", "").strip()
    return str(content).strip()

def deserialize_aoa_content(content_str: str) -> str:
    """
    Parses plain text, legacy JSON format, or Tiếng Việt/Tiếng Anh markers back into a single plain text string for the frontend.
    """
    if not content_str:
        return ""
        
    content_str = content_str.strip()
    
    # 1. Handle legacy JSON format first
    if content_str.startswith("{"):
        import json
        try:
            parsed = json.loads(content_str)
            if isinstance(parsed, dict):
                return parsed.get("vi", parsed.get("en", "")).strip()
        except:
            pass

    # 2. Handle legacy plain text bilingual format 'Tiếng Việt: ...\nTiếng Anh: ...'
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
    try:
        import json
        res = request_cms("GET", f"/aoa_posts", params={
            "sort": "-createdAt",
            "limit": 100
        })
        posts = res.get("data", [])
        result = []
        for p in posts:
            p_id = str(p.get("id"))
            try:
                fk_val = int(p_id) if p_id.isdigit() else p_id
            except:
                fk_val = p_id
            c_res = request_cms("GET", f"/aoa_comments", params={
                "filter": json.dumps({"fk_post": fk_val}),
                "sort": "id",
                "limit": 200
            })
            comments = c_res.get("data", [])
            
            raw_content = p.get("content", "")
            parsed_content = deserialize_aoa_content(raw_content)
                
            result.append({
                "id": p_id,
                "author_name": p.get("author_name", ""),
                "author_avatar": p.get("author_avatar", ""),
                "content": parsed_content,
                "graph_data": p.get("graph_data") or {"nodes": [], "edges": []},
                "timestamp": p.get("timestamp") or "",
                "likes": p.get("likes") or 0,
                "shares": p.get("shares") or 0,
                "post_status": p.get("post_status") or "active",
                "post_privacy": p.get("post_privacy") or "public",
                "liked_by": [],
                "comments": [
                    {
                        "author_name": c.get("author_name", ""),
                        "author_avatar": c.get("author_avatar", ""),
                        "content": deserialize_aoa_content(c.get("content", "")),
                        "timestamp": c.get("timestamp") or ""
                    }
                    for c in comments
                ]
            })
        return result
    except Exception:
        return []

def create_aoa_post(author_name: str, author_avatar: str, content: Any, graph_data: Dict[str, Any], post_privacy: str = "public") -> Dict[str, Any]:
    import datetime
    
    uploaded_avatar = upload_base64_image(author_avatar)
    content_str = serialize_aoa_content(content)
        
    payload = {
        "author_name": author_name,
        "author_avatar": uploaded_avatar,
        "content": content_str,
        "graph_data": graph_data,
        "likes": 0,
        "shares": 0,
        "timestamp": datetime.datetime.now().isoformat() + "Z",
        "post_status": "active",
        "post_privacy": post_privacy
    }
    user_info = get_user_by_username(author_name)
    if user_info:
        payload["Relation_Post_User"] = user_info["id"]
        payload["fk_author"] = user_info["id"]
        
    res = request_cms("POST", "/aoa_posts", json_data=payload)
    return res.get("data", {})

def update_aoa_post(post_id: str, post_data: Dict[str, Any]) -> Dict[str, Any]:
    payload = {}
    if "content" in post_data:
        payload["content"] = serialize_aoa_content(post_data["content"])
    if "likes" in post_data:
        payload["likes"] = post_data["likes"]
    if "shares" in post_data:
        payload["shares"] = post_data["shares"]
    if "post_status" in post_data:
        payload["post_status"] = post_data["post_status"]
    if "post_privacy" in post_data:
        payload["post_privacy"] = post_data["post_privacy"]
    if "report" in post_data:
        payload["report"] = post_data["report"]
        
    res = request_cms("PATCH", f"/aoa_posts/{post_id}", params={"filterByTk": post_id}, json_data=payload)
    return res.get("data", {})

def delete_aoa_post(post_id: str) -> bool:
    try:
        import json
        try:
            fk_val = int(post_id) if post_id.isdigit() else post_id
        except:
            fk_val = post_id
        c_res = request_cms("GET", "/aoa_comments", params={"filter": json.dumps({"fk_post": fk_val})})
        comments = c_res.get("data", [])
        for c in comments:
            request_cms("DELETE", f"/aoa_comments/{c['id']}", params={"filterByTk": c['id']})
            
        request_cms("DELETE", f"/aoa_posts/{post_id}", params={"filterByTk": post_id})
        return True
    except Exception:
        return False

def add_aoa_comment(post_id: str, author_name: str, author_avatar: str, content: Any) -> Dict[str, Any]:
    import datetime
    
    uploaded_avatar = upload_base64_image(author_avatar)
    content_str = serialize_aoa_content(content)
        
    try:
        rel_post_val = int(post_id) if post_id.isdigit() else post_id
    except:
        rel_post_val = post_id
        
    payload = {
        "Relation_AOA_Comments_Post": rel_post_val,
        "fk_post": rel_post_val,
        "author_name": author_name,
        "author_avatar": uploaded_avatar,
        "content": content_str,
        "timestamp": datetime.datetime.now().isoformat() + "Z",
        "created_at": datetime.datetime.now().isoformat() + "Z"
    }
    user_info = get_user_by_username(author_name)
    if user_info:
        payload["Relation_AOA_Users"] = user_info["id"]
        payload["fk_author"] = user_info["id"]
        
    res = request_cms("POST", "/aoa_comments", json_data=payload)
    return res.get("data", {})

# --- TASKS METHODS ---

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
            import json
            parsed = json.loads(val_stripped)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass
    res = []
    lines = val.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("Micro-steps:"):
            continue
        import re
        # 1. Match GFM task list / checklist or numbered checklist:
        # e.g., "- [ ] title", "* [x] title", "+ [ ] title", "1. [x] title"
        match_chk = re.match(r"^(?:(?:\d+\.)|[-*+])\s+\[([ xX])\]\s+(.*)$", line)
        if match_chk:
            marker = match_chk.group(1)
            content = match_chk.group(2).strip()
            if content:
                completed = True if marker in ["x", "X"] else False
                res.append({"title": content, "completed": completed})
                continue
                
        # 2. Match standard bullet/numbered list without checklist marker
        # e.g., "- title", "* title", "+ title", "1. title"
        match_simple = re.match(r"^(?:(?:\d+\.)|[-*+])\s+(.*)$", line)
        if match_simple:
            content = match_simple.group(1).strip()
            if content.startswith("[]"):
                content = content[2:].strip()
                res.append({"title": content, "completed": False})
            elif content.startswith("[x]") or content.startswith("[X]"):
                content = content[3:].strip()
                res.append({"title": content, "completed": True})
            elif content:
                res.append({"title": content, "completed": False})
            continue
            
        # 3. Fallback for non-list items
        res.append({"title": line, "completed": False})
    return res

def get_tasks(username: str) -> List[Dict[str, Any]]:
    try:
        import json
        user_info = get_user_by_username(username)
        if not user_info:
            return []
        res = request_cms("GET", f"/tasks", params={
            "filter": json.dumps({
                "$or": [
                    {"fk_user": user_info["id"]},
                    {"Relation_Tasks_Users.id": user_info["id"]}
                ]
            }),
            "limit": 500
        })
        tasks = res.get("data", [])
        filtered_tasks = []
        for t in tasks:
            uid = t.get("fk_user") or t.get("createdById")
            rel = t.get("Relation_Tasks_Users")
            if not uid and isinstance(rel, dict):
                uid = rel.get("id")
            if uid and str(uid) == str(user_info["id"]):
                filtered_tasks.append(t)
        
        return [
            {
                "id": str(t.get("id")),
                "title": t.get("title", ""),
                "goal": t.get("goal") or t.get("description") or "",
                "status": t.get("status", "backlog"),
                "deadline": t.get("deadline") or "",
                "effort": t.get("effort") or 1,
                "subtasks": deserialize_subtasks(t.get("subtasks")),
                "contextLink": t.get("contextLink") or ""
            }
            for t in filtered_tasks
        ]
    except Exception:
        return []

def create_task(username: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    import traceback
    with open('create_task_log.txt', 'a', encoding='utf-8') as f:
        f.write('CREATE TASK CALLED: ' + task_data.get('title', '') + '\\n')
        f.write(''.join(traceback.format_stack()) + '\\n')
    with open('create_task_log.txt', 'a', encoding='utf-8') as f: f.write('CREATE TASK CALLED: ' + task_data.get('title', '') + '\\n')
    user_info = get_user_by_username(username)
    if not user_info:
        raise ValueError(f"User {username} not found")
    user_id = user_info["id"]

    import json
    try:
        effort_val = int(task_data.get("effort") or 1)
    except (ValueError, TypeError):
        effort_val = 1

    payload = {
        # REMOVED deprecated "username" column
        "title": task_data.get("title", "")[:255] if task_data.get("title") else "",
        "goal": task_data.get("goal", "")[:255] if task_data.get("goal") else "",
        "description": task_data.get("goal", "")[:255] if task_data.get("goal") else "",
        "status": task_data.get("status", "backlog"),
        "deadline": task_data.get("deadline") or None,
        "effort": effort_val,
        "subtasks": serialize_subtasks(task_data.get("subtasks", [])),
        "contextLink": task_data.get("contextLink", "")[:255] if task_data.get("contextLink") else "",
        "fk_user": user_id,
        "Relation_Tasks_Users": user_id
    }
        
    task_id = task_data.get("id")
    if task_id and isinstance(task_id, str) and task_id.isdigit():
        payload["id"] = int(task_id)
        
    res = request_cms("POST", "/tasks", json_data=payload)
    data = res.get("data")
    if not data:
        data = {}
    if isinstance(data, list):
        data = data[0] if data else {}
    if not isinstance(data, dict):
        data = {}

    return {
        "id": str(data.get("id") or ""),
        "title": data.get("title", ""),
        "goal": data.get("goal") or data.get("description") or "",
        "status": data.get("status", "backlog"),
        "deadline": data.get("deadline") or "",
        "effort": data.get("effort") or 1,
        "subtasks": deserialize_subtasks(data.get("subtasks")),
        "contextLink": data.get("contextLink") or ""
    }

def update_task(task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    import json
    payload = {}
    if "title" in task_data:
        payload["title"] = task_data["title"][:255] if task_data["title"] else ""
    if "goal" in task_data:
        payload["goal"] = task_data["goal"][:255] if task_data["goal"] else ""
        payload["description"] = task_data["goal"][:255] if task_data["goal"] else ""
    if "status" in task_data:
        payload["status"] = task_data["status"]
    if "deadline" in task_data:
        payload["deadline"] = task_data["deadline"] or None
    if "effort" in task_data:
        try:
            payload["effort"] = int(task_data["effort"]) if task_data["effort"] is not None else 1
        except (ValueError, TypeError):
            payload["effort"] = 1
    if "subtasks" in task_data:
        payload["subtasks"] = serialize_subtasks(task_data["subtasks"])
    if "contextLink" in task_data:
        payload["contextLink"] = task_data["contextLink"][:255] if task_data["contextLink"] else ""
        
    res = request_cms("PATCH", f"/tasks/{task_id}", params={"filterByTk": task_id}, json_data=payload)
    data = res.get("data")
    if not data:
        data = {}
    if isinstance(data, list):
        data = data[0] if data else {}
    if not isinstance(data, dict):
        data = {}
        
    return {
        "id": str(data.get("id") or ""),
        "title": data.get("title", ""),
        "goal": data.get("goal") or data.get("description") or "",
        "status": data.get("status", "backlog"),
        "deadline": data.get("deadline") or "",
        "effort": data.get("effort") or 1,
        "subtasks": deserialize_subtasks(data.get("subtasks")),
        "contextLink": data.get("contextLink") or ""
    }

def delete_task(task_id: str) -> bool:
    try:
        request_cms("DELETE", f"/tasks/{task_id}", params={"filterByTk": task_id})
        return True
    except Exception:
        return False

# --- COHORT / ROADMAP METHODS ---

def recalculate_roadmap_progress(roadmap_id: int):
    import json
    try:
        # 1. Fetch parent roadmap record first to check if quiz has been taken
        res_road = request_cms("GET", f"/personal_roadmaps/{roadmap_id}", params={"filterByTk": roadmap_id})
        roadmap = res_road.get("data") or {}
        if isinstance(roadmap, list) and len(roadmap) > 0:
            roadmap = roadmap[0]
            
        if roadmap.get("graph_data_roadmap"):
            try:
                extra = json.loads(roadmap["graph_data_roadmap"])
                quiz = extra.get("quiz", {})
                if quiz and quiz.get("total_score") is not None:
                    # Keep the quiz total score as the progress history!
                    total_score = float(quiz.get("total_score", 0.0))
                    request_cms("PATCH", f"/personal_roadmaps/{roadmap_id}", params={"filterByTk": roadmap_id}, json_data={
                        "week_progress": total_score / 100.0
                    })
                    return
            except Exception as pe:
                print(f"Error reading quiz score: {pe}")
                
        # 2. If quiz hasn't been submitted, progress is 0.0 (do not set to task-completion percent!)
        request_cms("PATCH", f"/personal_roadmaps/{roadmap_id}", params={"filterByTk": roadmap_id}, json_data={
            "week_progress": 0.0
        })
    except Exception as e:
        print(f"Error recalculating roadmap progress for parent {roadmap_id}: {e}")

def get_cohort_members() -> List[Dict[str, Any]]:
    try:
        import json
        from datetime import datetime
        
        # 1. Fetch all parent roadmap records
        res = request_cms("GET", "/personal_roadmaps", params={"limit": 500})
        roadmaps = res.get("data", [])
        
        # Build user_map for resolving emails/usernames from user IDs
        user_map = {}
        user_ids = set()
        for r in roadmaps:
            rel = r.get("relation_roadmaps_user")
            if isinstance(rel, dict):
                r_id = rel.get("id")
                r_name = rel.get("email") or rel.get("username")
                if r_id and r_name:
                    user_map[int(r_id)] = r_name
            
            uid = r.get("fk_user") or r.get("createdById")
            if not uid and isinstance(rel, dict):
                uid = rel.get("id")
            if uid:
                try:
                    user_ids.add(int(uid))
                except:
                    pass
                    
        if user_ids:
            try:
                res_users = request_cms("GET", "/users", params={
                    "filter": json.dumps({"id": {"$in": list(user_ids)}}),
                    "limit": 100
                })
                users_data = res_users.get("data", [])
                for u in users_data:
                    u_id = u.get("id")
                    u_name = u.get("email") or u.get("username") or ""
                    if u_id and u_name:
                        user_map[int(u_id)] = u_name
            except Exception as ue:
                print(f"Failed to bulk fetch user profiles for cohort members: {ue}")

        # Group roadmap records by user
        user_roadmaps = {}
        for r in roadmaps:
            rel = r.get("relation_roadmaps_user")
            uid = r.get("fk_user") or r.get("createdById")
            if not uid and isinstance(rel, dict):
                uid = rel.get("id")
            if not uid:
                continue
            try:
                uid_int = int(uid)
            except:
                continue
            if uid_int not in user_roadmaps:
                user_roadmaps[uid_int] = []
            user_roadmaps[uid_int].append(r)

        result = []
        for uid_int, r_list in user_roadmaps.items():
            if not r_list:
                continue
            # Find the oldest roadmap record to get the start_date (Week 1)
            first_roadmap = min(r_list, key=lambda x: int(x.get("week") or 1))
            relation_user = first_roadmap.get("relation_roadmaps_user")
            created_by = first_roadmap.get("createdBy")
            
            username_val = ""
            try:
                username_val = user_map.get(uid_int, "")
            except:
                pass
            
            if not username_val:
                if isinstance(relation_user, dict):
                    username_val = relation_user.get("email") or relation_user.get("username") or ""
                elif isinstance(created_by, dict):
                    username_val = created_by.get("email") or created_by.get("username") or ""

            # Calculate current week dynamically based on maximum achieved week
            current_week = max(int(r.get("week") or 1) for r in r_list)
            
            # Find the parent roadmap row corresponding to the current active week
            active_roadmap = next((r for r in r_list if int(r.get("week") or 1) == current_week), None)
            if not active_roadmap:
                active_roadmap = max(r_list, key=lambda x: int(x.get("week") or 1))
                
            raw_progress = active_roadmap.get("week_progress")
            # In NocoBase, Percent is float (0.0 to 1.0). Convert to int (0 to 100)
            if raw_progress is not None:
                try:
                    progress = int(round(float(raw_progress) * 100))
                except:
                    progress = 0
            else:
                progress = 0
            
            # Get the date the user joined the cohort
            joined_date = ""
            if first_roadmap.get("createdAt"):
                joined_date = first_roadmap["createdAt"][:10]
            elif first_roadmap.get("start_date"):
                joined_date = first_roadmap["start_date"][:10]
            else:
                joined_date = datetime.now().strftime("%Y-%m-%d")

            result.append({
                "id": str(active_roadmap.get("id")),
                "cohort_id": "cohort_04",
                "username": username_val or active_roadmap.get("display_name", ""),
                "display_name": active_roadmap.get("display_name") or username_val or "Bạn",
                "week_progress": progress,
                "buddy": "Gia Cát AI",
                "joined": joined_date,
                "is_self": False
            })
        return result
    except Exception as e:
        print("get_cohort_members error:", e)
        return []

def add_cohort_member(username: str, display_name: str, buddy_name: str = "Gia Cát AI", is_self: bool = True, week_progress: int = 0) -> Dict[str, Any]:
    user_info = get_user_by_username(username)
    if not user_info:
        return {}
    import json
    try:
        res_existing = request_cms("GET", "/personal_roadmaps", params={
            "filter": json.dumps({"fk_user": user_info["id"], "week": 1}),
            "limit": 1
        })
        if not res_existing.get("data"):
            import datetime
            start_date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            parent_payload = {
                "fk_user": user_info["id"],
                "relation_roadmaps_user": user_info["id"],
                "roadmap_name": "Tái Thiết Vĩ Đại (The Great Rebuild)",
                "start_date": start_date_str,
                "week": 1,
                "total_weeks": 1,
                "week_progress": 0.0
            }
            res_parent = request_cms("POST", "/personal_roadmaps", json_data=parent_payload)
            return res_parent.get("data", {})
        return res_existing.get("data")[0]
    except Exception as e:
        print("add_cohort_member error:", e)
        return {}

def update_cohort_member_progress(member_id: str, username: str, progress: int) -> bool:
    return True

def clear_cohort_members(cohort_id: str = "cohort_04", username: Optional[str] = None) -> bool:
    try:
        import json
        if username:
            user_info = get_user_by_username(username)
            if not user_info:
                return False
            res = request_cms("GET", "/personal_roadmaps", params={
                "filter": json.dumps({"fk_user": user_info["id"]}),
                "limit": 200
            })
        else:
            res = request_cms("GET", "/personal_roadmaps", params={"limit": 200})
            
        roadmaps = res.get("data", [])
        for r in roadmaps:
            rid = r["id"]
            # 1. Fetch and delete all child tasks linked to this parent roadmap
            res_tasks = request_cms("GET", "/roadmap_tasks", params={
                "filter": json.dumps({"fk_roadmap": rid}),
                "limit": 100
            })
            for t in res_tasks.get("data", []):
                tid = t["id"]
                request_cms("DELETE", f"/roadmap_tasks/{tid}", params={"filterByTk": tid})
                
            # 2. Delete the parent roadmap record itself
            request_cms("DELETE", f"/personal_roadmaps/{rid}", params={"filterByTk": rid})
        return True
    except Exception as e:
        print("clear_cohort_members error:", e)
        return False

def get_personal_roadmap_tasks(username: str) -> List[Dict[str, Any]]:
    try:
        import json
        user_info = get_user_by_username(username)
        if not user_info:
            return []
        
        # 1. Fetch all parent roadmap records for this user
        res = request_cms("GET", "/personal_roadmaps", params={
            "filter": json.dumps({
                "$or": [
                    {"fk_user": user_info["id"]},
                    {"relation_roadmaps_user.id": user_info["id"]}
                ]
            }),
            "limit": 100
        })
        roadmaps = res.get("data", [])
        roadmap_ids = [r.get("id") for r in roadmaps if r.get("id")]
        if not roadmap_ids:
            return []
            
        roadmap_quizzes = {}
        for r in roadmaps:
            if r.get("graph_data_roadmap"):
                try:
                    p_extra = json.loads(r["graph_data_roadmap"])
                    if "quiz" in p_extra:
                        roadmap_quizzes[r.get("id")] = p_extra["quiz"]
                except:
                    pass
            
        # 2. Batch fetch all roadmap tasks linked to these parent roadmaps
        res_tasks = request_cms("GET", "/roadmap_tasks", params={
            "filter": json.dumps({"fk_roadmap": {"$in": roadmap_ids}}),
            "limit": 500
        })
        tasks_data = res_tasks.get("data", [])
        
        result = []
        for t in tasks_data:
            extra = {}
            if t.get("graph_data_roadmap"):
                try:
                    extra = json.loads(t["graph_data_roadmap"])
                except:
                    pass
            
            # Map NocoBase status (done, in_progress) to frontend status (done, backlog)
            frontend_status = "done" if t.get("status") == "done" else "backlog"
            
            task_type = extra.get("type", "core")
            
            quiz_data = None
            if task_type == "core":
                r_id = t.get("fk_roadmap")
                if not r_id and isinstance(t.get("Relation_Task_Roadmap"), dict):
                    r_id = t["Relation_Task_Roadmap"].get("id")
                elif not r_id:
                    r_id = t.get("Relation_Task_Roadmap")
                if r_id and r_id in roadmap_quizzes:
                    quiz_data = roadmap_quizzes[r_id]
            
            result.append({
                "id": str(t.get("id")),
                "title": t.get("task_title", ""),
                "goal": t.get("task_description") or "",
                "status": frontend_status,
                "deadline": "",
                "effort": extra.get("effort", 2),
                "subtasks": extra.get("subtasks") or [
                    {"title": "Phân tích yêu cầu bài học", "done": False},
                    {"title": "Hoàn thành chiêm nghiệm Socratic", "done": False}
                ],
                "contextLink": f"Lộ trình cá nhân - Tuần {t.get('week') or 1} - The Great Rebuild",
                "week": int(t.get('week') or 1),
                "type": task_type,
                "description": t.get("task_description") or "",
                "essay": t.get("user_answer") or extra.get("essay", ""),
                "quiz": quiz_data
            })
        return result
    except Exception as e:
        print("get_personal_roadmap_tasks error:", e)
        return []

def create_personal_roadmap_task(username: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    user_info = get_user_by_username(username)
    if not user_info:
        raise ValueError(f"User {username} not found")
        
    import json
    import datetime
    
    target_week = int(task_data.get("week") or 1)
    
    # 1. Fetch user's existing roadmaps to compute total_weeks and start_date
    start_date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    current_week = target_week
    try:
        res_existing = request_cms("GET", "/personal_roadmaps", params={
            "filter": json.dumps({"fk_user": user_info["id"]}),
            "sort": "week",
            "limit": 100
        })
        existing_list = res_existing.get("data", [])
        if existing_list:
            # Get the oldest start_date from Week 1 (or any first created)
            oldest = min(existing_list, key=lambda x: int(x.get("week") or 1))
            if oldest.get("start_date"):
                start_date_str = oldest.get("start_date")[:10]
    except Exception as ce:
        print("Error resolving start_date:", ce)
        
    # Calculate the real total_weeks unlocked by taking the maximum of:
    # 1. The new target week being populated
    # 2. Any existing unlocked week indices
    max_existing_week = target_week
    if existing_list:
        max_existing_week = max(max_existing_week, *(int(r.get("week") or 1) for r in existing_list))
    total_weeks_val = max_existing_week
        
    # 2. Check if a parent roadmap record exists for this specific week
    roadmap_id = None
    try:
        res_week = request_cms("GET", "/personal_roadmaps", params={
            "filter": json.dumps({"fk_user": user_info["id"], "week": target_week}),
            "limit": 1
        })
        week_data = res_week.get("data", [])
        if week_data:
            roadmap_id = week_data[0]["id"]
            # Update its total_weeks to match latest
            request_cms("PATCH", f"/personal_roadmaps/{roadmap_id}", params={"filterByTk": roadmap_id}, json_data={
                "total_weeks": total_weeks_val
            })
    except Exception as ce:
        print("Error checking specific week parent roadmap:", ce)
        
    # 3. Create parent week roadmap row if not exists
    if not roadmap_id:
        try:
            parent_payload = {
                "fk_user": user_info["id"],
                "relation_roadmaps_user": user_info["id"],
                "roadmap_name": "Tái Thiết Vĩ Đại (The Great Rebuild)",
                "start_date": start_date_str,
                "week": target_week,
                "total_weeks": total_weeks_val,
                "week_progress": 0.0
            }
            res_parent = request_cms("POST", "/personal_roadmaps", json_data=parent_payload)
            roadmap_id = res_parent.get("data", {}).get("id")
        except Exception as pe:
            print("Error creating parent week roadmap record:", pe)
            raise pe

    # 3.5 Update total_weeks for all existing roadmaps of this user to ensure consistency
    if existing_list:
        for r in existing_list:
            rid = r.get("id")
            if rid and rid != roadmap_id:
                try:
                    request_cms("PATCH", f"/personal_roadmaps/{rid}", params={"filterByTk": rid}, json_data={
                        "total_weeks": total_weeks_val
                    })
                except Exception as ex:
                    print(f"Error updating total_weeks for existing roadmap record {rid}: {ex}")

    # 4. Insert child task into roadmap_tasks linked to roadmap_id
    extra = {
        "effort": task_data.get("effort", 2),
        "subtasks": task_data.get("subtasks") or [
            {"title": "Phân tích yêu cầu bài học", "done": False},
            {"title": "Hoàn thành chiêm nghiệm Socratic", "done": False}
        ],
        "type": task_data.get("type", "core"),
        "essay": task_data.get("essay", "")
    }
    
    db_status = "done" if task_data.get("status") == "done" else "in_progress"
    
    task_payload = {
        "fk_roadmap": roadmap_id,
        "Relation_Task_Roadmap": {"id": roadmap_id},
        "task_title": task_data.get("title", ""),
        "task_description": task_data.get("description") or task_data.get("goal") or "",
        "status": db_status,
        "week": target_week,
        "user_answer": task_data.get("essay") or task_data.get("user_answer") or "",
        "graph_data_roadmap": json.dumps(extra, ensure_ascii=False)
    }
    
    res_task = request_cms("POST", "/roadmap_tasks", json_data=task_payload)
    
    # 5. Recalculate and update progress on the parent row
    if roadmap_id:
        recalculate_roadmap_progress(roadmap_id)
        
    return res_task.get("data", {})

def update_personal_roadmap_task(task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    import json
    
    # 1. Fetch existing task from roadmap_tasks
    task_id_int = int(task_id) if isinstance(task_id, str) and task_id.isdigit() else task_id
    res_get = request_cms("GET", "/roadmap_tasks", params={"filter": json.dumps({"id": task_id_int})})
    existing = res_get.get("data")
    if not existing:
        existing = {}
    if isinstance(existing, list):
        existing = existing[0] if existing else {}
    if not isinstance(existing, dict):
        existing = {}
        
    roadmap_id = existing.get("fk_roadmap")
    if not roadmap_id and isinstance(existing.get("Relation_Task_Roadmap"), dict):
        roadmap_id = existing["Relation_Task_Roadmap"].get("id")
    elif not roadmap_id:
        roadmap_id = existing.get("Relation_Task_Roadmap")
    
    extra = {}
    if existing.get("graph_data_roadmap"):
        try:
            extra = json.loads(existing["graph_data_roadmap"])
        except:
            pass
            
    payload = {}
    if "status" in task_data:
        payload["status"] = "done" if task_data["status"] == "done" else "in_progress"
        
    if "title" in task_data:
        payload["task_title"] = task_data["title"]
        
    if "description" in task_data:
        payload["task_description"] = task_data["description"]
    elif "goal" in task_data:
        payload["task_description"] = task_data["goal"]
        
    if "week" in task_data:
        try:
            payload["week"] = int(task_data["week"]) if task_data["week"] is not None else 1
        except (ValueError, TypeError):
            payload["week"] = 1
        
    if "subtasks" in task_data:
        extra["subtasks"] = task_data["subtasks"]
    if "effort" in task_data:
        extra["effort"] = task_data["effort"]
    if "type" in task_data:
        extra["type"] = task_data["type"]
    if "essay" in task_data or "user_answer" in task_data:
        essay_val = task_data.get("essay") or task_data.get("user_answer") or ""
        extra["essay"] = essay_val
        payload["user_answer"] = essay_val
        
    payload["graph_data_roadmap"] = json.dumps(extra, ensure_ascii=False)
    
    res = request_cms("PATCH", f"/roadmap_tasks/{task_id}", params={"filterByTk": task_id}, json_data=payload)
    
    # 2. Recalculate and update parent week progress
    if roadmap_id:
        recalculate_roadmap_progress(roadmap_id)
        
    # Return mapped task for compatibility
    t = res.get("data")
    if not t:
        t = {}
    if isinstance(t, list) and len(t) > 0:
        t = t[0]
    if not isinstance(t, dict):
        t = {}
        
    mapped = {
        "id": str(t.get("id") or ""),
        "title": t.get("task_title", ""),
        "goal": t.get("task_description") or "",
        "status": "done" if t.get("status") == "done" else "backlog",
        "deadline": "",
        "effort": extra.get("effort", 2),
        "subtasks": extra.get("subtasks") or [],
        "week": int(t.get('week') or 1),
        "type": extra.get("type", "core"),
        "description": t.get("task_description") or "",
        "essay": t.get("user_answer") or extra.get("essay", "")
    }
    return mapped

def delete_personal_roadmap_task(task_id: str) -> bool:
    try:
        # 1. Fetch task first to get its parent roadmap_id
        import json
        task_id_int = int(task_id) if isinstance(task_id, str) and task_id.isdigit() else task_id
        res_get = request_cms("GET", "/roadmap_tasks", params={"filter": json.dumps({"id": task_id_int})})
        existing = res_get.get("data") or {}
        if isinstance(existing, list):
            existing = existing[0] if existing else {}
        roadmap_id = existing.get("fk_roadmap")
        if not roadmap_id and isinstance(existing.get("Relation_Task_Roadmap"), dict):
            roadmap_id = existing["Relation_Task_Roadmap"].get("id")
        elif not roadmap_id:
            roadmap_id = existing.get("Relation_Task_Roadmap")
        
        # 2. Delete task
        request_cms("DELETE", f"/roadmap_tasks/{task_id}", params={"filterByTk": task_id})
        
        # 3. Recalculate parent progress
        if roadmap_id:
            recalculate_roadmap_progress(roadmap_id)
        return True
    except Exception:
        return False

def get_cohort_syllabus(cohort_id: Optional[str] = None) -> List[Dict[str, Any]]:
    # Fallback to perfect default static syllabus if NocoBase table is missing
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

    try:
        res = request_cms("GET", f"/cohort_syllabus", params={
            "sort": "week",
            "limit": 200
        })
        syllabus = res.get("data", [])
        if not syllabus:
            return fallback_syllabus
            
        # Tách syllabus mặc định (cohort_04) và syllabus cá nhân (cohort_id == username)
        global_syllabus = {s.get("week") or 1: s for s in syllabus if s.get("cohort_id") == "cohort_04"}
        user_syllabus = {s.get("week") or 1: s for s in syllabus if s.get("cohort_id") == cohort_id} if cohort_id else {}
        
        # Merge: Ưu tiên syllabus cá nhân
        merged_syllabus_dict = {}
        for w in range(1, 13):
            # Khởi tạo bằng fallback tĩnh nếu không có gì
            fallback_week = next((fw for fw in fallback_syllabus if fw["week"] == w), None)
            base = global_syllabus.get(w) or fallback_week
            if base:
                merged_syllabus_dict[w] = base.copy()
            # Ghi đè bằng dữ liệu cá nhân
            if w in user_syllabus:
                merged_syllabus_dict[w] = user_syllabus[w].copy()
                
        # Format lại kết quả trả về
        result = []
        for w in sorted(merged_syllabus_dict.keys()):
            s = merged_syllabus_dict[w]
            result.append({
                "id": str(s.get("id", f"w{w}")),
                "cohort_id": s.get("cohort_id", cohort_id or "cohort_04"),
                "week": s.get("week") or 1,
                "phase": s.get("phase", "unlearn"),
                "title": s.get("title", ""),
                "description": s.get("description", ""),
                "status": s.get("status", "upcoming"),
                "tasks": s.get("tasks") or []
            })
        return result
    except Exception:
        return fallback_syllabus

def clear_cohort_syllabus(cohort_id: str = "cohort_04") -> bool:
    try:
        res = request_cms("GET", f"/cohort_syllabus", params={"limit": 200})
        syllabus = res.get("data", [])
        for s in syllabus:
            if s.get("cohort_id") == cohort_id:
                sid = s["id"]
                request_cms("DELETE", f"/cohort_syllabus/{sid}", params={"filterByTk": sid})
        return True
    except Exception as e:
        print(f"clear_cohort_syllabus failed: {e}")
        return False

def update_cohort_syllabus_week(cohort_id: str, week: int, week_data: Dict[str, Any]) -> bool:
    try:
        res = request_cms("GET", "/cohort_syllabus", params={"limit": 200})
        syllabus = res.get("data", [])
        
        # Tìm record của riêng user này cho tuần này
        for s in syllabus:
            if s.get("cohort_id") == cohort_id and s.get("week") == week:
                sid = s["id"]
                request_cms("PUT", f"/cohort_syllabus/{sid}", json_data=week_data, params={"filterByTk": sid})
                return True
                
        # Nếu không tìm thấy, TẠO MỚI record cá nhân hóa cho user!
        payload = week_data.copy()
        payload["cohort_id"] = cohort_id
        payload["week"] = week
        payload["phase"] = "relearn" if week > 1 else "unlearn"
        payload["status"] = "upcoming"
        request_cms("POST", "/cohort_syllabus", json_data=payload)
        return True
    except Exception as e:
        print(f"update_cohort_syllabus_week failed for week {week}: {e}")
        return False

# --- ANALYTICS ASSESSMENTS METHODS ---

def get_analytics_assessments(username: str) -> List[Dict[str, Any]]:
    # Table analytics_assessments has been deleted from CMS, return empty list
    return []

def submit_analytics_assessment(username: str, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
    # Table analytics_assessments has been deleted from CMS, return success mock
    return {}

def reset_analytics_assessments(username: str) -> bool:
    # Table analytics_assessments has been deleted from CMS, return success mock
    return True
