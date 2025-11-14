"""JSON API endpoints used by the calendar UI."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.lib.calendar import month_context
from app.models import Idea, IdeaBrief
from app.schemas import (
    AttachmentSignRequest,
    AttachmentSignResponse,
    BriefUpdate,
    IdeaBriefRead,
    IdeaBriefVersionRead,
    IdeaCreate,
    IdeaRead,
    IdeaUpdate,
)
from app.services import (
    fetch_idea,
    get_or_create_brief,
    ideas_in_range,
    list_versions,
    parse_brief_content,
    restore_version,
    toggle_completion,
    update_brief,
)
from app.lib.storage import StorageConfigError, build_presigned_upload


def _to_read_model(idea: Idea) -> IdeaRead:
    return IdeaRead.model_validate(idea)


def _brief_response(idea: Idea, brief: IdeaBrief) -> IdeaBriefRead:
    return IdeaBriefRead(idea_id=idea.id, updated_at=brief.updated_at, content=parse_brief_content(brief))
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


@router.get("/ideas/{idea_id}/brief", response_model=IdeaBriefRead)
def read_brief(idea_id: int, db: Session = Depends(get_db)) -> IdeaBriefRead:
    idea = fetch_idea(db, idea_id)
    brief = get_or_create_brief(db, idea)
    return _brief_response(idea, brief)


@router.put("/ideas/{idea_id}/brief", response_model=IdeaBriefRead)
def write_brief(idea_id: int, payload: BriefUpdate, db: Session = Depends(get_db)) -> IdeaBriefRead:
    idea = fetch_idea(db, idea_id)
    brief = update_brief(db, idea, payload.content, autosave=False, label=payload.label)
    return _brief_response(idea, brief)


@router.post("/ideas/{idea_id}/brief/autosave", response_model=IdeaBriefRead)
def autosave_brief(idea_id: int, payload: BriefUpdate, db: Session = Depends(get_db)) -> IdeaBriefRead:
    idea = fetch_idea(db, idea_id)
    brief = update_brief(db, idea, payload.content, autosave=True, label=payload.label or "Autosave")
    return _brief_response(idea, brief)


@router.get("/ideas/{idea_id}/brief/versions", response_model=list[IdeaBriefVersionRead])
def brief_versions(idea_id: int, db: Session = Depends(get_db)) -> list[IdeaBriefVersionRead]:
    idea = fetch_idea(db, idea_id)
    versions = list_versions(db, idea)
    return [IdeaBriefVersionRead.model_validate(v) for v in versions]


@router.post("/ideas/{idea_id}/brief/versions/{version_id}/restore", response_model=IdeaBriefRead)
def restore_brief_version(
    idea_id: int,
    version_id: int,
    db: Session = Depends(get_db),
) -> IdeaBriefRead:
    idea = fetch_idea(db, idea_id)
    version, content = restore_version(db, version_id)
    if version.idea_id != idea.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autosave not found")
    brief = update_brief(db, idea, content, autosave=True, label=version.label or "Restore")
    return _brief_response(idea, brief)


@router.post("/ideas/{idea_id}/brief/attachments/sign", response_model=AttachmentSignResponse)
def presign_attachment(
    idea_id: int,
    payload: AttachmentSignRequest,
    db: Session = Depends(get_db),
) -> AttachmentSignResponse:
    # Ensure the idea exists before generating storage credentials.
    fetch_idea(db, idea_id)
    try:
        presigned = build_presigned_upload(payload.filename, payload.content_type)
    except StorageConfigError as exc:  # pragma: no cover - depends on env config
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    return AttachmentSignResponse(
        key=presigned["key"],
        url=presigned["url"],
        upload_url=presigned["upload_url"],
        fields=presigned["fields"],
        content_type=presigned["content_type"],
    )

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
