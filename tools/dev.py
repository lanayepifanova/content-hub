#!/usr/bin/env python3
"""
Developer utility CLI (stub) invoked via ch.py.

Replace these implementations with real FastAPI/SQLModel workflows as the app evolves.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from pathlib import Path
from typing import Sequence

DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "contenthub.db"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(exist_ok=True)


def cmd_init_db(_args: argparse.Namespace) -> int:
    ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS ideas (id INTEGER PRIMARY KEY, title TEXT)")
    conn.commit()
    conn.close()
    print(f"Initialized database at {DB_PATH}")
    return 0


def cmd_runserver(args: argparse.Namespace) -> int:
    ensure_data_dir()
    host = args.host
    port = args.port
    print("Starting stub development server...")
    print(f"Simulated FastAPI app available at http://{host}:{port}")
    if args.reload:
        print("--reload requested (not needed for stub server).")
    automation = os.environ.get("CH_AUTOMATION") == "1"
    if automation:
        print("Automation mode: skipping network bind; assuming success.")
        return 0

    print("Press Ctrl+C to stop.")
    from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

    try:
        server = ThreadingHTTPServer((host, port), SimpleHTTPRequestHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
        return 0
    except OSError as exc:
        print(f"Unable to bind to {host}:{port}: {exc}", file=sys.stderr)
        return 1
    return 0


def cmd_create_admin(_args: argparse.Namespace) -> int:
    print("create-admin not fully implemented yet; this is a placeholder.")
    return 0


def cmd_create_invite(_args: argparse.Namespace) -> int:
    print("create-invite not fully implemented yet; this is a placeholder.")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tools/dev.py", description="ContentHub dev utilities")
    sub = p.add_subparsers(dest="command", required=True)

    runserver = sub.add_parser("runserver", help="Start development server")
    runserver.add_argument("--host", default="127.0.0.1")
    runserver.add_argument("--port", type=int, default=8000)
    runserver.add_argument("--reload", action="store_true", help="Ignored in stub server (for compatibility).")
    runserver.set_defaults(func=cmd_runserver)

    init_db = sub.add_parser("init-db", help="Initialize database")
    init_db.set_defaults(func=cmd_init_db)

    create_admin = sub.add_parser("create-admin", help="Create admin user")
    create_admin.set_defaults(func=cmd_create_admin)

    create_invite = sub.add_parser("create-invite", help="Create invite token")
    create_invite.set_defaults(func=cmd_create_invite)

    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
