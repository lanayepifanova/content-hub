"""SQLAlchemy models for the minimal ContentHub restart."""

from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text

from database import Base


class Idea(Base):
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
