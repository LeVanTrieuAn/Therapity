"""
Therapity — Diary Models
DiaryEntry: individual notes/reflections with AI insights.
DiaryFolder: organizational folders for diary entries.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class DiaryEntry(Base):
    __tablename__ = "diary_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    content: Mapped[str | None] = mapped_column(Text, nullable=True, default="")
    ai_insight: Mapped[str | None] = mapped_column(Text, nullable=True, default="")
    mood: Mapped[str | None] = mapped_column(String(50), nullable=True, default="Calm")
    folder: Mapped[str | None] = mapped_column(String(255), nullable=True, default="")
    date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="diary_entries")

    def __repr__(self):
        return f"<DiaryEntry {self.title}>"


class DiaryFolder(Base):
    __tablename__ = "diary_folders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="diary_folders")

    def __repr__(self):
        return f"<DiaryFolder {self.name}>"
