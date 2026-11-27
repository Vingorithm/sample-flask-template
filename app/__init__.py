"""Application factory.

Create the app with ``create_app()``; the config is chosen by the ``APP_ENV``
environment variable (development | testing | production) unless a name is
passed explicitly.
"""

from __future__ import annotations

import os

from flask import Flask

from .cli import register_cli
from .config import get_config
from .dev_assets import maybe_start_tailwind_watcher
from .errors import register_error_handlers
from .extensions import csrf, db, migrate
from .logging_setup import configure_logging
from .security import register_security_headers
from .template_helpers import register_template_helpers


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    config_class = get_config(config_name)
    app.config.from_object(config_class)
    # Optional per-machine overrides that should never be committed.
    app.config.from_pyfile("config.py", silent=True)
    config_class.validate(app)

    os.makedirs(app.instance_path, exist_ok=True)

    configure_logging(app)
    register_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_security_headers(app)
    register_template_helpers(app)
    register_cli(app)
    maybe_start_tailwind_watcher(app)
    return app


def register_extensions(app: Flask) -> None:
    db.init_app(app)
    # SQLite cannot ALTER most things in place; batch mode makes Alembic
    # migrations portable between SQLite (dev) and MySQL (prod).
    is_sqlite = app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite")
    migrate.init_app(app, db, render_as_batch=is_sqlite, compare_type=True)
    csrf.init_app(app)

    # Import models so Alembic autogenerate can see them.
    from . import models  # noqa: F401


def register_blueprints(app: Flask) -> None:
    from .blueprints.api import bp as api_bp
    from .blueprints.main import bp as main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
