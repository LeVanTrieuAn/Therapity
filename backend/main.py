import os
import datetime
import json
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Literal
from dotenv import load_dotenv
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

import aoa
import great_rebuild
import user_profile
import mindset_analyzer
import context_learner
import cms_helper
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

import llm_patcher
os.environ["LLM_MODEL"] = llm_patcher.ACTIVE_MODEL

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("Missing OPENAI_API_KEY in environment variables")

import httpx
client = OpenAI(
    api_key=api_key,
    base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
    timeout=httpx.Timeout(500.0)
)

# Tăng giới hạn thread pool cho các endpoints đồng bộ (def)
import anyio
try:
    anyio.to_thread.current_default_thread_limiter().total_tokens = 200
except Exception:
    pass


# Lấy model mặc định từ .env (lấy cái đầu tiên trong danh sách)
DEFAULT_MODEL = os.getenv("LLM_MODEL", "thapsang").split(",")[0].strip()


from fastapi.routing import APIRoute
from fastapi import Request, Response
import json

class NocoBaseRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()
        async def custom_route_handler(request: Request) -> Response:
            if request.method in ["POST", "PUT", "PATCH"]:
                body = await request.body()
                if body:
                    try:
                        data = json.loads(body)
                        print("NocoBaseRoute intercepted body:", data, flush=True)
                        if isinstance(data, dict) and "data" in data:
                            new_body = json.dumps(data["data"]).encode("utf-8")
                            # Override cached body so FastAPI uses the unwrapped data
                            request._body = new_body
                            request._json = data["data"]
                            print("Overrode request._body:", request._body, flush=True)
                    except Exception as e:
                        print("Exception in NocoBaseRoute:", e, flush=True)
            
            response = await original(request)
            
            if hasattr(response, "body") and response.media_type == "application/json":
                try:
                    data = json.loads(response.body)
                    if not (isinstance(data, dict) and ("data" in data or "detail" in data)):
                        new_body = json.dumps({"data": data}).encode("utf-8")
                        return Response(content=new_body, status_code=response.status_code, media_type="application/json")
                except Exception:
                    pass
            return response
        return custom_route_handler

app = FastAPI(title="Thapsang API - Unified Lighthouse Server", version="3.0.0")
app.router.route_class = NocoBaseRoute

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request
@app.middleware("http")
async def add_no_cache_header(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/v1/cohort") or request.url.path.startswith("/api/v1/tasks") or request.url.path.startswith("/api/v1/db/chats"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

ROOT_DIR = os.path.dirname(BASE_DIR)
DATABASE_DIR = os.path.join(ROOT_DIR, "database")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

from fastapi.responses import Response

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content="", media_type="image/x-icon")


THAPSANG_DB = os.path.join(DATABASE_DIR, "thapsang_db.json")
AOA_DB = os.path.join(DATABASE_DIR, "aoa_db.json")
COHORT_DB = os.path.join(DATABASE_DIR, "cohort_db.json")

def load_json_db(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return default
    return default

def save_json_db(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- MODELS ---
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = DEFAULT_MODEL
    username: Optional[str] = None
    total_user_messages: Optional[int] = None
    session_id: Optional[str] = None
    voice: Optional[str] = None
    graph_data: Optional[dict] = None


class WelcomeRequest(BaseModel):
    username: str
    lang: Optional[str] = "vi"
    session_id: Optional[str] = None
    voice: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class RequestOTPRequest(BaseModel):
    username: Optional[str] = None
    email: str

class ForgotPasswordResetRequest(BaseModel):
    email: str
    otp: str
    new_password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    full_name: str
    otp: str

class PostRequest(BaseModel):
    author_name: str
    author_displayName: Optional[str] = ""
    author_avatar: Optional[str] = ""
    content: str
    graph_data: dict
    post_privacy: Optional[str] = "public"

class CommentRequest(BaseModel):
    author_name: str
    author_displayName: Optional[str] = ""
    author_avatar: Optional[str] = ""
    content: str

class RepostRequest(BaseModel):
    original_post_id: str
    author_name: str
    author_displayName: Optional[str] = ""
    author_avatar: Optional[str] = ""
    content: str
    post_privacy: Optional[str] = "public"

class UpdatePostRequest(BaseModel):
    username: str
    content: str

class ReportPostRequest(BaseModel):
    username: str
    category: str
    details: str

class MicrostepsRequest(BaseModel):
    title: str
    goal: Optional[str] = ""
    effort: int
    lang: Optional[str] = "vi"


# --- UI ROUTES ---
@app.get("/")
async def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}

@app.get("/i18n.js")
async def i18n_script():
    return FileResponse(os.path.join(FRONTEND_DIR, "i18n.js"))

@app.get("/cache-manager.js")
async def cache_manager_script():
    return FileResponse(os.path.join(FRONTEND_DIR, "cache-manager.js"))

@app.get("/mindmap-tree.js")
async def mindmap_tree_script():
    return FileResponse(os.path.join(FRONTEND_DIR, "mindmap-tree.js"))

@app.get("/version.txt")
async def get_version():
    return FileResponse(os.path.join(FRONTEND_DIR, "version.txt"))

@app.get("/coach")
async def coach_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "coach.html"), headers={"Cache-Control": "no-store, max-age=0"})

@app.get("/aoa")
async def aoa_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "aoa.html"), headers={"Cache-Control": "no-store, max-age=0"})

@app.get("/tasks")
async def tasks_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "tasks.html"), headers={"Cache-Control": "no-store, max-age=0"})

@app.get("/cohort")
async def cohort_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "cohort.html"))

@app.get("/diary")
async def diary_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "diary.html"))

@app.get("/onboarding")
async def onboarding_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "onboarding.html"))

# --- COHORT HELPER FUNCTIONS ---
def load_cohort_metadata():
    import json
    filepath = os.path.join(FRONTEND_DIR, "cohort_metadata.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "program_title": "The Great Rebuild",
        "buddy_name": "Gia Cát AI",
        "buddy_reason": "Chương trình tái tạo tư duy 12 tuần: Phá bỏ định kiến cũ, Xây dựng hệ thống mới, Vận hành thực chiến."
    }

def save_cohort_metadata(metadata):
    import json
    filepath = os.path.join(FRONTEND_DIR, "cohort_metadata.json")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Failed to save cohort metadata: {e}")

# --- COHORT API ENDPOINTS ---
@app.get("/api/v1/cohort:list")
async def get_cohort_data():
    members = cms_helper.get_cohort_members()
    syllabus = cms_helper.get_cohort_syllabus()
    metadata = load_cohort_metadata()
    
    # Calculate bottlenecks based on real members
    late_members = [m for m in members if m.get("week_progress", 0) < 50]
    late_count = len(late_members)
    late_percentage = round((late_count / len(members)) * 100) if members else 0
    
    bottlenecks_list = []
    for m in members:
        prog = m.get("week_progress", 0)
        if prog < 85:
            bottlenecks_list.append({
                "label": f"Điểm nghẽn ở: {m.get('display_name') or m.get('username')}",
                "percentage": 100 - prog,
                "type": "error" if prog < 40 else "warning"
            })
            
    ai_insight = (
        f"Phát hiện {late_count} thành viên đang bị chậm tiến độ học tập. "
        "Hãy liên hệ hỗ trợ hoặc kích hoạt hành động phụ trợ để gỡ điểm nghẽn cùng đồng đội!"
    ) if late_count > 0 else "Hệ thống ghi nhận tiến độ học tập tuyệt vời của toàn bộ Cohort!"

    return {
        "cohort_info": {
            "id": "cohort_04",
            "title": "Cohort 04",
            "program": metadata.get("program_title", "The Great Rebuild"),
            "current_week": 2,
            "total_weeks": 12,
            "current_phase": "relearn",
            "start_date": metadata.get("start_date", "2026-05-04"),
            "description": metadata.get("buddy_reason", "Chương trình tái tạo tư duy 12 tuần: Phá bỏ định kiến cũ, Xây dựng hệ thống mới, Vận hành thực chiến.")
        },
        "syllabus": syllabus,
        "members": members,
        "bottleneck_analysis": {
            "week": 2,
            "generated_at": "2026-05-18T09:00:00Z",
            "total_members": len(members),
            "late_count": late_count,
            "late_percentage": late_percentage,
            "bottlenecks": bottlenecks_list,
            "ai_insight": ai_insight
        },
        "activity_feed": [],
        "dynamic_pivot": {
            "triggered": late_count > 0,
            "reason": f"Phát hiện {late_count} thành viên bị nghẽn học tập." if late_count > 0 else "Tiến độ học tập ổn định",
            "pivot_task": {
                "id": "pivot_w3_1",
                "title": "Học tập đồng hành: Hỗ trợ đồng đội gặp khó khăn",
                "description": "Chủ động chia sẻ cách vượt qua điểm nghẽn nhận thức.",
                "type": "supplementary",
                "auto_added": True
            }
        }
    }

class JoinCohortRequest(BaseModel):
    username: str
    display_name: Optional[str] = None
    current_tasks: Optional[list] = []

@app.post("/api/v1/cohort:join")
def join_cohort_endpoint(req: JoinCohortRequest, background_tasks: BackgroundTasks):
    if not req.username:
        raise HTTPException(status_code=400, detail="Username is required")
    display_name = req.display_name or req.username

    # 1. Gather user's actual context from database
    chats = cms_helper.get_chat_sessions(req.username)
    diaries = cms_helper.get_diary_entries(req.username)
    assessments = cms_helper.get_analytics_assessments(req.username)

    # Calculate user prompts count (real user prompts)
    user_prompt_count = 0
    chats_list = list(chats.values())
    for c in chats_list:
        msgs = c.get("chat_history") or c.get("messages") or []
        for m in msgs:
            if m.get("role") == "user":
                user_prompt_count += 1

    # Check if dialogue info is sufficient (minimum 10 user prompts)
    if user_prompt_count < 10:
        return {
            "status": "insufficient_info",
            "prompt_count": user_prompt_count,
            "message": f"Chưa đủ thông tin đối thoại: Bạn mới có {user_prompt_count}/10 lần đối thoại với AI Coach."
        }

    # 2. Summarize context for AI Prompt
    chats_text = ""
    for idx, c in enumerate(chats_list[:3]):
        msgs = c.get("chat_history") or c.get("messages") or []
        chat_content = " ".join([m.get("content", "") for m in msgs[-5:] if m.get("content")])
        chats_text += f"- Chat Session {idx+1} '{c.get('custom_title') or c.get('id')}': {chat_content[:800]}\n"
    
    diaries_text = ""
    for idx, d in enumerate(diaries[:3]):
        d_title = d.get('title') or "Untitled"
        d_content = d.get('content') or ""
        diaries_text += f"- Diary {idx+1} '{d_title}': {d_content[:800]}\n"
        
    assessments_text = ""
    for a in assessments:
        assessments_text += f"- Decision Quality: {a.get('decisionQualityScore')}, Mindset Retention: {a.get('mindsetRetentionScore')}\n"

    # Inject current tasks to be preserved
    current_tasks_text = ""
    if req.current_tasks:
        current_tasks_text = "Here are the user's active/completed tasks that MUST BE PRESERVED and integrated into the new syllabus. You must not delete, replace, or skip these tasks. Instead, place them in their respective weeks (e.g. Week 1, Week 2) and append new, advanced tasks for subsequent weeks:\n"
        for t in req.current_tasks:
            current_tasks_text += f"- Title: '{t.get('title')}', Status: '{t.get('status')}', Context: '{t.get('contextLink')}'\n"

    ai_prompt = f"""You are the Socratic AI Coach of Thapsang Mindset OS.
The user "{display_name}" (username: {req.username}) has triggered the AI Personal Roadmap Allocation. Your goal is to deeply analyze their actual learning history, goals, diaries, and mindset scores to design a highly personalized, real 12-week learning path.

{current_tasks_text}

Here is their actual dialog history with you (AI Coach):
{chats_text or "No chat history found."}

Here are their recent reflective diary entries:
{diaries_text or "No diary entries found."}

Here are their mindset DNA analytics scores:
{assessments_text or "No mindset DNA scores found."}

Based on this deep actual data, you must:
1. MATCH them with a highly compatible AI Socratic Mentor or Coach (e.g. "Tuệ Lâm AI", "Minh Trí AI", "Gia Cát AI", "Socrates AI", "Khổng Minh AI") and provide a clear Socratic rationale of why this roadmap was custom designed for them.
2. CLASSIFY them into a customized 12-week Program (e.g. "Tái Thiết Vĩ Đại (The Great Rebuild)", "Chuyển Đổi Tâm Thế (The Mindset Shift)", or another relevant title).
3. DESIGN a real, personalized 12-week syllabus. For each of the 12 weeks, define:
   - week (an integer from 1 to 12)
   - phase (must be one of: "unlearn", "relearn", "execute")
   - title_vi (Vietnamese week title)
   - title_en (English week title)
   - description_vi (Vietnamese week description)
   - description_en (English week description)
   - status (week 1 must be "active", weeks 2 to 12 must be "upcoming")
   - tasks (exactly 2 tasks: 1 "core" task and 1 "supplementary" task. Each task must have separate translations: "title_vi", "title_en", "type" which is "core" or "supplementary", a personalized detailed Socratic Vietnamese "description_vi", a detailed English "description_en", and a customized "effort" in hours which is an integer from 1 to 4 based on task complexity. IMPORTANT: Inside the task descriptions, if there are numbered lists, steps or bullet points (such as 1), 2), or 1., 2.), you MUST format them on newlines using literal "\n" so they render clean and beautiful!)

You MUST respond with a single, valid JSON object conforming exactly to this JSON schema (do NOT wrap it in any Markdown codeblocks or other formatting, just return raw JSON):
{{
  "program_title": "Custom Program Title",
  "buddy_name": "Buddy Name (e.g. Minh Trí AI)",
  "buddy_reason": "Socratic rationale for buddy matching and why this roadmap was custom designed for them",
  "syllabus": [
    {{
      "week": 1,
      "phase": "unlearn",
      "title_vi": "Tiêu đề tiếng Việt Tuần 1",
      "title_en": "English Week 1 Title",
      "description_vi": "Mô tả tiếng Việt Tuần 1",
      "description_en": "English Week 1 Description",
      "status": "active",
      "tasks": [
        {{
          "title_vi": "Tên nhiệm vụ cốt lõi tiếng Việt",
          "title_en": "Core Task English Title",
          "type": "core",
          "description_vi": "Mô tả chi tiết nhiệm vụ cốt lõi bằng tiếng Việt (xuống dòng cho các mục 1)\\n2))",
          "description_en": "Personalized Socratic core task detailed instruction in English (use newlines for lists or steps)",
          "effort": 3
        }},
        {{
          "title_vi": "Tên nhiệm vụ bổ trợ tiếng Việt",
          "title_en": "Supplementary Task English Title",
          "type": "supplementary",
          "description_vi": "Mô tả chi tiết nhiệm vụ bổ trợ bằng tiếng Việt",
          "description_en": "Personalized Socratic supplementary task detailed instruction in English",
          "effort": 2
        }}
      ]
    }},
    ...
  ]
}}
"""
    # Use fallback syllabus directly to ensure instant joins without OpenAI latency or allocation errors
    fallback_syllabus = [
        {
            "week": 1,
            "phase": "unlearn",
            "title": "Nhận diện & Gỡ bỏ Định kiến cũ",
            "title_en": "Cognitive Unlearning",
            "description": "Nhận diện những mô thức tư duy cũ kỹ và rào cản nhận thức đang kìm hãm sự phát triển của bạn. Bắt đầu quá trình 'dọn dẹp' tâm trí.",
            "description_en": "Identify outdated thought patterns and cognitive barriers holding back your growth. Begin the mental 'cleanup' process.",
            "status": "active",
            "tasks": []
        },
        {
            "week": 2,
            "phase": "relearn",
            "title": "Thiết lập Tư duy Tăng trưởng",
            "title_en": "Establishing Growth Mindset",
            "description": "Kiến tạo nền tảng cho sự thay đổi thông qua việc chấp nhận thử thách, học từ thất bại và áp dụng phương pháp Socratic để tự vấn.",
            "description_en": "Build a foundation for change by embracing challenges, learning from failure, and applying the Socratic method for self-inquiry.",
            "status": "upcoming",
            "tasks": []
        },
        {
            "week": 3,
            "phase": "relearn",
            "title": "Khám phá Giá trị Cốt lõi",
            "title_en": "Uncovering Core Values",
            "description": "Đào sâu vào nội tâm để tìm ra những giá trị chân thật nhất định hình các quyết định và mục tiêu sống của bạn.",
            "description_en": "Dig deep within to discover the truest values that shape your decisions and life goals.",
            "status": "upcoming",
            "tasks": []
        },
        {
            "week": 4,
            "phase": "relearn",
            "title": "Tái cấu trúc Hệ thống Niềm tin",
            "title_en": "Belief System Restructuring",
            "description": "Xây dựng lại bộ lọc nhận thức, thay thế niềm tin giới hạn bằng những hệ quy chiếu trao quyền mạnh mẽ hơn.",
            "description_en": "Rebuild your cognitive filters, replacing limiting beliefs with more powerful, empowering frameworks.",
            "status": "upcoming",
            "tasks": []
        },
        {
            "week": 5,
            "phase": "relearn",
            "title": "Tư duy Hệ thống & Phân tích",
            "title_en": "Foundations of Systems Thinking",
            "description": "Học cách nhìn nhận các vấn đề phức tạp theo chuỗi liên kết, từ đó tìm ra điểm đòn bẩy (leverage points) để tạo sự thay đổi lớn.",
            "description_en": "Learn to view complex problems as interconnected chains to find leverage points for massive change.",
            "status": "upcoming",
            "tasks": []
        },
        {
            "week": 6,
            "phase": "relearn",
            "title": "Lập trình lại Thói quen",
            "title_en": "Habit Reprogramming",
            "description": "Thiết kế các vòng lặp thói quen nhỏ (micro-habits) để hiện thực hóa tư duy mới vào các hành động tự động hàng ngày.",
            "description_en": "Design micro-habit loops to actualize new mindsets into automatic daily actions.",
            "status": "upcoming",
            "tasks": []
        },
        {
            "week": 7,
            "phase": "execute",
            "title": "Xây dựng Bản đồ Mục tiêu",
            "title_en": "Goal Mapping & Trajectory",
            "description": "Bắt đầu chặng thực chiến: Chuyển hóa tầm nhìn thành các cột mốc (milestones) đo lường được và định hướng rõ ràng.",
            "description_en": "Begin the execution phase: Translate your vision into measurable milestones and clear trajectories.",
            "status": "upcoming",
            "tasks": []
        },
        {
            "week": 8,
            "phase": "execute",
            "title": "Thiết kế Quy trình Hành động",
            "title_en": "Designing Action Workflows",
            "description": "Xây dựng hệ thống vận hành cá nhân, chuẩn hóa các bước thực thi để loại bỏ sự ma sát và tăng cường tính kỷ luật.",
            "description_en": "Build your personal operating system, standardizing execution steps to eliminate friction and boost discipline.",
            "status": "upcoming",
            "tasks": []
        },
        {
            "week": 9,
            "phase": "execute",
            "title": "Vượt qua Vùng An Toàn",
            "title_en": "Breaking the Comfort Zone",
            "description": "Chủ động đối mặt với những rủi ro có tính toán, thử nghiệm hành động mới để mở rộng năng lực thực thi của bản thân.",
            "description_en": "Proactively face calculated risks, experimenting with new actions to expand your execution capabilities.",
            "status": "upcoming",
            "tasks": []
        },
        {
            "week": 10,
            "phase": "execute",
            "title": "Tối ưu hóa Hiệu suất",
            "title_en": "Performance Optimization",
            "description": "Đo lường kết quả, tinh chỉnh hệ thống làm việc và loại bỏ những yếu tố làm tiêu hao năng lượng không cần thiết.",
            "description_en": "Measure results, refine your workflow systems, and eliminate elements that drain unnecessary energy.",
            "status": "upcoming",
            "tasks": []
        },
        {
            "week": 11,
            "phase": "execute",
            "title": "Tự nhận thức & Phản hồi",
            "title_en": "Self-Awareness & Feedback Loop",
            "description": "Ứng dụng phương pháp phản tư sâu sắc, thu thập dữ liệu từ hành động để liên tục cập nhật và hoàn thiện chu trình.",
            "description_en": "Apply deep reflection methods, gathering data from actions to continuously update and perfect the cycle.",
            "status": "upcoming",
            "tasks": []
        },
        {
            "week": 12,
            "phase": "execute",
            "title": "Hoàn thiện Tái thiết Vĩ đại",
            "title_en": "The Great Rebuild Integration",
            "description": "Tích hợp toàn bộ bài học 12 tuần thành một bản sắc cá nhân mới, sẵn sàng duy trì sự phát triển bền vững trong dài hạn.",
            "description_en": "Integrate all 12 weeks of lessons into a new personal identity, ready to sustain long-term growth.",
            "status": "upcoming",
            "tasks": []
        }
    ]
    
    cohort_design = {
        "program_title": "Tái Thiết Vĩ Đại (The Great Rebuild)",
        "buddy_name": "Gia Cát AI",
        "buddy_reason": "Chương trình tái tạo tư duy 12 tuần: Phá bỏ định kiến cũ, Xây dựng hệ thống mới, Vận hành thực chiến.",
        "syllabus": fallback_syllabus
    }

    # Save dynamic cohort metadata to cohort_metadata.json
    import datetime
    metadata = {
        "program_title": cohort_design.get("program_title", "Tái Thiết Vĩ Đại (The Great Rebuild)"),
        "buddy_name": cohort_design.get("buddy_name", "Gia Cát AI"),
        "buddy_reason": cohort_design.get("buddy_reason", "Chương trình học tập 12 tuần của riêng bạn, phá bỏ định kiến cũ, xây dựng hệ thống mới."),
        "start_date": datetime.datetime.now().strftime("%Y-%m-%d")
    }
    save_cohort_metadata(metadata)

    # Clean old tables for the specific user (only clear roadmaps and tasks, NOT syllabus)
    cms_helper.clear_cohort_members("cohort_04", username=req.username)

    # Insert self only to NocoBase (no classmate peers)
    buddy_name = cohort_design.get("buddy_name", "Gia Cát AI")
    res = cms_helper.add_cohort_member(req.username, display_name, buddy_name=buddy_name, is_self=True, week_progress=0)

    return {"status": "success", "message": "Successfully joined cohort and initialized default syllabus."}

def auto_generate_quiz_for_week(username: str, week: int, roadmap_id: int, parent_extra: dict, core_task: dict, supp_task: dict, user_info: dict, lang: str = "vi"):
    import json
    # 1. Fetch onboarding and diaries
    onboarding = user_info.get("onboarding") or {}
    core_context = onboarding.get("_core_context", "")
    if not core_context and onboarding:
        try:
            import context_learner
            core_context = context_learner.generate_context_from_onboarding(username, onboarding)
        except Exception as ce:
            print(f"Error generating onboarding context: {ce}")
            
    interests = onboarding.get("interests", [])
    problems = onboarding.get("problems", [])
    goals = onboarding.get("goals", [])
    
    diary_summary = ""
    try:
        entries = cms_helper.get_diary_entries(username)
        if entries:
            latest_entries = entries[-3:]
            diary_lines = []
            for idx, entry in enumerate(latest_entries):
                title = entry.get("title", "")
                mood = entry.get("mood", "")
                content = entry.get("content", "")
                if content and len(content) > 150:
                    content = content[:150] + "..."
                diary_lines.append(f"- Nhật ký {idx+1}: Tiêu đề: {title} | Cảm xúc: {mood} | Nội dung: {content}")
            diary_summary = "\n".join(diary_lines)
    except Exception as de:
        print(f"Error fetching diaries for auto quiz: {de}")

    def get_task_translations(task: dict, default_title: str) -> tuple[str, str]:
        title = task.get("title") or ""
        if " ||| " in title:
            parts = title.split(" ||| ")
            return parts[0].strip(), parts[1].strip()
        title_vi = task.get("title_vi") or title or default_title
        title_en = task.get("title_en") or title or default_title
        return title_vi.strip(), title_en.strip()

    def get_desc_translations(task: dict, default_desc: str = "") -> tuple[str, str]:
        desc = task.get("description") or ""
        if " ||| " in desc:
            parts = desc.split(" ||| ")
            return parts[0].strip(), parts[1].strip()
        desc_vi = task.get("description_vi") or desc or default_desc
        desc_en = task.get("description_en") or desc or default_desc
        return desc_vi.strip(), desc_en.strip()

    core_title_vi, core_title_en = get_task_translations(core_task, "Nhiệm vụ cốt lõi")
    supp_title_vi, supp_title_en = get_task_translations(supp_task, "Nhiệm vụ bổ trợ")
    
    core_desc_vi, core_desc_en = get_desc_translations(core_task, "")
    supp_desc_vi, supp_desc_en = get_desc_translations(supp_task, "")

    # Fetch recent chat sessions
    chats_text = ""
    try:
        chats = cms_helper.get_chat_sessions(username)
        chats_list = list(chats.values())
        for idx, c in enumerate(chats_list[:3]):
            msgs = c.get("chat_history") or c.get("messages") or []
            chat_content = " ".join([m.get("content", "") for m in msgs[-5:] if m.get("content")])
            if chat_content:
                chats_text += f"- Chat Session {idx+1}: {chat_content[:500]}\n"
    except Exception as ce:
        print(f"Error fetching chats for auto quiz: {ce}")

    ai_prompt = f"""You are the Socratic AI Coach of Thapsang.
The user is at Week {week} of their Personal Roadmap.

Here is the user's LONG-TERM SOCRATIC CORE CONTEXT (personality, cognitive blocks, behavioral patterns):
{core_context or "Chưa có thông tin bối cảnh dài hạn."}

Here are the user's general goals, problems, and interests:
- Problems: {", ".join(problems) if problems else "None"}
- Goals: {", ".join(goals) if goals else "None"}
- Interests: {", ".join(interests) if interests else "None"}

Here is the user's LATEST CHAT COACH HISTORY (representing their most recent conversations and queries):
{chats_text or "Chưa ghi nhận cuộc hội thoại gần đây."}

Here are the user's LATEST DIARY ENTRIES (representing their current real-world emotional struggles and active mindsets):
{diary_summary or "Chưa ghi nhận nhật ký gần đây."}

Here are the user's assigned Socratic tasks for this week:
Task 1 (Core) Vietnamese Title: {core_title_vi}
Task 1 (Core) Vietnamese Description: {core_desc_vi}

Task 2 (Supplementary) Vietnamese Title: {supp_title_vi}
Task 2 (Supplementary) Vietnamese Description: {supp_desc_vi}

You must generate exactly 8 Socratic multiple-choice questions customized to the user's assigned tasks, their core psychological blocks/goals, their chat history, and their diary mood states.
IMPORTANT INSTRUCTIONS FOR QUIZ QUALITY:
1. Highly Personalized & Practical: Every question must directly connect to the user's assigned tasks, their diary feelings, their onboarding problems, or their cognitive blocks. Avoid generic, dry textbook questions.
2. Avoid Academics & Definitions: Do NOT ask for definitions of terms (e.g., 'What is a fixed mindset?'). Focus on real-life choices and mental blindspots.
3. Each question must have exactly 4 choices (options).
4. Ensure a strict separate bilingual translation structure. For every question, you must provide BOTH high-fidelity Vietnamese and English versions inside 'question_vi', 'question_en', 'options_vi' (exactly 4 options), and 'options_en' (exactly 4 options). No mixed-languages inside the translation fields.
5. NO REPETITION: All 8 questions MUST be completely UNIQUE and DIVERSE. Do NOT repeat the same question structure, same topic, or same options. Explore 8 different distinct angles, scenarios, or psychological obstacles related to the week's tasks.

You MUST respond with a single, valid JSON object conforming exactly to this JSON schema (do NOT wrap it in any Markdown codeblocks or other formatting, just return raw JSON):
{{
  "questions": [
    {{
      "id": 1,
      "question_vi": "Câu hỏi trắc nghiệm bằng tiếng Việt...",
      "question_en": "High-fidelity English translation of the same question...",
      "options_vi": [
        "Lựa chọn A...",
        "Lựa chọn B...",
        "Lựa chọn C...",
        "Lựa chọn D..."
      ],
      "options_en": [
        "Option A...",
        "Option B...",
        "Option C...",
        "Option D..."
      ],
      "correct_answer": 0  // Index of correct option (0 to 3)
    }},
    ...
  ]
}}
"""
    quiz_data = None
    try:
        model_name = os.getenv("LLM_MODEL", "thapsang").split(",")[0].strip()
        
        content = ""
        # 1. Try streaming first (Highly reliable workaround for the proxy)
        try:
            stream_response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": ai_prompt}],
                temperature=0.2,
                top_p=0.9,
                max_tokens=3000,
                stream=True
            )
            chunks = []
            for chunk in stream_response:
                if getattr(chunk, "choices", None) and chunk.choices[0].delta.content:
                    chunks.append(chunk.choices[0].delta.content)
            content = "".join(chunks).strip()
        except Exception as se:
            print(f"Streaming quiz generation failed: {se}. Falling back to non-streaming with proxy workaround.")
            
        # 2. Fallback to non-streaming with proxy JSON parser
        if not content:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": ai_prompt}],
                temperature=0.2,
                top_p=0.9,
                max_tokens=3000
            )
            if getattr(response, "choices", None):
                content = response.choices[0].message.content.strip()
            elif hasattr(response, "error") and response.error and isinstance(response.error, dict):
                details_str = response.error.get("details", "{}")
                try:
                    try:
                        parsed_details = json.loads(details_str)
                        content = parsed_details["choices"][0]["message"]["content"].strip()
                    except Exception:
                        if "data:" in details_str:
                            chunks_text = ""
                            for line in details_str.splitlines():
                                line = line.strip()
                                if line.startswith("data:"):
                                    json_str = line[5:].strip()
                                    if json_str and json_str != "[DONE]":
                                        try:
                                            chunk_obj = json.loads(json_str)
                                            if "choices" in chunk_obj and len(chunk_obj["choices"]) > 0:
                                                delta = chunk_obj["choices"][0].get("delta", {})
                                                chunks_text += delta.get("content", "")
                                        except Exception:
                                            pass
                            if chunks_text:
                                content = chunks_text.strip()
                except Exception:
                    pass
                    
        if not content:
            raise ValueError("No valid text response from LLM proxy for quiz")
            
        import re
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            content = match.group(0)
        else:
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
        content = content.strip()
        
        quiz_data = json.loads(content)
        if "questions" not in quiz_data or len(quiz_data["questions"]) != 8:
            raise ValueError("AI failed to generate exactly 8 questions")
    except Exception as e:
        print(f"Failed to generate auto AI quiz: {e}. Using fallback 8-question Socratic quiz.")
        import fallback_quiz_data
        quiz_data = fallback_quiz_data.get_fallback_quiz_for_week(week, core_title_vi, core_title_en, supp_title_vi, supp_title_en)
        
    # Shuffle options to guarantee all A, B, C, D appear as correct answers at least once across the 8 questions
    import random
    questions = quiz_data.get("questions", [])
    if len(questions) >= 4:
        targets = [0, 1, 2, 3] + [random.randint(0, 3) for _ in range(len(questions) - 4)]
        random.shuffle(targets)
        for q, target_ans in zip(questions, targets):
            curr_ans = q.get("correct_answer", 0)
            if curr_ans != target_ans:
                # Ensure options lists exist and have enough elements before swapping
                if len(q.get("options_vi", [])) > max(curr_ans, target_ans) and len(q.get("options_en", [])) > max(curr_ans, target_ans):
                    q["options_vi"][curr_ans], q["options_vi"][target_ans] = q["options_vi"][target_ans], q["options_vi"][curr_ans]
                    q["options_en"][curr_ans], q["options_en"][target_ans] = q["options_en"][target_ans], q["options_en"][curr_ans]
                    q["correct_answer"] = target_ans

    parent_extra["quiz"] = {
        "questions": questions,
        "created_at": datetime.datetime.now().isoformat() + "Z",
        "attempts": []
    }
    patch_data = {
        "graph_data_roadmap": json.dumps(parent_extra, ensure_ascii=False),
        "test_flag": "Activated"
    }
    cms_helper.request_cms("PATCH", f"/personal_roadmaps/{roadmap_id}", params={"filterByTk": roadmap_id}, json_data=patch_data)

import threading
from functools import wraps

personalize_lock = threading.Lock()

def locked(lock):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return wrapper
    return decorator

class PersonalizeWeekRequest(BaseModel):
    username: str
    week: int

@app.post("/api/v1/cohort:personalize_week")
def personalize_week_endpoint(req: PersonalizeWeekRequest, background_tasks: BackgroundTasks):
    if not req.username or not req.week:
        raise HTTPException(status_code=400, detail="Username and Week are required")
        
    user_info = cms_helper.get_user_by_username(req.username)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Check if tasks already exist for this week to prevent concurrent duplicates
    import json
    existing_tasks = cms_helper.get_personal_roadmap_tasks(req.username)
    week_tasks = [t for t in existing_tasks if t.get("week") == req.week]
    if week_tasks:
        syllabus = cms_helper.get_cohort_syllabus(cohort_id=req.username)
        matching_week = next((s for s in syllabus if s.get("week") == req.week), None)
        t_combined = matching_week.get("title") if matching_week else f"Tuần {req.week}"
        d_combined = matching_week.get("description") if matching_week else ""
        
        # Map the tasks format back to syllabus format
        combined_tasks_for_syllabus = []
        for task in week_tasks:
            combined_tasks_for_syllabus.append({
                "title": task.get("title"),
                "type": task.get("type", "core"),
                "description": task.get("description") or task.get("goal") or "",
                "effort": task.get("effort")
            })
        
        frontend_week_design = {
            "title": t_combined,
            "description": d_combined,
            "tasks": combined_tasks_for_syllabus
        }
        return {"status": "success", "week_data": frontend_week_design}

    # Verify sequential unlock: user MUST have passed req.week - 1
    if req.week > 1:
        res_prev = cms_helper.request_cms("GET", "/personal_roadmaps", params={
            "filter": json.dumps({
                "week": req.week - 1,
                "$or": [
                    {"fk_user": user_info["id"]},
                    {"relation_roadmaps_user.id": user_info["id"]}
                ]
            }),
            "limit": 1
        })
        prev_roadmaps = res_prev.get("data", [])
        if not prev_roadmaps:
            raise HTTPException(status_code=403, detail=f"Bạn chưa hoàn thành Tuần {req.week - 1}.")
        
        prev_progress = prev_roadmaps[0].get("week_progress") or 0.0
        if float(prev_progress) < 0.5:
            raise HTTPException(status_code=403, detail=f"Bạn phải vượt qua bài trắc nghiệm Tuần {req.week - 1} để mở khóa Tuần {req.week}.")
            
    from fastapi.responses import JSONResponse
    with personalize_lock:
        # Gather latest user context (chats and diaries)
        chats = {}
        diaries = []
        try:
            chats = cms_helper.get_chat_sessions(req.username)
            diaries = cms_helper.get_diary_entries(req.username)
        except Exception as e_ctx:
            print(f"Context fetch error: {e_ctx}")

        chats_list = list(chats.values())
        chats_text = ""
        for idx, c in enumerate(chats_list[:5]): # Get more recent chats
            msgs = c.get("chat_history") or c.get("messages") or []
            chat_content = " ".join([m.get("content", "") for m in msgs[-8:] if m.get("content")])
            chats_text += f"- Chat Session {idx+1}: {chat_content[:800]}\n"
    
        diaries_text = ""
        for idx, d in enumerate(diaries[:5]):
            diaries_text += f"- Diary {idx+1} '{d.get('title')}': {d.get('content')[:800]}\n"

        user_name = user_info.get("nickname") or user_info.get("username", req.username).split('@')[0]
        recent_topic = ""
        if diaries:
            recent_topic = diaries[0].get("title", "")
        if not recent_topic and chats_list:
            c_hist = chats_list[0].get("chat_history") or chats_list[0].get("messages") or []
            if c_hist:
                recent_topic = c_hist[0].get("content", "")[:50]
                
        topic_str = f" về vấn đề '{recent_topic}'" if recent_topic else ""
        topic_str_en = f" regarding '{recent_topic}'" if recent_topic else ""
        
        themes = {
            1: {
                "vi_title": f"Thiết lập nền tảng", "en_title": f"Setting Foundations",
                "vi_core": f"{user_name} thân mến, tuần khởi đầu này là để định vị bản thân. Từ những chia sẻ gần đây{topic_str}, hãy thiết kế một hành động nhỏ nhất để bước ra khỏi vùng quen thuộc và quan sát cảm xúc của bạn.",
                "en_core": f"Dear {user_name}, this initial week is about self-positioning. Based on your recent thoughts{topic_str_en}, design the smallest possible action to step out of your comfort zone and observe your feelings.",
                "vi_supp": f"Ghi lại những rào cản tâm lý đầu tiên bạn gặp phải khi thực hiện thử nghiệm trên.",
                "en_supp": f"Document the initial psychological barriers you encountered during your experiment."
            },
            2: {
                "vi_title": f"Bắt mạch điểm mù", "en_title": f"Identifying Blindspots",
                "vi_core": f"Ở tuần 2, chúng ta tập trung vào những gì bị che khuất. Với băn khoăn{topic_str}, {user_name} hãy thử làm ngược lại thói quen thường ngày trong 1 tình huống cụ thể và xem điều gì thực sự xảy ra.",
                "en_core": f"In week 2, we focus on the unseen. Given your reflections{topic_str_en}, try doing the exact opposite of your usual habit in a specific situation and see what happens.",
                "vi_supp": f"Viết lại khoảnh khắc bạn nhận ra giả định ban đầu của mình là sai lệch.",
                "en_supp": f"Write about the moment you realized your initial assumption was flawed."
            },
            3: {
                "vi_title": f"Giải cấu trúc niềm tin", "en_title": f"Deconstructing Beliefs",
                "vi_core": f"Tuần 3 là lúc thách thức tận gốc rễ. Hãy lấy một kết luận bạn vừa rút ra{topic_str} và áp dụng kỹ thuật '5 lần Tại Sao' để tìm ra nguyên nhân cốt lõi chưa từng lộ diện.",
                "en_core": f"Week 3 challenges the root. Take a recent conclusion{topic_str_en} and apply the '5 Whys' technique to uncover the true underlying cause.",
                "vi_supp": f"Chia sẻ cảm giác chông chênh khi niềm tin cũ bị phá vỡ và góc nhìn mới hé mở.",
                "en_supp": f"Share the feeling of instability when an old belief breaks and a new perspective opens."
            },
            4: {
                "vi_title": f"Quan sát không phán xét", "en_title": f"Non-judgmental Observation",
                "vi_core": f"Tuần 4 yêu cầu sự tĩnh tại. Dựa trên trăn trở{topic_str}, {user_name} hãy chọn vai trò 'người quan sát thứ 3' trong các quyết định sắp tới: ghi nhận nhưng không phản ứng ngay lập tức.",
                "en_core": f"Week 4 requires stillness. Based on your concerns{topic_str_en}, adopt a 'third-party observer' role in upcoming decisions: acknowledge without immediate reaction.",
                "vi_supp": f"Nhật ký tuần này hãy tập trung vào khoảng hở (gap) giữa lúc sự việc xảy ra và lúc bạn phản ứng.",
                "en_supp": f"Focus your diary on the gap between an event happening and your reaction to it."
            },
            5: {
                "vi_title": f"Tái thiết góc nhìn", "en_title": f"Perspective Reconstruction",
                "vi_core": f"Giờ là lúc xây dựng lại. Với những dữ liệu thực tế{topic_str}, hãy thiết lập một hành động mới đại diện cho phiên bản mà {user_name} muốn hướng tới, và thực thi nó ít nhất 3 lần.",
                "en_core": f"It is time to rebuild. With the real-world data{topic_str_en}, establish a new action representing the version of you strive to be, and execute it at least 3 times.",
                "vi_supp": f"Ghi lại những ma sát và sự gượng gạo khi áp dụng góc nhìn mới vào thực tiễn.",
                "en_supp": f"Document the friction and awkwardness of applying this new perspective practically."
            },
            6: {
                "vi_title": f"Đo lường sự phản kháng", "en_title": f"Measuring Resistance",
                "vi_core": f"Tuần 6, sự kháng cự sẽ xuất hiện. {user_name} hãy cố tình chọn làm một việc khó khăn{topic_str} để đo lường xem 'tiếng nói nhỏ' trong đầu bạn đang biện hộ như thế nào.",
                "en_core": f"In week 6, resistance appears. Intentionally choose to do a difficult task{topic_str_en} to measure how the 'little voice' in your head makes excuses.",
                "vi_supp": f"Viết lại nguyên văn những lý do ngụy biện mà tâm trí bạn tạo ra để trốn tránh hành động.",
                "en_supp": f"Write down verbatim the rationalizations your mind created to avoid taking action."
            },
            7: {
                "vi_title": f"Kết nối các điểm chạm", "en_title": f"Connecting the Dots",
                "vi_core": f"Tuần 7 là điểm giao thoa. Hãy nhìn lại những hành động{topic_str} của 6 tuần qua, tìm ra một mẫu số chung (pattern) và thiết kế một thử nghiệm giải quyết hoàn toàn khác biệt.",
                "en_core": f"Week 7 is a junction. Look back at your actions{topic_str_en} over the past 6 weeks, identify a common pattern, and experiment with a completely different approach.",
                "vi_supp": f"Nhật ký tổng hợp: Bạn đã thay đổi cách ra quyết định như thế nào so với tuần 1?",
                "en_supp": f"Synthesis diary: How has your decision-making changed compared to week 1?"
            },
            8: {
                "vi_title": f"Thử nghiệm nghịch lý", "en_title": f"Paradox Experimentation",
                "vi_core": f"Tuần 8 đòi hỏi tư duy nghịch đảo. {user_name} hãy tìm một khía cạnh{topic_str} mà bạn luôn cho là 'đúng', và thử đóng vai 'luật sư của quỷ' để hành động ngược lại niềm tin đó.",
                "en_core": f"Week 8 requires inverse thinking. Find an aspect{topic_str_en} you always assumed was 'right', and play 'devil's advocate' by acting against that belief.",
                "vi_supp": f"Ghi chép lại những phát hiện bất ngờ khi bạn thử nhìn thế giới qua lăng kính đối lập.",
                "en_supp": f"Note the surprising discoveries when you tried viewing the world through an opposing lens."
            },
            9: {
                "vi_title": f"Thích nghi với sự sụp đổ", "en_title": f"Adapting to Breakdown",
                "vi_core": f"Ở tuần 9, thất bại là tư liệu. Nếu bạn vừa trải qua sự chệch hướng{topic_str}, hãy thiết kế một bước đệm nhỏ để quay lại đường đua thay vì tự dằn vặt.",
                "en_core": f"In week 9, failure is data. If you recently experienced a deviation{topic_str_en}, design a small stepping stone to get back on track instead of blaming yourself.",
                "vi_supp": f"Phản tư: Cơ chế phòng vệ nào đã kích hoạt khiến bạn đi chệch hướng, và bài học là gì?",
                "en_supp": f"Reflection: What defense mechanism triggered your deviation, and what is the lesson?"
            },
            10: {
                "vi_title": f"Nội tâm hóa hệ giá trị", "en_title": f"Internalizing Value Systems",
                "vi_core": f"Tuần 10 giúp cắm rễ sâu hơn. Hãy biến những đúc kết{topic_str} thành một bộ nguyên tắc cá nhân ngắn gọn và áp dụng nó vào một quyết định quan trọng trong tuần này.",
                "en_core": f"Week 10 deepens the roots. Turn your takeaways{topic_str_en} into a concise personal code of principles and apply it to a major decision this week.",
                "vi_supp": f"Viết lại cảm giác khi đưa ra quyết định dựa trên hệ nguyên tắc thay vì cảm xúc nhất thời.",
                "en_supp": f"Write about the feeling of making a decision based on principles rather than fleeting emotions."
            },
            11: {
                "vi_title": f"Giải phóng sự phụ thuộc", "en_title": f"Releasing Dependency",
                "vi_core": f"Chặng áp chót! {user_name} hãy tự đóng vai Socratic Coach để phân tích chính các vấn đề hiện tại{topic_str}. Tự đặt ra câu hỏi sắc bén nhất cho bản thân và thực thi câu trả lời.",
                "en_core": f"Penultimate stage! Act as your own Socratic Coach to analyze your current issues{topic_str_en}. Ask yourself the sharpest question and act on the answer.",
                "vi_supp": f"Nhật ký tự vấn: Đâu là câu hỏi mà bạn sợ phải tự trả lời nhất lúc này?",
                "en_supp": f"Self-inquiry diary: What is the question you are most afraid to answer right now?"
            },
            12: {
                "vi_title": f"Tự chủ", "en_title": f"Autonomy",
                "vi_core": f"Tuần cuối cùng. Dựa trên thành quả{topic_str}, {user_name} hãy vạch ra một lộ trình duy trì sự tự nhận thức mà không cần sự can thiệp của AI Coach.",
                "en_core": f"Final week. Based on your outcomes{topic_str_en}, outline a roadmap to maintain self-awareness without the AI Coach's intervention.",
                "vi_supp": f"Thư gửi bản thân: Bạn của 12 tuần tới sẽ cảm ơn bạn của hiện tại vì điều gì?",
                "en_supp": f"Letter to yourself: What will the 'you' 12 weeks from now thank the 'current you' for?"
            }
        }
        
        theme = themes.get(req.week, themes[1])
        fb_core_title_vi = f"{theme['vi_title']}: {recent_topic}" if recent_topic else f"{theme['vi_title']} ({user_name})"
        fb_core_title_en = f"{theme['en_title']}: {recent_topic}" if recent_topic else f"{theme['en_title']} ({user_name})"
        fb_core_vi = theme['vi_core']
        fb_core_en = theme['en_core']
        fb_supp_vi = theme['vi_supp']
        fb_supp_en = theme['en_supp']

        ai_prompt = f"""You are the Socratic AI Coach of Thapsang Mindset OS.
    The user is at Week {req.week} of their 12-week Personal Roadmap.
    Your goal is to deeply analyze their latest dialog history and recent reflective diaries to design EXACTLY 2 highly personalized, high-fidelity tasks for Week {req.week}.
    CRITICAL REQUIREMENT: You MUST generate EXACTLY 1 "core" task and EXACTLY 1 "supplementary" task. No more, no less. Do not generate two core tasks. Do not generate two supplementary tasks.

    Here is their latest dialog history:
    {chats_text or "No recent chats found."}

    Here are their recent diaries:
    {diaries_text or "No recent diaries found."}

    Based on this latest actual context, update the tasks for Week {req.week} to specifically target their current cognitive bottlenecks, blindspots, or goals.
    Provide a concise title and description for Week {req.week}, and EXACTLY 2 tasks (the first MUST have type "core", the second MUST have type "supplementary"). Each task must have separate translations: "title_vi", "title_en", "type" (which is strictly "core" or "supplementary"), a personalized detailed Socratic Vietnamese "description_vi", a detailed English "description_en", and a customized "effort" in hours which is an integer from 1 to 4 based on task complexity. IMPORTANT: Inside the task descriptions, if there are numbered lists, steps or bullet points (such as 1), 2), or 1., 2.), you MUST format them on newlines using literal "\n" so they render clean and beautiful!

    You MUST respond with a single, valid JSON object conforming exactly to this JSON schema (do NOT wrap it in any Markdown codeblocks or other formatting, just return raw JSON):
    {{
      "title_vi": "Tiêu đề tiếng Việt Tuần {req.week}",
      "title_en": "English Week {req.week} Title",
      "description_vi": "Mô tả tiếng Việt Tuần {req.week}",
      "description_en": "English Week {req.week} Description",
      "tasks": [
        {{
          "title_vi": "Tên nhiệm vụ cốt lõi tiếng Việt",
          "title_en": "Core Task English Title",
          "type": "core",
          "description_vi": "Mô tả chi tiết nhiệm vụ cốt lõi bằng tiếng Việt (xuống dòng cho các mục 1)\n2))",
          "description_en": "Personalized Socratic core task detailed instruction in English (use newlines for lists or steps)",
          "effort": 3
        }},
        {{
          "title_vi": "Tên nhiệm vụ bổ trợ tiếng Việt",
          "title_en": "Supplementary Task English Title",
          "type": "supplementary",
          "description_vi": "Mô tả chi tiết nhiệm vụ bổ trợ bằng tiếng Việt",
          "description_en": "Personalized Socratic supplementary task detailed instruction in English",
          "effort": 2
        }}
      ]
    }}
    """
        is_fallback = False
        # Call LLM
        try:
            from openai import OpenAI as _OpenAI
            _client = _OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
            )
            model_name = os.getenv("LLM_MODEL", "thapsang").split(",")[0].strip()

            resp = _client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": ai_prompt}],
                temperature=0.3,
                top_p=0.95,
                timeout=150.0  # Increased timeout for reasoning models
            )
            ai_response_text = ""
            if getattr(resp, "choices", None):
                ai_response_text = resp.choices[0].message.content.strip()

            if ai_response_text:
                import re
                import json
                ai_response_text = re.sub(r'<think>.*?</think>', '', ai_response_text, flags=re.DOTALL).strip()
                json_match = re.search(r'\{.*\}', ai_response_text, re.DOTALL)
                if json_match:
                    ai_response_text = json_match.group(0)
                week_design = json.loads(ai_response_text)
        
                # Post-process to guarantee EXACTLY 1 core and 1 supplementary task
                tasks = week_design.get("tasks", [])
                core_tasks = [t for t in tasks if t.get("type") == "core"]
                supp_tasks = [t for t in tasks if t.get("type") == "supplementary"]
        
                final_tasks = []
        
                # 1. Ensure 1 core task
                if core_tasks:
                    final_tasks.append(core_tasks[0])
                else:
                    final_tasks.append(tasks[0] if len(tasks) > 0 else {
                        "title_vi": fb_core_title_vi,
                        "title_en": fb_core_title_en,
                        "description_vi": fb_core_vi,
                        "description_en": fb_core_en,
                        "effort": 3
                    })
                final_tasks[0]["type"] = "core"
        
                # 2. Ensure 1 supplementary task
                if supp_tasks:
                    final_tasks.append(supp_tasks[0])
                else:
                    final_tasks.append(tasks[1] if len(tasks) > 1 else {
                        "title_vi": f"Nhật ký Socratic Tuần {req.week} | Socratic Diary",
                        "title_en": f"Socratic Diary Week {req.week}",
                        "description_vi": fb_supp_vi,
                        "description_en": fb_supp_en,
                        "effort": 2
                    })
                final_tasks[1]["type"] = "supplementary"
        
                week_design["tasks"] = final_tasks
            else:
                raise ValueError("No valid text response from LLM proxy")
        
        except Exception as e:
            print(f"Failed to personalize week {req.week}: {e}. Using fallback week tasks.")
            is_fallback = True
            # Fallback to predefined week syllabus tasks
            syllabus = cms_helper.get_cohort_syllabus(cohort_id=req.username)
            matching_week = next((s for s in syllabus if s.get("week") == req.week), None)
            if matching_week:
                week_design = {
                    "title": matching_week.get("title"),
                    "description": matching_week.get("description"),
                    "tasks": matching_week.get("tasks")
                }
            else:
                week_design = {
                    "title": f"Chặng {req.week} của {user_name}: Hành động & Phản tư | Week {req.week}: Action & Reflection",
                    "description": f"Vận hành chu trình thực tế và đào sâu vào những gì {user_name} đã đúc kết được gần đây.",
                    "tasks": [
                        {
                            "title_vi": fb_core_title_vi,
                            "title_en": fb_core_title_en,
                            "type": "core",
                            "description_vi": fb_core_vi,
                            "description_en": fb_core_en,
                            "effort": 3
                        },
                        {
                            "title_vi": f"Nhật ký Socratic Tuần {req.week} | Socratic Diary",
                            "title_en": f"Socratic Diary Week {req.week}",
                            "type": "supplementary",
                            "description_vi": fb_supp_vi,
                            "description_en": fb_supp_en,
                            "effort": 2
                        }
                    ]
                }

        # Update NocoBase/CMS syllabus for this week
        t_vi = week_design.get("title_vi") or week_design.get("title", "")
        t_en = week_design.get("title_en") or week_design.get("title", "")
        t_combined = f"{t_vi} ||| {t_en}" if " ||| " not in t_vi else t_vi

        d_vi = week_design.get("description_vi") or week_design.get("description", "")
        d_en = week_design.get("description_en") or week_design.get("description", "")
        d_combined = f"{d_vi} ||| {d_en}" if " ||| " not in d_vi else d_vi

        combined_tasks_for_syllabus = []
        for t in week_design.get("tasks", []):
            tv = t.get("title_vi") or t.get("title", "")
            te = t.get("title_en") or t.get("title", "")
            tc = f"{tv} ||| {te}" if " ||| " not in tv else tv
            
            dv = t.get("description_vi") or t.get("description", "")
            de = t.get("description_en") or t.get("description", "")
            dc = f"{dv} ||| {de}" if " ||| " not in dv else dv
            
            combined_tasks_for_syllabus.append({
                "title": tc,
                "type": t.get("type", "core"),
                "description": dc,
                "effort": t.get("effort", 3)
            })

        try:
            cms_helper.update_cohort_syllabus_week(
                cohort_id=req.username,
                week=req.week,
                week_data={
                    "title": t_combined,
                    "description": d_combined,
                    "tasks": combined_tasks_for_syllabus
                }
            )
        except Exception as e:
            print(f"Failed to save syllabus to CMS: {e}")

        # Also push into personal_roadmaps table as tasks
        try:
            if user_info:
                for task in week_design.get("tasks", []):
                    task_title_vi = task.get("title_vi") or task.get("title") or ""
                    task_title_en = task.get("title_en") or task.get("title") or ""
                    task_title_combined = f"{task_title_vi} ||| {task_title_en}"

                    task_desc_vi = task.get("description_vi") or task.get("description") or ""
                    task_desc_en = task.get("description_en") or task.get("description") or ""

                    if not task_desc_vi:
                        task_desc_vi = "Nhiệm vụ cốt lõi giúp bạn thực hành tái cấu trúc tư duy sâu." if task.get("type") == "core" else "Nhiệm vụ bổ trợ giúp bạn mở rộng góc nhìn và kiến thức."
                    if not task_desc_en:
                        task_desc_en = "Core Socratic task to practice deep mental unlearning." if task.get("type") == "core" else "Supplementary Socratic task to expand perspective and cognitive growth."

                    task_desc_combined = f"{task_desc_vi} ||| {task_desc_en}"

                    task_data = {
                        "title": task_title_combined,
                        "week": req.week,
                        "status": "in_progress",
                        "goal": task_desc_combined,
                        "type": task.get("type", "core"),
                        "subtasks": [
                            {"title": "Phân tích yêu cầu bài học ||| Analyze lesson requirements", "done": False},
                            {"title": "Hoàn thành chiêm nghiệm Socratic ||| Complete Socratic reflection", "done": False}
                        ],
                        "effort": task.get("effort") or (3 if task.get("type") == "core" else 2)
                    }
                    cms_helper.create_personal_roadmap_task(req.username, task_data)
        except Exception as e:
            print(f"Failed to personalize tasks in personal_roadmaps for week {req.week}: {e}")

        # Auto-generate 8-question quiz immediately from the start
        try:
            if user_info:
                import json
                res_week = cms_helper.request_cms("GET", "/personal_roadmaps", params={
                    "filter": json.dumps({
                        "week": req.week,
                        "$or": [
                            {"fk_user": user_info["id"]},
                            {"relation_roadmaps_user.id": user_info["id"]}
                        ]
                    }),
                    "limit": 1
                })
                roadmaps = res_week.get("data", [])
                if roadmaps:
                    parent_record = roadmaps[0]
                    roadmap_id = parent_record["id"]
                    parent_extra = {}
                    if parent_record.get("graph_data_roadmap"):
                        try:
                            parent_extra = json.loads(parent_record["graph_data_roadmap"])
                        except:
                            pass
            
                    existing_quiz = parent_extra.get("quiz", {})
                    if not (existing_quiz and "questions" in existing_quiz and len(existing_quiz["questions"]) == 8):
                        core_task = next((t for t in week_design.get("tasks", []) if t.get("type") == "core"), None)
                        supp_task = next((t for t in week_design.get("tasks", []) if t.get("type") == "supplementary"), None)
                        if core_task and supp_task:
                            background_tasks.add_task(
                                auto_generate_quiz_for_week,
                                req.username,
                                req.week,
                                roadmap_id,
                                parent_extra,
                                core_task,
                                supp_task,
                                user_info,
                                "vi"
                            )
        except Exception as qe:
            print(f"Auto quiz generation failed in personalize_week: {qe}")

        # Reconstruct combined week_design for frontend response compatibility
        frontend_week_design = {
            "title": t_combined,
            "description": d_combined,
            "tasks": combined_tasks_for_syllabus
        }
        
        if is_fallback:
            return JSONResponse(status_code=200, content={"status": "success", "week_data": frontend_week_design})
        else:
            return JSONResponse(status_code=200, content={"status": "success", "week_data": frontend_week_design})


@app.get("/api/v1/cohort:check_context")
async def check_context_endpoint(username: str):
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")
    chats = cms_helper.get_chat_sessions(username)
    user_prompt_count = 0
    chats_list = list(chats.values())
    for c in chats_list:
        msgs = c.get("chat_history") or c.get("messages") or []
        for m in msgs:
            if m.get("role") == "user":
                user_prompt_count += 1
                
    return {
        "prompt_count": user_prompt_count,
        "is_sufficient": user_prompt_count >= 10,
        "required_count": 10
    }

@app.get("/api/v1/cohort:members")
def get_cohort_members_endpoint():
    members = cms_helper.get_cohort_members()
    return {"members": members}

@app.get("/api/v1/cohort:syllabus")
def get_cohort_syllabus_endpoint(username: Optional[str] = None, week: Optional[int] = None):
    syllabus = cms_helper.get_cohort_syllabus(cohort_id=username) if username else []
    if not syllabus:
        syllabus = cms_helper.get_cohort_syllabus(cohort_id="cohort_04")

    metadata = load_cohort_metadata()
    
    start_date = None
    current_week = 1
    active_quiz = {}
    weekly_progress_history = {}
    if username:
        try:
            import json
            user_info = cms_helper.get_user_by_username(username)
            if user_info:
                # Fetch all personal roadmaps to find max week
                res_roadmaps = cms_helper.request_cms("GET", "/personal_roadmaps", params={
                    "filter": json.dumps({
                        "$or": [
                            {"fk_user": user_info["id"]},
                            {"relation_roadmaps_user.id": user_info["id"]}
                        ]
                    }),
                    "limit": 100
                })
                roadmaps = res_roadmaps.get("data", [])
                weekly_progress_history = {}
                if roadmaps:
                    current_week = max(int(r.get("week") or 1) for r in roadmaps)
                    for r in roadmaps:
                        w = int(r.get("week") or 1)
                        prog_val = r.get("week_progress") or 0.0
                        if prog_val > 1.0:
                            weekly_progress_history[str(w)] = int(prog_val)
                        else:
                            weekly_progress_history[str(w)] = int(prog_val * 100.0)
                    
                    # Determine which week's quiz to return
                    target_quiz_week = week if week is not None else current_week
                    
                    # Find target week roadmap row to get its active quiz
                    active_roadmap = next((r for r in roadmaps if int(r.get("week") or 1) == target_quiz_week), None)
                    if active_roadmap and active_roadmap.get("graph_data_roadmap"):
                        try:
                            extra_data = json.loads(active_roadmap["graph_data_roadmap"])
                            if "quiz" in extra_data:
                                active_quiz = extra_data["quiz"]
                        except:
                            pass
                    
                    # Get start_date
                    res_db = cms_helper.request_cms("GET", "/personal_roadmaps", params={
                        "filter": json.dumps({"fk_user": user_info["id"]}),
                        "sort": "createdAt",
                        "limit": 1
                    })
                    db_data = res_db.get("data", [])
                    if db_data and db_data[0].get("start_date"):
                        start_date = db_data[0].get("start_date")[:10]
        except Exception as e:
            print(f"Error fetching data from DB for {username}: {e}")
            
    if not start_date:
        start_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
    return {
        "syllabus": syllabus,
        "cohort_info": {
            "id": "cohort_04",
            "title": "Personal Roadmap",
            "program": metadata.get("program_title", "The Great Rebuild"),
            "current_week": current_week,
            "total_weeks": 12,
            "current_phase": "unlearn" if current_week <= 2 else ("relearn" if current_week <= 6 else "execute"),
            "weekly_progress_history": weekly_progress_history,
        },
        "active_quiz": active_quiz
    }


@app.get("/api/v1/cohort:activity")
def get_cohort_activity():
    members = cms_helper.get_cohort_members()
    
    # 1. Build a real activity feed from members
    import datetime
    feed = []
    for m in members:
        prog = m.get("week_progress", 0)
        if prog > 0:
            feed.append({
                "type": "success" if prog == 100 else "gold",
                "user": m.get("display_name") or m.get("username"),
                "action": "vừa cập nhật tiến độ lên",
                "target": f"{prog}%!",
                "time": "Hôm nay"
            })
            
    if not feed:
        feed.append({
            "type": "info",
            "user": "Hệ thống",
            "action": "đã khởi tạo Cohort học tập thành công",
            "target": "Chào mừng thành viên mới!",
            "time": "Vừa xong"
        })

    # 2. Calculate real bottlenecks
    late_members = [m for m in members if m.get("week_progress", 0) < 50]
    late_count = len(late_members)
    total_count = len(members)
    late_percentage = round((late_count / total_count) * 100) if total_count > 0 else 0
    
    bottlenecks_list = []
    for m in members:
        prog = m.get("week_progress", 0)
        if prog < 85:
            bottlenecks_list.append({
                "label": f"Điểm nghẽn ở: {m.get('display_name') or m.get('username')}",
                "percentage": 100 - prog,
                "type": "error" if prog < 40 else "warning"
            })
            
    if late_count > 0:
        ai_insight = f"Phát hiện {late_count} thành viên đang bị chậm tiến độ học tập. Coach khuyên bạn nên kích hoạt hành động phụ trợ để hỗ trợ đồng đội!"
    else:
        ai_insight = "Tuyệt vời! Toàn bộ Cohort đang duy trì tiến độ học tập xuất sắc và kỷ luật cao chặng đầu."

    # 3. Dynamic pivot
    triggered = late_count > 0
    reason = f"Phát hiện {late_count} thành viên bị nghẽn học tập." if triggered else "Tiến độ học tập của Cohort cực kỳ ổn định."

    return {
        "feed": feed,
        "bottleneck": {
            "week": 2,
            "generated_at": datetime.datetime.now().isoformat() + "Z",
            "total_members": total_count,
            "late_count": late_count,
            "late_percentage": late_percentage,
            "bottlenecks": bottlenecks_list,
            "ai_insight": ai_insight
        },
        "pivot": {
            "triggered": triggered,
            "reason": reason,
            "pivot_task": {
                "id": "pivot_w3_1",
                "title": "Học tập đồng hành: Hỗ trợ đồng đội gặp khó khăn",
                "description": "Chủ động chia sẻ cách vượt qua điểm nghẽn nhận thức.",
                "type": "supplementary",
                "auto_added": True
            }
        }
    }

@app.post("/api/v1/cohort:member_progress")
@app.post("/api/v1/cohort:update_progress")
def update_member_progress(body: dict):
    username = body.get("username")
    progress = body.get("week_progress")
    if username and progress is not None:
        members = cms_helper.get_cohort_members()
        member_id = None
        for m in members:
            if m["username"] == username:
                member_id = m["id"]
                break
        if not member_id:
            # Fallback: transition the self placeholder
            for m in members:
                if m.get("is_self") or m["username"] == "user":
                    member_id = m["id"]
                    break
        if member_id:
            cms_helper.update_cohort_member_progress(member_id, username, int(progress))
    return {"status": "success"}


def generate_retrospective_helper(username: str, display_name: str, progress: float, tasks: list, request_method: str, lang: str = "vi"):
    bottleneck = {
        "week": 2,
        "generated_at": "2026-05-18T09:00:00Z",
        "total_members": 1,
        "late_count": 0,
        "late_percentage": 0,
        "bottlenecks": [],
        "ai_insight": "Hệ thống ghi nhận tiến độ học tập độc lập của bạn trong Cohort 04. Hãy tiếp tục duy trì kỷ luật và hoàn thành các mục tiêu đề ra!"
    }
    
    if not tasks and request_method == "GET":
        members = cms_helper.get_cohort_members()
        user_member = None
        for m in members:
            if m.get("username") == username or m.get("is_self"):
                user_member = m
                break
        if user_member:
            progress = user_member.get("week_progress", 0)
            default_display = "You" if lang == "en" else "Bạn"
            display_name = user_member.get("display_name", default_display)

    # Analyze the tasks and their statuses
    total_tasks = len(tasks)
    completed_tasks = [t for t in tasks if t.get("status") == "done"]
    pending_tasks = [t for t in tasks if t.get("status") != "done"]

    tasks_summary = ""
    if lang == "en":
        if tasks:
            tasks_summary += f"- Total planned tasks: {total_tasks}\n"
            tasks_summary += f"- Completed tasks: {len(completed_tasks)}\n"
            for t in completed_tasks:
                tasks_summary += f"  + [COMPLETED] {t.get('title')}\n"
            tasks_summary += f"- Remaining tasks: {len(pending_tasks)}\n"
            for t in pending_tasks:
                tasks_summary += f"  + [IN PROGRESS] {t.get('title')}\n"
        else:
            tasks_summary = "- No tasks have been added to this week's tracking list in the DO section yet.\n"
    else:
        if tasks:
            tasks_summary += f"- Tổng số nhiệm vụ đã lập kế hoạch: {total_tasks}\n"
            tasks_summary += f"- Nhiệm vụ đã hoàn thành: {len(completed_tasks)}\n"
            for t in completed_tasks:
                tasks_summary += f"  + [ĐÃ XONG] {t.get('title')}\n"
            tasks_summary += f"- Nhiệm vụ còn lại: {len(pending_tasks)}\n"
            for t in pending_tasks:
                tasks_summary += f"  + [ĐANG LÀM] {t.get('title')}\n"
        else:
            tasks_summary = "- Chưa có nhiệm vụ nào được thêm vào danh sách theo dõi của tuần này trong phần DO.\n"

    if lang == "en":
        ai_prompt = f"""You are the Socratic AI Coach of The Great Rebuild program (PDCA Level 2).
    Write a personalized weekend Retrospective (Evaluation & Reflection) specifically for cohort member "{display_name}" (username: {username}).

    Their progress and actual data from the action (DO) phase this week:
    - Completion progress: {progress}%
    {tasks_summary}

    Requirements:
    1. Directly provide insightful commentary and evaluate their progress based closely on the actual completed / in-progress tasks.
    2. Ask 1 self-reflective question using the Socratic method to help them identify their own bottlenecks, based on uncompleted tasks, time management, or commitment.
    3. The tone must be wise, empathetic, and highly conducive to deep self-awareness.
    4. Write in English, concisely around 80-120 words. Do not use generic cliches or long formal greetings."""
    else:
        ai_prompt = f"""Bạn là AI Socratic Coach của chương trình The Great Rebuild (PDCA Level 2).
    Hãy viết một nhận xét Retrospective (Đánh giá & Chiêm nghiệm) cá nhân hóa cuối tuần dành riêng cho thành viên "{display_name}" (tài khoản: {username}).

    Tiến trình và Dữ liệu thực tế từ phần hành động (DO) của họ tuần này:
    - Tiến độ hoàn thành: {progress}%
    {tasks_summary}

    Yêu cầu:
    1. Trực tiếp nhận xét sâu sắc và đánh giá tiến độ của họ (phải dựa sát thực tế số nhiệm vụ đã hoàn thành / đang thực hiện).
    2. Đưa ra 1 câu hỏi tự vấn phản chiếu theo phương pháp Socratic để họ tự nhận diện điểm nghẽn của mình dựa trên những nhiệm vụ chưa hoàn thành hoặc cách thức quản lý thời gian, sự cam kết.
    3. Giọng điệu thông tuệ, thấu cảm, thúc đẩy sự tự thức tỉnh mạnh mẽ.
    4. Viết bằng tiếng Việt, cô đọng khoảng 80-120 từ. Không dùng các câu từ sáo rỗng hay chào hỏi dài dòng."""

    try:
        from openai import OpenAI as _OpenAI
        _client = _OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
        )
        resp = _client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "thapsang").split(",")[0].strip(),
            messages=[{"role": "user", "content": ai_prompt}],
            max_tokens=1024,
            temperature=0.4,
            top_p=0.95,
        )
        ai_text = resp.choices[0].message.content.strip()
    except Exception as e:
        # Fallback tailored retrospective
        if lang == "en":
            if progress == 100:
                ai_text = f"Congratulations {display_name}! You have successfully completed all planned tasks this week. Reflect on this: how can you elevate your standards of excellence or further optimize your workflow in the next cycle?"
            elif progress > 0:
                ai_text = f"Hello {display_name}, you have completed {progress}% of your pathway this week. Take a moment to reflect on your uncompleted tasks: what invisible bottlenecks or biases are quietly holding you back?"
            else:
                ai_text = f"Hello {display_name}, your progress is currently at {progress}%. What primary barrier is preventing you from taking action? What is the single knot you need to untie first?"
        else:
            if progress == 100:
                ai_text = f"Chúc mừng {display_name}! Bạn đã xuất sắc hoàn thành tất cả nhiệm vụ đặt ra tuần này. Hãy tự hỏi: Bạn có thể nâng cao tiêu chuẩn hiệu suất hoặc tối ưu hóa quy trình làm việc của mình như thế nào trong chặng tiếp theo?"
            elif progress > 0:
                ai_text = f"Chào {display_name}, bạn đã hoàn thành {progress}% chặng đường tuần này. Hãy dành một phút nhìn lại các nhiệm vụ chưa hoàn thành: Có điểm nghẽn hay thiên kiến nào đang âm thầm trì hoãn bạn chạm đích?"
            else:
                ai_text = f"Chào {display_name}, tiến trình của bạn hiện tại là {progress}%. Bạn đang gặp rào cản nào trong việc bắt tay vào hành động? Nút thắt đầu tiên cần tháo gỡ là gì?"

    return {
        "retrospective": ai_text,
        "avg_progress": round(progress, 1),
        "bottlenecks": bottleneck.get("bottlenecks", []),
        "late_percentage": bottleneck.get("late_percentage", 0),
        "week": 2
    }

@app.get("/api/v1/cohort:ai_retrospective")
def get_ai_retrospective_get(username: str = "user", lang: str = "vi"):
    default_display = "You" if lang == "en" else "Bạn"
    return generate_retrospective_helper(username, default_display, 0, [], "GET", lang)

class AIRetrospectiveRequest(BaseModel):
    username: str = "user"
    display_name: str = "Bạn"
    progress: float = 0
    tasks: list = []
    lang: str = "vi"

@app.post("/api/v1/cohort:ai_retrospective")
def get_ai_retrospective_post(req: AIRetrospectiveRequest):
    username = req.username
    display_name = req.display_name
    progress = req.progress
    tasks = req.tasks
    lang = req.lang
    if display_name == "Bạn" and lang == "en":
        display_name = "You"
    return generate_retrospective_helper(username, display_name, progress, tasks, "POST", lang)


class AIBottleneckRequest(BaseModel):
    username: str = "user"
    progress: float = 0
    tasks: list = []
    lang: str = "vi"

@app.post("/api/v1/cohort:ai_bottleneck")
def get_ai_bottleneck(req: AIBottleneckRequest):
    username = req.username
    progress = req.progress
    tasks = req.tasks
    lang = req.lang

    completed_tasks = [t for t in tasks if t.get("status") == "done"]
    pending_tasks = [t for t in tasks if t.get("status") != "done"]

    completed_str = ", ".join([t.get("title") for t in completed_tasks])
    pending_str = ", ".join([t.get("title") for t in pending_tasks])

    if lang == "en":
        ai_prompt = f"""You are the Socratic AI Coach of Thapsang Mindset OS (PDCA Level 2).
Analyze the individual weekly progress and potential cognitive/execution bottlenecks for the user "{username}".

Dữ liệu thực tế:
- Progress completed: {progress}%
- Completed tasks: {completed_str or "None yet"}
- Pending tasks: {pending_str or "None yet"}

Requirements:
1. Provide a Socratic, deep insight (under 60 words) on why they are facing these bottlenecks or how they can sustain momentum.
2. Identify 1-3 specific bottlenecks with labels and estimated difficulty/severity percentage (0-100). Label format should be concise, e.g. "Struggling with task X".
3. Propose a Pivot: if they have any pending tasks, pivot should be triggered (true). Suggest 1 extremely actionable, small, Socratic pivot task to help them bypass the primary bottleneck (e.g., "Divide X into 15-minute micro-steps").
4. If progress is 100%, triggered should be true (or false) but pivot task should be "Plan next week's goals early".

Return ONLY a valid JSON object matching this schema (do NOT wrap it in any Markdown codeblocks or other formatting, just return raw JSON):
{{
  "ai_insight": "Concise Socratic insight...",
  "bottlenecks": [
    {{"label": "Specific bottleneck label", "percentage": 85, "type": "error"}},
    ...
  ],
  "pivot": {{
    "triggered": true,
    "reason": "Socratic reasoning why they need this minor adjustment",
    "pivot_task": {{
      "title": "Supporting task title...",
      "description": "Short description...",
      "type": "supplementary",
      "auto_added": true
    }}
  }}
}}
"""
    else:
        ai_prompt = f"""Bạn là AI Socratic Coach của chương trình Thapsang Mindset OS (PDCA Level 2).
Hãy phân tích tiến độ tuần và các điểm nghẽn nhận thức/hành động của người dùng "{username}".

Dữ liệu thực tế:
- Tiến độ hoàn thành: {progress}%
- Nhiệm vụ đã xong: {completed_str or "Chưa có"}
- Nhiệm vụ chưa xong: {pending_str or "Chưa có"}

Yêu cầu:
1. Đưa ra chiêm nghiệm Socratic sâu sắc (dưới 60 từ) về lý do họ gặp điểm nghẽn hoặc cách họ duy trì đà phát triển.
2. Xác định 1-3 điểm nghẽn cụ thể với nhãn (label) và mức độ nghẽn/trở lực (percentage từ 0 đến 100). Định dạng nhãn ngắn gọn, ví dụ: "Gặp khó khăn ở nhiệm vụ X".
3. Đề xuất một Pivot (Điều chỉnh linh hoạt): nếu họ còn nhiệm vụ chưa xong, triggered sẽ là true. Đề xuất 1 nhiệm vụ phụ trợ rất nhỏ, cực kỳ dễ thực hiện để giúp họ vượt qua điểm nghẽn (ví dụ: "Chia nhỏ X thành các bước 15 phút").
4. Nếu tiến độ là 100%, triggered có thể là true/false và đề xuất nhiệm vụ lập kế hoạch sớm cho tuần tới.

Hãy trả về DUY NHẤT một đối tượng JSON hợp lệ tuân thủ chính xác cấu trúc sau (không bọc trong khối code markdown, không giải thích gì thêm):
{{
  "ai_insight": "Chiêm nghiệm Socratic ngắn gọn...",
  "bottlenecks": [
    {{"label": "Nhãn điểm nghẽn cụ thể", "percentage": 85, "type": "error"}},
    ...
  ],
  "pivot": {{
    "triggered": true,
    "reason": "Lý do Socratic vì sao cần điều chỉnh nhỏ này",
    "pivot_task": {{
      "title": "Tên nhiệm vụ phụ trợ...",
      "description": "Mô tả ngắn...",
      "type": "supplementary",
      "auto_added": true
    }}
  }}
}}
"""

    try:
        from openai import OpenAI as _OpenAI
        _client = _OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
        )
        resp = _client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "thapsang").split(",")[0].strip(),
            messages=[{"role": "user", "content": ai_prompt}],
            max_tokens=1024,
            temperature=0.2,
            top_p=0.9,
        )
        ai_text = resp.choices[0].message.content.strip()
        if ai_text.startswith("```json"):
            ai_text = ai_text[7:]
        if ai_text.endswith("```"):
            ai_text = ai_text[:-3]
        import re
        ai_text = re.sub(r'<think>.*?</think>', '', ai_text, flags=re.DOTALL).strip()
        import json
        res_data = json.loads(ai_text)
        return res_data
    except Exception as e:
        print(f"AI Bottleneck analysis failed: {e}")
        # Fallback
        is_en = lang == "en"
        if progress == 100:
            return {
                "ai_insight": "Congratulations! 100% weekly goals completed." if is_en else "Chúc mừng! Bạn đã hoàn thành 100% mục tiêu của tuần.",
                "bottlenecks": [{"label": "No bottlenecks" if is_en else "Không có điểm nghẽn", "percentage": 0, "type": "success"}],
                "pivot": {
                    "triggered": True,
                    "reason": "Sustaining momentum by preparing ahead." if is_en else "Duy trì đà phát triển bằng cách chuẩn bị trước.",
                    "pivot_task": {
                        "title": "Set Next Week's Plan Early" if is_en else "Thiết lập Kế hoạch sớm cho Tuần tiếp",
                        "description": "Plan key tasks for the upcoming week." if is_en else "Hoạch định các mục tiêu cốt lõi tuần tới.",
                        "type": "supplementary",
                        "auto_added": True
                    }
                }
            }
        else:
            primary_task = pending_tasks[0].get("title", "Active Task") if pending_tasks else ("Active Task" if is_en else "Nhiệm vụ đang làm")
            return {
                "ai_insight": f"Bottleneck detected at '{primary_task}'." if is_en else f"Phát hiện điểm nghẽn tại '{primary_task}'.",
                "bottlenecks": [{"label": f"Difficulty: {primary_task}" if is_en else f"Trở ngại ở: {primary_task}", "percentage": 75, "type": "error"}],
                "pivot": {
                    "triggered": True,
                    "reason": "Break down stalled task." if is_en else "Chia nhỏ nhiệm vụ đang bị đình trệ.",
                    "pivot_task": {
                        "title": f"Deconstruct '{primary_task}'" if is_en else f"Chia nhỏ '{primary_task}'",
                        "description": "Divide into smaller subtasks." if is_en else "Phân rã thành các phần việc nhỏ hơn.",
                        "type": "supplementary",
                        "auto_added": True
                    }
                }
            }


# --- CORE API ENDPOINTS ---
@app.get("/api/v1/db:chats")
def get_chats(username: Optional[str] = None):
    return cms_helper.get_chat_sessions(username)

@app.post("/api/v1/db:chats")
def save_chats(data: dict):
    saved_ids = {}
    for session_id, chat_data in data.items():
        username = chat_data.get("username")
        if username:
            try:
                saved_entry = cms_helper.save_chat_session(session_id, username, chat_data)
                if saved_entry and "id" in saved_entry:
                    saved_ids[session_id] = str(saved_entry["id"])
            except Exception as e:
                print(f"Error saving chat session {session_id} for user {username}: {e}")
    return {"status": "success", "saved_ids": saved_ids}

@app.delete("/api/v1/db_chats:delete/{session_id}")
def delete_chat(session_id: str):
    success = cms_helper.delete_chat_session(session_id)
    if success:
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Không tìm thấy phiên thảo luận")

@app.get("/api/v1/db:aoa")
def get_aoa_db():
    return aoa.load_aoa_db()

@app.post("/api/v1/db:aoa")
def save_aoa_db(data: dict):
    return {"status": "success"}

# --- FRONTEND BRIDGE ENDPOINTS ---
@app.post("/api/v1/auth:login")
def login(req: LoginRequest):
    user_info = cms_helper.get_user_by_username(req.username)
    if not user_info:
        user_info = cms_helper.get_user_by_email(req.username)
        
    if not user_info:
        # Fallback for default user
        if req.username == "user" and req.password in ["user123", "Thapsang@123"]:
            # Auto-create fallback user in CMS so future operations succeed
            try:
                cms_helper.create_user({
                    "username": "user",
                    "password": "Thapsang@123",
                    "email": "user@thapsang.vn",
                    "displayName": "Bạn",
                    "bio": "Học hỏi, chia sẻ và cùng nhau phát triển tại cộng đồng Thapsang. Đam mê tri thức và sự sáng tạo.",
                    "avatar": "",
                    "banner": "",
                    "following_list": [],
                    "onboarded": False
                })
            except Exception as e:
                pass
            user_info = cms_helper.get_user_by_username("user")
            
            # If still no user_info (e.g. CMS is down), mock one
            if not user_info:
                user_info = {
                    "username": "user",
                    "email": "user@thapsang.vn",
                    "displayName": "Bạn",
                    "bio": "Học hỏi, chia sẻ và cùng nhau phát triển tại cộng đồng Thapsang. Đam mê tri thức và sự sáng tạo.",
                    "avatar": "",
                    "banner": "",
                    "following_list": [],
                    "onboarded": False
                }
            
    if not user_info:
        raise HTTPException(status_code=401, detail="Sai thông tin đăng nhập")
        
    authenticated = False
    auth_err_msg = ""
    if user_info:
        if user_info.get("email"):
            authenticated, auth_err_msg = cms_helper.authenticate_user(user_info["email"], req.password)
        if not authenticated and user_info.get("username"):
            authenticated, auth_err_msg = cms_helper.authenticate_user(user_info["username"], req.password)
        if not authenticated and user_info.get("password") == req.password:
            authenticated = True
            
    # Always allow the default 'user' with correct password to bypass CMS auth
    if not authenticated and req.username == "user" and req.password in ["user123", "Thapsang@123"]:
        authenticated = True
            
    if not authenticated:
        if "maximum number of sign-in attempts" in auth_err_msg:
            raise HTTPException(status_code=429, detail="Số lần nhập sai đã hơn 5 lần, vui lòng thử lại sau.")
        
        # Write debug info to a file in the mounted database volume
        debug_path = os.path.join(DATABASE_DIR, "debug_login.txt")
        try:
            with open(debug_path, "a", encoding="utf-8") as f:
                import datetime
                f.write(f"[{datetime.datetime.now()}] Login failed for '{req.username}'. user_info found: {bool(user_info)}\n")
                if user_info:
                    f.write(f"   Password matches plain text: {user_info.get('password') == req.password}\n")
        except:
            pass
        raise HTTPException(status_code=401, detail="Sai thông tin đăng nhập")
        
    return {
        "status": "success",
        "username": user_info["username"],
        "avatar": user_info.get("avatar", ""),
        "banner": user_info.get("banner", ""),
        "displayName": user_info.get("displayName", user_info["username"]),
        "bio": user_info.get("bio", "Học hỏi, chia sẻ và cùng nhau phát triển tại cộng đồng Thapsang. Đam mê tri thức và sự sáng tạo."),
        "following_list": user_info.get("following_list", []),
        "onboarded": user_info.get("onboarded", False)
    }

@app.get("/api/v1/auth_profile:get/{username}")
def get_user_profile(username: str):
    user_info = cms_helper.get_user_by_username(username)
    if not user_info:
        clean_name = username.split("@")[0] if "@" in username else username
        return {
            "username": username,
            "displayName": clean_name,
            "bio": "Học hỏi, chia sẻ và cùng nhau phát triển tại cộng đồng Thapsang. Đam mê tri thức và sự sáng tạo.",
            "avatar": "",
            "banner": "",
            "following_list": [],
            "onboarded": False
        }
    
    clean_display = user_info.get("displayName", username)
    if clean_display and "@" in clean_display:
        clean_display = clean_display.split("@")[0]
        
    return {
        "username": username,
        "displayName": clean_display,
        "bio": user_info.get("bio", "Học hỏi, chia sẻ và cùng nhau phát triển tại cộng đồng Thapsang. Đam mê tri thức và sự sáng tạo."),
        "avatar": user_info.get("avatar", ""),
        "banner": user_info.get("banner", ""),
        "following_list": user_info.get("following_list", []),
        "onboarded": user_info.get("onboarded", False)
    }

@app.post("/api/v1/auth_profile:post/{username}")
async def update_user_profile(username: str, request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    
    user_info = cms_helper.get_user_by_username(username)
    if not user_info:
        cms_helper.create_user({
            "username": username,
            "password": "defaultpassword123",
            "displayName": data.get("displayName", username),
            "bio": data.get("bio", ""),
            "avatar": data.get("avatar", ""),
            "banner": data.get("banner", ""),
            "following_list": data.get("following_list", []),
            "onboarded": data.get("onboarded", False)
        })
    else:
        cms_helper.update_user(user_info["id"], data)
    return {"status": "success"}

# --- ONBOARDING API ENDPOINTS ---
@app.post("/api/v1/auth_onboarding:post/{username}")
async def save_onboarding(username: str, request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    
    user_info = cms_helper.get_user_by_username(username)
    if not user_info:
        cms_helper.create_user({
            "username": username,
            "password": "defaultpassword123",
            "onboarding": data,
            "onboarded": True
        })
    else:
        cms_helper.update_user(user_info["id"], {"onboarding": data, "onboarded": True})
        
    generated_context = None
    try:
        generated_context = context_learner.generate_context_from_onboarding(username, data)
    except Exception as e:
        print(f"Error generating context from onboarding for {username}: {e}")
    return {"status": "success", "context": generated_context}

@app.get("/api/v1/profile:get/{username}/context")
def get_user_context(username: str):
    user_info = cms_helper.get_user_by_username(username)
    if not user_info:
        return {"username": username, "context": None}
    onboarding = user_info.get("onboarding") or {}
    ctx = onboarding.get("_core_context") if isinstance(onboarding, dict) else None
    return {"username": username, "context": ctx}

@app.get("/api/v1/auth_onboarding:get/{username}")
def get_onboarding(username: str):
    user_info = cms_helper.get_user_by_username(username)
    if not user_info:
        return {"onboarded": False, "data": None}
    return {"onboarded": user_info.get("onboarded", False), "data": user_info.get("onboarding")}

# --- DIARY API ENDPOINTS ---
class GenerateDiaryRequest(BaseModel):
    session_id: str
    username: str
    model: Optional[str] = None

@app.post("/api/v1/diary:generate")
def api_generate_diary(req: GenerateDiaryRequest, background_tasks: BackgroundTasks):
    try:
        sessions = cms_helper.get_chat_sessions(req.username)
        session_data = sessions.get(str(req.session_id))
        if not session_data:
            return {"error": "Session not found"}
            
        history_for_summary = session_data.get("chat_history", [])
        
        session_title = session_data.get("custom_title") if session_data and session_data.get("custom_title") else ""
        if not session_title:
            if history_for_summary and "title" in history_for_summary[0] and history_for_summary[0]["title"]:
                session_title = history_for_summary[0]["title"]
            else:
                session_title = req.session_id or "Chưa đặt tên"
                
        if session_title.startswith("temp_"):
            session_title = "Phiên mới"
            
        print(f"DEBUG: Triggering manual diary summary for user {req.username}, session {session_title}")
        background_tasks.add_task(
            generate_coach_clinical_diary_summary,
            req.username,
            session_title,
            history_for_summary,
            req.model
        )
        return {"status": "success", "message": "Diary generation started"}
    except Exception as ex:
        print("Lỗi khi trigger manual diary summary:", ex)
        raise HTTPException(status_code=500, detail=str(ex))

class DiaryEntryRequest(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    mood: Optional[str] = "Calm"
    folder: Optional[str] = ""
    skip_ai: Optional[bool] = False

class FolderRequest(BaseModel):
    name: str

@app.get("/api/v1/diary:get/{username}")
def get_diaries(username: str):
    return cms_helper.get_diary_entries(username)

@app.post("/api/v1/diary:create/{username}")
def create_diary(username: str, req: DiaryEntryRequest):
    ai_insight = "AI Socratic Coach đang chờ suy ngẫm từ bài viết của bạn. Hãy viết nội dung và nhấn 'Lưu & Khám phá AI' để soi chiếu bản thân."
    
    existing = None
    if req.id and not str(req.id).startswith("temp_"):
        try:
            res = cms_helper.request_cms("GET", f"/diary_entries/{req.id}")
            existing_data = res.get("data")
            if isinstance(existing_data, dict):
                existing = existing_data
            elif isinstance(existing_data, list) and len(existing_data) > 0:
                existing = existing_data[0]
        except:
            pass

    if req.skip_ai and existing:
        ai_insight = existing.get("aiInsight", ai_insight)
    elif req.content.strip():
        ai_prompt = f"""Bạn là AI Socratic Coach của hệ thống Thapsang.
        Người dùng '{username}' vừa viết nhật ký tự sự (Diary/Self-Reflection) với tâm trạng '{req.mood}':
        Tiêu đề: {req.title}
        Nội dung: {req.content}
        
        Hãy đưa ra 1 lời phản hồi ngắn gọn dưới 80 từ theo phương pháp Socratic. Thay vì đưa ra lời khuyên sáo rỗng, hãy đặt 1 câu hỏi sâu sắc để giúp người dùng tự phản tỉnh và nhìn thấu bản chất vấn đề. Viết bằng tiếng Việt cực kỳ ấm áp và trí tuệ."""
        
        try:
            from openai import OpenAI as _OpenAI
            _client = _OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
            )
            resp = _client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "thapsang").split(",")[0].strip(),
                messages=[{"role": "user", "content": ai_prompt}],
                max_tokens=200,
                temperature=0.4,
                top_p=0.95
            )
            ai_insight = resp.choices[0].message.content.strip()
        except Exception as e:
            print("Diary AI Error:", e)
            ai_insight = "Cuộc sống luôn có những góc nhìn ẩn giấu. Bạn có nghĩ điều bận tâm này đang là tấm gương phản chiếu mong muốn thực sự bên trong bạn?"

    date_val = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if req.skip_ai and existing and existing.get("date"):
        date_val = existing.get("date")

    entry_data = {
        "title": req.title,
        "content": req.content,
        "folder": req.folder or "",
        "ai_insight": ai_insight,
        "date": date_val
    }
    
    entry_to_return = cms_helper.save_diary_entry(req.id, username, entry_data)
    return {"status": "success", "entry": entry_to_return}

@app.delete("/api/v1/diary:destroy/{username}/{entry_id}")
def delete_diary(username: str, entry_id: str):
    cms_helper.delete_diary_entry(entry_id)
    return {"status": "success"}

@app.get("/api/v1/diary:get/{username}/folders")
def get_diary_folders(username: str):
    return cms_helper.get_diary_folders(username)

@app.post("/api/v1/diary:create/{username}/folders")
def add_diary_folder(username: str, req: FolderRequest):
    cms_helper.create_diary_folder(username, req.name.strip())
    folders = cms_helper.get_diary_folders(username)
    return {"status": "success", "folders": folders}

@app.delete("/api/v1/diary_{username}:delete/folders/{folder_name}")
def delete_diary_folder(username: str, folder_name: str):
    cms_helper.delete_diary_folder(username, folder_name)
    return {"status": "success"}



# --- OTP STORE ---
OTP_STORE = {}

import random
import string
import smtplib
from email.message import EmailMessage

def generate_otp(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def send_otp_email(to_email: str, otp: str):
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not smtp_user or not smtp_password:
        raise ValueError("SMTP credentials are not configured in environment variables.")
        
    msg = EmailMessage()
    msg['Subject'] = 'Mã xác nhận OTP - Thapsang'
    msg['From'] = smtp_user
    msg['To'] = to_email

    html_content = f"""
    <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #dfe2eb; background-color: #0a0c10; margin: 0; padding: 0;">
            <div style="max-width: 600px; margin: 20px auto; padding: 40px; background-color: #10141a; border: 1px solid #2d323d; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #e9c400; margin: 0; font-size: 28px; letter-spacing: 2px; text-transform: uppercase;">Thapsang</h1>
                    <div style="width: 50px; height: 2px; background: #e9c400; margin: 10px auto;"></div>
                </div>
                
                <p style="font-size: 16px; color: #b0b8c9;">Chào bạn,</p>
                <p style="font-size: 16px; color: #b0b8c9;">Bạn vừa yêu cầu mã xác thực để gia nhập cộng đồng <b>Thapsang</b>. Hãy sử dụng mã OTP dưới đây để hoàn tất quá trình đăng ký:</p>
                
                <div style="text-align: center; margin: 40px 0;">
                    <div style="display: inline-block; background: rgba(233, 196, 0, 0.1); border: 2px solid #e9c400; padding: 15px 30px; border-radius: 12px;">
                        <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #e9c400; font-family: monospace;">
                            {otp}
                        </span>
                    </div>
                </div>
                
                <p style="font-size: 14px; color: #8a94a6; text-align: center;">Mã có hiệu lực trong 5 phút. Nếu bạn không thực hiện yêu cầu này, vui lòng bỏ qua email.</p>
                
                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #2d323d; text-align: center;">
                    <p style="font-size: 12px; color: #5c667a; margin: 0;">
                        Thapsang - Kiến tạo bản đồ tư duy & Phản chiếu tri thức
                    </p>
                    <p style="font-size: 11px; color: #444b59; margin-top: 5px;">
                        Đây là tin nhắn tự động, vui lòng không phản hồi.
                    </p>
                </div>
            </div>
        </body>
    </html>
    """
    msg.add_alternative(html_content, subtype='html')
    
    try:
        # Thêm timeout 15 giây để tránh bị treo nếu mạng lỗi
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15)
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"Đã gửi email OTP thành công tới {to_email}")
    except smtplib.SMTPAuthenticationError:
        print(f"LỖI XÁC THỰC: Gmail từ chối mật khẩu. Hãy đảm bảo bạn dùng 'Mật khẩu ứng dụng' và đã bật 2FA.")
    except Exception as e:
        print(f"LỖI GỬI EMAIL CHI TIẾT: {type(e).__name__} - {e}")

@app.post("/api/v1/auth:request_otp")
def request_otp(req: RequestOTPRequest):
    # Check if user exists by email or by username matching email
    user_info = cms_helper.get_user_by_email(req.email)
    if not user_info:
        user_info = cms_helper.get_user_by_username(req.email)
    if not user_info and req.username:
        user_info = cms_helper.get_user_by_username(req.username)
        
    if user_info or req.email == "user" or (req.username and req.username == "user"):
        raise HTTPException(status_code=400, detail="Tài khoản đã tồn tại")
    
    otp = generate_otp()
    OTP_STORE[req.email] = otp
    
    # Gửi email thật
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    if not smtp_user or not smtp_password or "@" not in smtp_user:
        raise HTTPException(
            status_code=500,
            detail="Hệ thống chưa được cấu hình dịch vụ gửi email (SMTP). Vui lòng thiết lập biến môi trường SMTP_USER và SMTP_PASSWORD."
        )
    
    send_otp_email(req.email, otp)
    print(f"📩 Hệ thống đang gửi mã OTP tới email: {req.email}")
        
    return {"status": "success", "message": "OTP đã được gửi"}

@app.post("/api/v1/auth:register")
def register(req: RegisterRequest):
    if req.email not in OTP_STORE or OTP_STORE[req.email].upper() != req.otp.upper():
        raise HTTPException(status_code=400, detail="Mã OTP không hợp lệ hoặc đã hết hạn")

    username = req.email
    user_info = cms_helper.get_user_by_email(req.email)
    if not user_info:
        user_info = cms_helper.get_user_by_username(username)
    if not user_info and req.username:
        user_info = cms_helper.get_user_by_username(req.username)
        
    if user_info or username == "user" or (req.username and req.username == "user"):
        raise HTTPException(status_code=400, detail="Tài khoản đã tồn tại")
    
    try:
        cms_helper.create_user({
            "username": username,
            "password": req.password,
            "email": req.email,
            "displayName": req.full_name or username,
            "bio": "Học hỏi, chia sẻ và cùng nhau phát triển tại cộng đồng Thapsang. Đam mê tri thức và sự sáng tạo.",
            "avatar": "",
            "banner": "",
            "following_list": [],
            "onboarded": False
        })
    except Exception as e:
        error_msg = "Có lỗi xảy ra khi tạo tài khoản"
        if hasattr(e, "response") and e.response is not None:
            try:
                err_data = e.response.json()
                if "errors" in err_data and len(err_data["errors"]) > 0:
                    cms_msg = err_data["errors"][0].get("message", "")
                    if "username in password" in cms_msg:
                        error_msg = "Mật khẩu không được chứa tên đăng nhập"
                    elif "alpha and numeric" in cms_msg:
                        error_msg = "Mật khẩu phải bao gồm cả chữ cái và chữ số"
                    elif "already exists" in cms_msg:
                        error_msg = "Tài khoản hoặc email đã tồn tại"
                    elif cms_msg:
                        error_msg = cms_msg
            except:
                pass
        raise HTTPException(status_code=400, detail=error_msg)
    
    if req.email in OTP_STORE:
        del OTP_STORE[req.email]
    
    return {
        "status": "success",
        "username": username,
        "avatar": "",
        "banner": "",
        "displayName": req.full_name or username,
        "bio": "Học hỏi, chia sẻ và cùng nhau phát triển tại cộng đồng Thapsang. Đam mê tri thức và sự sáng tạo.",
        "following_list": []
    }

@app.post("/api/v1/auth:forgot_password_request_otp")
def forgot_password_request_otp(req: RequestOTPRequest):
    user_info = cms_helper.get_user_by_email(req.email)
    if not user_info:
        raise HTTPException(status_code=404, detail="Email không tồn tại trong hệ thống")
        
    otp = generate_otp()
    OTP_STORE[req.email] = otp
    
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    if not smtp_user or not smtp_password or "@" not in smtp_user:
        raise HTTPException(
            status_code=500,
            detail="Hệ thống chưa được cấu hình dịch vụ gửi email (SMTP). Vui lòng thiết lập biến môi trường SMTP_USER và SMTP_PASSWORD."
        )
    
    send_otp_email(req.email, otp)
    print(f"📩 Hệ thống đang gửi mã Khôi phục mật khẩu tới email: {req.email}")
        
    return {"status": "success", "message": "OTP khôi phục đã được gửi"}

@app.post("/api/v1/auth:forgot_password_reset")
def forgot_password_reset(req: ForgotPasswordResetRequest):
    if req.email not in OTP_STORE or OTP_STORE[req.email].upper() != req.otp.upper():
        raise HTTPException(status_code=400, detail="Mã OTP không hợp lệ hoặc đã hết hạn")

    user_info = cms_helper.get_user_by_email(req.email)
    if not user_info:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
        
    try:
        cms_helper.update_user(user_info["id"], {"password": req.new_password})
    except Exception as e:
        error_str = str(e)
        # Handle CMS password validation errors gracefully
        if "Password must be different" in error_str:
            raise HTTPException(status_code=400, detail="Mật khẩu mới phải khác với 3 mật khẩu gần đây nhất.")
        if "must include" in error_str or "alphanumeric" in error_str.lower() or "alpha and numeric" in error_str:
            raise HTTPException(status_code=400, detail="Mật khẩu phải bao gồm cả chữ và số.")
        raise HTTPException(status_code=400, detail="Mật khẩu không hợp lệ theo quy tắc của hệ thống.")
    
    if req.email in OTP_STORE:
        del OTP_STORE[req.email]
    
    return {"status": "success", "message": "Mật khẩu đã được đặt lại thành công"}

@app.get("/api/v1/profile:get/{username}/stats")
def get_stats(username: str):
    try:
        stats = user_profile.get_user_stats(username)
    except Exception as e:
        stats = [85, 75, 60, 90, 65, 80]
    return {"stats": stats}

@app.get("/api/v1/profile:get/{username}/mindset")
def get_mindset(username: str):
    """Phân tích toàn diện tư duy người dùng từ AOA + Coach."""
    try:
        result = mindset_analyzer.analyze_mindset(username)
        return result
    except Exception as e:
        print(f"[mindset] Error for {username}: {e}")
        # Fallback an toàn
        return {
            "radar_stats": [75, 70, 65, 80, 60, 72],
            "dims": ["Khách quan", "Cảm xúc", "Tiêu cực", "Tích cực", "Sáng tạo", "Tổng quan"],
            "keywords": ["Tư duy logic", "Sáng tạo", "Cân bằng cảm xúc", "Lập kế hoạch"],
            "analysis_text": "AI đang thu thập dữ liệu. Hãy tiếp tục chia sẻ trên AOA và trò chuyện với Coach.",
            "mbti_suggestions": [
                {"type": "INFJ", "score": 65, "reason": "Phong cách viết sâu sắc, hướng nội, tìm kiếm ý nghĩa trong trải nghiệm."},
                {"type": "INTJ", "score": 25, "reason": "Khuynh hướng lập kế hoạch chiến lược và tư duy hệ thống."},
                {"type": "INFP", "score": 10, "reason": "Biểu đạt cảm xúc tinh tế và tính lý tưởng."},
            ]
        }

@app.get("/api/v1/aoa:posts")
def get_aoa_posts():
    return aoa.load_aoa_db()

@app.post("/api/v1/aoa:posts")
def create_aoa_post(req: PostRequest):
    try:
        new_post = aoa.create_post(req.author_name, req.author_avatar, req.content, req.graph_data, req.post_privacy)
        return {"status": "success", "post": new_post}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating post: {str(e)}")

@app.post("/api/v1/aoa_posts:post/{post_id}/like")
def like_aoa_post(post_id: str, username: str):
    db = aoa.load_aoa_db()
    for post in db["posts"]:
        if post["id"] == post_id:
            likes_data = aoa.load_json_db(aoa.AOA_LIKES_FILE, {})
            if post_id not in likes_data:
                likes_data[post_id] = []
                
            if username in likes_data[post_id]:
                likes_data[post_id].remove(username)
                new_likes_count = max(0, post.get("likes", 1) - 1)
                liked_status = False
            else:
                likes_data[post_id].append(username)
                new_likes_count = post.get("likes", 0) + 1
                liked_status = True
                
            aoa.save_json_db(aoa.AOA_LIKES_FILE, likes_data)
            cms_helper.update_aoa_post(post_id, {"likes": new_likes_count})
            return {"status": "success", "likes": new_likes_count, "liked": liked_status}
    raise HTTPException(status_code=404, detail="Post not found")

@app.post("/api/v1/aoa_posts:post/{post_id}/comment")
def comment_aoa_post(post_id: str, req: CommentRequest):
    try:
        import datetime
        
        comment_content = req.content
            
        cms_helper.add_aoa_comment(post_id, req.author_name, req.author_avatar, comment_content)
        
        db = aoa.load_aoa_db()
        for post in db["posts"]:
            if post["id"] == post_id:
                return {"status": "success", "comments": post.get("comments", [])}
        raise HTTPException(status_code=404, detail="Post not found")
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error adding comment: {str(e)}")

@app.post("/api/v1/aoa_posts:post/{post_id}/report")
def report_aoa_post(post_id: str, req: ReportPostRequest):
    try:
        db = aoa.load_aoa_db()
        for post in db["posts"]:
            if str(post.get("id")) == str(post_id):
                existing_report = post.get("report") or ""
                new_report_entry = f"Id người báo cáo: {req.username}\nHạng mục bị báo cáo: {req.category}\nChi tiết báo cáo: {req.details}"
                
                if existing_report.strip():
                    updated_report = f"{existing_report}\n---\n{new_report_entry}"
                else:
                    updated_report = new_report_entry
                
                cms_helper.update_aoa_post(post_id, {"report": updated_report})
                return {"status": "success"}
                
        raise HTTPException(status_code=404, detail="Post not found")
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error reporting post: {str(e)}")

@app.patch("/api/v1/aoa_posts:patch/{post_id}")
def update_aoa_post_content(post_id: str, req: UpdatePostRequest):
    try:
        db = aoa.load_aoa_db()
        for post in db["posts"]:
            if post["id"] == post_id:
                if post["author_name"] != req.username:
                    raise HTTPException(status_code=403, detail="Not authorized to edit this post")
                
                cms_helper.update_aoa_post(post_id, {"content": req.content})
                return {"status": "success", "content": req.content}
                
        raise HTTPException(status_code=404, detail="Post not found")
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating post: {str(e)}")

@app.delete("/api/v1/aoa_posts:delete/{post_id}")
def delete_aoa_post(post_id: str, username: str, permanent: bool = False):
    try:
        db = aoa.load_aoa_db()
        for i, post in enumerate(db["posts"]):
            if post["id"] == post_id:
                if post["author_name"] != username:
                    raise HTTPException(status_code=403, detail="Not authorized to delete this post")
                
                if permanent:
                    cms_helper.delete_aoa_post(post_id)
                    status = "permanent_deleted"
                else:
                    cms_helper.update_aoa_post(post_id, {"post_status": "deleted"})
                    actions_data = aoa.load_json_db(aoa.AOA_ACTIONS_FILE, {})
                    if post_id not in actions_data:
                        actions_data[post_id] = {}
                    if "deleted_by" not in actions_data[post_id]:
                        actions_data[post_id]["deleted_by"] = []
                    if username not in actions_data[post_id]["deleted_by"]:
                        actions_data[post_id]["deleted_by"].append(username)
                    aoa.save_json_db(aoa.AOA_ACTIONS_FILE, actions_data)
                    status = "soft_deleted"
                    
                update_repost_shares(post_id, -1)
                return {"status": "success", "action": status}
        raise HTTPException(status_code=404, detail="Post not found")
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error deleting post: {str(e)}")

def update_repost_shares(post_id: str, increment: int):
    try:
        import aoa
        import cms_helper
        reposts_data = aoa.load_json_db(aoa.REPOSTS_FILE, {})
        if post_id in reposts_data:
            orig_id = str(reposts_data[post_id].get("id"))
            db_local = aoa.load_aoa_db()
            for op in db_local["posts"]:
                if str(op["id"]) == orig_id:
                    new_shares = max(0, op.get("shares", 0) + increment)
                    cms_helper.update_aoa_post(orig_id, {"shares": new_shares})
                    break
    except Exception as e:
        import traceback
        traceback.print_exc()

@app.post("/api/v1/aoa_posts:post/{post_id}/restore")
def restore_aoa_post(post_id: str, username: str):
    try:
        cms_helper.update_aoa_post(post_id, {"post_status": "active"})
        update_repost_shares(post_id, 1)
        actions_data = aoa.load_json_db(aoa.AOA_ACTIONS_FILE, {})
        if post_id in actions_data:
            if "deleted_by" in actions_data[post_id] and username in actions_data[post_id]["deleted_by"]:
                actions_data[post_id]["deleted_by"].remove(username)
            if "hidden_by" in actions_data[post_id] and username in actions_data[post_id]["hidden_by"]:
                actions_data[post_id]["hidden_by"].remove(username)
            aoa.save_json_db(aoa.AOA_ACTIONS_FILE, actions_data)
        return {"status": "success", "message": "Post restored"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error restoring post: {str(e)}")

@app.post("/api/v1/aoa_posts:post/{post_id}/hide")
def hide_aoa_post(post_id: str, username: str):
    try:
        db = aoa.load_aoa_db()
        current_status = "active"
        for post in db["posts"]:
            if post["id"] == post_id:
                current_status = post.get("post_status") or "active"
                break

        actions_data = aoa.load_json_db(aoa.AOA_ACTIONS_FILE, {})
        if post_id not in actions_data:
            actions_data[post_id] = {}
        if "hidden_by" not in actions_data[post_id]:
            actions_data[post_id]["hidden_by"] = []
            
        if username in actions_data[post_id]["hidden_by"] or current_status == "hidden":
            if username in actions_data[post_id]["hidden_by"]:
                actions_data[post_id]["hidden_by"].remove(username)
            status = "unhidden"
            cms_helper.update_aoa_post(post_id, {"post_status": "active"})
            update_repost_shares(post_id, 1)
        else:
            if username not in actions_data[post_id]["hidden_by"]:
                actions_data[post_id]["hidden_by"].append(username)
            status = "hidden"
            cms_helper.update_aoa_post(post_id, {"post_status": "hidden"})
            update_repost_shares(post_id, -1)
            
        aoa.save_json_db(aoa.AOA_ACTIONS_FILE, actions_data)
        return {"status": "success", "action": status}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error hiding post: {str(e)}")

@app.post("/api/v1/aoa_posts:post/{post_id}/save")
def save_aoa_post(post_id: str, username: str):
    try:
        actions_data = aoa.load_json_db(aoa.AOA_ACTIONS_FILE, {})
        if post_id not in actions_data:
            actions_data[post_id] = {}
        if "saved_by" not in actions_data[post_id]:
            actions_data[post_id]["saved_by"] = []
            
        if username in actions_data[post_id]["saved_by"]:
            actions_data[post_id]["saved_by"].remove(username)
            saved_status = False
        else:
            actions_data[post_id]["saved_by"].append(username)
            saved_status = True
            
        aoa.save_json_db(aoa.AOA_ACTIONS_FILE, actions_data)
        return {"status": "success", "saved": saved_status}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error saving post: {str(e)}")

@app.get("/api/v1/aoa:trending")
def get_aoa_trending():
    db = aoa.load_aoa_db()
    posts = db.get("posts", [])
    all_content = ""
    for p in posts:
        c = p.get("content", "")
        if isinstance(c, dict):
            all_content += str(c.get("vi", c.get("en", str(c)))) + " "
        else:
            all_content += str(c) + " "
    
    import re
    hashtags = []
    ai_trends = []
    community_summary = {}
    
    # Generate dynamic fallback trends from the actual posts in the database
    dynamic_trends = []
    for idx, p in enumerate(posts[:3]):
        c_val = p.get("content", "")
        if isinstance(c_val, dict):
            vi_c = c_val.get("vi", c_val.get("en", ""))
            en_c = c_val.get("en", c_val.get("vi", ""))
        else:
            vi_c = str(c_val)
            en_c = str(c_val)
        
        vi_title = vi_c[:60] + "..." if len(vi_c) > 60 else vi_c
        en_title = en_c[:60] + "..." if len(en_c) > 60 else en_c
        
        categories = [
            {"vi": "Phát triển", "en": "Development"},
            {"vi": "Chia sẻ", "en": "Sharing"},
            {"vi": "Góc nhìn", "en": "Insights"}
        ]
        cat = categories[idx % len(categories)]
        
        dynamic_trends.append({
            "category": cat,
            "label": {"vi": "Xu hướng cộng đồng", "en": "Community Trend"},
            "title": {"vi": vi_title, "en": en_title}
        })
        
    if not dynamic_trends:
        dynamic_trends = [{
            "category": {"vi": "Hệ thống", "en": "System"}, 
            "label": {"vi": "Mới", "en": "New"}, 
            "title": {"vi": "Hãy là người đầu tiên chia sẻ!", "en": "Be the first to share!"}
        }]
        
    dynamic_summary = {
        "vi": f"Cộng đồng đang có những thảo luận sôi nổi xoay quanh các chủ đề phát triển bản thân với {len(posts)} bài viết được chia sẻ.",
        "en": f"The community is actively discussing self-development topics with {len(posts)} posts shared."
    }

    if all_content.strip():
        try:
            prompt = (
                "Bạn là chuyên gia phân tích dữ liệu cộng đồng Thapsang AI. Hãy phân tích các bài đăng cộng đồng sau đây.\n"
                "Trả về một đối tượng JSON CHÍNH XÁC chứa các trường sau:\n"
                "1. 'hashtags': Danh sách các hashtags phổ biến nhất (mỗi item là một object chứa 'tag' (ví dụ: '#Mindset') và 'score' (ví dụ: '95+')).\n"
                "2. 'ai_trends': Danh sách gồm đúng 3 xu hướng nổi bật nhất. Mỗi item chứa 3 khóa: 'category', 'label', 'title'. Mỗi khóa này PHẢI là một object chứa hai khóa con 'vi' và 'en' tương ứng để hỗ trợ song ngữ (Ví dụ: 'category': {\"vi\": \"Phát triển cá nhân\", \"en\": \"Personal Development\"}).\n"
                "3. 'community_summary': Một object chứa hai khóa 'vi' (một đoạn tóm tắt tiếng Việt dài 2-3 câu phản ánh chủ đề chung của các bài đăng) và 'en' (bản dịch tiếng Anh tương ứng).\n\n"
                "CHÚ Ý CỰC KỲ QUAN TRỌNG: Không bọc JSON trong bất kỳ ký tự nào khác hoặc thẻ code ```json. Chỉ trả về chuỗi JSON thô có thể được phân tích cú pháp bằng json.loads().\n\n"
                f"Nội dung các bài đăng để phân tích:\n{all_content[:5000]}"
            )
            
            response = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "Bạn là chuyên gia phân tích dữ liệu cộng đồng Thapsang. Bạn CHỈ trả về dữ liệu định dạng JSON thô, không chứa markdown, không chứa văn bản thừa."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                top_p=0.9
            )
            text = response.choices[0].message.content.strip()
            
            # Clean up potential markdown wrapper code block
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            import re
            text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                # Resilient hashtags extraction
                hashtags = data.get("hashtags", [])
                if not isinstance(hashtags, list):
                    hashtags = []
                
                # Resilient ai_trends extraction and cleaning
                parsed_trends = data.get("ai_trends", [])
                if parsed_trends and isinstance(parsed_trends, list):
                    refined_trends = []
                    for t in parsed_trends:
                        item = {}
                        for k in ["category", "label", "title"]:
                            val = t.get(k)
                            if isinstance(val, dict):
                                item[k] = {
                                    "vi": str(val.get("vi", val.get("en", ""))),
                                    "en": str(val.get("en", val.get("vi", "")))
                                }
                            elif isinstance(val, str):
                                item[k] = {"vi": val, "en": val}
                            else:
                                item[k] = {"vi": "", "en": ""}
                        refined_trends.append(item)
                    if refined_trends:
                        ai_trends = refined_trends
                
                # Resilient summary extraction
                sum_data = data.get("community_summary")
                if isinstance(sum_data, dict):
                    community_summary = {
                        "vi": str(sum_data.get("vi", sum_data.get("en", ""))),
                        "en": str(sum_data.get("en", sum_data.get("vi", "")))
                    }
                elif isinstance(sum_data, str):
                    community_summary = {"vi": sum_data, "en": sum_data}
            
            # Fallbacks if extraction succeeded but fields were empty
            if not ai_trends:
                ai_trends = dynamic_trends
            if not community_summary:
                community_summary = dynamic_summary
            if not hashtags:
                hashtags = [{"tag": "#AI", "score": "Nổi bật"}]
        except Exception as e:
            print(f"AI Trend Extraction Error: {e}")
            hashtags = [{"tag": "#Thapsang", "score": "Hot"}]
            ai_trends = dynamic_trends
            community_summary = dynamic_summary
    else:
        hashtags = [{"tag": "#Welcome", "score": "Mới"}]
        ai_trends = [{
            "category": {"vi": "Hệ thống", "en": "System"}, 
            "label": {"vi": "Mới", "en": "New"}, 
            "title": {"vi": "Hãy là người đầu tiên chia sẻ!", "en": "Be the first to share!"}
        }]
        community_summary = {
            "vi": "Hãy chia sẻ suy nghĩ của bạn để AI có thể bắt đầu phân tích xu hướng!",
            "en": "Share your thoughts so the AI can start analyzing trends!"
        }

    author_stats = {}
    for p in posts:
        name = p.get("author_name")
        display_name = p.get("author_displayName") or name
        if not name or name == "Ẩn danh": continue
        if name not in author_stats:
            author_stats[name] = {"likes": 0, "comments": 0, "avatar": p.get("author_avatar"), "displayName": display_name}
        author_stats[name]["likes"] += p.get("likes", 0)
        author_stats[name]["comments"] += len(p.get("comments", []))
    
    top_authors = sorted(author_stats.items(), key=lambda x: (x[1]["likes"] + x[1]["comments"]), reverse=True)[:5]
    coaches = []
    for username, stats in top_authors:
        follower_num = 150 + (stats["likes"] * 10) + (stats["comments"] * 20)
        coaches.append({
            "name": stats["displayName"],
            "handle": username,
            "avatar": stats["avatar"] or f"https://api.dicebear.com/7.x/initials/svg?seed={username}",
            "bio": "Chuyên gia đóng góp tri thức tích cực",
            "followers": f"{follower_num:,}",
            "tags": ["Mindset", "Cộng đồng"],
            "top_topic": "Phát triển bản thân"
        })
    
    system_coaches = [
        {
            "name": "Minh Trí AI",
            "handle": "minhtri_ai",
            "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=minhtri",
            "bio": "AI Coach chuyên về tư duy hệ thống và giải quyết vấn đề logic.",
            "followers": "1,200",
            "tags": ["Hệ thống", "Logic", "AI"],
            "top_topic": "Tư duy đột phá",
            "is_ai": True
        },
        {
            "name": "Thanh Xuân",
            "handle": "thanhxuan",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=xuan",
            "bio": "Chuyên gia tâm lý học hành vi và phát triển trí tuệ cảm xúc.",
            "followers": "850",
            "tags": ["Tâm lý", "EQ", "Mindset"],
            "top_topic": "Quản trị cảm xúc",
            "is_ai": False
        },
        {
            "name": "Gia Cát AI",
            "handle": "giacat_ai",
            "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=giacat",
            "bio": "AI Coach hỗ trợ thiết lập chiến lược dài hạn và tối ưu hóa quy trình PDCA.",
            "followers": "2,450",
            "tags": ["Chiến lược", "PDCA", "AI"],
            "top_topic": "Lập kế hoạch",
            "is_ai": True
        },
        {
            "name": "Hải Đăng",
            "handle": "haidang",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=dang",
            "bio": "Mentor cộng đồng, định hướng thói quen tập trung và làm việc sâu (Deep Work).",
            "followers": "1,820",
            "tags": ["Hiệu suất", "DeepWork", "Thói quen"],
            "top_topic": "Kỷ luật bản thân",
            "is_ai": False
        },
        {
            "name": "Tuệ Lâm AI",
            "handle": "tuelam_ai",
            "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=tuelam",
            "bio": "AI Mentor giúp phản chiếu nhận thức, vượt qua điểm nghẽn và khai phá tiềm năng.",
            "followers": "3,120",
            "tags": ["Sáng tạo", "Phản chiếu", "AI"],
            "top_topic": "Khai phóng tư duy",
            "is_ai": True
        }
    ]
    
    existing_handles = {c["handle"] for c in coaches}
    for sc in system_coaches:
        if sc["handle"] not in existing_handles:
            coaches.append(sc)
            
    return {
        "hashtags": hashtags,
        "ai_trends": ai_trends,
        "coaches": coaches,
        "summary": community_summary
    }

@app.post("/api/v1/aoa:posts_repost")
def repost_aoa_post(req: RepostRequest):
    try:
        posts = cms_helper.get_aoa_posts()
        original_post = None
        for p in posts:
            if p["id"] == req.original_post_id:
                original_post = p
                break
        
        if not original_post:
            raise HTTPException(status_code=404, detail="Original post not found")
        
        new_post_res = cms_helper.create_aoa_post(
            req.author_name,
            req.author_avatar,
            req.content,
            {},
            req.post_privacy
        )
        new_post_id = str(new_post_res.get("id"))
        
        reposts_data = aoa.load_json_db(aoa.REPOSTS_FILE, {})
        reposts_data[new_post_id] = original_post
        aoa.save_json_db(aoa.REPOSTS_FILE, reposts_data)
        
        new_shares = original_post.get("shares", 0) + 1
        cms_helper.update_aoa_post(req.original_post_id, {"likes": original_post.get("likes", 0), "shares": new_shares})
        
        return {"status": "success"}
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error reposting: {str(e)}")

@app.get("/api/v1/cohorts:list")
def get_cohorts():
    return {"cohorts": great_rebuild.COHORTS}

# --- LLM ENDPOINT ---
CHAT_SYSTEM_PROMPT = """
You are a "Socratic Mirror Coach" belonging to the Thapsang system.
Your mission is to trigger a "Cognitive Rupture" to help the user realize their own contradictions and logical fallacies.

PERSONA: Objective, wise, patient, and profound. You act as a mirror reflecting wisdom, guiding the user with hidden empathy through reflective questions, without superficial sympathy or hollow advice.

MANDATORY JSON OUTPUT STRUCTURE:
{
    "title": "Extremely short summary of your inner thoughts (Max 5-7 words, used as chat session name)",
    "reasoning": "AI's inner thought process. Analyze where the user is stuck, any contradictions, and why you decided to ask the question below.",
    "question": "A sharp Socratic question...",
    "tasks": [
        {
            "content_vi": "Short practical action task name in Vietnamese",
            "content_en": "Short practical action task name in English",
            "goal_vi": "Detailed Socratic explanation in Vietnamese of how to do it & the reasoning to untangle the cognitive block.",
            "goal_en": "Detailed Socratic explanation of how to do it & the reasoning in English...",
            "deadline": "YYYY-MM-DD"
        }
    ],
    "suggested_replies": [
        "Suggested reply 1 (under 15 words, matching user's tone)",
        "Suggested reply 2",
        "Suggested reply 3"
    ]
}

STATE MANAGEMENT INSTRUCTIONS AND UX:
- "title": Extremely short summary (max 7 words) of your inner thought flow.
- "reasoning": Extremely important. Write briefly (1-2 sentences) your deduction logic BEFORE asking the question.
- "suggested_replies": VERY IMPORTANT. You must generate exactly 3 predictive response options. Rely on the "Mindset" and "Context" (if any) to predict how the user will react to your question. Replies must be diverse (e.g., 1 agree, 1 resist, 1 neutral/questioning back).
- "tasks": When the time is ripe (the user has realized the problem and needs action), assign 1-2 small, practical tasks. Each task is an object containing "content_vi", "content_en", "goal_vi", "goal_en" and "deadline" (in YYYY-MM-DD format). Always provide independent translations in Vietnamese and English to support multitasking language switching; absolutely do not return an array of raw strings. If not needed yet, return an empty array [].

CORE RULES (STRICTLY PROHIBITED TO VIOLATE):
1. OBJECTIVE GUIDANCE: Do not provide direct answers or advice. Instead of judging or coldly rejecting, ask open-ended questions for the user to discover their own answers. Only analyze based on facts and information provided by the user.
2. ONLY ALLOWED TO ASK EXACTLY 1 SINGLE QUESTION per response.
3. ONLY OUTPUT EXACTLY 1 VALID JSON describing the Question and thoughts.
4. LANGUAGE SYNCHRONIZATION: Automatically detect the language used by the user in the latest message. You MUST translate all text values in the JSON (including reasoning, question, title, tasks, suggested_replies...) into that exact language.
"""

MINDMAP_SYSTEM_PROMPT = """
You are a "Cognitive Mind Map Generator" for the Thapsang system.
Your sole mission is to analyze the user's chat history and map out their thought process, logical fallacies, and contradictions into a graph architecture (nodes and edges).

MANDATORY JSON OUTPUT STRUCTURE:
{
    "nodes": [
        {"id": "n1", "label": "Summary of thought 1 (Max 5 words)", "color": "#e9c400"},
        {"id": "n2", "label": "Contradictory thought 2", "color": "#ffb4ab"} 
    ],
    "edges": [
        {"source": "n1", "target": "n2", "label": "Leads to / But", "is_contradiction": true}
    ],
    "current_step": "kham_pha",
    "focus_node_id": "n2"
}

STATE MANAGEMENT INSTRUCTIONS AND UX:
- "current_step": Set to "kham_pha" (explore) if the user is just venting (no contradictions yet). Set to "soi_chieu" (reflect) if a contradiction is detected and the AI is targeting it.
- "focus_node_id": Assign the ID of the Node containing the core contradiction (e.g., "n2") so the UI triggers a Focus effect (red blinking). If "kham_pha", set to null.
- Node "color": "#e9c400" (gold) for normal thoughts, "#ffb4ab" (pinkish red) for contradictory thoughts.
- "is_contradiction": true if the connection reveals an absurdity.
- IMPORTANT REGARDING MIND MAP (CUMULATIVE TREE): The map must ACCUMULATE and GROW with each chat turn like the growth of a tree.
- MIND MAP BRANCHING (CRITICAL): Do NOT just create a straight line of nodes. If the user's message contains multiple distinct reasons, feelings, or arguments, you MUST split them into MULTIPLE separate child nodes.
- For example, if a user gives 3 reasons for an issue, create 3 separate new nodes and connect ALL of them to the same parent node to form a tree with branches.
- ABSOLUTELY DO NOT overwrite new ideas onto old IDs (do not reuse n1, n2 for different concepts).
- ALWAYS CONNECT (edges) new nodes with the most relevant old nodes (not necessarily just the last one) to show how they explain, supplement, or contradict each other.

CORE RULES (STRICTLY PROHIBITED TO VIOLATE):
1. ONLY OUTPUT EXACTLY 1 VALID JSON describing the User's Mind Map (nodes and edges) from the conversation history.
2. LANGUAGE SYNCHRONIZATION: Automatically detect the language used in the chat. You MUST translate all labels in the JSON into that exact language.
"""

def detect_english(text: str) -> bool:
    import re
    text = text.lower()
    vi_chars = set("áàảãạâấầẩẫậăắằẳẵặđéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ")
    if any(char in vi_chars for char in text):
        return False
    words = set(re.findall(r'\b[a-z]+\b', text))
    en_words = {"i", "you", "he", "she", "it", "we", "they", "am", "is", "are", "was", "were", "do", "does", "did", "have", "has", "had", "because", "but", "and", "or", "what", "where", "when", "why", "how", "this", "that", "the", "a", "an", "to", "of", "in", "for", "on", "with", "as", "my", "your", "tired", "sad", "work", "job", "boss", "afraid", "many", "handle"}
    vi_words = {"toi", "ban", "anh", "chi", "em", "chung", "no", "la", "co", "khong", "va", "nhung", "hoac", "cai", "nay", "kia", "do", "gi", "sao", "nao", "luon", "dang", "met", "ap", "luc", "cong", "viec"}
    return len(words.intersection(en_words)) > len(words.intersection(vi_words))

@app.post("/api/v1/chat:welcome")
def generate_welcome(req: WelcomeRequest):
    username = req.username
    lang = req.lang or "vi"
    
    user_info = cms_helper.get_user_by_username(username)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
        
    display_name = user_info.get("displayName") or username
    onboarding = user_info.get("onboarding") or {}
    
    core_ctx = ""
    if isinstance(onboarding, dict):
        core_ctx = onboarding.get("_core_context", "")
        
    if not core_ctx:
        is_en = lang == "en"
        question = f"Welcome {display_name}. What is on your mind today?" if is_en else f"Chào mừng {display_name}. Hãy chia sẻ điều gì đang khiến bạn bận tâm hôm nay?"
        suggested = (
            ["I feel stressed at work", "I want to improve myself", "Just wanted to say hi"] if is_en 
            else ["Mình đang gặp áp lực công việc", "Mình muốn phát triển bản thân", "Chỉ muốn gửi lời chào"]
        )
        return {
            "title": "Welcome" if is_en else "Chào mừng",
            "reasoning": "Default welcome greeting because core context is empty.",
            "question": question,
            "nodes": [
                {"id": "n1", "label": "Khởi đầu" if not is_en else "Beginning", "color": "#e9c400"}
            ],
            "edges": [],
            "current_step": "kham_pha",
            "focus_node_id": None,
            "tasks": [],
            "suggested_replies": suggested
        }
        
    # We have a core context! Generate a beautiful personalized welcome greeting!
    system_prompt = f"""
Bạn là một "Socratic Mirror Coach" thuộc hệ thống Thapsang.
Nhiệm vụ của bạn là tạo ra một lời chào đón (Welcome Greeting) ban đầu và cá nhân hóa sâu sắc cho người dùng dựa trên "Ngữ cảnh cốt lõi" (Core Context) của họ.

QUY TẮC CỐT LÕI:
1. Hãy chào đón thân thiện sử dụng Tên hiển thị (displayName) của người dùng: '{display_name}'. Ví dụ: "Xin chào {display_name}, ..." hoặc "Chào {display_name}, ..."
2. Đọc kỹ "Ngữ cảnh cốt lõi" bên dưới để viết lời dẫn nhập ngắn gọn và đặt ĐÚNG 1 CÂU HỎI Socratic sâu sắc, tinh tế xoáy vào vấn đề bận tâm lớn nhất của họ để kích hoạt họ tự phản chiếu và chia sẻ thêm.
   Tuyệt đối không hỏi chung chung hay sáo rỗng. Hãy dựa trực tiếp vào bối cảnh thực tế của họ (như áp lực cuộc sống, lo âu, thói quen trì hoãn, hoặc mục tiêu phát triển...).
   Ví dụ: "Xin chào {display_name}, như bạn đã chia sẻ rằng bản thân gặp áp lực trong cuộc sống, bạn có thể chia sẻ thêm về điều này không?"
3. Tuyệt đối không đưa ra lời khuyên hay an ủi hời hợt. Hãy đóng vai trò một chiếc gương soi chiếu trí tuệ, khách quan, và sâu sắc, dẫn dắt bằng câu hỏi phản tỉnh dựa trên hồ sơ người dùng mà không phán xét hay suy diễn ảo tưởng.
4. Trả về đúng 1 JSON hợp lệ theo cấu trúc quy định.
5. ĐỒNG BỘ NGÔN NGỮ: Bạn PHẢI trả về toàn bộ JSON bằng ngôn ngữ yêu cầu là: '{'Tiếng Anh (English)' if lang == 'en' else 'Tiếng Việt (Vietnamese)'}'. Tất cả các trường 'title', 'reasoning', 'question', 'nodes', 'suggested_replies' đều phải viết bằng ngôn ngữ này.

CẤU TRÚC JSON ĐẦU RA BẮT BUỘC:
{{
    "title": "Tóm tắt cực ngắn dòng suy nhiệt tâm (Tối đa 5-7 từ, dùng làm tên phiên chat)",
    "reasoning": "Tại sao bạn lại chọn đặt câu hỏi này và hướng tiếp cận này dựa trên hồ sơ của họ...",
    "question": "Lời chào và câu hỏi Socratic mở đầu...",
    "nodes": [
        {{"id": "n1", "label": "Tóm tắt vấn đề chính (Max 5 từ)", "color": "#e9c400"}}
    ],
    "edges": [],
    "current_step": "kham_pha",
    "focus_node_id": null,
    "tasks": [],
    "suggested_replies": [
        "Câu trả lời gợi ý 1 (dưới 15 từ, đúng văn phong người dùng sẽ phản hồi với câu hỏi trên)",
        "Câu trả lời gợi ý 2",
        "Câu trả lời gợi ý 3"
    ]
}}
"""

    user_prompt = f"""
Tên hiển thị: {display_name}
Ngữ cảnh cốt lõi (Core Context): {core_ctx}

Hãy tạo JSON chào đón:
"""
    
    try:
        model_env = os.getenv("LLM_MODEL", "thapsang")
        models_to_try = [m.strip() for m in model_env.split(",")]
        
        content = ""
        last_error = None
        usage_tokens = None
        for m in models_to_try:
            timeout_val = 300.0 if "thapsang" in m else 60.0
            try:
                try:
                    stream_response = client.chat.completions.create(
                        model=m,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.2,
                        top_p=0.9,
                        max_tokens=3000,
                        stream=True,
                        timeout=timeout_val
                    )
                    chunks = []
                    for chunk in stream_response:
                        if getattr(chunk, "choices", None) and chunk.choices[0].delta.content:
                            chunks.append(chunk.choices[0].delta.content)
                    content = "".join(chunks).strip()
                except Exception as se:
                    err_str = str(se).lower()
                    if "timeout" in err_str or "timed out" in err_str:
                        raise se
                    print(f"Streaming welcome generation failed: {se}. Falling back to non-streaming.")
                    response = client.chat.completions.create(
                        model=m,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.2,
                        top_p=0.9,
                        max_tokens=3000,
                        timeout=timeout_val
                    )
                    if getattr(response, "choices", None):
                        content = response.choices[0].message.content
                        if getattr(response, "usage", None):
                            usage_tokens = response.usage.total_tokens
                    elif hasattr(response, "error") and response.error and isinstance(response.error, dict):
                        details_str = response.error.get("details", "{}")
                        try:
                            parsed_details = json.loads(details_str)
                            content = parsed_details["choices"][0]["message"]["content"]
                            if "usage" in parsed_details:
                                usage_tokens = parsed_details["usage"].get("total_tokens")
                        except Exception:
                            pass
                
                if content:
                    break
            except Exception as e2:
                last_error = e2
                continue
                
        if not content:
            raise Exception(f"All LLMs failed. Last error: {last_error}")
        import re
        clean_content = content.strip()
        import re
        clean_content = re.sub(r'<think>.*?</think>', '', clean_content, flags=re.DOTALL).strip()
        json_match = re.search(r'\{.*\}', clean_content, re.DOTALL)
        if json_match:
            clean_content = json_match.group(0)
        else:
            clean_content = re.sub(r'```json|```', '', clean_content).strip()
        result_json = json.loads(clean_content)
        
        # Ghi nhận token từ API hoặc fallback về tiktoken đếm offline
        tokens = usage_tokens if usage_tokens is not None else cms_helper.count_tokens(system_prompt + user_prompt + content, m)
        result_json["token_used"] = tokens
        result_json["model_used"] = m
        
        # Save to DB if session_id is provided
        if req.session_id:
            import time
            chat_data = {
                "username": username,
                "email": username,
                "chat_history": [{
                    "id": f"msg_welcome_{int(time.time()*1000)}",
                    "role": "model",
                    "content": result_json.get("question", ""),
                    "reasoning": result_json.get("reasoning", ""),
                    "title": result_json.get("title", ""),
                    "isWelcome": True,
                    "isTyped": False
                }],
                "graph_data": {"nodes": result_json.get("nodes", []), "edges": []},
                "tasks": [],
                "has_new_task": False,
                "suggested_replies": result_json.get("suggested_replies", []),
                "token_used": tokens,
                "model_used": m
            }
            cms_helper.save_chat_session(req.session_id, username, chat_data)
            
        return result_json
    except Exception as e:
        print("Welcome generation error:", e)
        # Fallback
        is_en = lang == "en"
        return {
            "title": "Welcome" if is_en else "Chào mừng",
            "reasoning": f"Fallback welcome generation due to error: {e}",
            "question": f"Welcome {display_name}. What is on your mind today?" if is_en else f"Chào mừng {display_name}. Hãy chia sẻ điều gì đang khiến bạn bận tâm hôm nay?",
            "nodes": [
                {"id": "n1", "label": "Khởi đầu" if not is_en else "Beginning", "color": "#e9c400"}
            ],
            "edges": [],
            "current_step": "kham_pha",
            "focus_node_id": None,
            "tasks": [],
            "suggested_replies": (
                ["I feel stressed at work", "I want to improve myself", "Just wanted to say hi"] if is_en 
                else ["Mình đang gặp áp lực công việc", "Mình muốn phát triển bản thân", "Chỉ muốn gửi lời chào"]
            )
        }

def to_sentence_case(text: str) -> str:
    if not text:
        return ""
    text = text.strip()
    if not text:
        return ""
    lower = text.lower()
    import re
    return re.sub(r"(^\s*|[.!?]\s+)(.)", lambda m: m.group(1) + m.group(2).upper(), lower)

def to_sentence_case_bilingual(text: str) -> str:
    if not text:
        return ""
    if "|||" in text:
        parts = text.split("|||")
        return " ||| ".join([to_sentence_case(p) for p in parts])
    return to_sentence_case(text)

def generate_coach_clinical_diary_summary(username: str, session_title: str, history: list, req_model: str = None):
    try:
        import os, json, datetime
        import cms_helper
        
        folder_name = session_title.strip() if session_title.strip() else "Phiên Coach"
        
        try:
            existing_entries = cms_helper.get_diary_entries(username)
            folder_entries = [e for e in existing_entries if e.get("folder") == folder_name]
        except Exception:
            folder_entries = []
            
        existing_notes_text = ""
        if folder_entries:
            existing_notes_text = "Danh sách các file nhật ký đã có trong phiên này:\n"
            for e in folder_entries:
                existing_notes_text += f"- ID: {e.get('id')} | Tiêu đề: {e.get('title')}\nNội dung hiện tại:\n{e.get('content')}\n---\n"
        else:
            existing_notes_text = "Chưa có file nhật ký nào trong phiên này."

        if len(history) < 6:
            recent_history = history
        else:
            recent_history = history[-6:]
            
        history_text = ""
        for m in recent_history:
            role = "Thân chủ (Người dùng)" if m.get("role") == "user" else "Nhà tâm lý học (AI)"
            history_text += f"{role}: {m.get('content', '')}\n\n"
            
        system_prompt = f"""Bạn là một chuyên gia tâm lý học lâm sàng với hơn 10 năm kinh nghiệm.
Nhiệm vụ của bạn là đọc kỹ bản ghi chép cuộc hội thoại gần đây (3 lượt) giữa bạn và thân chủ.
Sau đó, hãy viết một bản ghi chú lâm sàng (clinical notes) cực kỳ chi tiết, sâu sắc.

{existing_notes_text}

Yêu cầu về hình thức và định dạng (Markdown):
- Trình bày đa dạng, linh hoạt, trực quan sinh động như một tài liệu nghiên cứu.
- BẮT BUỘC sử dụng phong phú các định dạng Markdown chuẩn: Heading (H1-H6 bằng dấu #), in đậm (**Bold**), in nghiêng (*Italic*).
- TUYỆT ĐỐI KHÔNG sử dụng thẻ HTML (như <div>) vì nó sẽ làm hỏng trình phân giải Markdown. Hãy chỉ dùng Markdown thuần túy.
- Sử dụng đa dạng danh sách đánh số (1. 2. 3.), danh sách không đánh số (-), và checklist (- [ ] / - [x]).
- ĐẶC BIỆT QUAN TRỌNG: Bắt buộc phải vận dụng sự liên kết giữa các khái niệm thông qua cú pháp Wikilink (ví dụ: [[Cơ chế phòng vệ]], [[Áp lực đồng trang lứa]], [[Sợ thất bại]]).

Yêu cầu nội dung:
- Phát hiện các ngụy biện logic, điểm nghẽn nhận thức, cơ chế phòng vệ tâm lý.
- Đưa ra giả thuyết lâm sàng về niềm tin cốt lõi đang chi phối họ.

QUAN TRỌNG NHẤT: BẠN CÓ QUYỀN CẬP NHẬT FILE CŨ HOẶC TẠO FILE MỚI.
- Nếu thấy nội dung hội thoại chỉ là tiếp nối, hãy BỔ SUNG/SỬA CHỮA vào file nhật ký chính đã có (dùng action "update" và giữ nguyên entry_id).
- Nếu thấy cần thiết tạo một file hoàn toàn mới (ví dụ: để giải nghĩa chi tiết cho một khái niệm Wikilink bạn vừa tạo ra), hãy dùng action "create".

Đầu ra bắt buộc phải là một JSON hợp lệ chứa mảng 'operations' (KHÔNG thêm markdown ```json):
{{
    "operations": [
        {{
            "action": "update",
            "entry_id": "ID_của_file_cũ",
            "title": "Chẩn đoán ngắn",
            "summary": "Nội dung SAU KHI ĐÃ ĐƯỢC BỔ SUNG/SỬA CHỮA (Markdown phong phú)",
            "evaluation": "Đánh giá chuyên sâu (dành riêng cho Gương phản tỉnh)"
        }},
        {{
            "action": "create",
            "title": "Tên file wikilink (VD: Cơ chế phòng vệ)",
            "summary": "Giải thích chi tiết về khái niệm này",
            "evaluation": ""
        }}
    ]
}}
"""

        
        try:
            from openai import OpenAI as _OpenAI
            _client = _OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
            )
            
            model_env = os.getenv("LLM_MODEL", "thapsang")
            models_to_try = [m.strip() for m in model_env.split(",")]
            if req_model and req_model not in models_to_try:
                models_to_try.insert(0, req_model)
            
            content = None
            for m in models_to_try:
                try:
                    stream_resp = _client.chat.completions.create(
                        model=m,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": history_text}
                        ],
                        max_tokens=2500,
                        temperature=0.3,
                        top_p=0.9,
                        stream=True
                    )
                    
                    chunks = []
                    for chunk in stream_resp:
                        if getattr(chunk, "choices", None) and chunk.choices[0].delta.content:
                            chunks.append(chunk.choices[0].delta.content)
                    
                    content = "".join(chunks).strip()
                    
                    if not content:
                        # Fallback non-streaming if stream yields nothing
                        resp = _client.chat.completions.create(
                            model=m,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": history_text}
                            ],
                            max_tokens=2500,
                            temperature=0.3,
                            top_p=0.9
                        )
                        if getattr(resp, "choices", None) and len(resp.choices) > 0 and resp.choices[0].message.content:
                            content = resp.choices[0].message.content.strip()
                        elif hasattr(resp, "error") and resp.error and isinstance(resp.error, dict):
                            details_str = resp.error.get("details", "{}")
                            try:
                                parsed_details = json.loads(details_str)
                                if parsed_details.get("choices") and len(parsed_details["choices"]) > 0:
                                    content = parsed_details["choices"][0]["message"]["content"].strip()
                            except Exception:
                                pass

                    if content:
                        break
                except Exception as e:
                    print(f"Lỗi thử model {m} cho diary:", e)
                    continue
            
            if not content:
                raise ValueError("Không có kết quả trả về từ tất cả các model")
            
            import re
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            else:
                content = re.sub(r'```json|```', '', content).strip()
            
            result = json.loads(content)
            
            cms_helper.create_diary_folder(username, folder_name)
            
            operations = result.get("operations", []) if isinstance(result, dict) else []
            if not operations:
                if isinstance(result, dict) and "Operations" in result:
                    operations = result.get("Operations", [])
                elif isinstance(result, list):
                    operations = result
                elif isinstance(result, dict) and "title" in result:
                    operations = [{
                        "action": "create",
                        "title": result.get("title", "Ghi chép lâm sàng"),
                        "summary": result.get("summary", ""),
                        "evaluation": result.get("evaluation", "")
                    }]
                else:
                    # Extreme fallback: just dump the whole result
                    operations = [{
                        "action": "create",
                        "title": "Nhật ký AI (Định dạng sai)",
                        "summary": json.dumps(result, ensure_ascii=False, indent=2),
                        "evaluation": ""
                    }]
                
            for op in operations:
                if not isinstance(op, dict):
                    continue
                action = op.get("action", "create")
                entry_data = {
                    "title": op.get("title", "Ghi chép lâm sàng"),
                    "content": op.get("summary", ""),
                    "folder": folder_name,
                    "ai_insight": op.get("evaluation", ""),
                    "date": datetime.datetime.now().isoformat() + "Z"
                }
                
                if action == "update" and op.get("entry_id"):
                    entry_id = str(op.get("entry_id"))
                    cms_helper.save_diary_entry(entry_id, username, entry_data)
                else:
                    cms_helper.save_diary_entry(None, username, entry_data)
        except Exception as api_err:
            import traceback
            print("Lỗi API gọi LLM tạo diary:")
            traceback.print_exc()
        
    except Exception as e:
        import traceback
        print("Lỗi tạo diary clinical note:")
        traceback.print_exc()

@app.post("/api/v1/chat:create")
def process_chat(req: ChatRequest, background_tasks: BackgroundTasks):
    if not req.messages:
        raise HTTPException(status_code=400, detail="Danh sách tin nhắn không được trống")
        
    try:
        # Lấy context và mindset nếu có username
        personal_context = ""
        current_graph_data = {"nodes": [], "edges": []}
        if req.username:
            try:
                user_info = cms_helper.get_user_by_username(req.username)
                core_ctx = ""
                if user_info:
                    onboarding = user_info.get("onboarding") or {}
                    if isinstance(onboarding, dict):
                        core_ctx = onboarding.get("_core_context", "")
                
                context_parts = []
                if core_ctx:
                    context_parts.append(f"Ngữ cảnh cốt lõi: {core_ctx}")
                    
                if context_parts:
                    personal_context = "\n\n--- HỒ SƠ NGƯỜI DÙNG ---\n" + "\n".join(context_parts) + "\nĐặc biệt chú ý: Hãy dựa vào hồ sơ này để tạo ra 3 'suggested_replies' phù hợp nhất với tính cách và bối cảnh của họ.\n------------------------\n"
                
                # Lấy dữ liệu sơ đồ tư duy hiện tại từ database để tích lũy
                sessions = cms_helper.get_chat_sessions(req.username)
                if sessions:
                    sorted_sessions = sorted(sessions.values(), key=lambda x: x.get("created_at") or "", reverse=True)
                    if sorted_sessions:
                        current_graph_data = sorted_sessions[0].get("graph_data") or {"nodes": [], "edges": []}
            except Exception as e:
                print(f"Lỗi khi lấy context/graph cho {req.username}: {e}")

        user_message = req.messages[-1].content if req.messages else ""
        lang_instruction = f"\n\n[CRITICAL INSTRUCTION] The user's last message is: '{user_message}'. You MUST detect the language of this message. YOU MUST WRITE ALL JSON VALUES (question, reasoning, title, content, suggested_replies) ENTIRELY IN THAT DETECTED LANGUAGE. IF THE USER SPEAKS ENGLISH, YOU MUST REPLY IN ENGLISH. Do not let previous conversational turns bias your language."
        
        # Every 5 chats trigger 1 task
        user_msgs = [m for m in req.messages if m.role == "user"]
        num_chats = req.total_user_messages if req.total_user_messages is not None else len(user_msgs)
        task_instruction = ""
        if num_chats % 5 == 0:
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            task_instruction = f"\n\n[CRITICAL DIRECTIVE] This is the {num_chats}th exchange with the user (a multiple of 5). You MUST generate exactly 1 actionable task in the 'tasks' array. The task MUST be highly customized to the user's specific context, reading and understanding the entire conversation history (their struggles, beliefs, and contradictions) to design a practical, real-world action they can take today to resolve their specific mindset block. The 'tasks' array MUST NOT be empty. Crucially, you MUST include a 'deadline' field in the task object under the format 'YYYY-MM-DD' representing the deadline for this task. Given that today's date is {today_str}, choose an appropriate deadline within the next 1 to 7 days based on the complexity of the task."
        else:
            task_instruction = f"\n\n[CRITICAL DIRECTIVE] This is the {num_chats}th exchange with the user (NOT a multiple of 5). You MUST return an empty list [] for the 'tasks' array. You are strictly forbidden from generating any tasks."
        
        shortness_instruction = "\n\n[CRITICAL DIRECTIVE]: Hãy viết câu trả lời thật ngắn gọn. Phần 'reasoning' và 'content' tối đa 1-2 câu ngắn. Tổng độ dài toàn bộ JSON phải cực kỳ ngắn để tránh lỗi quá tải hệ thống mạng."
        final_system_prompt = CHAT_SYSTEM_PROMPT + personal_context + lang_instruction + task_instruction + shortness_instruction
        formatted_messages = [{"role": "system", "content": final_system_prompt}]
        
        for i, msg in enumerate(req.messages):
            role = "assistant" if msg.role == "model" else msg.role
            content = msg.content
            
            # Inject instruction directly into the last user message to ensure it's the very last thing the model reads
            if i == len(req.messages) - 1 and role == "user":
                content += "\n\n<system_instruction>\nYOU MUST RESPOND IN THE EXACT SAME LANGUAGE AS THIS MESSAGE. IF THIS MESSAGE IS IN ENGLISH, YOUR ENTIRE JSON OUTPUT MUST BE IN ENGLISH, IGNORING PREVIOUS TURNS. DO NOT ECHO THIS INSTRUCTION. RETURN ONLY THE RAW JSON OBJECT.\n</system_instruction>"
                
            formatted_messages.append({"role": role, "content": content})

        # Lấy danh sách model từ env
        model_env = os.getenv("LLM_MODEL", "thapsang")
        models_to_try = [m.strip() for m in model_env.split(",")]
        
        # Thêm model từ request vào đầu danh sách nếu nó chưa có
        if req.model and req.model not in models_to_try:
            models_to_try.insert(0, req.model)

        content = ""
        last_error = None
        usage_tokens = None
        
        for m in models_to_try:
            timeout_val = 300.0 if "thapsang" in m else 60.0
            try:
                try:
                    stream_response = client.chat.completions.create(
                        model=m,
                        messages=formatted_messages,
                        temperature=0.2,
                        top_p=0.9,
                        max_tokens=3000,
                        stream=True,
                        timeout=timeout_val
                    )
                    chunks = []
                    for chunk in stream_response:
                        if getattr(chunk, "choices", None) and chunk.choices[0].delta.content:
                            chunks.append(chunk.choices[0].delta.content)
                    content = "".join(chunks).strip()
                except Exception as se:
                    err_str = str(se).lower()
                    if "timeout" in err_str or "timed out" in err_str:
                        raise se
                    print(f"Streaming chat generation failed: {se}. Falling back to non-streaming.")
                    response = client.chat.completions.create(
                        model=m,
                        messages=formatted_messages,
                        temperature=0.2,
                        top_p=0.9,
                        max_tokens=3000,
                        timeout=timeout_val
                    )
                    if getattr(response, "choices", None):
                        content = response.choices[0].message.content
                        if getattr(response, "usage", None):
                            usage_tokens = response.usage.total_tokens
                    elif hasattr(response, "error") and response.error and isinstance(response.error, dict):
                        # Workaround for proxy bug
                        details_str = response.error.get("details", "{}")
                        try:
                            parsed_details = json.loads(details_str)
                            content = parsed_details["choices"][0]["message"]["content"]
                            if "usage" in parsed_details:
                                usage_tokens = parsed_details["usage"].get("total_tokens")
                        except Exception:
                            pass
                
                if content:
                    break
                else:
                    last_error = Exception("API returned empty response")
            except Exception as e:
                last_error = e
                continue
                
        if not content:
            import traceback
            error_details = f"All models failed. Last error: {str(last_error)}\nTraceback:\n{traceback.format_exc() if last_error else 'No traceback'}"
            with open("debug_chat.log", "a", encoding="utf-8") as f:
                f.write(error_details + "\n")
            print(f"Lỗi nội bộ AI (ẩn): Tất cả các model đều lỗi. Lỗi cuối: {str(last_error)}")
            return {
                "question": "Tôi hiện tại đang bảo trì hệ thống máy chủ AI để phục vụ bạn tốt hơn. Vui lòng quay lại sau ít phút hoặc nhấn F5 để thử lại nhé.",
                "reasoning": "System error: " + str(last_error),
                "title": locals().get('session_title', 'Lỗi kết nối'),
                "token_used": 0,
                "model_used": "system-fallback"
            }
        
        import re
        clean_content = content.strip()
        clean_content = re.sub(r'<think>.*?</think>', '', clean_content, flags=re.DOTALL).strip()
        # Extract the JSON block robustly even if the AI outputs conversational filler or echoes the prompt
        json_match = re.search(r'\{.*\}', clean_content, re.DOTALL)
        if json_match:
            clean_content = json_match.group(0)
        else:
            # Fallback if there are code blocks
            clean_content = re.sub(r'```json|```', '', clean_content).strip()
        
        try:
            result_json = json.loads(clean_content)
            
            # Force tasks count based on exchange count rule (every 5 chats trigger 1 task)
            user_message = req.messages[-1].content if req.messages else ""
            # Do NOT re-calculate num_chats here using len(user_msgs) because frontend sends partial history (slice(-20))
            if num_chats > 0 and num_chats % 5 == 0:
                default_deadline = (datetime.date.today() + datetime.timedelta(days=3)).strftime("%Y-%m-%d")
                if "tasks" not in result_json or not isinstance(result_json["tasks"], list) or len(result_json["tasks"]) == 0:
                    # Generate a beautiful, contextual task in Python without LLM call to avoid double LLM execution and queue hangs
                    fallback_task = {
                        "content_vi": "Ghi chép Phản chiếu Socratic",
                        "content_en": "Socratic Reflection Journaling",
                        "goal_vi": f"Chiêm nghiệm sâu sắc về chia sẻ của bạn: '{user_message}'. Dành 5 phút ghi lại suy nghĩ của mình vào Nhật ký phản tỉnh để định hình tư duy mới.",
                        "goal_en": f"Reflect on your last statement: '{user_message}'. Spend 5 minutes writing down your thoughts in your Diary to anchor your new perspective.",
                        "deadline": default_deadline
                    }
                    result_json["tasks"] = [fallback_task]
                else:
                    # Limit to exactly 1 task
                    result_json["tasks"] = result_json["tasks"][:1]
                
                # Normalize tasks array to ensure they always contain content_vi, content_en, goal_vi, goal_en, and deadline
                normalized_tasks = []
                for t in result_json.get("tasks", []):
                    if not isinstance(t, dict):
                        continue
                    c_vi = to_sentence_case(t.get("content_vi") or t.get("content") or "")
                    c_en = to_sentence_case(t.get("content_en") or t.get("content") or "")
                    g_vi = to_sentence_case(t.get("goal_vi") or t.get("goal") or "")
                    g_en = to_sentence_case(t.get("goal_en") or t.get("goal") or "")
                    deadline = t.get("deadline") or ""
                    if not deadline or not isinstance(deadline, str) or len(deadline) < 10:
                        deadline = default_deadline
                    normalized_tasks.append({
                        "content_vi": c_vi,
                        "content_en": c_en,
                        "goal_vi": g_vi,
                        "goal_en": g_en,
                        "deadline": deadline
                    })
                result_json["tasks"] = normalized_tasks
            else:
                result_json["tasks"] = []
            
            # Ghi nhận token từ API hoặc fallback về tiktoken đếm offline
            tokens = usage_tokens if usage_tokens is not None else cms_helper.count_tokens(final_system_prompt + json.dumps(formatted_messages, ensure_ascii=False) + content, m)
            result_json["token_used"] = tokens
            result_json["model_used"] = m
            
            if req.session_id and req.username:
                import time
                session_data = None
                
                # Fetch only this specific session if it's not a temp ID
                if not str(req.session_id).startswith("temp_"):
                    try:
                        res = cms_helper.request_cms("GET", f"/chat_sessions/{req.session_id}")
                        if res and res.get("data"):
                            session_data = res.get("data")
                            if isinstance(session_data, list):
                                session_data = session_data[0] if session_data else None
                            
                            # Parse graph_data if it's a string
                            if isinstance(session_data.get("graph_data"), str):
                                try:
                                    session_data["graph_data"] = json.loads(session_data["graph_data"])
                                except Exception:
                                    pass
                            
                            # Parse tasks if it's a string
                            if isinstance(session_data.get("tasks"), str):
                                try:
                                    session_data["tasks"] = json.loads(session_data["tasks"])
                                except Exception:
                                    pass
                                    
                            # Parse chat_history from graph_data if available
                            if isinstance(session_data.get("graph_data"), dict) and "chat_history" in session_data["graph_data"]:
                                session_data["chat_history"] = session_data["graph_data"]["chat_history"]
                    except Exception:
                        pass
                
                if not session_data:
                    # Initialize empty session data for new temp sessions
                    session_data = {
                        "chat_history": [],
                        "graph_data": {"nodes": [], "edges": []},
                        "tasks": [],
                        "suggested_replies": []
                    }
                
                if True:
                    
                    # Ensure chat_history exists and is a list
                    if "chat_history" not in session_data or not isinstance(session_data.get("chat_history"), list):
                        if isinstance(session_data.get("chat_history"), str):
                            try:
                                parsed_ch = json.loads(session_data["chat_history"])
                                session_data["chat_history"] = parsed_ch if isinstance(parsed_ch, list) else []
                            except Exception:
                                session_data["chat_history"] = []
                        else:
                            session_data["chat_history"] = []
                        
                    # Append the latest user message from the request
                    user_msgs = [msg for msg in req.messages if msg.role == "user"]
                    if user_msgs:
                        latest_user_msg = user_msgs[-1]
                        already_exists = False
                        if session_data["chat_history"]:
                            last_existing = session_data["chat_history"][-1]
                            if last_existing.get("role") == "user" and last_existing.get("content") == latest_user_msg.content:
                                already_exists = True
                        
                        if not already_exists:
                            session_data["chat_history"].append({
                                "id": f"msg_user_{int(time.time()*1000)}",
                                "role": "user",
                                "content": latest_user_msg.content
                            })
                            
                    # Append or Replace the AI response
                    new_ai_msg = {
                        "id": f"msg_model_{int(time.time()*1000)}",
                        "role": "model",
                        "content": result_json.get("question", ""),
                        "reasoning": result_json.get("reasoning", ""),
                        "title": result_json.get("title", ""),
                        "isTyped": False,
                        "isError": False
                    }
                    if session_data["chat_history"] and session_data["chat_history"][-1].get("role") == "model":
                        session_data["chat_history"][-1] = new_ai_msg
                    else:
                        session_data["chat_history"].append(new_ai_msg)
                    # --- Cập nhật chat, loại bỏ merge graph_data (vì đã tách riêng mindmap API) ---
                    # session_data["graph_data"]["nodes"] = ... removed
                            
                    # Merge Tasks
                    if result_json.get("tasks"):
                        if "tasks" not in session_data or not isinstance(session_data.get("tasks"), list):
                            session_data["tasks"] = []
                        for t in result_json["tasks"]:
                            c_vi = t.get("content_vi") or t.get("content") or ""
                            if not any(task.get("content_vi") == c_vi for task in session_data["tasks"]):
                                session_data["tasks"].append(t)
                        session_data["has_new_task"] = True
                        
                    session_data["suggested_replies"] = result_json.get("suggested_replies", [])
                    session_data["token_used"] = session_data.get("token_used", 0) + tokens
                    session_data["model_used"] = m
                    if req.voice:
                        session_data["voice"] = req.voice
                    
                    # Persist to CMS
                    try:
                        cms_helper.save_chat_session(req.session_id, req.username, session_data)
                    except Exception as db_err:
                        pass
            
            # --- TÍNH NĂNG: Ghi chép bệnh án lâm sàng sau mỗi 3 prompt ---
            if req.username and num_chats > 0 and num_chats % 3 == 0:
                result_json["ask_diary_consent"] = True
            # -----------------------------------------------------------
            
            return result_json
        except json.JSONDecodeError:
            return {
                "question": clean_content,
                "token_used": usage_tokens if usage_tokens is not None else cms_helper.count_tokens(clean_content, m),
                "model_used": m
            }
        
    except Exception as e:
        print("Chat endpoint error:", e)
        # Chỉ trả về thông báo lỗi thân thiện với người dùng
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

@app.post("/api/v1/chat:mindmap")
def generate_mindmap(req: ChatRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="Danh sách tin nhắn không được trống")
    try:
        current_graph_data = {"nodes": [], "edges": []}
        if hasattr(req, "graph_data") and req.graph_data:
            current_graph_data = req.graph_data
        elif req.username:
            try:
                sessions = cms_helper.get_chat_sessions(req.username)
                if sessions:
                    if req.session_id and req.session_id in sessions:
                        g_data = sessions[req.session_id].get("graph_data")
                    else:
                        sorted_sessions = sorted(sessions.values(), key=lambda x: x.get("created_at") or "", reverse=True)
                        g_data = sorted_sessions[0].get("graph_data") if sorted_sessions else None
                        
                    if isinstance(g_data, str):
                        try:
                            g_data = json.loads(g_data)
                        except:
                            g_data = {"nodes": [], "edges": []}
                    current_graph_data = g_data or {"nodes": [], "edges": []}
            except Exception as e:
                print(f"Lỗi khi lấy graph cho mindmap {req.username}: {e}")

        graph_instruction = ""
        if isinstance(current_graph_data, dict) and (current_graph_data.get("nodes") or current_graph_data.get("edges")):
            graph_instruction = f"\n\n[CRITICAL DIRECTIVE: CUMULATIVE MIND MAP BUILDING]\nHere is the user's CURRENT MIND MAP from previous turns of this session:\n{json.dumps(current_graph_data, ensure_ascii=False)}\n\nYou MUST continue building this mind map. You are strictly forbidden from overwriting, deleting, or changing the IDs/labels of the existing nodes (e.g. do not reuse n1, n2 if they already exist in the list). You MUST generate NEW nodes with NEW incremented IDs (e.g. n3, n4, n5...) for any new thoughts/arguments, and connect them with edges to the existing nodes to show logical progression or contradictions. REMEMBER TO BRANCH OUT: If the user provides multiple reasons/points, create multiple separate new nodes branching from the same parent node, rather than making a straight line.\n"

        user_message = req.messages[-1].content if req.messages else ""
        lang_instruction = f"\n\n[CRITICAL INSTRUCTION] The user's last message is: '{user_message}'. You MUST detect the language of this message. YOU MUST WRITE ALL JSON VALUES ENTIRELY IN THAT DETECTED LANGUAGE."

        final_system_prompt = MINDMAP_SYSTEM_PROMPT + graph_instruction + lang_instruction
        formatted_messages = [{"role": "system", "content": final_system_prompt}]
        
        for msg in req.messages:
            role = "assistant" if msg.role == "model" else msg.role
            formatted_messages.append({"role": role, "content": msg.content})

        model_env = os.getenv("LLM_MODEL", "thapsang")
        models_to_try = [m.strip() for m in model_env.split(",")]
        
        if req.model and req.model not in models_to_try:
            models_to_try.insert(0, req.model)
            
        content = ""
        last_error = None
        for m in models_to_try:
            timeout_val = 300.0 if "thapsang" in m else 120.0
            try:
                response = client.chat.completions.create(
                    model=m,
                    messages=formatted_messages,
                    temperature=0.2,
                    top_p=0.9,
                    max_tokens=3000,
                    timeout=timeout_val,
                    stream=True
                )
                
                content = ""
                for chunk in response:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, "content") and delta.content:
                            content += delta.content
                
                if content:
                    break
                else:
                    last_error = Exception("API returned empty response after streaming")
            except Exception as e:
                last_error = e
                continue
                
        if not content:
            print("API returned empty response. Falling back to existing graph.")
            if isinstance(current_graph_data, dict) and (current_graph_data.get("nodes") or current_graph_data.get("edges")):
                return current_graph_data
            else:
                return {"nodes": [], "edges": [], "current_step": "kham_pha", "focus_node_id": None}

        import re
        clean_content = content.strip()
        clean_content = re.sub(r'<think>.*?</think>', '', clean_content, flags=re.DOTALL).strip()
        
        json_match = re.search(r'\{.*\}', clean_content, re.DOTALL)
        if json_match:
            clean_content = json_match.group(0)
        else:
            clean_content = re.sub(r'```json|```', '', clean_content).strip()

        try:
            result_json = json.loads(clean_content)
        except json.JSONDecodeError:
            print("Mindmap JSON parse error:", clean_content)
            result_json = {"nodes": [], "edges": [], "current_step": "kham_pha", "focus_node_id": None}
            
        return result_json

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print("MINDMAP ERROR TRACEBACK:", tb)
        raise HTTPException(status_code=500, detail=f"System Error: {str(e)} | Traceback: {tb}")



# --- COHORT PERSONAL ROADMAP TASKS API ENDPOINTS ---
class CohortTaskRequest(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    goal: Optional[str] = ""
    status: Optional[str] = "backlog"
    week: Optional[int] = 1
    effort: Optional[int] = 2
    type: Optional[str] = "core"
    subtasks: Optional[list] = []
    description: Optional[str] = ""
    essay: Optional[str] = ""

@app.get("/api/v1/cohort_tasks:get/{username}")
def get_cohort_tasks_endpoint(username: str):
    try:
        return cms_helper.get_personal_roadmap_tasks(username)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting cohort tasks: {str(e)}")

@app.post("/api/v1/cohort_tasks:post/{username}")
def create_cohort_task_endpoint(username: str, req: CohortTaskRequest):
    try:
        task_data = req.dict()
        new_task = cms_helper.create_personal_roadmap_task(username, task_data)
        return {"status": "success", "task": new_task}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating cohort task: {str(e)}")

@app.patch("/api/v1/cohort_tasks:patch/{task_id}")
def update_cohort_task_endpoint(task_id: str, req: CohortTaskRequest):
    try:
        task_data = req.dict(exclude_unset=True)
        updated_task = cms_helper.update_personal_roadmap_task(task_id, task_data)
        return {"status": "success", "task": updated_task}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating cohort task: {str(e)}")


# --- COHORT QUIZ & SOCRATIC GRADING API ENDPOINTS ---
class GenerateQuizRequest(BaseModel):
    username: str
    week: int
    lang: Optional[str] = "vi"

class SubmitQuizRequest(BaseModel):
    username: str
    week: int
    answers: List[int]
    lang: Optional[str] = "vi"

@app.post("/api/v1/cohort:generate_quiz")
def generate_quiz_endpoint(req: GenerateQuizRequest):
    if not req.username or not req.week:
        raise HTTPException(status_code=400, detail="Username and week are required")
        
    lang = req.lang or "vi"
    
    # 1. Fetch personal roadmap tasks for the week
    tasks = cms_helper.get_personal_roadmap_tasks(req.username)
    week_tasks = [t for t in tasks if t.get("week") == req.week]
    core_task = next((t for t in week_tasks if t.get("type") == "core"), None)
    supp_task = next((t for t in week_tasks if t.get("type") == "supplementary"), None)
    
    if not core_task or not supp_task:
        raise HTTPException(
            status_code=400,
            detail="Bạn chưa được giao đủ nhiệm vụ cốt lõi và bổ trợ của tuần này." if lang == "vi" else "You haven't been assigned both core and supplementary tasks for this week."
        )
    if core_task.get("status") != "done" or supp_task.get("status") != "done":
        raise HTTPException(
            status_code=400,
            detail="Vui lòng hoàn thành cả 2 nhiệm vụ (cốt lõi & bổ trợ) trước khi làm trắc nghiệm." if lang == "vi" else "Please complete both core and supplementary tasks before starting the quiz."
        )

    # 2. Fetch parent personal_roadmap row
    user_info = cms_helper.get_user_by_username(req.username)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
        
    res_week = cms_helper.request_cms("GET", "/personal_roadmaps", params={
        "filter": json.dumps({
            "week": req.week,
            "$or": [
                {"fk_user": user_info["id"]},
                {"relation_roadmaps_user.id": user_info["id"]}
            ]
        }),
        "limit": 1
    })
    roadmaps = res_week.get("data", [])
    if not roadmaps:
        raise HTTPException(status_code=404, detail="Parent roadmap record not found")
        
    parent_record = roadmaps[0]
    roadmap_id = parent_record["id"]
    
    parent_extra = {}
    if parent_record.get("graph_data_roadmap"):
        try:
            parent_extra = json.loads(parent_record["graph_data_roadmap"])
        except:
            pass
            
    existing_quiz = parent_extra.get("quiz", {})
    if existing_quiz and "questions" in existing_quiz and len(existing_quiz["questions"]) == 8:
        stripped_questions = []
        for q in existing_quiz["questions"]:
            stripped_questions.append({
                "id": q["id"],
                "question_vi": q.get("question_vi") or q.get("question", ""),
                "question_en": q.get("question_en") or q.get("question", ""),
                "options_vi": q.get("options_vi") or q.get("options", []),
                "options_en": q.get("options_en") or q.get("options", [])
            })
        return {
            "status": "success",
            "questions": stripped_questions,
            "already_exists": True
        }

    # 3. Call OpenAI to generate Socratic quiz with dynamic personalization context
    onboarding = user_info.get("onboarding") or {}
    core_context = onboarding.get("_core_context", "")
    
    # Dynamically generate core context if empty
    if not core_context and onboarding:
        try:
            import context_learner
            core_context = context_learner.generate_context_from_onboarding(req.username, onboarding)
        except Exception as ce:
            print(f"Error generating onboarding context: {ce}")
            
    interests = onboarding.get("interests", [])
    problems = onboarding.get("problems", [])
    goals = onboarding.get("goals", [])
    
    # Try fetching latest diary entries to extract short-term emotional states and active mindsets
    diary_summary = ""
    try:
        entries = cms_helper.get_diary_entries(req.username)
        if entries:
            # Take the latest 3 diary entries to preserve high-fidelity context without bloating prompt
            latest_entries = entries[-3:]
            diary_lines = []
            for idx, entry in enumerate(latest_entries):
                title = entry.get("title", "")
                mood = entry.get("mood", "")
                content = entry.get("content", "")
                if content and len(content) > 150:
                    content = content[:150] + "..."
                diary_lines.append(f"- Nhật ký {idx+1}: Tiêu đề: {title} | Cảm xúc: {mood} | Nội dung: {content}")
            diary_summary = "\n".join(diary_lines)
    except Exception as de:
        print(f"Error fetching diaries for quiz personalization: {de}")

    # 2.5 Split bilingual translations for task titles to prevent ||| from leaking into Socratic questions
    def split_translation(text: str) -> tuple[str, str]:
        if not text:
            return "", ""
        if " ||| " in text:
            parts = text.split(" ||| ")
            return parts[0].strip(), parts[1].strip()
        if " | " in text:
            parts = text.split(" | ")
            return parts[0].strip(), parts[1].strip()
        if " / " in text:
            parts = text.split(" / ")
            return parts[0].strip(), parts[1].strip()
        if " |" in text:
            parts = text.split(" |")
            return parts[0].strip(), parts[1].strip()
        if " /" in text:
            parts = text.split(" /")
            return parts[0].strip(), parts[1].strip()
        return text.strip(), text.strip()

    core_title_vi_raw = core_task.get("title_vi") or core_task.get("title") or "Nhiệm vụ cốt lõi"
    supp_title_vi_raw = supp_task.get("title_vi") or supp_task.get("title") or "Nhiệm vụ bổ trợ"

    core_title_vi, core_title_en = split_translation(core_title_vi_raw)
    supp_title_vi, supp_title_en = split_translation(supp_title_vi_raw)

    ai_prompt = f"""You are the Socratic AI Coach of Thapsang.
The user is at Week {req.week} of their Personal Roadmap.
Week Title: {parent_record.get('roadmap_name', 'Tái Thiết Vĩ Đại')} - Tuần {req.week}

Here is the user's LONG-TERM SOCRATIC CORE CONTEXT (personality, cognitive blocks, behavioral patterns):
{core_context or "Chưa có thông tin bối cảnh dài hạn."}

Here are the user's general goals, problems, and interests:
- Problems: {", ".join(problems) if problems else "None"}
- Goals: {", ".join(goals) if goals else "None"}
- Interests: {", ".join(interests) if interests else "None"}

Here are the user's LATEST DIARY ENTRIES (representing their current real-world emotional struggles and active mindsets):
{diary_summary or "Chưa ghi nhận nhật ký gần đây."}

Here are the user's assigned Socratic tasks for this week:
Task 1 (Core) Vietnamese Title: {core_title_vi}
Task 1 (Core) English Title: {core_title_en}

Task 2 (Supplementary) Vietnamese Title: {supp_title_vi}
Task 2 (Supplementary) English Title: {supp_title_en}

You must generate exactly 8 Socratic multiple-choice questions customized to the user's assigned tasks, their core psychological blocks/goals, their diary mood states, and the week's theme.
IMPORTANT INSTRUCTIONS FOR QUIZ QUALITY:
1. Highly Personalized & Practical: Every question must directly connect to the user's assigned tasks, their diary feelings, their onboarding problems, or their cognitive blocks. Avoid generic, dry textbook questions.
2. Avoid Academics & Definitions: Do NOT ask for definitions of terms (e.g., 'What is a fixed mindset?', 'Define Socratic method...'). Avoid academic jargon.
3. Focus on Core Nature of the Problem: Write questions that help the learner explore the core nature of their own mindsets, cognitive bottlenecks, or behavioral patterns. Challenge their underlying assumptions. Let them see the practical essence and real-life choices behind the concept.
4. Each question must have exactly 4 choices (options).
5. Ensure a strict separate bilingual translation structure. For every question, you must provide BOTH high-fidelity Vietnamese and English versions (strictly matching each other) inside 'question_vi', 'question_en', 'options_vi' (exactly 4 options), and 'options_en' (exactly 4 options). No mixed-languages inside the translation fields.
6. NO REPETITION: All 8 questions MUST be completely UNIQUE and DIVERSE. Do NOT repeat the same question structure, same topic, or same options. Explore 8 different distinct angles, scenarios, or psychological obstacles related to the week's theme and tasks.

You MUST respond with a single, valid JSON object conforming exactly to this JSON schema (do NOT wrap it in any Markdown codeblocks or other formatting, just return raw JSON):
{{
  "questions": [
    {{
      "id": 1,
      "question_vi": "Câu hỏi trắc nghiệm bằng tiếng Việt, tập trung chi tiết vào bài luận, tâm trạng nhật ký và thực tế hành vi của người học...",
      "question_en": "High-fidelity English translation of the same question...",
      "options_vi": [
        "Lựa chọn A...",
        "Lựa chọn B...",
        "Lựa chọn C...",
        "Lựa chọn D..."
      ],
      "options_en": [
        "Option A...",
        "Option B...",
        "Option C...",
        "Option D..."
      ],
      "correct_answer": 0  // Index of correct option (0 to 3)
    }},
    ...
  ]
}}
"""
    quiz_data = None
    try:
        model_name = os.getenv("LLM_MODEL", "thapsang").split(",")[0].strip()
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": ai_prompt}],
            temperature=0.3,
            top_p=0.9,
            presence_penalty=0.6,
            frequency_penalty=0.6,
            max_tokens=3000
        )
        content = response.choices[0].message.content.strip()
        
        import re
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            content = match.group(0)
        else:
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
        content = content.strip()
        
        quiz_data = json.loads(content)
        if "questions" not in quiz_data or len(quiz_data["questions"]) != 8:
            raise ValueError("AI failed to generate exactly 8 questions")
    except Exception as e:
        print(f"Failed to generate AI quiz: {e}. Using fallback week-specific Socratic quiz.")
        
        # Build 10 dynamic fallback Socratic questions using the actual weekly tasks to ensure they are NEVER repeating!
        fallback_questions = []
        fallback_questions.append({
            "id": 1,
            "question_vi": f"Khi thực hiện nhiệm vụ cốt lõi '{core_title_vi}', bài học quan trọng nhất về mặt nhận thức Socratic là gì?",
            "question_en": f"When executing the core task '{core_title_en}', what is the most important Socratic cognitive takeaway?",
            "options_vi": ["Chứng minh bản thân luôn luôn đúng và không có sai lầm", "Nhận diện những rào cản hành vi và rèn luyện tính tự soi chiếu sâu sắc", "Chỉ hoàn thành nhiệm vụ để đối phó với yêu cầu hệ thống", "Bỏ qua mọi cảm xúc tiêu cực và ép mình phải tích cực"],
            "options_en": ["To prove yourself always correct with zero errors", "To identify behavioral friction and practice deep self-reflection", "To complete the task solely to satisfy system requirements", "To ignore negative emotions and force empty positivity"],
            "correct_answer": 1
        })
        fallback_questions.append({
            "id": 2,
            "question_vi": f"Làm thế nào để nhiệm vụ bổ trợ '{supp_title_vi.strip()}' giúp bạn củng cố mục tiêu học tập của Tuần {req.week}?",
            "question_en": f"How does the supplementary task '{supp_title_en.strip()}' support your learning goals for Week {req.week}?",
            "options_vi": ["Nó cung cấp góc nhìn bổ sung và thực hành mở rộng để tháo gỡ điểm nghẽn", "Nó là nhiệm vụ tùy chọn không mang lại bất cứ giá trị thực tế nào", "Nó thay thế hoàn toàn nhiệm vụ cốt lõi nên không cần làm cái kia", "Nó làm tăng khối lượng công việc để gây áp lực cho người học"],
            "options_en": ["It provides complementary perspectives and extended practice to resolve bottlenecks", "It is a fully optional task with no practical value", "It replaces the core task entirely, making it redundant", "It increases workload simply to put pressure on the learner"],
            "correct_answer": 0
        })
        fallback_questions.append({
            "id": 3,
            "question_vi": f"Tại sao việc soi chiếu sâu sắc trong các chặng như Tuần {req.week} lại vượt trội hơn việc chỉ thực thi hành động thụ động?",
            "question_en": f"Why does deep reflection in cycles like Week {req.week} outperform passive task execution?",
            "options_vi": ["Nó giúp tự truy vấn các giả định ẩn sâu để kiến tạo sự thấu hiểu đích thực", "Nó tốn nhiều thời gian và làm giảm tốc độ thực thi dự án", "Nó giúp đổ lỗi cho hoàn cảnh một cách khoa học", "Nó khiến người học không cần phải hành động nữa"],
            "options_en": ["It challenges hidden assumptions to construct genuine insight", "It wastes time and slows down actual execution speed", "It provides a scientific way to blame external circumstances", "It makes actual execution unnecessary for the learner"],
            "correct_answer": 0
        })
        fallback_questions.append({
            "id": 4,
            "question_vi": f"Theo mô hình phát triển nhận thức, điểm nghẽn thực thi lớn nhất bạn gặp phải ở Tuần {req.week} thường xuất phát từ đâu?",
            "question_en": f"According to cognitive models, where does your biggest execution bottleneck in Week {req.week} typically originate?",
            "options_vi": ["Sự thiếu hụt thời gian tuyệt đối trong ngày", "Mô thức tư duy cũ và sự kháng cự của vùng an toàn nhận thức", "Do AI Coach đưa ra các câu hỏi quá khó phản biện", "Do hệ thống không tự động tích hợp thói quen hộ bạn"],
            "options_en": ["An absolute lack of time in your daily schedule", "Old mental paradigms and resistance from your cognitive comfort zone", "The Socratic AI Coach asking overly challenging questions", "The system not automatically building habits for you"],
            "correct_answer": 1
        })
        fallback_questions.append({
            "id": 5,
            "question_vi": "Trong chu trình tự học và chuyển hóa Socratic, thái độ đúng đắn nhất đối với sự 'không biết' là gì?",
            "question_en": "In the Socratic self-learning and transformation cycle, what is the best attitude toward 'not knowing'?",
            "options_vi": ["Cảm thấy xấu hổ và cố gắng che giấu nó bằng mọi cách", "Chấp nhận nó như điểm khởi đầu khách quan để khám phá và mở rộng nhận thức", "Bỏ qua nó và tin rằng mình đã hiểu rõ mọi thứ", "Chờ đợi người khác đến giải thích hộ toàn bộ"],
            "options_en": ["Feeling ashamed and attempting to conceal it at all costs", "Accepting it as the objective starting point for discovery and growth", "Ignoring it and believing you already know everything", "Waiting for someone else to explain everything for you"],
            "correct_answer": 1
        })
        fallback_questions.append({
            "id": 6,
            "question_vi": f"Sau khi hoàn thành viết bài chiêm nghiệm Tuần {req.week}, bước tiếp theo để thói quen được củng cố bền vững là gì?",
            "question_en": f"After writing your Week {req.week} reflection, what is the next step to sustainably consolidate this habit?",
            "options_vi": ["Ngừng theo dõi và chuyển sang thói quen mới hoàn toàn khác biệt", "Đưa bài học vào chu trình PDCA (Plan-Do-Check-Act) thực tế mỗi ngày", "Tự hài lòng và tin rằng nhận thức đã tự động thay đổi vĩnh viễn", "Chờ đợi AI nhắc nhở mới tiếp tục thực hành"],
            "options_en": ["Stop tracking and transition to a completely different habit", "Integrate the takeaway into your daily practical PDCA loop", "Be complacent and believe mindsets changed automatically and permanently", "Wait for AI reminders before practicing again"],
            "correct_answer": 1
        })
        fallback_questions.append({
            "id": 7,
            "question_vi": "Làm thế nào để duy trì sự nhất quán giữa nhận thức lý thuyết và hành động thực tế?",
            "question_en": "How can one maintain consistency between theoretical mindsets and practical actions?",
            "options_vi": ["Chỉ tập trung đọc sách mà không tham gia thực thi thực tế", "Thiết kế môi trường hỗ trợ và cài đặt các tín hiệu kích hoạt hành vi rõ ràng", "Suy nghĩ thật nhiều và hy vọng hành động tự xảy ra", "Đổ lỗi cho việc thiếu ý chí khi không làm được"],
            "options_en": ["Focus exclusively on reading theory without any practical execution", "Design a supportive environment and set explicit behavioral trigger signals", "Think excessively and hope that action happens naturally", "Blame a lack of willpower whenever execution fails"],
            "correct_answer": 1
        })
        fallback_questions.append({
            "id": 8,
            "question_vi": f"Mục tiêu cốt lõi của bài trắc nghiệm soi chiếu Tuần {req.week} là gì?",
            "question_en": f"What is the core goal of the Week {req.week} reflective Socratic quiz?",
            "options_vi": ["Đánh giá học thuật xem bạn có thuộc lòng định nghĩa không", "Tạo cơ hội để bạn đối thoại với chính mình qua phản biện khách quan", "Tính điểm số để xếp hạng và trừng phạt người học", "Hoàn thành thủ tục hành chính bắt buộc của lighthouse"],
            "options_en": ["Focus exclusively on academics and reciting definitions", "Create an opportunity for you to dialogue with yourself through objective reflection", "Calculate scores to rank and punish learners", "Complete a mandatory administrative procedure for the lighthouse"],
            "correct_answer": 1
        })
        quiz_data = {"questions": fallback_questions}

    # 4. Save quiz to parent record's graph_data_roadmap
    parent_extra["quiz"] = {
        "questions": quiz_data["questions"],
        "created_at": datetime.datetime.now().isoformat() + "Z"
    }
    
    cms_helper.request_cms("PATCH", f"/personal_roadmaps/{roadmap_id}", params={"filterByTk": roadmap_id}, json_data={
        "graph_data_roadmap": json.dumps(parent_extra, ensure_ascii=False),
        "test_flag": "Activated"
    })
    
    # Strip correct answers before returning to client
    stripped = []
    for q in quiz_data["questions"]:
        stripped.append({
            "id": q["id"],
            "question_vi": q.get("question_vi") or q.get("question", ""),
            "question_en": q.get("question_en") or q.get("question", ""),
            "options_vi": q.get("options_vi") or q.get("options", []),
            "options_en": q.get("options_en") or q.get("options", [])
        })
        
    return {
        "status": "success",
        "questions": stripped
    }

@app.post("/api/v1/cohort:submit_quiz")
def submit_quiz_endpoint(req: SubmitQuizRequest):
    if not req.username or not req.week or req.answers is None:
        raise HTTPException(status_code=400, detail="Username, week, and answers are required")
        
    lang = req.lang or "vi"
    
    # 1. Fetch parent record
    user_info = cms_helper.get_user_by_username(req.username)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
        
    res_week = cms_helper.request_cms("GET", "/personal_roadmaps", params={
        "filter": json.dumps({
            "week": req.week,
            "$or": [
                {"fk_user": user_info["id"]},
                {"relation_roadmaps_user.id": user_info["id"]}
            ]
        }),
        "limit": 1
    })
    roadmaps = res_week.get("data", [])
    if not roadmaps:
        raise HTTPException(status_code=404, detail="Parent roadmap record not found")
        
    parent_record = roadmaps[0]
    roadmap_id = parent_record["id"]
    
    parent_extra = {}
    if parent_record.get("graph_data_roadmap"):
        try:
            parent_extra = json.loads(parent_record["graph_data_roadmap"])
        except:
            pass
            
    quiz_data = parent_extra.get("quiz", {})
    if not quiz_data or "questions" not in quiz_data:
        raise HTTPException(
            status_code=400,
            detail="Bài trắc nghiệm chưa được kích hoạt cho tuần này." if lang == "vi" else "The quiz has not been activated for this week."
        )

    questions = quiz_data["questions"]
    
    if len(req.answers) != 8:
        raise HTTPException(
            status_code=400,
            detail="Bạn phải trả lời đầy đủ 8 câu hỏi." if lang == "vi" else "You must answer all 8 questions."
        )

    # 2. Grade Quiz (80% of total grade)
    correct_count = 0
    for i, q in enumerate(questions):
        user_ans = req.answers[i]
        correct_ans = q.get("correct_answer", 0)
        if user_ans == correct_ans:
            correct_count += 1
            
    quiz_score = float(correct_count) * 10.0 # max 80

    # 3. Call AI Socratic Essay Evaluator to grade reflections (1-20% bonus points)
    bonus_score = 15
    critique = "Bạn đã thực sự nghiêm túc chiêm nghiệm và đối diện thẳng thắn với các định kiến giới hạn của bản thân. Hãy tiếp tục duy trì tâm thế cởi mở này ở những tuần tiếp theo!" if lang == "vi" else "You have taken deep responsibility for your own growth and challenged your limiting assumptions. Keep this open mindset for the upcoming cycles!"
    
    attempts = quiz_data.get("attempts", [])
    if attempts:
        last_attempt = attempts[-1]
        bonus_score = last_attempt.get("essay_bonus", 15)
        critique = last_attempt.get("critique", critique)
    else:
        # Fetch essays
        tasks = cms_helper.get_personal_roadmap_tasks(req.username)
        week_tasks = [t for t in tasks if t.get("week") == req.week]
        core_task = next((t for t in week_tasks if t.get("type") == "core"), None)
        supp_task = next((t for t in week_tasks if t.get("type") == "supplementary"), None)
    
        task1_title = core_task.get("title") if core_task else "Core Task"
        task1_essay = core_task.get("essay") if core_task else ""
        task2_title = supp_task.get("title") if supp_task else "Supplementary Task"
        task2_essay = supp_task.get("essay") if supp_task else ""

        # Analyze Core Essay and Supplementary Essay using heuristic (fast)
        essay1_len = len(task1_essay.strip()) if task1_essay else 0
        essay2_len = len(task2_essay.strip()) if task2_essay else 0
        
        # Socratic self-questioning and reflection keywords
        socratic_keywords = [
            "định kiến", "giới hạn", "nhận thức", "mô thức", "thói quen", "unlearn", "relearn", 
            "bias", "habit", "reflection", "tư duy", "lý do", "tại sao", "nghi ngờ", "giả định",
            "học hỏi", "thay đổi", "cản trở", "động lực", "mục tiêu", "bài học", "chuyển hóa",
            "self-limiting", "belief", "assumptions", "mindset", "unlearning", "cognitive",
            "why", "how", "rupture", "pattern", "routine", "barrier", "struggle", "breakthrough"
        ]
        
        kw_count1 = sum(1 for kw in socratic_keywords if kw in task1_essay.lower()) if task1_essay else 0
        kw_count2 = sum(1 for kw in socratic_keywords if kw in task2_essay.lower()) if task2_essay else 0
        
        # Self-questioning check (contains question marks "?")
        q_count1 = task1_essay.count("?") if task1_essay else 0
        q_count2 = task2_essay.count("?") if task2_essay else 0
        
        # Calculate dynamic scores out of 10 for Core Essay
        score1 = 5  # Base score
        if essay1_len > 500: score1 += 3
        elif essay1_len > 250: score1 += 2
        elif essay1_len > 100: score1 += 1
        
        score1 += min(3, kw_count1 // 2)
        score1 += min(2, q_count1)
        score1 = min(10, score1)
        
        # Calculate dynamic scores out of 10 for Supplementary Essay
        score2 = 5  # Base score
        if essay2_len > 500: score2 += 3
        elif essay2_len > 250: score2 += 2
        elif essay2_len > 100: score2 += 1
        
        score2 += min(3, kw_count2 // 2)
        score2 += min(2, q_count2)
        score2 = min(10, score2)
        
        # Combined heuristic bonus score (max 20)
        bonus_score = score1 + score2
        
        # Dynamic critique aligned with calculated score
        if bonus_score >= 18:
            critique = (
                "Bạn đã thực hiện một phiên soi chiếu tuyệt vời! Bài viết thể hiện sự trung thực tuyệt đối, dũng cảm đối diện với những đứt gãy nhận thức cốt lõi và tự đặt câu hỏi sâu sắc. Trí tuệ Socratic của bạn đang phát triển rất mạnh mẽ."
                if lang == "vi" else
                "Exceptional reflection! Your essay displays complete self-honesty, courage in facing core cognitive ruptures, and deep self-questioning. Your Socratic wisdom is growing remarkably."
            )
        elif bonus_score >= 14:
            critique = (
                "Bài chiêm nghiệm của bạn rất tốt. Bạn đã nhận diện rõ thói quen và định kiến giới hạn. Để đạt hiệu quả cao hơn nữa ở các tuần kế tiếp, hãy cố gắng đặt thêm nhiều câu hỏi đào sâu nguyên nhân gốc rễ của những hành vi đó."
                if lang == "vi" else
                "Very good reflection. You identified limiting habits and beliefs clearly. For even greater breakthroughs in upcoming weeks, try to ask more probing questions about the root causes of those behaviors."
            )
        else:
            critique = (
                "Cảm ơn bài viết chiêm nghiệm của bạn. Dù đã hoàn thành, bài viết còn hơi ngắn hoặc mang tính mô tả chung chung. Hãy dành thêm thời gian tĩnh lặng để tự truy vấn sâu hơn về các giả định ẩn sâu bên trong mình."
                if lang == "vi" else
                "Thank you for your reflection. While completed, the content is somewhat descriptive or brief. Try spending more quiet time to actively question the hidden assumptions behind your daily routines."
            )

    total_score = quiz_score + bonus_score
    passed = total_score >= 50.0

    # 4. Save attempt in parent extra
    attempt = {
        "answers": req.answers,
        "correct_count": correct_count,
        "quiz_score": quiz_score,
        "essay_bonus": bonus_score,
        "critique": critique,
        "total_score": total_score,
        "passed": passed,
        "timestamp": datetime.datetime.now().isoformat() + "Z"
    }
    
    if "attempts" not in quiz_data:
        quiz_data["attempts"] = []
    quiz_data["attempts"].append(attempt)
    
    highest_score = max(a.get("total_score", 0) for a in quiz_data["attempts"])
    highest_passed = any(a.get("passed", False) for a in quiz_data["attempts"])
    
    quiz_data["passed"] = highest_passed
    quiz_data["total_score"] = highest_score
    
    parent_extra["quiz"] = quiz_data

    # Generate detailed text format for final_test long text column
    final_test_lines = []
    option_letters = ["A", "B", "C", "D"]
    for i, q in enumerate(questions):
        q_vi = q.get("question_vi") or q.get("question", "")
        q_en = q.get("question_en") or ""
        question_text = f"{q_vi} / {q_en}" if q_en else q_vi
        
        opts_vi = q.get("options_vi") or q.get("options", [])
        opts_en = q.get("options_en") or []
        
        final_test_lines.append(f"Câu hỏi {i+1}: {question_text}")
        
        for idx in range(4):
            opt_vi = opts_vi[idx] if idx < len(opts_vi) else ""
            opt_en = opts_en[idx] if idx < len(opts_en) else ""
            opt_text = f"{opt_vi} / {opt_en}" if opt_en else opt_vi
            final_test_lines.append(f"  - Đáp án {option_letters[idx]}: {opt_text}")
            
        correct_idx = q.get("correct_answer", 0)
        user_idx = req.answers[i]
        
        correct_letter = option_letters[correct_idx] if 0 <= correct_idx < 4 else str(correct_idx)
        user_letter = option_letters[user_idx] if 0 <= user_idx < 4 else str(user_idx)
        
        final_test_lines.append(f"  => Đáp án chính xác: {correct_letter}")
        final_test_lines.append(f"  => Đáp án của người dùng: {user_letter}")
        final_test_lines.append("")
        
    final_test_str = "\n".join(final_test_lines)
    
    # Use highest_score for week_progress instead of the latest attempt's total_score
    new_progress = float(highest_score) / 100.0
    current_progress = parent_record.get("week_progress") or 0.0
    
    patch_data = {
        "graph_data_roadmap": json.dumps(parent_extra, ensure_ascii=False),
        "final_test": final_test_str
    }
    
    if new_progress > current_progress:
        patch_data["week_progress"] = new_progress

    cms_helper.request_cms("PATCH", f"/personal_roadmaps/{roadmap_id}", params={"filterByTk": roadmap_id}, json_data=patch_data)

    return {
        "status": "success",
        "passed": passed,
        "correct_count": correct_count,
        "quiz_score": quiz_score,
        "essay_bonus": bonus_score,
        "critique": critique,
        "total_score": total_score,
        "attempt": attempt
    }


# --- VOICE API ENDPOINTS ---
@app.post("/api/v1/voice:generate")
async def generate_voice(request: Request):
    try:
        data = await request.json()
        text = data.get("text")
        voice_id = data.get("voice_id")
        
        url = "https://mapi.mojo.vn/v2/api/generate"
        import os
        api_key = os.getenv("VOICE_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="VOICE_API_KEY is missing")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        payload = {
            "platform": "web",
            "index": "gen-voice",
            "data": {
                "app_name": "gen-voice",
                "speed": 1,
                "text": text,
                "voice": voice_id
            }
        }
        
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload, timeout=15.0)
            if resp.status_code != 200:
                print("Mojo API Generate Error:", resp.status_code, resp.text)
            resp.raise_for_status()
            result = resp.json()
            return result
    except Exception as e:
        print(f"Error generating voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/voice:status")
async def check_voice_status(request: Request):
    try:
        data = await request.json()
        ref_id = data.get("id")
        
        url = "https://mapi.mojo.vn/v2/api/get"
        import os
        api_key = os.getenv("VOICE_GET_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="VOICE_GET_API_KEY is missing")
            
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        payload = {
            "platform": "web",
            "index": "gen-voice",
            "data": {
                "id": ref_id
            }
        }
        
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload, timeout=15.0)
            if resp.status_code != 200:
                print("Mojo API Status Error:", resp.status_code, resp.text)
            resp.raise_for_status()
            result = resp.json()
            
            if result.get("data", {}).get("status") == "done":
                media_url = result["data"].get("media_url")
                if media_url and "mapi.mojo.vn" in media_url:
                    try:
                        audio_resp = await client.get(media_url, timeout=15.0)
                        if audio_resp.status_code == 200:
                            import uuid
                            from urllib.parse import urlparse
                            
                            cms_base_url = os.getenv("CMS_BASE_URL", "http://localhost:13000/api")
                            cms_api_key = os.getenv("CMS_API_KEY")
                            upload_headers = {"Authorization": f"Bearer {cms_api_key}"}
                            upload_url = f"{cms_base_url}/attachments:create"
                            
                            filename = f"voice_{uuid.uuid4().hex}.wav"
                            files = {"file": (filename, audio_resp.content, "audio/wav")}
                            
                            upload_resp = await client.post(upload_url, headers=upload_headers, files=files, timeout=30.0)
                            if upload_resp.status_code == 200:
                                upload_data = upload_resp.json().get("data", {})
                                relative_url = upload_data.get("url")
                                if relative_url:
                                    parsed_url = urlparse(cms_base_url)
                                    cms_origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
                                    new_media_url = f"{cms_origin}{relative_url}"
                                    result["data"]["media_url"] = new_media_url
                    except Exception as upload_err:
                        print(f"Error uploading voice to CMS: {upload_err}")
                        
            return result
    except Exception as e:
        print(f"Error checking voice status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- TASKS API ENDPOINTS ---
class TaskRequest(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    goal: Optional[str] = ""
    status: Optional[str] = "backlog"
    deadline: Optional[str] = ""
    effort: Optional[int] = 1
    subtasks: Optional[list] = []
    contextLink: Optional[str] = ""
    feedback: Optional[str] = None

@app.post("/api/v1/tasks:generate_microsteps")
def generate_microsteps_endpoint(req: MicrostepsRequest):
    if not req.title:
        raise HTTPException(status_code=400, detail="Task title is required")
        
    effort = max(1, req.effort)
    lang = req.lang or "vi"
    ai_prompt = f"""You are a meticulous task planner for the Thapsang Mindset OS (PDCA Level 2).
Your goal is to break down a high-level task into exactly {effort} actionable, concrete, and highly focused Pomodoro-sized (25 minutes) micro-steps/subtasks.

Task Title: {req.title}
Task Goal: {req.goal or 'No specific goal.'}

Requirements:
1. You MUST generate EXACTLY {effort} micro-steps/subtasks. No more, no less.
2. Each micro-step represents a 25-minute Pomodoro block of work. It must be highly actionable, specific, and clear.
3. You MUST provide a BILINGUAL title for each micro-step, in the EXACT format: "Vietnamese Title ||| English Title".
   For example: "Phân tích yêu cầu bài học ||| Analyze lesson requirements" or "Hoàn thành chiêm nghiệm Socratic ||| Complete Socratic reflection".
   Ensure that the Vietnamese translation is natural, professional, and clear, and the English translation is accurate.
4. Return ONLY a valid JSON array of objects conforming exactly to this schema, without any Markdown formatting (no ```json code blocks, just raw text):
[
  {{"title": "Mô tả bước bằng tiếng Việt ||| Step description in English", "completed": false}},
  ...
]
"""

    ai_response_text = ""
    # Try streaming first to bypass proxy response truncation/wrapping bug
    try:
        from openai import OpenAI as _OpenAI
        _client = _OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
        )
        model_name = os.getenv("LLM_MODEL", "thapsang").split(",")[0].strip()
        
        try:
            stream_response = _client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": ai_prompt}],
                temperature=0.2,
                top_p=0.9,
                stream=True
            )
            chunks = []
            for chunk in stream_response:
                if chunk.choices and chunk.choices[0].delta.content:
                    chunks.append(chunk.choices[0].delta.content)
            ai_response_text = "".join(chunks).strip()
        except Exception as se:
            print(f"Streaming failed in generate_microsteps: {se}. Falling back to non-streaming.")
            
        # Fallback to non-streaming with proxy JSON parser
        if not ai_response_text:
            resp = _client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": ai_prompt}],
                max_tokens=1024,
                temperature=0.2,
                top_p=0.9,
            )
            if getattr(resp, "choices", None):
                ai_response_text = resp.choices[0].message.content.strip()
            elif hasattr(resp, "error") and resp.error and isinstance(resp.error, dict):
                details_str = resp.error.get("details", "{}")
                try:
                    import json
                    parsed_details = json.loads(details_str)
                    ai_response_text = parsed_details["choices"][0]["message"]["content"].strip()
                except Exception:
                    pass
                    
        if ai_response_text:
            import re
            ai_response_text = re.sub(r'<think>.*?</think>', '', ai_response_text, flags=re.DOTALL).strip()
            if ai_response_text.startswith("```json"):
                ai_response_text = ai_response_text[7:]
            if ai_response_text.endswith("```"):
                ai_response_text = ai_response_text[:-3]
            ai_response_text = ai_response_text.strip()
            
            import json
            subtasks = json.loads(ai_response_text)
            if isinstance(subtasks, list):
                cleaned_subtasks = []
                for item in subtasks:
                    if isinstance(item, dict) and "title" in item:
                        cleaned_subtasks.append({
                            "title": to_sentence_case_bilingual(item["title"]),
                            "completed": bool(item.get("completed", False))
                        })
                
                if len(cleaned_subtasks) == effort:
                    return {"status": "success", "subtasks": cleaned_subtasks}
                
                if len(cleaned_subtasks) > effort:
                    cleaned_subtasks = cleaned_subtasks[:effort]
                else:
                    while len(cleaned_subtasks) < effort:
                        idx = len(cleaned_subtasks) + 1
                        title = f"Step {idx} for {req.title}" if lang == "en" else f"Bước {idx} cho {req.title}"
                        cleaned_subtasks.append({"title": to_sentence_case_bilingual(title), "completed": False})
                return {"status": "success", "subtasks": cleaned_subtasks}
            else:
                raise ValueError("AI did not return a valid list array")
                
    except Exception as e:
        print(f"Error in generate-microsteps AI: {e}. Falling back to default list generation.")
        
    fallback_subtasks = []
    for idx in range(1, effort + 1):
        if effort == 1:
            title = f"Execute core task: {req.title}" if lang == "en" else f"Thực hiện nhiệm vụ cốt lõi: {req.title}"
        elif idx == 1:
            title = f"Prepare and plan for: {req.title}" if lang == "en" else f"Chuẩn bị tài nguyên và lập kế hoạch cho: {req.title}"
        elif idx == effort:
            title = f"Finalize, review and wrap up: {req.title}" if lang == "en" else f"Kiểm tra chất lượng, hoàn thiện và đóng gói: {req.title}"
        else:
            title = f"Execute phase {idx-1} of: {req.title}" if lang == "en" else f"Triển khai phân đoạn {idx-1} của: {req.title}"
            
        fallback_subtasks.append({"title": to_sentence_case_bilingual(title), "completed": False})
        
    return {"status": "success", "subtasks": fallback_subtasks}

def validate_task_goal_length(goal: Optional[str]) -> Optional[str]:
    if not goal:
        return goal
    if "|||" in goal:
        parts = [p.strip() for p in goal.split("|||")]
        valid_parts = []
        for p in parts:
            if len(p) > 200:
                valid_parts.append(p[:197] + "...")
            else:
                valid_parts.append(p)
        return " ||| ".join(valid_parts)
    else:
        if len(goal) > 200:
            return goal[:197] + "..."
        return goal

@app.get("/api/v1/tasks:get/{username}")
def get_tasks_endpoint(username: str):
    try:
        return cms_helper.get_tasks(username)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting tasks: {str(e)}")

@app.post("/api/v1/tasks:create/{username}")
def create_task_endpoint(username: str, req: TaskRequest):
    try:
        req.goal = validate_task_goal_length(req.goal)
        task_data = req.dict()
        new_task = cms_helper.create_task(username, task_data)
        return {"status": "success", "task": new_task}
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")

@app.patch("/api/v1/tasks:update/{task_id}")
def update_task_endpoint(task_id: str, req: TaskRequest):
    try:
        if req.goal is not None:
            req.goal = validate_task_goal_length(req.goal)
        task_data = req.dict(exclude_unset=True)
        updated_task = cms_helper.update_task(task_id, task_data)
        return {"status": "success", "task": updated_task}
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")

@app.delete("/api/v1/tasks:destroy/{task_id}")
def delete_task_endpoint(task_id: str):
    try:
        # If it's a local un-synced task, return success immediately
        if task_id.startswith("cohort_"):
            return {"status": "success"}
            
        cms_helper.delete_task(task_id)
        # Always return success to allow frontend to clear it from UI and local cache.
        # If it was already deleted on CMS (404), it's safe. 
        # If CMS failed for other reasons, returning success prevents it from being stuck.
        return {"status": "success"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Fallback to success to unstuck the UI
        return {"status": "success"}

# Mount frontend làm static assets (CSS, JS, Images, v.v)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

if __name__ == "__main__":
    import asyncio
    
    async def start_server(port):
        config = uvicorn.Config(app, host="0.0.0.0", port=port)
        server = uvicorn.Server(config)
        await server.serve()

    async def run_multiple_ports():
        # Khởi chạy ứng dụng trên cả 2 cổng để tương thích với hạ tầng cũ và mới
        await asyncio.gather(
            start_server(8000),
            start_server(8501)
        )
        
    print("Starting Unified Server on ports 8000 and 8501")
    asyncio.run(run_multiple_ports())
