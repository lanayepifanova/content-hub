# ContentHub Minimal

Single-command FastAPI starter.

## Usage

```bash
./run.sh
```

The script will:
1. Create `.venv` with `python3 -m venv` if it does not exist.
2. Activate the environment and install `fastapi`, `uvicorn`, and `sqlalchemy`.
3. Launch `uvicorn main:app --reload` on `http://127.0.0.1:8000`.

Optional overrides:

```bash
HOST=0.0.0.0 PORT=9000 RELOAD=false ./run.sh
```

Stop the server with `Ctrl+C` and rerun the same command to restart.
