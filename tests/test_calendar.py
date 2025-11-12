from __future__ import annotations

from datetime import date

import pytest

from app import database
from app.database import Base
from app.lib.calendar import month_context
from app.routers import ideas
from app.schemas import IdeaCreate, IdeaUpdate


@pytest.fixture()
def db_session(tmp_path):
    test_db = tmp_path / "test.db"
    database.configure_database(f"sqlite:///{test_db}")
    Base.metadata.create_all(bind=database.engine)
    session = database.SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_month_context_spans_six_weeks():
    ctx = month_context(2024, 5)
    assert len(ctx["weeks"]) == 6
    assert ctx["weeks"][0][0].weekday() == 0  # starts on Monday
    assert ctx["weeks"][-1][-1].weekday() == 6  # ends on Sunday


def test_idea_crud_flow(db_session):
    payload = IdeaCreate(title="Record hooks", target_date=date.today(), description="Testing!")
    created = ideas.create_idea(payload, db=db_session)
    idea_id = created.id
    assert created.title == payload.title

    updated = ideas.patch_idea(idea_id, IdeaUpdate(title="Edited title"), db=db_session)
    assert updated.title == "Edited title"

    toggled = ideas.toggle_idea(idea_id, db=db_session)
    assert toggled.completed is True

    calendar = ideas.calendar_api(db=db_session)
    assert any(item.id == idea_id for item in calendar)

    ideas.delete_idea(idea_id, db=db_session)
    assert ideas.calendar_api(db=db_session) == []
