"""ContentHub Calendar – FastAPI app for day-based video planning."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Idea

STATIC_DIR = Path("static")
TEMPLATE_DIR = Path("templates")
STATIC_DIR.mkdir(exist_ok=True)
TEMPLATE_DIR.mkdir(exist_ok=True)

app = FastAPI(title="ContentHub Calendar", version="0.3.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

Base.metadata.create_all(bind=engine)


class IdeaCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    target_date: date
    description: str | None = Field(default=None, max_length=2000)


class IdeaUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    target_date: date | None = None
    description: str | None = Field(default=None, max_length=2000)


class IdeaRead(BaseModel):
    id: int
    title: str
    description: str | None
    target_date: date
    created_at: datetime
    completed: bool
    completed_at: datetime | None

    class Config:
        from_attributes = True


class TogglePayload(BaseModel):
    completed: bool | None = None


def fetch_idea(db: Session, idea_id: int) -> Idea:
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")
    return idea


def month_context(year: int, month: int) -> dict:
    first_day = date(year, month, 1)
    start = first_day - timedelta(days=first_day.weekday())
    days = [start + timedelta(days=i) for i in range(42)]
    weeks = [days[i : i + 7] for i in range(0, 42, 7)]
    last_day = days[-1]

    prev_month_anchor = first_day - timedelta(days=1)
    next_month_anchor = last_day + timedelta(days=1)

    return {
        "weeks": weeks,
        "range_start": days[0],
        "range_end": days[-1],
        "current_month": month,
        "current_year": year,
        "previous": (prev_month_anchor.year, prev_month_anchor.month),
        "next": (next_month_anchor.year, next_month_anchor.month),
        "current_label": first_day.strftime("%B %Y"),
        "previous_label": date(prev_month_anchor.year, prev_month_anchor.month, 1).strftime("%b"),
        "next_label": date(next_month_anchor.year, next_month_anchor.month, 1).strftime("%b"),
    }


@app.get("/", response_class=HTMLResponse)
def calendar_page(
    request: Request,
    year: int | None = None,
    month: int | None = None,
    db: Session = Depends(get_db),
):
    today = date.today()
    year = year or today.year
    month = month or today.month

    ctx = month_context(year, month)
    weeks = ctx["weeks"]
    start = ctx["range_start"]
    end = ctx["range_end"]

    ideas = (
        db.query(Idea)
        .filter(Idea.target_date >= start, Idea.target_date <= end)
        .order_by(Idea.target_date.asc(), Idea.created_at.asc())
        .all()
    )
    ideas_by_day: dict[date, list[Idea]] = defaultdict(list)
    for idea in ideas:
        ideas_by_day[idea.target_date].append(idea)

    return templates.TemplateResponse(
        "calendar.html",
        {
            "request": request,
            "weeks": weeks,
            "ideas_by_day": ideas_by_day,
            "today": today,
            "current_month": ctx["current_month"],
            "current_year": ctx["current_year"],
            "previous": ctx["previous"],
            "next": ctx["next"],
            "current_label": ctx["current_label"],
            "previous_label": ctx["previous_label"],
            "next_label": ctx["next_label"],
        },
    )


@app.get("/ideas/{idea_id}/edit", response_class=HTMLResponse)
def edit_page(request: Request, idea_id: int, db: Session = Depends(get_db)):
    idea = fetch_idea(db, idea_id)
    return templates.TemplateResponse(
        "edit.html",
        {"request": request, "idea": idea},
    )


@app.post("/ideas/{idea_id}/edit", response_class=HTMLResponse)
async def edit_submit(request: Request, idea_id: int, db: Session = Depends(get_db)):
    idea = fetch_idea(db, idea_id)
    form = await request.form()
    title = (form.get("title") or "").strip()
    if not title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title is required")
    idea.title = title
    idea.description = form.get("description") or None
    target = form.get("target_date")
    if target:
        idea.target_date = date.fromisoformat(target)
    completed = form.get("completed") == "on"
    idea.completed = completed
    idea.completed_at = datetime.utcnow() if completed else None
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


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
def patch_idea(idea_id: int, payload: IdeaUpdate, db: Session = Depends(get_db)):
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
    return IdeaRead.from_orm(idea)


@app.post("/api/ideas/{idea_id}/toggle", response_model=IdeaRead)
def toggle_idea(idea_id: int, db: Session = Depends(get_db)):
    idea = fetch_idea(db, idea_id)
    idea.completed = not idea.completed
    idea.completed_at = datetime.utcnow() if idea.completed else None
    db.commit()
    db.refresh(idea)
    return IdeaRead.from_orm(idea)


@app.delete("/api/ideas/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_idea(idea_id: int, db: Session = Depends(get_db)):
    idea = fetch_idea(db, idea_id)
    db.delete(idea)
    db.commit()
    return None


@app.get("/api/calendar")
def calendar_api(year: int | None = None, month: int | None = None, db: Session = Depends(get_db)):
    today = date.today()
    year = year or today.year
    month = month or today.month
    ctx = month_context(year, month)
    start = ctx["range_start"]
    end = ctx["range_end"]
    ideas = (
        db.query(Idea)
        .filter(Idea.target_date >= start, Idea.target_date <= end)
        .order_by(Idea.target_date.asc(), Idea.created_at.asc())
        .all()
    )
    return [IdeaRead.from_orm(idea) for idea in ideas]
