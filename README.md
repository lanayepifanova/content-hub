# ContentHub Calendar

Single-command workspace for planning video ideas directly on a visual calendar.

## Run Everything

```bash
./run.sh
```

The wrapper handles `.venv` creation, dependency installs (`fastapi`, `uvicorn`, `sqlalchemy`, `jinja2`), and launches `uvicorn main:app --reload` on `http://127.0.0.1:8000`.

Override defaults as needed:

```bash
HOST=0.0.0.0 PORT=9000 RELOAD=false ./run.sh
```

## Features
- **Calendar-first workflow:** the homepage is a monthly grid. Each day tile lets you add hooks inline, view what’s scheduled, and tick the checkbox once it’s filmed/published.
- **Quick data entry:** tap any day, type a sentence-long title, and hit `+`. Longer notes/scripts live on the dedicated edit page (`/ideas/{id}/edit`).
- **Completion tracking:** checkboxes instantly toggle completion status, and completed ideas show as muted/struck-out so you know what’s done.
- **Month navigation:** jump to previous/next months via the header nav or return to “Today” in one click.
- **REST API:**
  - `POST /api/ideas` – create `{title, target_date, description?}` for a specific day.
  - `PATCH /api/ideas/{id}` – update title, description, or day.
  - `POST /api/ideas/{id}/toggle` – flip the completion state (and timestamp) for quick check-offs.
  - `DELETE /api/ideas/{id}` – remove an entry.
  - `GET /api/calendar?year=&month=` – returns all ideas in the rendered range (for future integrations or exports).

## UI Quick Tour
1. Visit `http://127.0.0.1:8000`. The current month loads automatically; navigate via the arrows when needed.
2. Hover any day tile, type a title in the “Add idea” field, and press `+` to schedule it.
3. Click a checkbox to mark it complete (or uncheck to reopen it). Use the tiny **Edit** link for longer notes or date adjustments.
4. Delete ideas inline if you change plans—the calendar updates on refresh.

## Resetting the Database
The app stores data in `contenthub.db` (SQLite). Delete that file if you want a clean slate; it will be recreated automatically on the next run. Because the calendar redesign introduces new columns (`completed`, `completed_at`), remove `contenthub.db` once if it was created previously.
