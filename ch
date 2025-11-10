#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  cat <<'EOF' >&2
Python 3.10+ is required to run ContentHub tooling.
Install it via:
  - macOS: brew install python@3.11
  - Ubuntu: sudo apt install python3 python3-venv
  - Windows (WSL): sudo apt install python3
After installing, re-run ./ch setup
EOF
  exit 1
fi

exec "$PYTHON_BIN" "$SCRIPT_DIR/ch.py" "$@"
