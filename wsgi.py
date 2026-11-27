"""WSGI entry point (used by `flask` CLI, Waitress and tests)."""

from app import create_app

app = create_app()
