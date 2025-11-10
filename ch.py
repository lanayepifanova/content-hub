"""
ContentHub cross-platform launcher.

Stage 1: CLI skeleton, logging utilities, and shared helpers.
Subsequent stages will fill in environment bootstrap and runtime command logic.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Sequence
from types import SimpleNamespace

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR
VENV_DIR = REPO_ROOT / ".venv"
DEV_TOOL = REPO_ROOT / "tools" / "dev.py"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = "8000"


class Ansi:
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    RESET = "\033[0m"


def supports_color() -> bool:
    return sys.stdout.isatty() and os.name != "nt"


def colorize(text: str, color: str) -> str:
    if not supports_color():
        return text
    return f"{color}{text}{Ansi.RESET}"


def info(msg: str) -> None:
    print(colorize(msg, Ansi.CYAN))


def success(msg: str) -> None:
    print(colorize(msg, Ansi.GREEN))


def warn(msg: str) -> None:
    print(colorize(msg, Ansi.YELLOW), file=sys.stderr)


def error(msg: str) -> None:
    print(colorize(msg, Ansi.RED), file=sys.stderr)


def base_python() -> str:
    override = os.environ.get("CH_PYTHON")
    if override:
        return override
    return sys.executable or "python3"


def python_in_venv() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def run_cmd(
    args: Sequence[str],
    *,
    check: bool = False,
    env: dict | None = None,
) -> subprocess.CompletedProcess:
    info(f"$ {' '.join(args)}")
    return subprocess.run(args, check=check, env=env)


def dev_invoke(python_exe: str, argv: Iterable[str]) -> int:
    cmd = [python_exe, str(DEV_TOOL), *argv]
    result = run_cmd(cmd)
    return result.returncode


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ch",
        description="ContentHub launcher – wraps tools/dev.py for cross-platform workflows.",
    )
    subparsers = p.add_subparsers(dest="command")

    subparsers.add_parser("setup", help="Create virtualenv, install deps, init database.")

    runserver = subparsers.add_parser("runserver", help="Start the FastAPI development server.")
    runserver.add_argument("--host", default=DEFAULT_HOST, help="Host to bind (default: 127.0.0.1)")
    runserver.add_argument("--port", default=DEFAULT_PORT, help="Port to bind (default: 8000)")
    runserver.add_argument("--reload", action="store_true", help="Enable uvicorn reload")

    subparsers.add_parser("init-db", help="Initialize database / run seeds.")
    subparsers.add_parser("create-admin", help="Create an admin user.")
    subparsers.add_parser("create-invite", help="Create an invite token.")

    passthrough = subparsers.add_parser("dev", help="Pass remaining args directly to tools/dev.py")
    passthrough.add_argument("dev_args", nargs=argparse.REMAINDER)

    return p


def ensure_venv() -> str:
    """
    Create the .venv folder if missing and return the interpreter path.
    """
    if not VENV_DIR.exists():
        info("Creating virtual environment (.venv)...")
        run_cmd([base_python(), "-m", "venv", str(VENV_DIR)], check=True)
    venv_python = python_in_venv()
    if not venv_python.exists():
        raise SystemExit("Virtualenv python not found after creation.")
    return str(venv_python)


def ensure_pip(python_exe: str) -> None:
    """Make sure pip is available inside the venv."""
    probe = subprocess.run(
        [python_exe, "-m", "pip", "--version"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if probe.returncode == 0:
        return

    warn("pip missing inside .venv – running ensurepip (requires Python ensurepip module).")
    ensure_result = subprocess.run([python_exe, "-m", "ensurepip", "--upgrade"])
    if ensure_result.returncode != 0:
        raise SystemExit(
            "Unable to install pip in the virtualenv. Repair your Python installation or reinstall with pip support."
        )


def pip_install(python_exe: str, *args: str) -> None:
    run_cmd([python_exe, "-m", "pip", *args], check=True)


def install_project(python_exe: str) -> None:
    try:
        pip_install(python_exe, "install", "-e", ".")
    except subprocess.CalledProcessError:
        warn("pip install -e . failed; falling back to .pth injection (offline mode).")
        site_packages = subprocess.check_output(
            [
                python_exe,
                "-c",
                "import site; import sys; "
                "paths = site.getsitepackages() if hasattr(site, 'getsitepackages') else [site.getusersitepackages()]; "
                "print(paths[0])",
            ],
            text=True,
        ).strip()
        pth_path = Path(site_packages) / "contenthub.pth"
        pth_path.write_text(str(REPO_ROOT))
        success(f"Linked repo into venv via {pth_path}")


def create_env_file() -> None:
    env_file = REPO_ROOT / ".env"
    template = REPO_ROOT / ".env.example"
    if env_file.exists():
        return
    if not template.exists():
        warn("No .env.example found; skipping .env creation (create manually if needed).")
        return
    shutil.copyfile(template, env_file)
    success("Created .env from .env.example")


def run_init_db(python_exe: str) -> int:
    return dev_invoke(python_exe, ["init-db"])


def ensure_cli_ready(python_exe: str) -> bool:
    check_script = (
        "import importlib.util as u\n"
        "missing=[name for name in ('fastapi','click') if u.find_spec(name) is None]\n"
        "import sys\n"
        "sys.exit(0 if not missing else 1)"
    )
    result = subprocess.run([python_exe, "-c", check_script])
    if result.returncode == 0:
        return True
    error("Missing dependencies (fastapi and/or click). Run ./ch setup to reinstall.")
    return False


def venv_python_or_die() -> str:
    venv_python = python_in_venv()
    if not venv_python.exists():
        error("Virtualenv not found. Run ./ch setup first.")
        raise SystemExit(1)
    return str(venv_python)


def handle_setup(_args: argparse.Namespace) -> int:
    """
    Stage 2: bootstrap environment, install dependencies, run init-db.
    """
    try:
        venv_python = ensure_venv()
        ensure_pip(venv_python)
        info("Installing project dependencies (editable)...")
        install_project(venv_python)
        create_env_file()
        info("Running init-db via tools/dev.py...")
        exit_code = run_init_db(venv_python)
        if exit_code != 0:
            error("init-db failed; see output above.")
            return exit_code
        success("Setup complete! Use ./ch runserver to start the app.")
        return 0
    except subprocess.CalledProcessError as exc:
        error(f"Command failed with exit code {exc.returncode}: {' '.join(exc.cmd)}")
        return exc.returncode or 1


def handle_runserver(args: argparse.Namespace) -> int:
    venv_python = venv_python_or_die()
    if not ensure_cli_ready(venv_python):
        return 1
    payload = ["runserver", "--host", args.host, "--port", str(args.port)]
    if args.reload:
        payload.append("--reload")
    exit_code = dev_invoke(venv_python, payload)
    if exit_code != 0:
        error("runserver failed; see logs above.")
    return exit_code


def handle_simple(command: str, _args: argparse.Namespace) -> int:
    venv_python = venv_python_or_die()
    if not ensure_cli_ready(venv_python):
        return 1
    exit_code = dev_invoke(venv_python, [command])
    if exit_code != 0:
        error(f"{command} failed; see logs above.")
    return exit_code


def handle_passthrough(args: argparse.Namespace) -> int:
    venv_python = venv_python_or_die()
    if not args.dev_args:
        parser().print_help()
        return 1
    exit_code = dev_invoke(venv_python, args.dev_args)
    if exit_code != 0:
        warn("tools/dev.py returned non-zero. Run ./ch --help for usage or ./ch setup if dependencies changed.")
    return exit_code


KNOWN_COMMANDS = {"setup", "runserver", "init-db", "create-admin", "create-invite", "dev"}


def main(argv: Sequence[str] | None = None) -> int:
    raw_args = list(argv) if argv is not None else sys.argv[1:]
    if raw_args and raw_args[0] in {"-h", "--help"}:
        parser().print_help()
        return 0
    if raw_args and raw_args[0] not in KNOWN_COMMANDS:
        # Passthrough to tools/dev.py automatically for unknown commands.
        return handle_passthrough(SimpleNamespace(dev_args=raw_args))

    args = parser().parse_args(raw_args)

    if args.command == "setup":
        return handle_setup(args)
    if args.command == "runserver":
        return handle_runserver(args)
    if args.command in {"init-db", "create-admin", "create-invite"}:
        return handle_simple(args.command, args)
    if args.command == "dev":
        return handle_passthrough(args)

    # No subcommand provided: show help by default
    parser().print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
