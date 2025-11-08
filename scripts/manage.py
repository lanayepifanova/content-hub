#!/usr/bin/env python3
"""
Helper entrypoint for Content Hub.

Usage examples:
  python3 scripts/manage.py dev
  python3 scripts/manage.py build
  python3 scripts/manage.py preview
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NPM = shutil.which("npm")


def run(cmd: list[str]) -> int:
    """Run a subprocess inside the project root."""
    return subprocess.call(cmd, cwd=ROOT)


def ensure_prereqs() -> None:
    if not NPM:
        sys.exit("npm is required but was not found on PATH.")


def ensure_dependencies() -> None:
    node_modules = ROOT / "node_modules"
    if node_modules.exists():
        return
    print("Installing npm dependencies…")
    code = run([NPM, "install"])
    if code != 0:
        sys.exit(code)


def warn_if_env_missing() -> None:
    env_file = ROOT / ".env"
    if not env_file.exists():
        print("⚠️  .env not found. Firestore may fail to connect.", file=sys.stderr)


def run_dev(args) -> None:  # noqa: ARG001
    ensure_dependencies()
    warn_if_env_missing()
    sys.exit(run([NPM, "run", "dev"]))


def run_build(args) -> None:  # noqa: ARG001
    ensure_dependencies()
    warn_if_env_missing()
    sys.exit(run([NPM, "run", "build"]))


def run_preview(args) -> None:  # noqa: ARG001
    ensure_dependencies()
    warn_if_env_missing()
    sys.exit(run([NPM, "run", "preview"]))


def main() -> None:
    ensure_prereqs()
    parser = argparse.ArgumentParser(description="Content Hub helper CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("dev", help="Install dependencies if needed, then run `npm run dev`.").set_defaults(
        func=run_dev
    )
    sub.add_parser("build", help="Install dependencies then run `npm run build`.").set_defaults(func=run_build)
    sub.add_parser("preview", help="Serve the production build locally.").set_defaults(func=run_preview)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
