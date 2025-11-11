"""ContentHub Idea Inbox – FastAPI + SQLAlchemy + Jinja templates."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Idea, IdeaStatus

STATIC_DIR = Path("static")
TEMPLATE_DIR = Path("templates")
STATIC_DIR.mkdir(exist_ok=True)
TEMPLATE_DIR.mkdir(exist_ok=True)

app = FastAPI(title="ContentHub Idea Inbox", version="0.2.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

Base.metadata.create_all(bind=engine)

STATUSES = [IdeaStatus.BACKLOG, IdeaStatus.DRAFTING, IdeaStatus.SCHEDULED, IdeaStatus.PUBLISHED]


class IdeaCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    target_date: date | None = None


class IdeaRead(BaseModel):
    id: int
    title: str
    description: str | None
    status: IdeaStatus
    created_at: datetime
    target_date: date | None

    class Config:
        orm_mode = True


class IdeaStatusUpdate(BaseModel):
    status: IdeaStatus


@app.get("/", response_class=HTMLResponse)
@app.get("/inbox", response_class=HTMLResponse)
def inbox_page(request: Request, db: Session = Depends(get_db)):
    ideas = db.query(Idea).order_by(Idea.created_at.desc()).all()
    grouped: dict[IdeaStatus, list[Idea]] = {status: [] for status in STATUSES}
    for idea in ideas:
        grouped[IdeaStatus(idea.status)].append(idea)

    calendar_map: dict[date, list[Idea]] = defaultdict(list)
    for idea in ideas:
        if idea.target_date:
            calendar_map[idea.target_date].append(idea)
    calendar_items = sorted(calendar_map.items(), key=lambda pair: pair[0])

    return templates.TemplateResponse(
        "inbox.html",
        {
            "request": request,
            "statuses": STATUSES,
            "grouped": grouped,
            "calendar_items": calendar_items,
        },
    )


@app.get("/api/ideas", response_model=list[IdeaRead])
def list_ideas(db: Session = Depends(get_db)):
    ideas = db.query(Idea).order_by(Idea.created_at.desc()).all()
    return [IdeaRead.from_orm(idea) for idea in ideas]


@app.post("/api/ideas", response_model=IdeaRead, status_code=status.HTTP_201_CREATED)
def create_idea(payload: IdeaCreate, db: Session = Depends(get_db)):
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title is required")
    idea = Idea(title=title, description=payload.description, target_date=payload.target_date)
    db.add(idea)
    db.commit()
    db.refresh(idea)
    return IdeaRead.from_orm(idea)


@app.patch("/api/ideas/{idea_id}", response_model=IdeaRead)
def update_idea_status(idea_id: int, payload: IdeaStatusUpdate, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")
    idea.status = payload.status
    db.commit()
    db.refresh(idea)
    return IdeaRead.from_orm(idea)


@app.get("/api/calendar")
def calendar_feed(db: Session = Depends(get_db)):
    ideas = db.query(Idea).filter(Idea.target_date.isnot(None)).all()
    calendar: dict[str, list[dict[str, str]]] = {}
    for idea in ideas:
        key = idea.target_date.isoformat()
        calendar.setdefault(key, []).append({"id": idea.id, "title": idea.title, "status": idea.status})
    return calendar
