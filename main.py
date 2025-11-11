"""Minimal FastAPI app with a single Idea model."""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Idea

# Ensure tables exist on startup.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ContentHub Minimal", version="0.1.0")


class IdeaCreate(BaseModel):
    title: str
    description: str | None = None


class IdeaRead(BaseModel):
    id: int
    title: str
    description: str | None = None

    class Config:
        orm_mode = True


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {"message": "ContentHub starter is running"}


@app.get("/ideas", response_model=list[IdeaRead], tags=["ideas"])
def list_ideas(db: Session = Depends(get_db)):
    return db.query(Idea).all()


@app.post("/ideas", response_model=IdeaRead, tags=["ideas"], status_code=201)
def create_idea(payload: IdeaCreate, db: Session = Depends(get_db)):
    idea = Idea(title=payload.title, description=payload.description)
    db.add(idea)
    db.commit()
    db.refresh(idea)
    return idea


@app.get("/ideas/{idea_id}", response_model=IdeaRead, tags=["ideas"])
def get_idea(idea_id: int, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea
