# ch_launcher – Step 2 Feature Description

## Problem
Manual environment setup and OS-specific wrappers make it slow for contributors to run the modular FastAPI + SQLModel app locally. We need a single Python launcher (`ch.py`) with lightweight shell/batch wrappers so anyone can bootstrap the stack and browse the app via `http://127.0.0.1:8000` in minutes.

## User Stories
- As a new contributor, I want `./ch setup` to create the virtualenv, install dependencies, and prep the database so I can start building without memorizing bespoke steps.
- As a backend engineer, I want `./ch runserver` (and `ch.bat runserver`) to expose every registered FastAPI module so I can inspect the UI in my browser during development.
- As a maintainer, I want all CLI commands to reuse `tools/dev.py` so business logic stays centralized and future modules inherit the same workflows automatically.
- As a Windows teammate, I want a native `ch.bat` wrapper that handles Python detection and forwards arguments exactly like the Bash wrapper so cross-platform parity is guaranteed.

## Core Requirements
- Provide `ch.py` with commands: `setup`, `runserver`, `init-db`, `create-admin`, `create-invite`, plus passthrough to `tools/dev.py` for any other arguments.
- Keep wrappers (`ch`, `ch.bat`, optional `ch.ps1`) extremely thin: detect Python ≥3.10, show friendly guidance if missing, otherwise exec `ch.py`.
- `setup` must create `.venv`, ensure/upgrade `pip`, install the project editable, copy `.env` from `.env.example` when available, and run `init-db`.
- Runtime commands must ensure FastAPI + Click are installed, then forward to `tools/dev.py` through the venv interpreter, preserving exit codes and stdout/stderr.
- Unknown commands should forward to `tools/dev.py` and on failure print contextual help plus remediation (“run ./ch setup”).

## User Flow
1. Contributor clones the repo and runs `./ch setup` (or `ch.bat setup` on Windows).
2. Launcher creates/initializes `.venv`, installs dependencies, copies `.env`, and seeds the SQLite DB via `init-db`.
3. Contributor runs `./ch runserver` to start the FastAPI dev server; output includes host/port hints.
4. Contributor visits `http://127.0.0.1:8000` in a browser to verify modular routes, tags, and idea modules load correctly.
5. For admin tasks (`create-admin`, `create-invite`) or other `tools/dev.py` commands, contributor keeps using `./ch <command>`; errors display guidance.

## Success Criteria
- Fresh checkout on macOS/Linux: `./ch setup && ./ch runserver` completes without manual edits and the UI is reachable in a browser.
- Fresh checkout on Windows (CMD): `ch.bat setup && ch.bat runserver` works identically, with clear messages if Python is missing.
- All commands delegate to `tools/dev.py`, keeping business logic centralized and modules auto-registered.
- CLI help text clearly explains available commands, dependency expectations, and how to access the local webserver.
- Documentation (README/onboarding) references `ch.py` workflows so new contributors no longer rely on ad-hoc instructions.
