"""Async database engine and session factory."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import settings
from app.core.dialect import IS_SQLITE
from app.models.base import Base

# SQLite (dev) doesn't support pool_pre_ping the same way; use safe defaults.
_engine_kwargs: dict = {"echo": settings.app_env == "dev"}
if IS_SQLITE:
    # check_same_thread=False is required for async SQLite usage.
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    _engine_kwargs["pool_pre_ping"] = True

engine = create_async_engine(settings.database_url, **_engine_kwargs)


async def get_db() -> AsyncSession:
    """Yield an async database session."""
    async with AsyncSession(engine, expire_on_commit=False) as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables. Used for SQLite dev mode and tests; prod uses Alembic."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
