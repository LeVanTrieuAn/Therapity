"""
Therapity — AOA (Ask of Anything) Social Feed Router
Posts, comments, likes, trending.
"""

import uuid
import datetime
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.aoa import AOAPost, AOAComment, AOALike, AOAAction
from app.schemas.schemas import PostRequest, CommentRequest, RepostRequest, UpdatePostRequest, ReportPostRequest
from app.services.llm_service import get_llm_service

router = APIRouter(prefix="/api/v1/aoa", tags=["AOA Social Feed"])


@router.get("/posts")
async def get_aoa_posts(db: AsyncSession = Depends(get_db)):
    """Get all active public posts."""
    stmt = (
        select(AOAPost)
        .where(AOAPost.status == "active")
        .order_by(AOAPost.created_at.desc())
    )
    result = await db.execute(stmt)
    posts = result.scalars().all()

    output = []
    for p in posts:
        # Get author info
        author_stmt = select(User).where(User.id == p.author_id)
        author_result = await db.execute(author_stmt)
        author = author_result.scalar_one_or_none()

        # Get comments
        comment_stmt = select(AOAComment).where(AOAComment.post_id == p.id).order_by(AOAComment.created_at)
        comment_result = await db.execute(comment_stmt)
        comments = comment_result.scalars().all()

        comment_list = []
        for c in comments:
            c_author_stmt = select(User).where(User.id == c.author_id)
            c_author_result = await db.execute(c_author_stmt)
            c_author = c_author_result.scalar_one_or_none()
            comment_list.append({
                "id": str(c.id),
                "author_name": c_author.username if c_author else "unknown",
                "author_displayName": c_author.display_name if c_author else "",
                "author_avatar": c_author.avatar if c_author else "",
                "content": c.content,
                "timestamp": c.created_at.strftime("%H:%M %d/%m/%Y") if c.created_at else "",
            })

        output.append({
            "id": str(p.id),
            "author_name": author.username if author else "unknown",
            "author_avatar": author.avatar if author else "",
            "author_displayName": author.display_name if author else "",
            "content": p.content or "",
            "graph_data": p.graph_data or {},
            "timestamp": p.created_at.strftime("%H:%M %d/%m/%Y") if p.created_at else "",
            "likes": p.likes_count,
            "comments": comment_list,
            "shares": p.shares_count,
            "post_privacy": p.privacy,
            "post_status": p.status,
        })

    return {"posts": output}


@router.post("/posts")
async def create_post(req: PostRequest, db: AsyncSession = Depends(get_db)):
    """Create a new AOA post."""
    stmt = select(User).where(User.username == req.author_name)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    post = AOAPost(
        author_id=user.id,
        content=req.content,
        graph_data=req.graph_data or {},
        privacy=req.post_privacy or "public",
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)

    return {
        "status": "success",
        "post": {
            "id": str(post.id),
            "content": post.content,
            "timestamp": post.created_at.strftime("%H:%M %d/%m/%Y"),
        },
    }


@router.post("/posts/{post_id}/comments")
async def add_comment(post_id: str, req: CommentRequest, db: AsyncSession = Depends(get_db)):
    """Add a comment to a post."""
    try:
        pid = uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid post ID")

    stmt = select(User).where(User.username == req.author_name)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    comment = AOAComment(
        post_id=pid,
        author_id=user.id,
        content=req.content,
    )
    db.add(comment)
    await db.commit()

    return {"status": "success"}


@router.post("/posts/{post_id}/like")
async def toggle_like(post_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Toggle like on a post."""
    try:
        pid = uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid post ID")

    data = await request.json()
    username = data.get("username")

    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if already liked
    stmt = select(AOALike).where(AOALike.post_id == pid, AOALike.user_id == user.id)
    result = await db.execute(stmt)
    existing_like = result.scalar_one_or_none()

    post_stmt = select(AOAPost).where(AOAPost.id == pid)
    post_result = await db.execute(post_stmt)
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if existing_like:
        await db.delete(existing_like)
        post.likes_count = max(0, post.likes_count - 1)
        liked = False
    else:
        like = AOALike(post_id=pid, user_id=user.id)
        db.add(like)
        post.likes_count += 1
        liked = True

    await db.commit()
    return {"status": "success", "liked": liked, "likes": post.likes_count}


@router.post("/posts/{post_id}/action")
async def post_action(post_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Perform an action on a post (hide/delete/save/restore)."""
    try:
        pid = uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid post ID")

    data = await request.json()
    action = data.get("action")
    username = data.get("username")

    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    post_stmt = select(AOAPost).where(AOAPost.id == pid)
    post_result = await db.execute(post_stmt)
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if action in ("hide", "delete"):
        post.status = "hidden" if action == "hide" else "deleted"
    elif action == "restore":
        post.status = "active"
    elif action in ("save", "unsave"):
        # Toggle save action
        stmt = select(AOAAction).where(AOAAction.post_id == pid, AOAAction.user_id == user.id, AOAAction.action_type == "saved")
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if action == "save" and not existing:
            db.add(AOAAction(post_id=pid, user_id=user.id, action_type="saved"))
        elif action == "unsave" and existing:
            await db.delete(existing)

    await db.commit()
    return {"status": "success"}


@router.put("/posts/{post_id}")
async def update_post(post_id: str, req: UpdatePostRequest, db: AsyncSession = Depends(get_db)):
    """Update post content."""
    try:
        pid = uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid post ID")

    stmt = select(AOAPost).where(AOAPost.id == pid)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.content = req.content
    await db.commit()
    return {"status": "success"}


@router.post("/posts/{post_id}/report")
async def report_post(post_id: str, req: ReportPostRequest, db: AsyncSession = Depends(get_db)):
    """Report a post."""
    try:
        pid = uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid post ID")

    stmt = select(AOAPost).where(AOAPost.id == pid)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.report = f"{req.category}: {req.details} (by {req.username})"
    await db.commit()
    return {"status": "success"}


@router.post("/trending")
async def get_trending(request: Request):
    """AI-powered trending analysis."""
    llm = get_llm_service()
    prompt = """Bạn là AI phân tích xu hướng của cộng đồng Therapity.
Dựa trên các bài đăng gần đây, hãy tạo báo cáo xu hướng ngắn gọn với:
1. Top 5 hashtags phổ biến
2. Chủ đề đang được quan tâm nhất
3. Tóm tắt tâm lý chung của cộng đồng

Trả về JSON:
{
    "hashtags": ["#tag1", "#tag2"],
    "trending_topic": "Chủ đề nổi bật",
    "community_summary": "Tóm tắt ngắn"
}"""

    json_result, _, _ = llm.chat_completion_json(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=500,
    )

    if json_result:
        return json_result

    return {
        "hashtags": ["#Therapity", "#Mindset", "#Growth"],
        "trending_topic": "Phát triển bản thân",
        "community_summary": "Cộng đồng đang tập trung vào việc xây dựng thói quen tích cực.",
    }
