"""FastAPI dependency injection."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db


async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency."""
    async for session in get_db():
        yield session


DBDep = AsyncSession
