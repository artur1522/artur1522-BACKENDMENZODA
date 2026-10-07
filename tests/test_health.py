"""Tests del endpoint /api/health (sin tocar la base de datos)."""

import os

from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test")
os.environ.setdefault("JWT_SECRET", "test-secret")

from app.core.config import get_settings  # noqa: E402
from app.main import create_app  # noqa: E402


def test_health_returns_ok() -> None:
    get_settings.cache_clear()
    with TestClient(create_app()) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "EnterpriseCloud API"
