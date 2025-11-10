# ch_launcher – Step 3 Development Plan

Each stage is scoped to ≤1 hour (~≤50 LOC) and assumes Step 2 is approved.

## Stage 1 – `ch.py` Skeleton & Utilities
- **Goal**: Create the Python launcher file with argparse wiring, logging helpers, and cross-platform path utilities.
- **Dependencies**: Step 2 description, existing `tools/dev.py` behavior, repo root structure.
- **Changes**:
  - Add `ch.py` with `main(argv=None)` entrypoint, argparse command scaffolding (`setup`, `runserver`, etc.).
  - Implement helper functions: path resolvers (`SCRIPT_DIR`, `.venv`), `python_in_venv()`, `run_cmd()`, color-aware logger.
  - Add `dev_invoke()` stub that shells out to `tools/dev.py` through a provided interpreter.
- **Verification**: `python ch.py --help` shows commands; `python ch.py runserver --help` works (even though it won’t execute yet).
- **Risks**: Argument parsing drift versus existing wrappers; mitigate by mirroring current usage strings.

## Stage 2 – `setup` Command (env + deps)
- **Goal**: Implement environment bootstrap inside `ch.py`.
- **Dependencies**: Stage 1 helpers.
- **Changes**:
  - Detect/create `.venv` using base interpreter (`CH_PYTHON` override).
  - Add `ensure_pip()`, `pip install --upgrade pip`, `pip install -e .`.
  - Copy `.env.example` → `.env` when missing; warn if template absent.
  - Run `init-db` via `dev_invoke()` using venv interpreter.
- **Verification**: From clean checkout (`rm -rf .venv data`), run `python ch.py setup`; confirm `.venv` exists, editable install succeeds, `.env` created, `init-db` logs success.
- **Risks**: `ensurepip` unavailable on some Python installs; handle with guidance message instead of silent failure.

## Stage 3 – Runtime Commands & Dependency Checks
- **Goal**: Wire `runserver`, `init-db`, `create-admin`, `create-invite`, and passthrough behavior.
- **Dependencies**: Stage 2 (venv + dev invocation).
- **Changes**:
  - Implement `ensure_cli_ready()` that runs `fastapi` + `click` import test via venv interpreter; show “run ./ch setup” if missing.
  - For each command, call `dev_invoke(venv_python, command, *args)` and relay exit code/output.
  - Unknown commands: forward argv to `tools/dev.py`; on non-zero exit, print help snippet plus remediation.
  - Allow `runserver` flags (`--host`, `--port`, `--reload`) by passing them through.
- **Verification**: After `python ch.py setup`, run `python ch.py runserver --help`; then run `python ch.py init-db`; simulate unknown command (`python ch.py foo`) to ensure help message triggers.
- **Risks**: Infinite recursion/incorrect interpreter selection; guard by explicitly invoking venv python path.

## Stage 4 – Wrapper Updates (`ch`, `ch.bat`, optional `ch.ps1`)
- **Goal**: Replace existing wrappers with thin forwarders that detect Python and delegate to `ch.py`.
- **Dependencies**: Stage 3 (launcher functionality in place).
- **Changes**:
  - POSIX `ch`: detect `python3`/`python`, print friendly error if missing, `exec "$PY" "$DIR/ch.py" "$@"`.
  - Windows `ch.bat`: try `py -3` then `python`, print guidance if missing, run `"%PY%" "%~dp0ch.py" %*`.
  - Optional `ch.ps1`: mirror detection logic, include ExecutionPolicy guidance in comments.
- **Verification**: On macOS/Linux run `./ch --help`, `./ch runserver --help`; on Windows (or `cmd` via emulation) run `ch.bat --help`. Temporarily rename `python3` to simulate missing interpreter and confirm error text.
- **Risks**: Permission bits or CRLF endings breaking wrappers; verify file modes and line endings after edit.

## Stage 5 – Docs, Help Text, and Smoke Tests
- **Goal**: Finalize documentation and manual verification steps.
- **Dependencies**: Stages 1-4 complete.
- **Changes**:
  - Update README/onboarding snippets to reference `./ch setup` and browser URL.
  - Ensure `ch.py --help` includes usage instructions + link to docs.
  - Document verification results in Step 4 implementation summary and update `CLI_IMPLEMENTATION_CHECKLIST.md` if needed.
  - (Optional) Add `pyproject.toml` console script entry once `main()` is stable.
- **Verification**:
  - Run end-to-end smoke tests: `rm -rf .venv data && ./ch setup && ./ch runserver --no-reload` (POSIX) plus Windows equivalent; visit `http://127.0.0.1:8000`.
  - Confirm README instructions render correctly.
- **Risks**: Docs drifting from actual behavior; mitigate by copy-pasting commands from actual terminal session.
