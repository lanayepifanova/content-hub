# ContentHub

Modular FastAPI + SQLModel platform for AI-powered content ideation. This repo targets a single local developer environment where every workflow runs through the `ch` launcher (planned Python entrypoint plus thin wrappers).

## Quick Start

```bash
git clone <repo-url> content-hub
cd content-hub
./ch setup          # creates .venv, installs deps, copies .env, runs init-db
./ch runserver      # starts FastAPI on http://127.0.0.1:8000
```

Windows CMD:

```cmd
git clone <repo-url> content-hub
cd content-hub
ch.bat setup
ch.bat runserver
```

PowerShell:

```powershell
git clone <repo-url> content-hub
cd content-hub
.\ch.ps1 setup
.\ch.ps1 runserver
```

Then open `http://127.0.0.1:8000` (UI) or `/docs` (OpenAPI). If Python ≥3.10 is missing, the wrappers print guidance.

## Project Structure

```
app/                FastAPI app (core + modules)
data/               SQLite database (generated)
docs/plans/         Feature planning docs (Steps 1‑4)
tools/dev.py        Typer CLI invoked by ch.py
ch / ch.bat / ch.py Cross-platform launcher (in progress)
AI_PROJECT_GUIDE.md Comprehensive project guide
```

See `AI_PROJECT_GUIDE.md` for full layout, workflows, and standards.

## Development Process

1. Follow `FEATURE_DEVELOPMENT_PROCESS.md` (Step 1 optional, Steps 2‑4 required).
2. Create feature branch (`feature/<name>`).
3. Draft planning docs under `docs/plans/` and wait for approval (“Approved Step N”).
4. Implement in atomic stages (<1 hour each). Update the Step 4 implementation summary after every stage.
5. Run smoke tests (`./ch setup`, `./ch runserver --no-reload`, browser check) before requesting review.

## Key Commands

- `./ch setup` – bootstrap venv, install dependencies, run `init-db`.
- `./ch runserver [--host 0.0.0.0 --port 8000]` – start FastAPI with reload.
- `./ch init-db` – reapply migrations/seeds.
- `./ch create-admin` / `./ch create-invite` – helper commands from `tools/dev.py`.
- `./ch <anything>` – forwards arguments to `tools/dev.py`.

## Troubleshooting

- **Missing Python**: Install Python 3.10+ (python.org, brew, pyenv). Wrappers provide guidance.
- **Dependencies missing**: Re-run `./ch setup` to reinstall inside `.venv`.
- **Server won’t start**: Ensure `.env` exists (`cp .env.example .env`) and database path `data/contenthub.db` is writable. Delete the DB if needed and run `./ch init-db`.
- **Automation/CI**: Set `CH_AUTOMATION=1` to let `./ch runserver` skip binding a port during headless smoke tests.
- **Windows ExecutionPolicy issues**: Run `ch.bat` from CMD or execute `PowerShell -ExecutionPolicy Bypass -File ch.ps1 setup`.

## Documentation

- `AI_PROJECT_GUIDE.md` – Detailed architecture, workflow, testing, and deployment notes.
- `FEATURE_DEVELOPMENT_PROCESS.md` – Planning/approval process.
- `CLI_IMPLEMENTATION_CHECKLIST.md` / `CLI_IMPLEMENTATION_PLAN.md` – Launcher-specific references.
- `docs/plans/ch_launcher_step[2-4]_*.md` – Current feature’s planning + implementation summary.

Always keep documentation files in the repo; never delete planning artifacts. Update guides when behavior changes so new contributors can bootstrap the modular stack without guesswork.
