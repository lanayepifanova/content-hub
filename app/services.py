"""Domain services shared by routers."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Iterable

from fastapi import HTTPException, status
from sqlalchemy import case
from sqlalchemy.orm import Session

from app.models import Idea, IdeaBrief, IdeaBriefVersion, IdeaTemplate
from app.schemas import BriefContent

DEFAULT_TEMPLATE_SEED = [
    {
        "name": "Hook: Problem → Agitate → Solve",
        "body": "Open with the pain, stack 2 lines of agitation, then tease the fix.",
        "category": "Hook",
    },
    {
        "name": "Intro: Credibility Sandwich",
        "body": "1) Personal win  2) Lesson teaser  3) Invite viewer to stay.",
        "category": "Intro",
    },
    {
        "name": "CTA: DM Opt-in",
        "body": "DM me \"blueprint\" and I’ll send the full checklist.",
        "category": "CTA",
    },
]


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


def _blank_brief_content() -> BriefContent:
    return BriefContent()


def get_or_create_brief(db: Session, idea: Idea) -> IdeaBrief:
    """Return a brief for the idea, creating a blank canvas on first access."""
    if idea.brief:
        return idea.brief
    brief = IdeaBrief(idea_id=idea.id, content=_blank_brief_content().model_dump_json())
    db.add(brief)
    db.commit()
    db.refresh(brief)
    return brief


def parse_brief_content(brief: IdeaBrief) -> BriefContent:
    """Safely parse the stored JSON payload into a BriefContent object."""
    try:
        return BriefContent.model_validate_json(brief.content or "{}")
    except ValueError:
        return _blank_brief_content()


def update_brief(
    db: Session,
    idea: Idea,
    content: BriefContent,
    autosave: bool = False,
    label: str | None = None,
) -> IdeaBrief:
    """Persist the latest brief content and optionally snapshot an autosave version."""
    brief = get_or_create_brief(db, idea)
    brief.content = content.model_dump_json()
    if autosave:
        db.add(
            IdeaBriefVersion(
                idea_id=idea.id,
                snapshot=brief.content,
                label=label,
            )
        )
    db.commit()
    db.refresh(brief)
    return brief


def list_versions(db: Session, idea: Idea, limit: int = 10) -> list[IdeaBriefVersion]:
    """Return the most recent autosave versions for display."""
    return (
        db.query(IdeaBriefVersion)
        .filter(IdeaBriefVersion.idea_id == idea.id)
        .order_by(IdeaBriefVersion.created_at.desc())
        .limit(limit)
        .all()
    )


def restore_version(db: Session, version_id: int) -> tuple[IdeaBriefVersion, BriefContent]:
    """Load a stored snapshot and parse it into a BriefContent payload."""
    version = db.query(IdeaBriefVersion).filter(IdeaBriefVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autosave not found")
    content = BriefContent.model_validate_json(version.snapshot)
    return version, content


def ensure_seed_templates(db: Session) -> None:
    """Populate the templates table with baseline snippets exactly once."""
    existing = db.query(IdeaTemplate.id).first()
    if existing:
        return
    for data in DEFAULT_TEMPLATE_SEED:
        db.add(IdeaTemplate(**data))
    db.commit()


def list_templates(db: Session) -> Iterable[IdeaTemplate]:
    """Return templates ordered by favorites and rating."""
    ensure_seed_templates(db)
    rating_score = case(
        (IdeaTemplate.rating_count > 0, IdeaTemplate.rating_sum / IdeaTemplate.rating_count),
        else_=0,
    )
    return (
        db.query(IdeaTemplate)
        .order_by(IdeaTemplate.favorite.desc(), rating_score.desc(), IdeaTemplate.created_at.asc())
        .all()
    )


def create_template(db: Session, name: str, body: str, category: str | None = None) -> IdeaTemplate:
    ensure_seed_templates(db)
    template = IdeaTemplate(name=name, body=body, category=category)
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def fetch_template(db: Session, template_id: int) -> IdeaTemplate:
    template = db.query(IdeaTemplate).filter(IdeaTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return template


def update_template(
    db: Session,
    template: IdeaTemplate,
    *,
    name: str | None = None,
    body: str | None = None,
    category: str | None = None,
    favorite: bool | None = None,
) -> IdeaTemplate:
    if name is not None:
        template.name = name
    if body is not None:
        template.body = body
    if category is not None:
        template.category = category
    if favorite is not None:
        template.favorite = favorite
    db.commit()
    db.refresh(template)
    return template


def toggle_template_favorite(db: Session, template: IdeaTemplate, favorite: bool) -> IdeaTemplate:
    template.favorite = favorite
    db.commit()
    db.refresh(template)
    return template


def rate_template(db: Session, template: IdeaTemplate, rating: int) -> IdeaTemplate:
    template.rating_sum += rating
    template.rating_count += 1
    db.commit()
    db.refresh(template)
    return template
