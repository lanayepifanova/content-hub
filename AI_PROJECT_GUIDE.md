# ContentHub – Project Guide

## Environment Context
- All development happens in the local environment contained in this repository  
- Do not attempt to diagnose or change production systems directly from this workspace  
- Avoid `sudo` and global package installs; rely on project tooling instead  
- Use the git-style `./ch` wrapper (backed by `tools/dev.py`) to run local workflows (server, database init, admin creation)  

---

## Project Overview
**ContentHub** is a modular **AI-powered content ideation and management platform** built with **FastAPI** and **SQLModel**.  
The initial milestone focuses on a **content idea generator and idea repository** where users can brainstorm, categorize, and evolve ideas for writing, media, or campaigns.  

Over time, ContentHub will expand into a full creative workspace with **AI-assisted brainstorming**, **tagging**, **content pipelines**, and **workflow modules** that integrate seamlessly without modifying the core stack.  

---

## Technology Stack
- **Backend:** FastAPI application packaged under `app/`  
- **Database:** SQLite (SQLModel ORM) stored at `data/contenthub.db`  
- **Frontend:** Jinja2 templates rendered by FastAPI with vanilla CSS and progressive JS enhancements  
- **AI Layer:** OpenAI (or local LLM) integration for generating and organizing ideas  
- **Authentication:** Session-based login (with optional OAuth support planned)  
- **CLI Tooling:** Typer-based developer commands in `tools/dev.py`  

---

## Modular Architecture Vision
The platform is structured for **atomic modularity** — each creative capability should live in its own self-contained module.  

Each module must:
- Define routes, templates, and static assets under `app/modules/<module_name>/`  
- Contain a minimal service layer for business logic and persistence  
- Register dependencies and background tasks independently  
- Ship with documentation in `docs/plans/<module_name>_*.md` following the feature process  

The **core idea management** and **AI suggestion** modules will serve as reference implementations for future modules.  

---

## Repository Layout (Target)
```
content-hub/
├── app/
│   ├── main.py                 # FastAPI entrypoint
│   ├── core/                   # Settings, security, shared utilities
│   └── modules/
│       ├── idea_manager/       # Example module (routes, services, templates)
│       └── ai_suggestions/     # Example module for LLM-assisted features
├── data/
│   └── contenthub.db           # SQLite database (generated)
├── docs/
│   └── plans/                  # Feature planning docs (Step 1‑4 per feature)
├── templates/                  # Global Jinja2 templates (layout, partials)
├── static/                     # Shared CSS/JS assets
├── tools/
│   └── dev.py                  # Typer CLI used by wrappers (./ch)
├── ch                          # POSIX wrapper (calls ch.py → tools/dev.py)
├── ch.bat                      # Windows wrapper
├── ch.py                       # Cross-platform launcher (planned)
├── pyproject.toml              # Project metadata + dependencies
└── README.md                   # Quick start + onboarding links
```

Keep feature-specific files inside their module tree so modules stay isolated and portable.

---

## Development Workflow

1. **Plan with the Feature Development Process**  
   - Step 1 (optional), Step 2 (feature description), Step 3 (development plan), Step 4 (implementation summary) live under `docs/plans/`.  
   - Each step must be approved (“Approved Step N”) before proceeding; commit only after approval.
2. **Create a Feature Branch**  
   - Use `feature/<short-description>` (e.g., `feature/ch-launcher`).
3. **Environment Setup**  
   - Run `./ch setup` (or `ch.bat setup`) to create `.venv`, install dependencies, copy `.env`, and initialize the database via `tools/dev.py init-db`.  
   - Never install global dependencies; everything should live inside `.venv`.
4. **Implementation**  
   - Follow Step 3 stages in order; keep each stage ≤1 hour/≤50 LOC.  
   - After each stage, update the Step 4 implementation summary with verification notes.
5. **Verification**  
   - Manual smoke tests are sufficient unless the feature demands automation.  
   - Default server URL: `http://127.0.0.1:8000`.
6. **Review & Merge**  
   - Open PRs against `main`. Ensure planning docs + implementation changes are included. Request reviews focused on modularity and regression risk.

---

## Local Environment & Tooling

- **Python Version**: 3.10+ (match `pyproject.toml`). Prefer system Python or `pyenv`; avoid `sudo` installs.
- **Virtual Environment**: Managed automatically by `./ch setup`. If creating manually, `python -m venv .venv` and activate before running `pip install -e .`.
- **Environment Variables**:
  - Copy `.env.example` → `.env`. Minimum keys: `DATABASE_URL=sqlite:///data/contenthub.db`, `OPENAI_API_KEY=` (optional offline).
  - Restart the server after editing `.env`.
- **CLI Runner (`./ch`, `ch.bat`, `ch.ps1`)**:
  - `./ch setup` – bootstrap venv, install deps, copy `.env`, run `init-db`.
  - `./ch runserver [--host 0.0.0.0 --port 8000]` – start FastAPI with reload.
  - `./ch init-db` – apply migrations/seeds.
  - `./ch create-admin`, `./ch create-invite` – user management helpers.
  - Any other args pass directly to `tools/dev.py`.
  - Set `CH_AUTOMATION=1` when running `./ch runserver` in CI/headless environments to skip binding sockets.

---

## Running the App Locally

1. `./ch setup`
2. `./ch runserver --reload` (use `CH_AUTOMATION=1 ./ch runserver ...` for headless smoke tests)
3. Visit `http://127.0.0.1:8000` for the UI; `http://127.0.0.1:8000/docs` for OpenAPI.
4. Verify module routes (e.g., `/ideas`, `/ai/suggest`) render without errors.

If the server fails to start, ensure `.venv` is active and dependencies are installed via `./ch setup`.

---

## Database & Persistence

- SQLite file: `data/contenthub.db` (git-ignored). Delete to reset locally, then rerun `./ch init-db`.
- Models live alongside modules under `app/modules/<module>/models.py`.
- Avoid schema changes unless necessary; document any migration in Step 2/3 docs before implementation.
- Seeds and data maintenance scripts should live inside `tools/dev.py` commands, invoked via `./ch`.

---

## Testing & QA

- **Smoke Tests** (per feature stage):
  - `./ch setup`
  - `./ch runserver --no-reload`
  - `./ch init-db`
  - Browser check at `http://127.0.0.1:8000`
- **Automated Tests**:
  - Place pytest suites under `tests/`.
  - Run `python -m pytest` (or future `./ch test` command).
- **Cross-Platform**:
  - Validate wrappers on macOS/Linux (`./ch`) and Windows (`ch.bat`).  
  - For Windows-specific debugging, use `py -3` to ensure correct interpreter.

---

## Coding Standards

- Follow PEP 8 + type hints.
- Keep modules self-contained: routes, services, templates, static assets in module folder.
- Use dependency injection (`Depends`) for services; avoid global state.
- Use SQLModel sessions via shared helpers; prefer async endpoints when touching IO-bound tasks.
- Add concise comments before non-obvious logic; keep docstrings for services and complex functions.

---

## Observability & Diagnostics

- Use FastAPI logging; configure via `.env` (`LOG_LEVEL=info`/`debug`).
- For request tracing, leverage FastAPI middleware; log module name + request ID when helpful.
- When integrating AI providers, redact secrets and log truncated prompts/responses for debugging.

---

## Deployment (Future)

- Package via container (Dockerfile forthcoming) or `uvicorn app.main:app`.
- Store secrets in environment variables (never in code or `.env.example`).
- Plan migration to Postgres once concurrent multi-user access is required; document schema changes beforehand.

---

## Support & Contacts

- Planning issues → update `docs/plans/` and mention reviewers in PRs.
- Tooling/CLI issues (`./ch`, `ch.bat`, `ch.ps1`) → open repo issue with OS/Python/version details and exact command output.
- AI integration questions → document assumptions in planning docs or team chat before coding.

---

By following this guide alongside the feature development process, contributors can reliably stand up the modular FastAPI + SQLModel stack, iterate on new modules, and expose the application through the local webserver without bespoke setup steps.
