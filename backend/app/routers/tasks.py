"""
Therapity — Tasks Router
CRUD for PDCA tasks with AI-generated microsteps.
"""

import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.database import get_db
from app.models.user import User
from app.models.task import Task
from app.schemas.schemas import TaskCreateRequest, TaskUpdateRequest, MicrostepsRequest
from app.services.llm_service import get_llm_service

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


@router.get("/{username}")
async def get_tasks(username: str, db: AsyncSession = Depends(get_db)):
    """Get all tasks for a user."""
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return []

    stmt = select(Task).where(Task.user_id == user.id).order_by(Task.created_at.desc())
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    return [
        {
            "id": str(t.id),
            "title": t.title,
            "goal": t.goal or "",
            "status": t.status,
            "deadline": t.deadline or "",
            "effort": t.effort,
            "subtasks": t.subtasks or [],
            "context_link": t.context_link or "",
            "feedback": t.feedback or "",
            "source": t.source or "manual",
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in tasks
    ]


@router.post("/{username}")
async def create_task(username: str, req: TaskCreateRequest, db: AsyncSession = Depends(get_db)):
    """Create a new task."""
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    task = Task(
        user_id=user.id,
        title=req.title,
        goal=req.goal or "",
        status=req.status or "backlog",
        deadline=req.deadline or "",
        effort=req.effort or 1,
        subtasks=req.subtasks or [],
        context_link=req.context_link or "",
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    return {"status": "success", "task": {"id": str(task.id), "title": task.title}}


@router.put("/{username}/{task_id}")
async def update_task(username: str, task_id: str, req: TaskUpdateRequest, db: AsyncSession = Depends(get_db)):
    """Update an existing task."""
    try:
        tid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID")

    stmt = select(Task).where(Task.id == tid)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = req.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(task, field, value)

    await db.commit()
    return {"status": "success"}


@router.delete("/{username}/{task_id}")
async def delete_task(username: str, task_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a task."""
    try:
        tid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID")

    stmt = select(Task).where(Task.id == tid)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(task)
    await db.commit()
    return {"status": "success"}


@router.post("/microsteps")
async def generate_microsteps(req: MicrostepsRequest):
    """AI generates Pomodoro-style micro-steps for a task."""
    is_en = req.lang == "en"
    prompt = f"""Bạn là một AI thuộc hệ thống Therapity, chuyên gia chia nhỏ nhiệm vụ theo phương pháp Pomodoro.
Nhiệm vụ: "{req.title}"
Mục tiêu: "{req.goal}"
Mức độ nỗ lực (1-5): {req.effort}

Hãy chia thành 2-5 bước nhỏ, mỗi bước kéo dài khoảng 25 phút (1 Pomodoro).
Mỗi bước phải cụ thể, rõ ràng, khả thi ngay lập tức.

Trả về đúng 1 JSON hợp lệ:
{{
    "subtasks": [
        {{"title": "Bước 1: ...", "done": false}},
        {{"title": "Bước 2: ...", "done": false}}
    ]
}}

{'Write in English.' if is_en else 'Viết bằng tiếng Việt.'}
"""

    llm = get_llm_service()
    json_result, _, _ = llm.chat_completion_json(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1000,
    )

    if json_result and "subtasks" in json_result:
        return json_result

    # Fallback
    return {
        "subtasks": [
            {"title": "Bước 1: Nghiên cứu và hiểu rõ nhiệm vụ" if not is_en else "Step 1: Research and understand the task", "done": False},
            {"title": "Bước 2: Thực hiện phần cốt lõi" if not is_en else "Step 2: Execute the core part", "done": False},
            {"title": "Bước 3: Kiểm tra và hoàn thiện" if not is_en else "Step 3: Review and finalize", "done": False},
        ]
    }
