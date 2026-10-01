"""
Therapity — Cohort / Roadmap Router
Provides AI-personalized 12-week learning roadmap endpoints.
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.models.user import User
from app.models.cohort import CohortMember, PersonalRoadmap

router = APIRouter(prefix="/api/v1/cohort", tags=["cohort"])

# ── Syllabus template (12 weeks) ──────────────────────────────
DEFAULT_SYLLABUS = [
    {"week": 1,  "title": "Nhận diện Khuôn mẫu Tư duy",       "description": "Khám phá những tư duy cố hữu đang định hình hành vi hàng ngày."},
    {"week": 2,  "title": "Đứt gãy Nhận thức",                "description": "Phân tích các bias nhận thức phổ biến và cách chúng chi phối quyết định."},
    {"week": 3,  "title": "Hệ thống Niềm tin Cốt lõi",        "description": "Truy vết các niềm tin gốc rễ từ quá khứ ảnh hưởng đến hiện tại."},
    {"week": 4,  "title": "Phá vỡ Vùng An toàn",              "description": "Thực hành rời khỏi comfort zone để mở rộng năng lực."},
    {"week": 5,  "title": "Tái Thiết Mục tiêu",               "description": "Xây dựng hệ thống mục tiêu dựa trên giá trị cá nhân."},
    {"week": 6,  "title": "Kỹ năng Metacognition",             "description": "Học cách tư duy về chính quá trình tư duy của bạn."},
    {"week": 7,  "title": "Quản lý Cảm xúc Chiến lược",       "description": "Phát triển trí tuệ cảm xúc trong xung đột và áp lực."},
    {"week": 8,  "title": "Ra quyết định Dưới Bất định",       "description": "Framework ra quyết định khi không đủ thông tin."},
    {"week": 9,  "title": "Hệ thống Thói quen Mới",           "description": "Thiết kế và vận hành hệ thống thói quen bền vững."},
    {"week": 10, "title": "Giao tiếp Socratic",               "description": "Áp dụng phương pháp Socratic trong giao tiếp hàng ngày."},
    {"week": 11, "title": "Tích hợp và Đồng bộ",              "description": "Tổng hợp các kỹ năng đã học thành hệ thống vận hành cá nhân."},
    {"week": 12, "title": "Hành trình Tiếp theo",              "description": "Lộ trình phát triển dài hạn và cam kết với bản thân."},
]


# ── Helper: resolve user ──────────────────────────────────────
async def resolve_user(username: str, db: AsyncSession) -> User:
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ── GET /syllabus ─────────────────────────────────────────────
@router.get("/syllabus")
async def get_syllabus(
    username: str = Query(...),
    week: int = Query(1),
    db: AsyncSession = Depends(get_db),
):
    user = await resolve_user(username, db)
    
    # Get user's personalized syllabus from roadmaps
    stmt = select(PersonalRoadmap).where(PersonalRoadmap.user_id == user.id).order_by(PersonalRoadmap.week)
    result = await db.execute(stmt)
    roadmaps = result.scalars().all()
    
    # Build syllabus from roadmaps or fallback to default
    syllabus = []
    for s in DEFAULT_SYLLABUS:
        entry = {**s}
        for rm in roadmaps:
            if rm.week == s["week"] and rm.roadmap_name:
                entry["title"] = rm.roadmap_name
        syllabus.append(entry)
    
    # Find current week (highest week with tasks)
    max_week = max([rm.week for rm in roadmaps], default=1)
    
    # Weekly progress history
    weekly_progress = {}
    for rm in roadmaps:
        weekly_progress[str(rm.week)] = rm.week_progress or 0
    
    return {
        "syllabus": syllabus,
        "cohort_info": {
            "current_week": max(max_week, 1),
            "total_weeks": 12,
            "weekly_progress_history": weekly_progress,
        }
    }


# ── GET /activity ────────────────────────────────────────────
@router.get("/activity")
async def get_activity():
    return {"feed": [], "bottleneck": {}, "pivot": {}}


# ── GET /members ─────────────────────────────────────────────
@router.get("/members")
async def get_members(db: AsyncSession = Depends(get_db)):
    stmt = select(CohortMember)
    result = await db.execute(stmt)
    members = result.scalars().all()
    return {
        "members": [
            {
                "username": m.display_name or "User",
                "display_name": m.display_name or "User",
                "is_self": m.is_self,
                "week_progress": (m.week_progress or {}).get("current", 0),
            }
            for m in members
        ]
    }


# ── GET /tasks/{username} ────────────────────────────────────
@router.get("/tasks/{username}")
async def get_tasks(username: str, db: AsyncSession = Depends(get_db)):
    user = await resolve_user(username, db)
    stmt = select(PersonalRoadmap).where(PersonalRoadmap.user_id == user.id).order_by(PersonalRoadmap.week)
    result = await db.execute(stmt)
    roadmaps = result.scalars().all()
    
    tasks = []
    for rm in roadmaps:
        # Core task
        if rm.task_core:
            task = {
                "id": str(rm.id) + "_core",
                "week": rm.week,
                "type": "core",
                "title": rm.task_core.get("title", rm.roadmap_name or f"Core Task Week {rm.week}"),
                "goal": rm.task_core.get("goal", ""),
                "effort": rm.task_core.get("effort", 2),
                "status": rm.task_core.get("status", rm.status),
                "subtasks": rm.task_core.get("subtasks", []),
                "essay": rm.essay_core or "",
                "quiz": rm.quiz or None,
            }
            tasks.append(task)
        
        # Supplementary task
        if rm.task_supplementary:
            task = {
                "id": str(rm.id) + "_supp",
                "week": rm.week,
                "type": "supplementary",
                "title": rm.task_supplementary.get("title", f"Supplementary Task Week {rm.week}"),
                "goal": rm.task_supplementary.get("goal", ""),
                "effort": rm.task_supplementary.get("effort", 1),
                "status": rm.task_supplementary.get("status", "backlog"),
                "subtasks": rm.task_supplementary.get("subtasks", []),
                "essay": rm.essay_supplementary or "",
            }
            tasks.append(task)
    
    return tasks


# ── GET /check-context ───────────────────────────────────────
@router.get("/check-context")
async def check_context(username: str = Query(...), db: AsyncSession = Depends(get_db)):
    """Check if user has enough dialogue history for roadmap generation."""
    from app.models.chat_session import ChatSession
    
    user = await resolve_user(username, db)
    stmt = select(ChatSession).where(ChatSession.user_id == user.id)
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    
    prompt_count = 0
    for s in sessions:
        msgs = s.messages or []
        prompt_count += len([m for m in msgs if isinstance(m, dict) and m.get("role") == "user"])
    
    return {
        "prompt_count": prompt_count,
        "is_sufficient": prompt_count >= 10,
    }


# ── POST /join ───────────────────────────────────────────────
@router.post("/join")
async def join_cohort(data: dict, db: AsyncSession = Depends(get_db)):
    username = data.get("username", "")
    display_name = data.get("display_name", "")
    
    user = await resolve_user(username, db)
    
    # Check context
    from app.models.chat_session import ChatSession
    stmt = select(ChatSession).where(ChatSession.user_id == user.id)
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    prompt_count = sum(len([m for m in (s.messages or []) if isinstance(m, dict) and m.get("role") == "user"]) for s in sessions)
    
    if prompt_count < 10:
        return {"status": "insufficient_info", "message": "Not enough dialogue history."}
    
    # Check existing membership
    stmt = select(CohortMember).where(CohortMember.user_id == user.id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if not existing:
        member = CohortMember(
            user_id=user.id,
            display_name=display_name or username,
            is_self=True,
            week_progress={"current": 0},
        )
        db.add(member)
    
    # Create initial roadmap for week 1 if not exists
    stmt = select(PersonalRoadmap).where(
        and_(PersonalRoadmap.user_id == user.id, PersonalRoadmap.week == 1)
    )
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        roadmap = PersonalRoadmap(
            user_id=user.id,
            week=1,
            roadmap_name=DEFAULT_SYLLABUS[0]["title"],
            task_core={"title": "Khám phá khuôn mẫu tư duy cá nhân", "goal": "Viết ra 3 niềm tin cố hữu đang ảnh hưởng đến quyết định hàng ngày", "effort": 2, "status": "backlog"},
            task_supplementary={"title": "Nhật ký nhận thức", "goal": "Ghi lại những lúc bạn nhận ra bias trong tư duy", "effort": 1, "status": "backlog"},
            status="pending",
        )
        db.add(roadmap)
    
    await db.commit()
    return {"status": "success"}


# ── POST /personalize-week ───────────────────────────────────
@router.post("/personalize-week")
async def personalize_week(data: dict, db: AsyncSession = Depends(get_db)):
    username = data.get("username", "")
    week = data.get("week", 1)
    
    user = await resolve_user(username, db)
    
    # Check if roadmap already exists
    stmt = select(PersonalRoadmap).where(
        and_(PersonalRoadmap.user_id == user.id, PersonalRoadmap.week == week)
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        return {"status": "exists", "message": "Week already personalized"}
    
    # Create roadmap entry
    syllabus_entry = DEFAULT_SYLLABUS[week - 1] if week <= 12 else DEFAULT_SYLLABUS[-1]
    roadmap = PersonalRoadmap(
        user_id=user.id,
        week=week,
        roadmap_name=syllabus_entry["title"],
        task_core={
            "title": f"Thực hành: {syllabus_entry['title']}",
            "goal": syllabus_entry["description"],
            "effort": 2,
            "status": "backlog",
        },
        task_supplementary={
            "title": f"Bổ trợ: Chiêm nghiệm tuần {week}",
            "goal": f"Ghi lại những insight cá nhân trong quá trình học tuần {week}",
            "effort": 1,
            "status": "backlog",
        },
        status="pending",
    )
    db.add(roadmap)
    await db.commit()
    
    return {"status": "success"}


# ── PATCH /tasks/{task_id} ───────────────────────────────────
@router.patch("/tasks/{task_id}")
async def patch_task(task_id: str, data: dict, db: AsyncSession = Depends(get_db)):
    """Update task status, subtasks, or essay."""
    # task_id format: {roadmap_uuid}_{core|supp}
    parts = task_id.rsplit("_", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid task ID format")
    
    roadmap_id_str, task_type = parts
    try:
        roadmap_uuid = uuid.UUID(roadmap_id_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid roadmap ID")
    
    stmt = select(PersonalRoadmap).where(PersonalRoadmap.id == roadmap_uuid)
    result = await db.execute(stmt)
    roadmap = result.scalar_one_or_none()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    new_status = data.get("status")
    subtasks = data.get("subtasks")
    essay = data.get("essay")
    
    if task_type == "core":
        task_data = roadmap.task_core or {}
        if new_status: task_data["status"] = new_status
        if subtasks is not None: task_data["subtasks"] = subtasks
        roadmap.task_core = task_data
        if essay is not None: roadmap.essay_core = essay
        if new_status: roadmap.status = new_status
    elif task_type == "supp":
        task_data = roadmap.task_supplementary or {}
        if new_status: task_data["status"] = new_status
        if subtasks is not None: task_data["subtasks"] = subtasks
        roadmap.task_supplementary = task_data
        if essay is not None: roadmap.essay_supplementary = essay
    
    await db.commit()
    return {"status": "updated"}


# ── POST /update-progress ────────────────────────────────────
@router.post("/update-progress")
async def update_progress(data: dict, db: AsyncSession = Depends(get_db)):
    username = data.get("username", "")
    week_progress = data.get("week_progress", 0)
    
    user = await resolve_user(username, db)
    
    stmt = select(CohortMember).where(CohortMember.user_id == user.id)
    result = await db.execute(stmt)
    member = result.scalar_one_or_none()
    
    if member:
        member.week_progress = {"current": week_progress}
        await db.commit()
    
    return {"status": "updated"}


# ── POST /generate-quiz ──────────────────────────────────────
@router.post("/generate-quiz")
async def generate_quiz(data: dict, db: AsyncSession = Depends(get_db)):
    """Generate a Socratic quiz for the given week."""
    username = data.get("username", "")
    week = data.get("week", 1)
    lang = data.get("lang", "vi")
    
    user = await resolve_user(username, db)
    
    # Find roadmap for the week
    stmt = select(PersonalRoadmap).where(
        and_(PersonalRoadmap.user_id == user.id, PersonalRoadmap.week == week)
    )
    result = await db.execute(stmt)
    roadmap = result.scalar_one_or_none()
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found for this week")
    
    # Return existing quiz if available
    if roadmap.quiz and roadmap.quiz.get("questions"):
        return roadmap.quiz
    
    # Generate default quiz
    syllabus_entry = DEFAULT_SYLLABUS[week - 1] if week <= 12 else DEFAULT_SYLLABUS[-1]
    is_vi = lang == "vi"
    
    quiz = {
        "questions": [
            {
                "question": f"{'Khía cạnh nào' if is_vi else 'Which aspect'} {'của' if is_vi else 'of'} \"{syllabus_entry['title']}\" {'ảnh hưởng nhiều nhất đến bạn?' if is_vi else 'affects you the most?'}",
                "options": [
                    "Nhận thức cá nhân" if is_vi else "Personal awareness",
                    "Hành vi hàng ngày" if is_vi else "Daily behavior",
                    "Mối quan hệ xã hội" if is_vi else "Social relationships",
                    "Quyết định nghề nghiệp" if is_vi else "Career decisions",
                ],
            },
        ],
        "attempts": [],
    }
    
    roadmap.quiz = quiz
    await db.commit()
    
    return quiz


# ── POST /submit-quiz ────────────────────────────────────────
@router.post("/submit-quiz")
async def submit_quiz(data: dict, db: AsyncSession = Depends(get_db)):
    username = data.get("username", "")
    week = data.get("week", 1)
    answers = data.get("answers", [])
    
    user = await resolve_user(username, db)
    
    stmt = select(PersonalRoadmap).where(
        and_(PersonalRoadmap.user_id == user.id, PersonalRoadmap.week == week)
    )
    result = await db.execute(stmt)
    roadmap = result.scalar_one_or_none()
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    # Calculate score (simple scoring for now)
    total_score = min(len([a for a in answers if a is not None]) * 12.5, 100)
    
    attempt = {
        "answers": answers,
        "total_score": total_score,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    quiz = roadmap.quiz or {"questions": [], "attempts": []}
    if "attempts" not in quiz:
        quiz["attempts"] = []
    quiz["attempts"].append(attempt)
    roadmap.quiz = quiz
    roadmap.week_progress = total_score
    
    await db.commit()
    
    return {"attempt": attempt}


# ── POST /ai-retrospective ───────────────────────────────────
@router.post("/ai-retrospective")
async def ai_retrospective(data: dict):
    lang = data.get("lang", "vi")
    progress = data.get("progress", 0)
    
    return {
        "retrospective": (
            f"Bạn đã hoàn thành {progress}% tuần này. Hãy tiếp tục chiêm nghiệm sâu hơn."
            if lang == "vi"
            else f"You completed {progress}% this week. Keep reflecting deeper."
        ),
        "avg_progress": progress,
    }
