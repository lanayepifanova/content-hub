# ContentHub Calendar

Plan video ideas directly on a visual calendar, toggle completion, and keep track of scripts/notes in one place.

---

## Quickstart

```bash
./run.sh
```

The helper script bootstraps `.venv`, installs the editable project defined in `pyproject.toml`, and runs `uvicorn app.main:app --reload` on `http://127.0.0.1:8000`.

Override defaults as needed:

```bash
HOST=0.0.0.0 PORT=9000 RELOAD=false ./run.sh
```

Manual install:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

---

## Features
- Calendar-first workflow with 42-day grid and “Today” highlighting.
- Inline form per day for ultra-fast idea capture.
- Edit page for longer notes, script drafts, date changes, and completion toggles.
- REST API for CRUD + calendar exports (`/api/ideas`, `/api/calendar`).
- SQLite-backed persistence (auto-created `contenthub.db`).

---

## Project Layout

```
app/
├── config.py          # Paths + shared settings
├── database.py        # SQLAlchemy engine/session helpers
├── models.py          # ORM models
├── routers/           # HTML + API endpoints
├── schemas.py         # Pydantic contracts
├── services.py        # Domain helpers (fetch/toggle/query ideas)
├── lib/calendar.py    # Calendar math + grouping helpers
├── static/            # CSS / assets served via FastAPI
└── templates/         # Jinja2 views (calendar + edit)
run.sh                 # One-command dev server bootstrap
pyproject.toml         # Dependencies + tooling config
```

---

## Testing & Tooling

Install dev extras and run pytest:

```bash
pip install -e ".[dev]"
pytest
```

Format/lint (Ruff):

```bash
ruff check .
```

---

## UI Quick Tour
1. Visit `http://127.0.0.1:8000` to load the current month. Use the arrows for previous/next months or jump back to “Today”.
2. Hover any day tile, type a hook in “Add idea”, hit `+` to schedule it.
3. Toggle completion via the checkbox; edit or delete ideas inline.
4. Open the **Edit** link for richer notes or to mark completion with a timestamp.

---

## Resetting the Database

Delete `contenthub.db` if you want a clean slate. The file is recreated on the next run with the latest schema (including `completed` + `completed_at` columns).
