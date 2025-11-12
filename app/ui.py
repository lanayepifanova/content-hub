"""UI helpers such as template instances shared across routers."""

from __future__ import annotations

from fastapi.templating import Jinja2Templates

from app.config import TEMPLATE_DIR

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

__all__ = ["templates"]
