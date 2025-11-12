"""Centralized application configuration."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
STATIC_DIR = APP_DIR / "static"
TEMPLATE_DIR = APP_DIR / "templates"
DB_PATH = BASE_DIR / "contenthub.db"
DATABASE_URL = os.getenv("CONTENTHUB_DB_URL", f"sqlite:///{DB_PATH}")

# Ensure key folders exist when the app spins up (important for StaticFiles/Jinja2).
for directory in (STATIC_DIR, TEMPLATE_DIR):
    directory.mkdir(parents=True, exist_ok=True)
