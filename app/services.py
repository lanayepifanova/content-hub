"""Domain services shared by routers."""

from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Idea


def fetch_idea(db: Session, idea_id: int) -> Idea:
    """Return an idea or raise a 404."""
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found",
        )
    return idea


def toggle_completion(idea: Idea) -> None:
    """Flip the completion flag and timestamp."""
    idea.completed = not idea.completed
    idea.completed_at = datetime.now(timezone.utc) if idea.completed else None


def ideas_in_range(db: Session, start: date, end: date) -> list[Idea]:
    """Fetch ideas within the inclusive date range ordered for deterministic views."""
    return (
        db.query(Idea)
        .filter(Idea.target_date >= start, Idea.target_date <= end)
        .order_by(Idea.target_date.asc(), Idea.created_at.asc())
        .all()
    )
