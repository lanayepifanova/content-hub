from __future__ import annotations

from datetime import date

import pytest

from app import database
from app.database import Base
from app.lib.calendar import month_context
from app.routers import ideas, templates
from app.schemas import (
    BriefBlock,
    BriefContent,
    BriefUpdate,
    IdeaCreate,
    IdeaUpdate,
    TemplateCreate,
    TemplateFavoriteRequest,
    TemplateRatingRequest,
)


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


def test_brief_autosave_and_restore(db_session):
    payload = IdeaCreate(title="Brief builder", target_date=date.today(), description=None)
    created = ideas.create_idea(payload, db=db_session)
    content = BriefContent(
        blocks=[BriefBlock(id="b1", type="text", text="Intro line", checked=False)],
        hashtags=["#test"],
    )
    saved = ideas.write_brief(created.id, BriefUpdate(content=content), db=db_session)
    assert saved.content.blocks[0].text == "Intro line"

    autosave = ideas.autosave_brief(created.id, BriefUpdate(content=content, label="Autosave"), db=db_session)
    assert autosave.content.hashtags == ["#test"]

    versions = ideas.brief_versions(created.id, db=db_session)
    assert versions, "Autosave should create a version"

    restored = ideas.restore_brief_version(created.id, versions[0].id, db=db_session)
    assert restored.content.blocks[0].text == "Intro line"


def test_templates_router_seeds_defaults(db_session):
    catalog = templates.templates_index(db=db_session)
    assert catalog, "Seed templates should auto-populate"
    new_template = templates.templates_create(
        TemplateCreate(name="Quick CTA", body="Subscribe for part 2", category="CTA"),
        db=db_session,
    )
    assert new_template.name == "Quick CTA"


def test_template_favorite_and_rating(db_session):
    catalog = templates.templates_index(db=db_session)
    template = catalog[0]
    updated = templates.templates_favorite(
        template.id,
        TemplateFavoriteRequest(favorite=not template.favorite),
        db=db_session,
    )
    assert updated.favorite is (not template.favorite)

    rating_response = templates.templates_rate(
        template.id,
        TemplateRatingRequest(rating=5),
        db=db_session,
    )
    assert rating_response.rating_count >= 1
