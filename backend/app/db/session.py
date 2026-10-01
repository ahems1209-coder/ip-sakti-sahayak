import os
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from app.core.config import settings
from app.db.base import Base
from app.models.source import SourceRegistry


def _resolve_sqlite_path(db_url: str) -> Optional[str]:
    if "sqlite+aiosqlite:///" in db_url:
        rel_path = db_url.split("sqlite+aiosqlite:///")[-1]
    elif "sqlite:///" in db_url:
        rel_path = db_url.split("sqlite:///")[-1]
    else:
        return None

    if not rel_path:
        return None
    if rel_path.startswith("./"):
        rel_path = rel_path[2:]
    return os.path.abspath(rel_path)


async def _sqlite_schema_is_stale(db_url: str) -> bool:
    sqlite_path = _resolve_sqlite_path(db_url)
    if sqlite_path is None or not os.path.exists(sqlite_path):
        return False
    try:
        engine = create_async_engine(db_url, echo=False, future=True)
        async with engine.connect() as conn:
            required_columns = {
                "source_registry": {"source_family", "authority_type", "official_url", "technical_access_status", "source_origin"},
                "documents": {"source_id", "content_hash", "ingestion_hash", "verification_status"},
                "document_sections": {"chunk_id", "document_id", "content", "metadata_json"},
            }
            for table_name, required_fields in required_columns.items():
                result = await conn.execute(text(f"PRAGMA table_info({table_name})"))
                columns = {row[1] for row in result.fetchall()}
                if not required_fields.issubset(columns):
                    await engine.dispose()
                    return True
        await engine.dispose()
        return False
    except Exception:
        return False


def _create_app_engine(db_url: str):
    connect_args = {}
    if db_url.startswith("postgresql+asyncpg://"):
        connect_args["statement_cache_size"] = 0
    return create_async_engine(db_url, echo=False, future=True, connect_args=connect_args)


async def _migrate_postgresql_schema(connection) -> None:
    result = await connection.execute(text("""
        SELECT character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name = 'source_registry'
          AND column_name = 'access_type'
    """))
    current_length = result.scalar_one_or_none()
    required_length = SourceRegistry.__table__.c.access_type.type.length
    if current_length is not None and current_length < required_length:
        await connection.execute(text(
            f"ALTER TABLE source_registry ALTER COLUMN access_type TYPE VARCHAR({required_length})"
        ))


def get_engine():
    db_url = settings.get_database_url()
    if "sqlite" in db_url and "aiosqlite" not in db_url:
        db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://")
    return _create_app_engine(db_url)


async_engine = get_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


async def init_db():
    """Initialize database tables with graceful fallback to sqlite if postgres is unreachable."""
    global async_engine, AsyncSessionLocal
    db_url = settings.get_database_url()
    sqlite_path = _resolve_sqlite_path(db_url)
    if "sqlite" in db_url and sqlite_path and os.path.exists(sqlite_path):
        if await _sqlite_schema_is_stale(db_url):
            os.remove(sqlite_path)
            async_engine = _create_app_engine(db_url)
            AsyncSessionLocal = async_sessionmaker(
                bind=async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False
            )
            print(f"[DB WARN] Detected stale SQLite schema; rebuilt local database at {sqlite_path}.")

    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            if db_url.startswith("postgresql+asyncpg://"):
                await _migrate_postgresql_schema(conn)
    except Exception as e:
        if settings.ENVIRONMENT.lower() in {"production", "prod"}:
            raise RuntimeError("PostgreSQL initialization failed; SQLite fallback is disabled in production.") from e
        print(f"[DB WARN] PostgreSQL connection failed ({str(e)}). Falling back to local SQLite database.")
        fallback_url = "sqlite+aiosqlite:///./ip_sakti_db.sqlite"
        async_engine = _create_app_engine(fallback_url)
        AsyncSessionLocal = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
