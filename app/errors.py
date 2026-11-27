"""Error handlers: HTML pages for browsers, JSON for /api and JSON clients."""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

from .extensions import db


def wants_json() -> bool:
    if request.path.startswith("/api/"):
        return True
    best = request.accept_mimetypes.best_match(["application/json", "text/html"])
    return best == "application/json"


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        code = error.code or 500
        if code >= 500:
            # Leave the session usable for the next request.
            db.session.rollback()
            app.logger.exception("Server error on %s %s", request.method, request.path)

        if wants_json():
            return jsonify(error=error.name, message=error.description, status=code), code
        return render_template("errors/error.html", error=error, code=code), code
