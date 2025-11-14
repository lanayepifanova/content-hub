"""Reusable template/snippet endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    TemplateCreate,
    TemplateFavoriteRequest,
    TemplateFavoriteResponse,
    TemplateRatingRequest,
    TemplateRatingResponse,
    TemplateRead,
    TemplateUpdate,
)
from app.services import (
    create_template as persist_template,
    fetch_template,
    list_templates,
    rate_template,
    toggle_template_favorite,
    update_template as persist_template_update,
)

router = APIRouter(prefix="/api/templates", tags=["Templates"])


def _to_read(template) -> TemplateRead:
    rating = None
    if template.rating_count:
        rating = round(template.rating_sum / template.rating_count, 2)
    return TemplateRead(
        id=template.id,
        name=template.name,
        body=template.body,
        category=template.category,
        favorite=template.favorite,
        created_at=template.created_at,
        rating=rating,
        rating_count=template.rating_count,
    )


@router.get("", response_model=list[TemplateRead])
def templates_index(db: Session = Depends(get_db)) -> list[TemplateRead]:
    templates = list_templates(db)
    return [_to_read(item) for item in templates]


@router.post("", response_model=TemplateRead, status_code=status.HTTP_201_CREATED)
def templates_create(payload: TemplateCreate, db: Session = Depends(get_db)) -> TemplateRead:
    template = persist_template(db, name=payload.name.strip(), body=payload.body.strip(), category=payload.category)
    return _to_read(template)


@router.patch("/{template_id}", response_model=TemplateRead)
def templates_update(template_id: int, payload: TemplateUpdate, db: Session = Depends(get_db)) -> TemplateRead:
    template = fetch_template(db, template_id)
    template = persist_template_update(
        db,
        template,
        name=payload.name.strip() if payload.name else None,
        body=payload.body.strip() if payload.body else None,
        category=payload.category,
        favorite=payload.favorite,
    )
    return _to_read(template)


@router.post("/{template_id}/favorite", response_model=TemplateFavoriteResponse)
def templates_favorite(
    template_id: int,
    payload: TemplateFavoriteRequest,
    db: Session = Depends(get_db),
) -> TemplateFavoriteResponse:
    template = fetch_template(db, template_id)
    template = toggle_template_favorite(db, template, payload.favorite)
    return TemplateFavoriteResponse(id=template.id, favorite=template.favorite)


@router.post("/{template_id}/ratings", response_model=TemplateRatingResponse, status_code=status.HTTP_201_CREATED)
def templates_rate(
    template_id: int,
    payload: TemplateRatingRequest,
    db: Session = Depends(get_db),
) -> TemplateRatingResponse:
    template = fetch_template(db, template_id)
    template = rate_template(db, template, payload.rating)
    rating = round(template.rating_sum / template.rating_count, 2) if template.rating_count else None
    return TemplateRatingResponse(id=template.id, rating=rating, rating_count=template.rating_count)
