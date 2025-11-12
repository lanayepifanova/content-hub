# ContentHub Idea Inbox

Single-command workspace for capturing, organizing, and scheduling content ideas.

## Run Everything

```bash
./run.sh
```

The wrapper takes care of:
1. Creating `.venv` (if missing) with `python3 -m venv .venv`.
2. Activating it and installing `fastapi`, `uvicorn`, `sqlalchemy`, and `jinja2`.
3. Launching `uvicorn main:app --reload` on `http://127.0.0.1:8000`.

Override defaults as needed:

```bash
HOST=0.0.0.0 PORT=9000 RELOAD=false ./run.sh
```

## Features
- **Idea Inbox:** capture quick hooks (title is the only required field), add optional notes or target dates, move ideas between Backlog → Drafting → Scheduled → Published, and click **Edit** to open a dedicated script/notes page.
- **Calendar Peek:** any idea with a target date automatically shows up in the calendar list so you can see what’s planned.
- **REST API:**
  - `GET /api/ideas` – list ideas (JSON).
  - `POST /api/ideas` – create idea with `{title, description?, target_date?}`.
  - `PATCH /api/ideas/{id}` – update status via `{status}` (backlog/drafting/scheduled/published).
  - `PUT /api/ideas/{id}` – update title, description, target date, or status in one call.
  - `DELETE /api/ideas/{id}` – remove an idea entirely.
  - `GET /api/calendar` – grouped ideas keyed by date (`{"2025-01-15": [{"id":1,...}]}`).
- **Editor Page:** `GET /ideas/{id}/edit` + `POST /ideas/{id}/edit` let you tweak longer scripts through a simple HTML form if you prefer that over the inline buttons.

## UI Quick Tour
1. Visit `http://127.0.0.1:8000`.
2. Use the capture form at the top to add ideas rapidly; the board updates on refresh.
3. Move ideas to another column with a single click—each button triggers the REST endpoint.
4. Use the **Edit** link under each card to open a full form for tweaking the script/notes, status, or schedule.
5. Assign a target date to surface it in the calendar panel; delete items you no longer need with the **Delete** button.

## Resetting the Database
The app stores data in `contenthub.db` (SQLite). Delete that file if you want a clean slate; it will be recreated automatically on the next run.
