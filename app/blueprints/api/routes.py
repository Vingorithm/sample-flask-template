from flask import current_app, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ...extensions import db
from . import bp


@bp.get("/health")
def health():
    """Liveness + DB check for monitoring and the deploy smoke test."""
    try:
        db.session.execute(text("SELECT 1"))
        database = "ok"
    except SQLAlchemyError:
        current_app.logger.exception("Health check: database unreachable")
        db.session.rollback()
        database = "error"

    healthy = database == "ok"
    return jsonify(status="ok" if healthy else "degraded", database=database), (
        200 if healthy else 503
    )
