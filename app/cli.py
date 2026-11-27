"""Custom `flask` CLI commands."""

from __future__ import annotations

import click
from flask import Flask

from .extensions import db


def register_cli(app: Flask) -> None:
    @app.cli.command("seed")
    def seed() -> None:
        """Insert sample data for local development."""
        from .models import User

        if app.config["ENV_NAME"] == "production":
            raise click.ClickException("Refusing to seed a production database.")

        if db.session.scalar(db.select(User).filter_by(email="demo@example.com")):
            click.echo("Seed data already present.")
            return

        db.session.add(User(email="demo@example.com", name="Demo User"))
        db.session.commit()
        click.echo("Seed data inserted.")

    @app.cli.command("check-db")
    def check_db() -> None:
        """Verify the database connection from the current config."""
        db.session.execute(db.text("SELECT 1"))
        click.echo(f"Database OK: {db.engine.url.render_as_string(hide_password=True)}")
