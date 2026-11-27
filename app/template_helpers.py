"""Values and helpers available in every Jinja template."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from flask import Flask, current_app, url_for


def asset_url(filename: str) -> str:
    """url_for('static') plus ?v=<mtime> so browsers refetch changed files.

    Apache serves /static with long cache headers, so the version query
    string is what makes a new deploy visible immediately.
    """
    path = Path(current_app.static_folder or "") / filename
    version = int(path.stat().st_mtime) if path.is_file() else None
    return url_for("static", filename=filename, v=version)


def register_template_helpers(app: Flask) -> None:
    @app.context_processor
    def inject_globals() -> dict:
        return {
            "app_name": app.config["APP_NAME"],
            "current_year": datetime.now(UTC).year,
            "asset_url": asset_url,
        }
