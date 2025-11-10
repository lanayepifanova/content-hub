# CLI Implementation Checklist

## Environment & Tooling
- [ ] Work inside the local repository (see `AI_PROJECT_GUIDE.md`); avoid touching production systems or running privileged commands.
- [ ] Use project-provided tooling (`./ch`, `tools/dev.py`) for any setup, database seeding, or server routines; never bypass the wrappers because they keep modules registered correctly.
- [ ] Confirm Python environment + dependencies match the FastAPI/SQLModel stack already in the repo (Python ≥3.10, FastAPI, SQLModel); no global installs or system-level mutations.
- [ ] Keep `.venv` self-contained: install dependencies via `./ch setup` so module imports, SQLModel metadata, and migrations stay predictable.

## Planning Prerequisites
- [ ] Capture the CLI feature’s Step 2 **Feature Description** and Step 3 **Development Plan** in `docs/plans/` per `FEATURE_DEVELOPMENT_PROCESS.md` (and Step 1 Solution Assessment if trade-offs exist).
- [ ] Keep each step’s document under one page, bullet-focused, and committed only after user approval (“Approved Step N” handshake).
- [ ] Define atomic plan stages (≤ ~1 hour / 50 LOC) including verification steps before implementation begins.

## Architecture & Design Alignment
- [ ] Keep CLI commands Typer-based and colocated with the existing developer tooling (`tools/dev.py` or its module tree) to stay consistent with the stack.
- [ ] Ensure each command is modular: self-contained business logic, clean separation between FastAPI app modules and CLI helpers; reuse existing services instead of duplicating logic.
- [ ] Avoid schema changes unless absolutely necessary and explicitly justified; prefer existing SQLModel models and fields.

## Implementation Discipline
- [ ] Create and switch to a feature branch before starting Step 4 implementation.
- [ ] Implement plan stages sequentially; after each stage, run the defined manual smoke test and update the Step 4 implementation summary document.
- [ ] Keep commits granular per stage; do not mix planning updates with code changes.
- [ ] Use existing module conventions (`app/modules/<module_name>/...`) for any feature-specific helpers invoked by the CLI.

## Verification & Documentation
- [ ] After every stage, run the prescribed manual verification (e.g., `./ch cli <command>` smoke test) and record the outcome.
- [ ] Ensure new commands are discoverable (CLI `--help`, README snippet, or module docs) and reference the relevant planning documents.
- [ ] Conclude Step 4 with an updated implementation summary plus any module docs (`docs/plans/<module>_*.md`) required by the project guide.
- [ ] Confirm the CLI entry points are wired into automation or developer workflows so other contributors can use them without extra setup.
- [ ] Document how to reach the local FastAPI server (default `http://127.0.0.1:8000`) and which modules / routes are exposed so teammates can inspect them in a browser.

## Launcher-Specific Items (ch.py + wrappers)
- [ ] Keep `ch.py` pure stdlib (argparse/subprocess/pathlib) so it runs before dependencies install; expose `main()` for future console scripts.
- [ ] Ensure wrappers `ch` and `ch.bat` only detect Python and forward to `ch.py`; provide clear guidance when Python ≥3.10 is missing.
- [ ] Verify `ch.py setup` creates `.venv`, bootstraps pip, installs the project (`pip install -e .`), copies `.env`, and runs `init-db`.
- [ ] Ensure command handlers (`runserver`, `init-db`, `create-admin`, `create-invite`, passthrough) delegate to `tools/dev.py` via the venv interpreter and surface non-zero exits.
- [ ] Implement dependency checks (`fastapi`, `click`) and friendly remediation message (“run ./ch setup”) when they are absent.
- [ ] Smoke test `./ch runserver` (and `ch.bat runserver` on Windows) to confirm the FastAPI dev server starts, auto-loads modular routes, and is reachable via browser.

## Modular FastAPI + SQLModel Readiness
- [ ] Verify new CLI commands register modules via `app/modules/<module>/` so that FastAPI routers, templates, and static assets remain discoverable when the server runs.
- [ ] Confirm SQLModel interactions leverage existing models/session helpers; if new models are necessary, document them and surface migrations in planning docs before coding.
- [ ] When touching idea modules or future add-ons, ensure the CLI can target them (e.g., `./ch runserver --module idea_board`) without manual edits.
- [ ] Keep `.env` values (database URL, OpenAI keys) synchronized with `docs/plans` so running the local server + browser walkthrough works for every teammate.
