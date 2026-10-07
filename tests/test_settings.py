"""Tests de Settings: normalización de URL y propiedades derivadas."""

from app.core.config import Settings


def _settings(**kwargs) -> Settings:
    defaults = {"database_url": "postgresql://user:pass@localhost:5432/ec", "jwt_secret": "x"}
    defaults.update(kwargs)
    return Settings(**defaults)


def test_normalizes_postgres_url_to_psycopg():
    assert _settings().database_url == "postgresql+psycopg://user:pass@localhost:5432/ec"


def test_normalizes_bare_postgres_scheme():
    url = _settings(database_url="postgres://u:p@h/db").database_url
    assert url == "postgresql+psycopg://u:p@h/db"


def test_keeps_already_async_url():
    url = "postgresql+psycopg://u:p@h/db"
    assert _settings(database_url=url).database_url == url


def test_cors_origin_list_splits_and_strips():
    s = _settings(cors_origins=" http://a.test , http://b.test ,,")
    assert s.cors_origin_list == ["http://a.test", "http://b.test"]


def test_is_production_flag():
    assert _settings(environment="production").is_production
    assert _settings(environment="PROD").is_production
    assert not _settings(environment="development").is_production
