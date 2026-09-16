"""
Therapity — Cohort Learning Models
CohortMember: user enrollment in learning cohorts.
PersonalRoadmap: per-week learning path with tasks, quiz, and essay.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, Boolean, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class CohortMember(Base):
    __tablename__ = "cohort_members"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    cohort_id: Mapped[str] = mapped_column(String(100), nullable=False, default="cohort_04")
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    week_progress: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)
    buddy: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_self: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="cohort_memberships")

    def __repr__(self):
        return f"<CohortMember {self.user_id} in {self.cohort_id}>"


class PersonalRoadmap(Base):
    __tablename__ = "personal_roadmaps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    roadmap_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    task_core: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)
    task_supplementary: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)
    quiz: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)
    graph_data_roadmap: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)
    essay_core: Mapped[str | None] = mapped_column(Text, nullable=True)
    essay_supplementary: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_test: Mapped[str | None] = mapped_column(Text, nullable=True)
    test_flag: Mapped[str | None] = mapped_column(String(50), nullable=True)
    week_progress: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="personal_roadmaps")

    def __repr__(self):
        return f"<PersonalRoadmap user={self.user_id} week={self.week}>"
