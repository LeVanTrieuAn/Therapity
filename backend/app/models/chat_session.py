"""
Therapity — Chat Session Model
Stores AI Socratic Coach conversations, mindmap data, and session metadata.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    custom_title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    chat_history: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=list)
    graph_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)
    tasks: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=list)
    suggested_replies: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=list)
    token_used: Mapped[int] = mapped_column(Integer, default=0)
    model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)
    has_new_task: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="chat_sessions")

    def __repr__(self):
        return f"<ChatSession {self.id} user={self.user_id}>"
