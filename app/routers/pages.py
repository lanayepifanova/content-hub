"""HTML page routes (calendar + edit view)."""

from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.lib.calendar import group_ideas_by_day, month_context
from app.services import fetch_idea, ideas_in_range
from app.ui import templates

router = APIRouter(tags=["Pages"])


@router.get("/", response_class=HTMLResponse)
def calendar_page(
    request: Request,
    year: int | None = None,
    month: int | None = None,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    today = date.today()
    year = year or today.year
    month = month or today.month

    ctx = month_context(year, month)
    ideas = ideas_in_range(db, ctx["range_start"], ctx["range_end"])
    ideas_by_day = group_ideas_by_day(ideas)

    return templates.TemplateResponse(
        "calendar.html",
        {
            "request": request,
            "weeks": ctx["weeks"],
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


@router.get("/ideas/{idea_id}/edit", response_class=HTMLResponse)
def edit_page(request: Request, idea_id: int, db: Session = Depends(get_db)) -> HTMLResponse:
    idea = fetch_idea(db, idea_id)
    return templates.TemplateResponse(
        "edit.html",
        {"request": request, "idea": idea},
    )


@router.post("/ideas/{idea_id}/edit", response_class=HTMLResponse)
async def edit_submit(request: Request, idea_id: int, db: Session = Depends(get_db)) -> HTMLResponse:
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
    idea.completed_at = datetime.now(timezone.utc) if completed else None
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
