"""
Therapity — Auth Router
Login, Register (no OTP), Forgot Password (no email).
"""

import re
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.schemas.schemas import LoginRequest, RegisterRequest, ForgotPasswordResetRequest
from app.services.auth_service import (
    hash_password, verify_password, create_access_token, create_refresh_token
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

DEFAULT_BIO = "Học hỏi, chia sẻ và cùng nhau phát triển tại cộng đồng Therapity. Đam mê tri thức và sự sáng tạo."


def _validate_password(password: str):
    """Validate password strength."""
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Mật khẩu phải có ít nhất 6 ký tự.")
    if not re.search(r'[a-zA-Z]', password) or not re.search(r'\d', password):
        raise HTTPException(status_code=400, detail="Mật khẩu phải bao gồm cả chữ và số.")


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT tokens."""
    stmt = select(User).where(
        (User.username == req.username) | (User.email == req.username)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Sai thông tin đăng nhập")

    if not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Sai thông tin đăng nhập")

    token_data = {"sub": str(user.id), "username": user.username}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "status": "success",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "username": user.username,
        "displayName": user.display_name or user.username,
        "avatar": user.avatar or "",
        "banner": user.banner or "",
        "bio": user.bio or DEFAULT_BIO,
        "following_list": user.following_list or [],
        "onboarded": user.onboarded,
    }


@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register new user directly (no OTP required)."""
    _validate_password(req.password)

    # Check if user already exists
    stmt = select(User).where((User.email == req.email) | (User.username == req.email))
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Tài khoản đã tồn tại")

    # Create user with hashed password
    username = req.username or req.email
    user = User(
        username=username,
        email=req.email,
        password_hash=hash_password(req.password),
        display_name=req.full_name or username,
        bio=DEFAULT_BIO,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token_data = {"sub": str(user.id), "username": user.username}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "status": "success",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "username": user.username,
        "displayName": user.display_name or user.username,
        "avatar": "",
        "banner": "",
        "bio": DEFAULT_BIO,
        "following_list": [],
        "onboarded": False,
    }


@router.post("/forgot-password/reset")
async def forgot_password_reset(req: ForgotPasswordResetRequest, db: AsyncSession = Depends(get_db)):
    """Reset password (admin/direct reset — no OTP email)."""
    _validate_password(req.new_password)

    stmt = select(User).where(User.email == req.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")

    user.password_hash = hash_password(req.new_password)
    await db.commit()

    return {"status": "success", "message": "Mật khẩu đã được đặt lại thành công"}
