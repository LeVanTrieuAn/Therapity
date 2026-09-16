"""
Therapity — Diary Router
CRUD for diary entries + AI clinical notes generation.
"""

import json
import re
import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.diary import DiaryEntry, DiaryFolder
from app.schemas.schemas import DiaryEntryRequest, GenerateDiaryRequest, FolderRequest
from app.services.llm_service import get_llm_service

router = APIRouter(prefix="/api/v1/diary", tags=["Diary"])


@router.get("/{username}")
async def get_diaries(username: str, db: AsyncSession = Depends(get_db)):
    """Get all diary entries for a user."""
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return []

    stmt = select(DiaryEntry).where(DiaryEntry.user_id == user.id).order_by(DiaryEntry.created_at.desc())
    result = await db.execute(stmt)
    entries = result.scalars().all()

    return [
        {
            "id": str(e.id),
            "title": e.title,
            "content": e.content or "",
            "ai_insight": e.ai_insight or "",
            "mood": e.mood or "Calm",
            "folder": e.folder or "",
            "date": e.date or e.created_at.isoformat(),
        }
        for e in entries
    ]


@router.post("/{username}")
async def create_diary(username: str, req: DiaryEntryRequest, db: AsyncSession = Depends(get_db)):
    """Create or update a diary entry with AI Socratic insight."""
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate AI insight
    ai_insight = "AI Socratic Coach đang chờ suy ngẫm từ bài viết của bạn. Hãy viết nội dung và nhấn 'Lưu & Khám phá AI' để soi chiếu bản thân."

    if not req.skip_ai and req.content.strip():
        ai_prompt = f"""Bạn là AI Socratic Coach của hệ thống Therapity.
        Người dùng '{username}' vừa viết nhật ký tự sự (Diary/Self-Reflection) với tâm trạng '{req.mood}':
        Tiêu đề: {req.title}
        Nội dung: {req.content}
        
        Hãy đưa ra 1 lời phản hồi ngắn gọn dưới 80 từ theo phương pháp Socratic. Thay vì đưa ra lời khuyên sáo rỗng, hãy đặt 1 câu hỏi sâu sắc để giúp người dùng tự phản tỉnh và nhìn thấu bản chất vấn đề. Viết bằng tiếng Việt cực kỳ ấm áp và trí tuệ."""

        llm = get_llm_service()
        content, _, _ = llm.chat_completion(
            messages=[{"role": "user", "content": ai_prompt}],
            temperature=0.4,
            max_tokens=200,
        )
        if content:
            ai_insight = content

    # Update existing or create new
    entry = None
    if req.id:
        try:
            import uuid
            eid = uuid.UUID(req.id)
            stmt = select(DiaryEntry).where(DiaryEntry.id == eid, DiaryEntry.user_id == user.id)
            result = await db.execute(stmt)
            entry = result.scalar_one_or_none()
        except (ValueError, Exception):
            pass

    date_val = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if entry:
        entry.title = req.title
        entry.content = req.content
        entry.folder = req.folder or ""
        if not req.skip_ai:
            entry.ai_insight = ai_insight
        entry.date = date_val
    else:
        entry = DiaryEntry(
            user_id=user.id,
            title=req.title,
            content=req.content,
            ai_insight=ai_insight,
            mood=req.mood or "Calm",
            folder=req.folder or "",
            date=date_val,
        )
        db.add(entry)

    await db.commit()
    await db.refresh(entry)

    return {
        "status": "success",
        "entry": {
            "id": str(entry.id),
            "title": entry.title,
            "content": entry.content,
            "ai_insight": entry.ai_insight,
            "mood": entry.mood,
            "folder": entry.folder,
            "date": entry.date,
        },
    }


@router.delete("/{username}/{entry_id}")
async def delete_diary(username: str, entry_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a diary entry."""
    try:
        import uuid
        eid = uuid.UUID(entry_id)
        stmt = select(DiaryEntry).where(DiaryEntry.id == eid)
        result = await db.execute(stmt)
        entry = result.scalar_one_or_none()
        if entry:
            await db.delete(entry)
            await db.commit()
            return {"status": "success"}
    except Exception:
        pass
    raise HTTPException(status_code=404, detail="Diary entry not found")


@router.get("/{username}/folders")
async def get_diary_folders(username: str, db: AsyncSession = Depends(get_db)):
    """Get all diary folders for a user."""
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return []

    stmt = select(DiaryFolder).where(DiaryFolder.user_id == user.id).order_by(DiaryFolder.created_at)
    result = await db.execute(stmt)
    folders = result.scalars().all()
    return [f.name for f in folders]


@router.post("/{username}/folders")
async def add_diary_folder(username: str, req: FolderRequest, db: AsyncSession = Depends(get_db)):
    """Create a new diary folder."""
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check duplicate
    stmt = select(DiaryFolder).where(DiaryFolder.user_id == user.id, DiaryFolder.name == req.name.strip())
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        return {"status": "exists", "folders": await _get_folder_names(user.id, db)}

    folder = DiaryFolder(user_id=user.id, name=req.name.strip())
    db.add(folder)
    await db.commit()

    return {"status": "success", "folders": await _get_folder_names(user.id, db)}


@router.delete("/{username}/folders/{folder_name}")
async def delete_diary_folder(username: str, folder_name: str, db: AsyncSession = Depends(get_db)):
    """Delete a diary folder and all its entries."""
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete entries in folder
    decoded_name = folder_name.replace("%20", " ")
    stmt = select(DiaryEntry).where(DiaryEntry.user_id == user.id, DiaryEntry.folder == decoded_name)
    result = await db.execute(stmt)
    for entry in result.scalars():
        await db.delete(entry)

    # Delete folder
    stmt = select(DiaryFolder).where(DiaryFolder.user_id == user.id, DiaryFolder.name == decoded_name)
    result = await db.execute(stmt)
    folder = result.scalar_one_or_none()
    if folder:
        await db.delete(folder)

    await db.commit()
    return {"status": "success"}


@router.post("/generate")
async def api_generate_diary(req: GenerateDiaryRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """Trigger AI clinical diary summary generation in background."""
    # Get the chat session
    stmt = select(User).where(User.username == req.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        import uuid
        sid = uuid.UUID(req.session_id)
        from app.models.chat_session import ChatSession
        stmt = select(ChatSession).where(ChatSession.id == sid, ChatSession.user_id == user.id)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
    except Exception:
        session = None

    if not session:
        return {"error": "Session not found"}

    history = session.chat_history or []
    session_title = session.custom_title or "Phiên Coach"

    # Run in background
    background_tasks.add_task(
        _generate_clinical_diary, req.username, str(user.id), session_title, history, req.model
    )
    return {"status": "success", "message": "Diary generation started"}


async def _get_folder_names(user_id, db: AsyncSession) -> list:
    stmt = select(DiaryFolder).where(DiaryFolder.user_id == user_id)
    result = await db.execute(stmt)
    return [f.name for f in result.scalars()]


def _generate_clinical_diary(username: str, user_id: str, session_title: str, history: list, req_model: str = None):
    """Background task: AI generates clinical diary notes from chat history."""
    try:
        folder_name = session_title.strip() if session_title.strip() else "Phiên Coach"
        recent_history = history[-6:] if len(history) >= 6 else history

        history_text = ""
        for m in recent_history:
            role = "Thân chủ (Người dùng)" if m.get("role") == "user" else "Nhà tâm lý học (AI)"
            history_text += f"{role}: {m.get('content', '')}\n\n"

        system_prompt = f"""Bạn là một chuyên gia tâm lý học lâm sàng với hơn 10 năm kinh nghiệm thuộc hệ thống Therapity.
Nhiệm vụ của bạn là đọc kỹ bản ghi chép cuộc hội thoại gần đây giữa bạn và thân chủ.
Sau đó, hãy viết một bản ghi chú lâm sàng (clinical notes) cực kỳ chi tiết, sâu sắc.

Yêu cầu về hình thức và định dạng (Markdown):
- Trình bày đa dạng, linh hoạt, trực quan sinh động như một tài liệu nghiên cứu.
- BẮT BUỘC sử dụng phong phú các định dạng Markdown chuẩn: Heading (H1-H6 bằng dấu #), in đậm (**Bold**), in nghiêng (*Italic*).
- TUYỆT ĐỐI KHÔNG sử dụng thẻ HTML. Hãy chỉ dùng Markdown thuần túy.
- Sử dụng đa dạng danh sách đánh số (1. 2. 3.), danh sách không đánh số (-), và checklist (- [ ] / - [x]).
- ĐẶC BIỆT QUAN TRỌNG: Bắt buộc phải vận dụng sự liên kết giữa các khái niệm thông qua cú pháp Wikilink (ví dụ: [[Cơ chế phòng vệ]], [[Áp lực đồng trang lứa]], [[Sợ thất bại]]).

Yêu cầu nội dung:
- Phát hiện các ngụy biện logic, điểm nghẽn nhận thức, cơ chế phòng vệ tâm lý.
- Đưa ra giả thuyết lâm sàng về niềm tin cốt lõi đang chi phối họ.

Đầu ra bắt buộc phải là một JSON hợp lệ:
{{
    "operations": [
        {{
            "action": "create",
            "title": "Chẩn đoán ngắn",
            "summary": "Nội dung (Markdown phong phú)",
            "evaluation": "Đánh giá chuyên sâu (dành riêng cho Gương phản tỉnh)"
        }}
    ]
}}
"""
        llm = get_llm_service()
        json_result, _, _ = llm.chat_completion_json(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": history_text},
            ],
            temperature=0.3,
            max_tokens=2500,
        )

        if json_result:
            operations = json_result.get("operations", [])
            if not operations and isinstance(json_result, dict) and "title" in json_result:
                operations = [{"action": "create", "title": json_result.get("title", "Ghi chép"), "summary": json_result.get("summary", ""), "evaluation": json_result.get("evaluation", "")}]

            # Save diary entries synchronously using a new sync session
            from sqlalchemy import create_engine
            from sqlalchemy.orm import Session as SyncSession
            from app.config import get_settings
            import uuid

            settings = get_settings()
            sync_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
            sync_engine = create_engine(sync_url)

            with SyncSession(sync_engine) as sync_db:
                for op in operations:
                    if not isinstance(op, dict):
                        continue
                    entry = DiaryEntry(
                        user_id=uuid.UUID(user_id),
                        title=op.get("title", "Ghi chép lâm sàng"),
                        content=op.get("summary", ""),
                        ai_insight=op.get("evaluation", ""),
                        folder=folder_name,
                        date=datetime.datetime.now().isoformat() + "Z",
                    )
                    sync_db.add(entry)
                sync_db.commit()

            print(f"✅ Clinical diary generated for {username}: {len(operations)} entries")

    except Exception as e:
        import traceback
        print(f"❌ Error generating clinical diary: {e}")
        traceback.print_exc()
