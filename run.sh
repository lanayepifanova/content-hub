#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=".venv"
PYTHON="python3"
RELOAD=${RELOAD:-true}
HOST=${HOST:-127.0.0.1}
PORT=${PORT:-8000}

if [ ! -d "$VENV_DIR" ]; then
  echo "[setup] creating virtualenv in $VENV_DIR"
  $PYTHON -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

pip install --upgrade pip >/dev/null
pip install -e . >/dev/null

RELOAD_FLAG=""
if [ "$RELOAD" = "true" ]; then
  RELOAD_FLAG="--reload"
fi

echo "[run] starting uvicorn on http://$HOST:$PORT (reload=$RELOAD)"
exec uvicorn app.main:app --host "$HOST" --port "$PORT" $RELOAD_FLAG
