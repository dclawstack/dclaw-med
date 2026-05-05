"""Async database engine and session factory."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.app_env == "dev",
    pool_pre_ping=True,
)
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Yield an async database session."""
    async with AsyncSession(engine, expire_on_commit=False) as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
