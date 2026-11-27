"""Logging: console always, rotating file when LOG_TO_FILE is on.

Handlers are attached to the root logger so Flask, SQLAlchemy and Waitress
all write to the same place.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask
from flask.logging import default_handler

LOG_FORMAT = "%(asctime)s %(levelname)-8s [%(name)s] %(message)s"


def configure_logging(app: Flask) -> None:
    app.logger.removeHandler(default_handler)
    if app.testing:
        return

    root = logging.getLogger()
    root.setLevel(app.config["LOG_LEVEL"].upper())

    # create_app() may run more than once in a process; don't stack handlers.
    if getattr(root, "_flask_app_configured", False):
        return

    formatter = logging.Formatter(LOG_FORMAT)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    if app.config["LOG_TO_FILE"]:
        log_dir = Path(app.config["LOG_DIR"])
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=app.config["LOG_MAX_BYTES"],
            backupCount=app.config["LOG_BACKUP_COUNT"],
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    root._flask_app_configured = True  # type: ignore[attr-defined]
