"""SQLAlchemy models for the ContentHub calendar."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text

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
