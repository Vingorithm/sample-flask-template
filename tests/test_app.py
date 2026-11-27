import pytest

from app import create_app
from app.extensions import db
from app.models import User


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<html" in response.data


def test_security_headers(client):
    response = client.get("/")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "SAMEORIGIN"


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": "ok"}


def test_404_html(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert b"Error 404" in response.data


def test_404_json_for_api(client):
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404
    assert response.get_json()["status"] == 404


def test_seed_command(app, runner):
    result = runner.invoke(args=["seed"])
    assert "inserted" in result.output
    assert db.session.scalar(db.select(User).filter_by(email="demo@example.com"))


def test_production_requires_secret(monkeypatch):
    from app.config import ProductionConfig

    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", None)
    monkeypatch.setattr(ProductionConfig, "SQLALCHEMY_DATABASE_URI", "sqlite://")
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app("production")
