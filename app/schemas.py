"""Pydantic models shared by the API layer."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)
