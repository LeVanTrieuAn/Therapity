"""
Therapity — AOA (Ask of Anything) Social Feed Models
Posts, Comments, Likes, and Actions (save/hide/delete tracking).
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AOAPost(Base):
    __tablename__ = "aoa_posts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True, default="")
    graph_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    shares_count: Mapped[int] = mapped_column(Integer, default=0)
    privacy: Mapped[str] = mapped_column(String(50), default="public")
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, hidden, deleted
    report: Mapped[str | None] = mapped_column(Text, nullable=True)
    repost_of_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("aoa_posts.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    author = relationship("User", back_populates="aoa_posts")
    comments = relationship("AOAComment", back_populates="post", cascade="all, delete-orphan", order_by="AOAComment.created_at")
    likes = relationship("AOALike", back_populates="post", cascade="all, delete-orphan")
    actions = relationship("AOAAction", back_populates="post", cascade="all, delete-orphan")
    original_post = relationship("AOAPost", remote_side="AOAPost.id", foreign_keys=[repost_of_id])

    def __repr__(self):
        return f"<AOAPost {self.id} by user={self.author_id}>"


class AOAComment(Base):
    __tablename__ = "aoa_comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("aoa_posts.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    post = relationship("AOAPost", back_populates="comments")
    author = relationship("User")

    def __repr__(self):
        return f"<AOAComment {self.id} on post={self.post_id}>"


class AOALike(Base):
    __tablename__ = "aoa_likes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("aoa_posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    post = relationship("AOAPost", back_populates="likes")
    user = relationship("User")

    def __repr__(self):
        return f"<AOALike user={self.user_id} post={self.post_id}>"


class AOAAction(Base):
    __tablename__ = "aoa_actions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("aoa_posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)  # saved, hidden, deleted
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    post = relationship("AOAPost", back_populates="actions")
    user = relationship("User")

    def __repr__(self):
        return f"<AOAAction {self.action_type} user={self.user_id} post={self.post_id}>"
