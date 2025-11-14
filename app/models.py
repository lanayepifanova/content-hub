"""SQLAlchemy models for the ContentHub calendar."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp for default columns."""
    return datetime.now(timezone.utc)


class Idea(Base):
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    target_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    brief = relationship(
        "IdeaBrief",
        back_populates="idea",
        uselist=False,
        cascade="all, delete-orphan",
    )
    brief_versions = relationship(
        "IdeaBriefVersion",
        back_populates="idea",
        cascade="all, delete-orphan",
        order_by="IdeaBriefVersion.created_at.desc()",
    )


class IdeaBrief(Base):
    __tablename__ = "idea_briefs"

    id = Column(Integer, primary_key=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"), nullable=False, unique=True, index=True)
    content = Column(Text, nullable=False, default="{}")
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    idea = relationship("Idea", back_populates="brief")


class IdeaBriefVersion(Base):
    __tablename__ = "idea_brief_versions"

    id = Column(Integer, primary_key=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"), nullable=False, index=True)
    snapshot = Column(Text, nullable=False)
    label = Column(String(120), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    idea = relationship("Idea", back_populates="brief_versions")


class IdeaTemplate(Base):
    __tablename__ = "idea_templates"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    body = Column(Text, nullable=False)
    category = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    favorite = Column(Boolean, default=False, nullable=False)
    rating_sum = Column(Integer, default=0, nullable=False)
    rating_count = Column(Integer, default=0, nullable=False)
