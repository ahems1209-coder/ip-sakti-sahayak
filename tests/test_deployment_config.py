from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import Settings
from app.db import session as db_session


class _FailedTransaction:
    async def __aenter__(self):
        raise OSError("simulated database connection failure")

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class _UnavailableEngine:
    def begin(self):
        return _FailedTransaction()


def test_postgresql_engine_disables_asyncpg_statement_cache_only():
    engine_factory = Mock()
    original_factory = db_session.create_async_engine
    db_session.create_async_engine = engine_factory
    try:
        db_session._create_app_engine("postgresql+asyncpg://db.invalid/app")
        postgresql_connect_args = engine_factory.call_args.kwargs["connect_args"]

        db_session._create_app_engine("sqlite+aiosqlite:///./local.sqlite")
        sqlite_connect_args = engine_factory.call_args.kwargs["connect_args"]
    finally:
        db_session.create_async_engine = original_factory

    assert postgresql_connect_args == {"statement_cache_size": 0}
    assert sqlite_connect_args == {}


@pytest.mark.asyncio
async def test_postgresql_schema_migration_widens_source_access_type():
    connection = Mock()
    connection.execute = AsyncMock(side_effect=[Mock(scalar_one_or_none=Mock(return_value=20)), Mock()])

    await db_session._migrate_postgresql_schema(connection)

    migration = str(connection.execute.await_args_list[1].args[0])
    assert "ALTER TABLE source_registry ALTER COLUMN access_type TYPE VARCHAR(50)" in migration


def test_development_uses_local_sqlite_and_loopback_origins():
    settings = Settings(_env_file=None)

    assert settings.get_database_url().startswith("sqlite+aiosqlite://")
    assert any("localhost" in origin for origin in settings.get_allowed_origins())


def test_production_rejects_demo_mode_and_missing_cors_origin():
    with pytest.raises(ValueError, match="DEMO_MODE must be false"):
        Settings(_env_file=None, ENVIRONMENT="production")

    settings = Settings(_env_file=None, ENVIRONMENT="production", DEMO_MODE=False)
    with pytest.raises(ValueError, match="FRONTEND_URL or ALLOWED_ORIGINS"):
        settings.get_allowed_origins()


def test_production_requires_postgresql_configuration():
    settings = Settings(_env_file=None, ENVIRONMENT="production", DEMO_MODE=False)

    with pytest.raises(ValueError, match="DATABASE_URL"):
        settings.get_database_url()


def test_production_normalizes_postgresql_url_and_allows_configured_https_origin():
    settings = Settings(
        _env_file=None,
        ENVIRONMENT="production",
        DEMO_MODE=False,
        DATABASE_URL="postgresql://db",
        FRONTEND_URL="https://frontend.invalid",
    )

    assert settings.get_database_url().startswith("postgresql+asyncpg://")
    assert settings.get_allowed_origins() == ["https://frontend.invalid"]


def test_production_rejects_sqlite_and_insecure_cors_origins():
    sqlite_settings = Settings(
        _env_file=None,
        ENVIRONMENT="production",
        DEMO_MODE=False,
        DATABASE_URL="sqlite+aiosqlite:///./local.sqlite",
    )
    http_cors_settings = Settings(
        _env_file=None,
        ENVIRONMENT="production",
        DEMO_MODE=False,
        FRONTEND_URL="http://frontend.invalid",
    )

    with pytest.raises(ValueError, match="PostgreSQL"):
        sqlite_settings.get_database_url()
    with pytest.raises(ValueError, match="HTTPS"):
        http_cors_settings.get_allowed_origins()


@pytest.mark.asyncio
async def test_production_database_failure_does_not_fall_back_to_sqlite(monkeypatch):
    monkeypatch.setattr(db_session.settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(db_session.settings, "DEMO_MODE", False)
    monkeypatch.setattr(db_session.settings, "DATABASE_URL", "postgresql+asyncpg://db.invalid/app")
    monkeypatch.setattr(db_session, "async_engine", _UnavailableEngine())
    engine_factory = Mock()
    monkeypatch.setattr(db_session, "_create_app_engine", engine_factory)

    with pytest.raises(RuntimeError, match="SQLite fallback is disabled in production"):
        await db_session.init_db()

    engine_factory.assert_not_called()


@pytest.mark.asyncio
async def test_development_database_failure_may_fall_back_to_sqlite(monkeypatch):
    monkeypatch.setattr(db_session.settings, "ENVIRONMENT", "development")
    monkeypatch.setattr(db_session.settings, "DATABASE_URL", "postgresql+asyncpg://db.invalid/app")
    monkeypatch.setattr(db_session, "async_engine", _UnavailableEngine())
    fallback_urls = []

    def sqlite_engine_factory(url):
        fallback_urls.append(url)
        return create_async_engine("sqlite+aiosqlite:///:memory:", echo=False, future=True)

    monkeypatch.setattr(db_session, "_create_app_engine", sqlite_engine_factory)
    try:
        await db_session.init_db()
        assert fallback_urls == ["sqlite+aiosqlite:///./ip_sakti_db.sqlite"]
        async with db_session.async_engine.connect() as connection:
            assert await connection.scalar(text("SELECT 1")) == 1
    finally:
        await db_session.async_engine.dispose()