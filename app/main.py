"""FastAPI application factory for the ContentHub calendar."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app import database
from app.config import STATIC_DIR
from app.routers import ideas, pages, templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.Base.metadata.create_all(bind=database.engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="ContentHub Calendar",
        version="0.4.0",
        description="Plan video ideas on a visual calendar and toggle completion in one click.",
        lifespan=lifespan,
    )
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.include_router(pages.router)
    app.include_router(ideas.router)
    app.include_router(templates.router)
    return app


app = create_app()
