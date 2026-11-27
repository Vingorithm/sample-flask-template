"""Configuration classes, driven by environment variables (.env)."""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from sqlalchemy.engine import URL

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_str(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    return value if value not in (None, "") else default


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value not in (None, "") else default


def mysql_url_from_env() -> str | None:
    """Build a MySQL URL from DB_* variables (password is escaped safely)."""
    host = env_str("DB_HOST")
    if not host:
        return None
    url = URL.create(
        "mysql+pymysql",
        username=env_str("DB_USER"),
        password=env_str("DB_PASSWORD"),
        host=host,
        port=env_int("DB_PORT", 3306),
        database=env_str("DB_NAME"),
        query={"charset": "utf8mb4"},
    )
    return url.render_as_string(hide_password=False)


class Config:
    ENV_NAME = "base"

    APP_NAME = env_str("APP_NAME", "Flask App")
    SECRET_KEY = env_str("SECRET_KEY")

    # Database
    SQLALCHEMY_DATABASE_URI: str | None = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = {"pool_pre_ping": True}

    # Sessions / cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=env_int("SESSION_LIFETIME_HOURS", 12))

    # Forms / uploads
    WTF_CSRF_TIME_LIMIT = None  # token valid for the whole session
    MAX_CONTENT_LENGTH = env_int("MAX_UPLOAD_MB", 16) * 1024 * 1024

    # Logging
    LOG_LEVEL = env_str("LOG_LEVEL", "INFO")
    LOG_TO_FILE = env_bool("LOG_TO_FILE", False)
    LOG_DIR = env_str("LOG_DIR", str(BASE_DIR / "logs"))
    LOG_MAX_BYTES = env_int("LOG_MAX_MB", 10) * 1024 * 1024
    LOG_BACKUP_COUNT = env_int("LOG_BACKUP_COUNT", 10)

    @classmethod
    def validate(cls, app: Flask) -> None:
        """Hook for environment-specific sanity checks."""


class DevelopmentConfig(Config):
    ENV_NAME = "development"
    DEBUG = True
    SECRET_KEY = env_str("SECRET_KEY", "dev-insecure-secret-key")
    SQLALCHEMY_DATABASE_URI = env_str(
        "DATABASE_URL", f"sqlite:///{(BASE_DIR / 'instance' / 'dev.db').as_posix()}"
    )
    TEMPLATES_AUTO_RELOAD = True


class TestingConfig(Config):
    ENV_NAME = "testing"
    TESTING = True
    SECRET_KEY = "testing-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    LOG_TO_FILE = False


class ProductionConfig(Config):
    ENV_NAME = "production"
    DEBUG = False

    SQLALCHEMY_DATABASE_URI = env_str("DATABASE_URL") or mysql_url_from_env()
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        # Must be lower than MySQL's wait_timeout (default 28800s, often
        # lowered on shared hosts) so stale connections are recycled.
        "pool_recycle": env_int("DB_POOL_RECYCLE", 280),
        # Keep pool_size >= WAITRESS_THREADS so threads don't wait for a connection.
        "pool_size": env_int("DB_POOL_SIZE", 10),
        "max_overflow": env_int("DB_MAX_OVERFLOW", 10),
        "pool_timeout": env_int("DB_POOL_TIMEOUT", 30),
    }

    # Served over HTTPS by Apache.
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"
    LOG_TO_FILE = env_bool("LOG_TO_FILE", True)

    @classmethod
    def validate(cls, app: Flask) -> None:
        missing = [
            key for key in ("SECRET_KEY", "SQLALCHEMY_DATABASE_URI") if not app.config.get(key)
        ]
        if missing:
            raise RuntimeError(
                f"Production config incomplete, set these in .env: {', '.join(missing)}"
            )
        if len(app.config["SECRET_KEY"]) < 32:
            raise RuntimeError("SECRET_KEY must be at least 32 characters in production.")


CONFIGS: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name: str | None = None) -> type[Config]:
    name = (name or env_str("APP_ENV", "development")).lower()
    try:
        return CONFIGS[name]
    except KeyError:
        raise RuntimeError(f"Unknown APP_ENV '{name}'. Use one of: {', '.join(CONFIGS)}") from None
