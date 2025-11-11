"""SQLAlchemy models for the minimal ContentHub restart."""

from __future__ import annotations

from enum import Enum
from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, Enum as SqlEnum, Integer, String, Text

from database import Base


class Idea(Base):
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        SqlEnum("backlog", "drafting", "scheduled", "published", name="idea_status"),
        default="backlog",
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    target_date = Column(Date, nullable=True)


class IdeaStatus(str, Enum):
    BACKLOG = "backlog"
    DRAFTING = "drafting"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
