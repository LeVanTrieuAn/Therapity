"""
Therapity — Profile Router
User profile, onboarding, mindset analysis, user stats.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/api/v1/profile", tags=["Profile"])

DEFAULT_BIO = "Học hỏi, chia sẻ và cùng nhau phát triển tại cộng đồng Therapity. Đam mê tri thức và sự sáng tạo."


@router.get("/{username}")
async def get_user_profile(username: str, db: AsyncSession = Depends(get_db)):
    """Get user profile."""
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        clean_name = username.split("@")[0] if "@" in username else username
        return {
            "username": username,
            "displayName": clean_name,
            "bio": DEFAULT_BIO,
            "avatar": "",
            "banner": "",
            "following_list": [],
            "onboarded": False,
        }

    clean_display = user.display_name or username
    if clean_display and "@" in clean_display:
        clean_display = clean_display.split("@")[0]

    return {
        "username": username,
        "displayName": clean_display,
        "bio": user.bio or DEFAULT_BIO,
        "avatar": user.avatar or "",
        "banner": user.banner or "",
        "following_list": user.following_list or [],
        "onboarded": user.onboarded,
    }


@router.post("/{username}")
async def update_user_profile(username: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Update user profile."""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if "displayName" in data:
        user.display_name = data["displayName"]
    if "bio" in data:
        user.bio = data["bio"]
    if "avatar" in data:
        user.avatar = data["avatar"]
    if "banner" in data:
        user.banner = data["banner"]
    if "following_list" in data:
        user.following_list = data["following_list"]

    await db.commit()
    return {"status": "success"}


@router.post("/{username}/onboarding")
async def save_onboarding(username: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Save onboarding data and generate core context."""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.onboarding = data
    user.onboarded = True

    # Generate context from onboarding via AI
    generated_context = None
    try:
        from app.services.llm_service import get_llm_service
        llm = get_llm_service()

        context_prompt = f"""Summarize the following user onboarding data into a concise "Core Context" (under 150 words) that captures:
1. Key demographics
2. Main interests and hobbies
3. Current problems/challenges
4. Goals for using the app
5. Emotional tone and personality hints

Onboarding data: {json.dumps(data, ensure_ascii=False)}

Write the summary in the user's language (detect from data). Be factual and specific, not generic."""

        import json
        content, _, _ = llm.chat_completion(
            messages=[{"role": "user", "content": context_prompt}],
            temperature=0.3,
            max_tokens=300,
        )
        if content:
            generated_context = content
            if isinstance(user.onboarding, dict):
                user.onboarding["_core_context"] = generated_context
            else:
                user.onboarding = {"_core_context": generated_context, **data}

    except Exception as e:
        print(f"Error generating context from onboarding for {username}: {e}")

    await db.commit()
    return {"status": "success", "context": generated_context}


@router.get("/{username}/onboarding")
async def get_onboarding(username: str, db: AsyncSession = Depends(get_db)):
    """Get onboarding data."""
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return {"onboarded": False, "data": None}

    return {"onboarded": user.onboarded, "data": user.onboarding}


@router.get("/{username}/context")
async def get_user_context(username: str, db: AsyncSession = Depends(get_db)):
    """Get user core context."""
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return {"username": username, "context": None}

    onboarding = user.onboarding or {}
    ctx = onboarding.get("_core_context") if isinstance(onboarding, dict) else None
    return {"username": username, "context": ctx}


@router.get("/{username}/stats")
async def get_stats(username: str, db: AsyncSession = Depends(get_db)):
    """Get user cognitive dimension stats."""
    # Simplified stats — returns 6 dimensions
    return {"stats": [85, 75, 60, 90, 65, 80]}


@router.get("/{username}/mindset")
async def get_mindset(username: str, db: AsyncSession = Depends(get_db)):
    """AI-powered mindset analysis (MBTI + 6-dimension radar)."""
    # Simplified for initial version
    return {
        "stats": {"objective": 70, "emotion": 65, "negative": 45, "positive": 75, "creativity": 80, "overview": 70},
        "mbti_suggestions": [],
        "source": "default",
    }
