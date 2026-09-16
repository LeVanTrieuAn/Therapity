"""
Therapity — User Model
Stores user accounts, profiles, onboarding data, and settings.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True, default="")
    avatar: Mapped[str | None] = mapped_column(Text, nullable=True, default="")
    banner: Mapped[str | None] = mapped_column(Text, nullable=True, default="")
    following_list: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=list)
    onboarding: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)
    onboarded: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    diary_entries = relationship("DiaryEntry", back_populates="user", cascade="all, delete-orphan")
    diary_folders = relationship("DiaryFolder", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    aoa_posts = relationship("AOAPost", back_populates="author", cascade="all, delete-orphan")
    cohort_memberships = relationship("CohortMember", back_populates="user", cascade="all, delete-orphan")
    personal_roadmaps = relationship("PersonalRoadmap", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"
