"""Pydantic models shared by the API layer."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class IdeaCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    target_date: date
    description: str | None = Field(default=None, max_length=8000)


class IdeaUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    target_date: date | None = None
    description: str | None = Field(default=None, max_length=8000)


class IdeaRead(BaseModel):
    id: int
    title: str
    description: str | None
    target_date: date
    created_at: datetime
    completed: bool
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class BriefBlock(BaseModel):
    id: str
    type: Literal["text", "heading", "quote", "checklist"]
    text: str = ""
    checked: bool | None = None


class ShotListItem(BaseModel):
    id: str
    cue: str
    setup: str | None = None
    shot_type: str | None = None


class CTAItem(BaseModel):
    id: str
    text: str
    platform: str | None = None


class AttachmentItem(BaseModel):
    id: str
    filename: str
    url: str
    key: str
    content_type: str | None = None
    size: int | None = None


class BriefContent(BaseModel):
    blocks: list[BriefBlock] = Field(default_factory=list)
    shots: list[ShotListItem] = Field(default_factory=list)
    ctas: list[CTAItem] = Field(default_factory=list)
    hashtags: list[str] = Field(default_factory=list)
    thumbnail_notes: str | None = None
    attachments: list[AttachmentItem] = Field(default_factory=list)


class BriefUpdate(BaseModel):
    content: BriefContent
    label: str | None = None


class IdeaBriefRead(BaseModel):
    idea_id: int
    updated_at: datetime
    content: BriefContent


class IdeaBriefVersionRead(BaseModel):
    id: int
    idea_id: int
    label: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttachmentSignRequest(BaseModel):
    filename: str
    content_type: str = "application/octet-stream"
    size: int | None = None


class AttachmentSignResponse(BaseModel):
    key: str
    url: str
    upload_url: str
    fields: dict[str, str]
    content_type: str


class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=120)
    body: str = Field(..., min_length=1, max_length=500)
    category: str | None = Field(default=None, max_length=50)


class TemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=120)
    body: str | None = Field(default=None, min_length=1, max_length=500)
    category: str | None = Field(default=None, max_length=50)
    favorite: bool | None = None


class TemplateRead(BaseModel):
    id: int
    name: str
    body: str
    category: str | None
    favorite: bool
    created_at: datetime
    rating: float | None
    rating_count: int

    model_config = ConfigDict(from_attributes=True)


class TemplateFavoriteRequest(BaseModel):
    favorite: bool


class TemplateFavoriteResponse(BaseModel):
    id: int
    favorite: bool


class TemplateRatingRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)


class TemplateRatingResponse(BaseModel):
    id: int
    rating: float | None
    rating_count: int
