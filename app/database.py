"""Database session helpers."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL


def _build_engine(url: str) -> Engine:
    return create_engine(
        url,
        connect_args={"check_same_thread": False},
    )


engine = _build_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Provide a database session dependency for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def configure_database(url: str) -> None:
    """Rebuild the engine/session for tests or custom deployments."""
    global engine, SessionLocal
    engine = _build_engine(url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
