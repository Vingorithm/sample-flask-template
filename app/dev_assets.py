"""Run the Tailwind watcher automatically with `flask run` in development.

Only starts when all of these hold:
- TAILWIND_WATCH is on (default in development, off elsewhere),
- the current CLI command is `flask run` (not `flask db`, `flask seed`, tests, Waitress),
- we are in the reloader's parent process, so code reloads don't spawn duplicates.

The watcher is stopped when the Flask process exits.
"""

from __future__ import annotations

import atexit
import os
import shutil
import signal
import subprocess
import sys
from pathlib import Path

import click
from flask import Flask
from werkzeug.serving import is_running_from_reloader

INPUT_CSS = "app/static/src/input.css"
OUTPUT_CSS = "app/static/css/app.css"
TAILWIND_CLI = Path("node_modules/@tailwindcss/cli/dist/index.mjs")


def _is_flask_run() -> bool:
    ctx = click.get_current_context(silent=True)
    return ctx is not None and ctx.command.name == "run"


def maybe_start_tailwind_watcher(app: Flask) -> None:
    if not app.config.get("TAILWIND_WATCH") or not _is_flask_run() or is_running_from_reloader():
        return

    root = Path(app.root_path).parent
    node = shutil.which("node")
    if node is None:
        app.logger.warning("Tailwind watcher not started: Node.js not found in PATH.")
        return
    if not (root / TAILWIND_CLI).is_file():
        app.logger.warning("Tailwind watcher not started: run `npm install` first.")
        return

    # Call node directly (not npm.cmd) so Windows never shows the
    # "Terminate batch job (Y/N)?" prompt on Ctrl+C.
    cmd = [node, str(TAILWIND_CLI), "-i", INPUT_CSS, "-o", OUTPUT_CSS, "--watch=always"]
    kwargs: dict = {"cwd": root, "stdin": subprocess.DEVNULL}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True

    process = subprocess.Popen(cmd, **kwargs)
    atexit.register(_stop, process)
    click.secho(f" * Tailwind watcher running (pid {process.pid})", fg="cyan")


def _stop(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    if sys.platform == "win32":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(process.pid)],
            capture_output=True,
            check=False,
        )
    else:
        os.killpg(process.pid, signal.SIGTERM)
