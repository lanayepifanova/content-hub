# CLI Implementation Plan

Plan tailored to ContentHub’s goal of consolidating dev workflows behind a single cross-platform launcher (`ch.py`) with thin shell wrappers so teammates can stand up the modular FastAPI + SQLModel stack (and browse it locally) in minutes, per `AI_PROJECT_GUIDE.md` and `FEATURE_DEVELOPMENT_PROCESS.md`.

## Objective
Implement a single cross-platform Python launcher (`ch.py`) while keeping thin `ch` (Bash) and `ch.bat` (Batch) wrappers. The wrappers must (a) show a friendly message when Python ≥3.10 is unavailable and (b) otherwise forward all arguments to `ch.py`. The launcher needs feature parity with the current Bash helper and the Windows approach described in legacy planning notes (e.g., `CLI_SYNC_PLAN.md` if present).

## Deliverables
1. `ch.py` – Python entry point exposing commands `setup`, `runserver`, `init-db`, `create-admin`, `create-invite`, plus default passthrough to `tools/dev.py`.
2. Updated `ch` – Bash wrapper that checks for Python (`python3` then `python`) before delegating to `ch.py`.
3. Updated `ch.bat` – pure CMD batch wrapper that checks `py -3` then `python` and forwards args to `ch.py`.
4. Optional `ch.ps1` – PowerShell helper mirroring Batch behavior for PS-first users.
5. Optional `pyproject.toml` console-script entry (`ch = "ch:main"`) for `pipx`/editable installs.

## Functional Requirements
- `setup`
  - Create `.venv` (using base interpreter) if missing.
  - Ensure `pip` via `ensurepip`, upgrade `pip`, then `pip install -e .`.
  - Create `.env` from `.env.example` if missing; warn if template absent.
  - Run `init-db` through the venv interpreter; fail `setup` if it exits non-zero.
- `runserver`, `init-db`, `create-admin`, `create-invite`
  - Ensure dependencies (`fastapi`, `click`) are importable; instruct running `./ch setup` otherwise.
  - Forward to `tools/dev.py` via the venv interpreter, preserving exit codes and exposing FastAPI modules so the local browser can hit `http://127.0.0.1:8000`.
- Unknown commands
  - Pass through to `tools/dev.py`; if it returns non-zero, print a helpful message plus concise `ch` help, then exit 1.
- Dependency check
  - Attempt `import fastapi, click`. On failure, emit guidance to run `./ch setup`.
- Messaging / exit codes
  - Match existing UX: clear success/failure text, minimal noise, deterministic exit codes.

## Implementation Steps
1. **Introduce `ch.py`**
   - Detect base interpreter via `sys.executable`, overridable with `CH_PYTHON`.
   - Derive paths: `SCRIPT_DIR`, `.venv`, `tools/dev.py`.
   - Build logger helpers (ANSI-aware) and subprocess wrapper utilities.
   - Implement helpers:
     - `python_in_venv()` to resolve platform-specific venv interpreter.
     - `run_cmd(args, check=False)` for consistent logging.
     - `ensure_pip(venv_python)` to verify/install `pip`.
     - `create_env_file()` to copy `.env.example`.
     - `ensure_cli_ready()` to import `fastapi`/`click`.
     - `dev_invoke(venv_python, *args)` to execute `tools/dev.py`.
   - Implement argparse-based CLI dispatch covering the required commands with passthrough fallback.
2. **Update POSIX wrapper (`ch`)**
   - Resolve interpreter (`python3` fallback `python`).
   - On missing interpreter: print friendly guidance referencing python.org/brew + `PATH`.
   - Otherwise `exec "$PY" "$SCRIPT_DIR/ch.py" "$@"`; keep executable bit.
3. **Update Windows wrapper (`ch.bat`)**
   - Try `py -3` then `python`; store chosen interpreter.
   - On failure: echo guidance referencing python.org/winget and requirement for 3.10+; `exit /b 1`.
   - Otherwise run `"%PY%" "%~dp0ch.py" %*` (quotes for spaces).
4. **(Optional) PowerShell helper & console script**
   - Add `ch.ps1` mirroring CMD logic if we want native PS usage.
   - Update `pyproject.toml` with `[project.scripts] ch = "ch:main"` and ensure `ch.py` exposes `def main(argv: list[str] | None = None) -> int`.
5. **Testing & Docs**
   - Document workflows in README or `docs/plans`, including how to run `./ch runserver` and open the FastAPI UI in a browser.
   - Add notes to `CLI_IMPLEMENTATION_CHECKLIST.md` Step 4 summary once manual verification is done, especially around local webserver smoke tests.

## File-by-File Tasks
- `ch.py`
  - Pure-stdlib CLI (argparse/subprocess/pathlib) so it runs even before dependencies install.
  - Avoid importing project modules except dependency checks post-setup.
  - Provide `--help`, friendly error handling, and colorized logs when supported.
  - Expose convenience flags (e.g., `--host`, `--port`) for `runserver` to make browser-based testing painless.
- `ch` (Bash)
  - Minimal detection + exec. Reuse existing colored output for missing Python message.
- `ch.bat`
  - CMD-only script; no PowerShell commands.
- `ch.ps1` (optional)
  - Mirror behavior; mention ExecutionPolicy guidance in comments.
- `pyproject.toml`
  - Add console script section when ready; ensure `project.scripts` respects packaging rules.

## Acceptance Criteria
- Fresh POSIX checkout without `.venv`: `./ch setup` bootstraps env, installs deps, creates `.env`, runs `init-db`, exits 0; `./ch runserver` starts the FastAPI server and serves UI at `http://127.0.0.1:8000` (verified in browser).
- Fresh Windows checkout relying on `py -3`: `ch.bat setup` completes same flow; `ch.bat runserver` launches the FastAPI server and serves UI at the same address.
- Missing Python: wrappers emit guidance and exit 1 without running `ch.py`.
- Existing DB: `setup` reruns `init-db` safely without data loss.
- Unknown command: wrappers forward to `ch.py`, which forwards to `tools/dev.py`; on non-zero exit, help text + exit 1.

## Refinements & Edge Cases
- Require Python ≥3.10; mention in wrapper guidance and `ch.py` errors.
- If `ensurepip` absent/fails, instruct user to repair Python install and provide quick commands (`py -3 -m ensurepip --upgrade`, etc.).
- Keep path handling robust (quote everything).
- Keep imports lazy to avoid slow startup and to run on Windows without WSL.
- Document how to run PowerShell helper if ExecutionPolicy blocks it.
- Recommend CI coverage for Linux/macOS/Windows wrappers; simulate missing Python by PATH shims when possible.
- `.env` creation: warn (not fail) if `.env.example` is missing; log location of generated file and remind users to refresh the server after editing credentials or feature flags.

## Test Commands (Manual Smoke)
- POSIX: `rm -rf .venv data && ./ch setup && ./ch runserver --no-reload` (open browser at `http://127.0.0.1:8000` to confirm module routes); `./ch not-a-command` (expect help + exit 1).
- Windows CMD: `rmdir /s /q .venv & rmdir /s /q data & ch.bat setup & ch.bat runserver --no-reload` (open browser at same URL); `ch.bat not-a-command` (expect help + exit 1).

## Rollout Plan
1. Land `ch.py` + wrapper updates behind a feature branch/PR.
2. Validate on Linux, macOS, Windows (local or CI runners).
3. Update onboarding docs/README to reference `ch` workflows and optional console script install.
4. After stabilization, consider optional PowerShell helper or additional automation coverage.
