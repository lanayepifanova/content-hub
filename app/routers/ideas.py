"""JSON API endpoints used by the calendar UI."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.lib.calendar import month_context
from app.models import Idea
from app.schemas import IdeaCreate, IdeaRead, IdeaUpdate
from app.services import fetch_idea, ideas_in_range, toggle_completion


def _to_read_model(idea: Idea) -> IdeaRead:
    return IdeaRead.model_validate(idea)

router = APIRouter(prefix="/api", tags=["Ideas"])


@router.post("/ideas", response_model=IdeaRead, status_code=status.HTTP_201_CREATED)
def create_idea(payload: IdeaCreate, db: Session = Depends(get_db)) -> IdeaRead:
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title is required")
    idea = Idea(title=title, description=payload.description, target_date=payload.target_date)
    db.add(idea)
    db.commit()
    db.refresh(idea)
    return _to_read_model(idea)


@router.patch("/ideas/{idea_id}", response_model=IdeaRead)
def patch_idea(idea_id: int, payload: IdeaUpdate, db: Session = Depends(get_db)) -> IdeaRead:
    idea = fetch_idea(db, idea_id)
    if payload.title is not None:
        cleaned = payload.title.strip()
        if not cleaned:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title cannot be empty")
        idea.title = cleaned
    if payload.description is not None:
        idea.description = payload.description
    if payload.target_date is not None:
        idea.target_date = payload.target_date
    db.commit()
    db.refresh(idea)
    return _to_read_model(idea)


@router.post("/ideas/{idea_id}/toggle", response_model=IdeaRead)
def toggle_idea(idea_id: int, db: Session = Depends(get_db)) -> IdeaRead:
    idea = fetch_idea(db, idea_id)
    toggle_completion(idea)
    db.commit()
    db.refresh(idea)
    return _to_read_model(idea)


@router.delete("/ideas/{idea_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_idea(idea_id: int, db: Session = Depends(get_db)) -> Response:
    idea = fetch_idea(db, idea_id)
    db.delete(idea)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/calendar")
def calendar_api(year: int | None = None, month: int | None = None, db: Session = Depends(get_db)):
    today = date.today()
    year = year or today.year
    month = month or today.month
    ctx = month_context(year, month)
    ideas = ideas_in_range(db, ctx["range_start"], ctx["range_end"])
    return [_to_read_model(idea) for idea in ideas]
