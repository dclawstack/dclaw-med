"""Shared pytest fixtures for backend tests."""

from collections.abc import AsyncGenerator

import asyncpg
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.api.main import app
from app.core.config import settings
from app.core.database import get_db
from app.models.base import Base

TEST_DB_NAME = "dclaw_med_test"
TEST_DB_URL = settings.database_url.replace("/dclaw_med", f"/{TEST_DB_NAME}")


async def _ensure_test_database() -> None:
    admin_url = (
        settings.database_url
        .replace("postgresql+asyncpg://", "postgresql://")
        .rsplit("/", 1)[0]
        + "/postgres"
    )
    conn = await asyncpg.connect(admin_url)
    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", TEST_DB_NAME
        )
        if not exists:
            await conn.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')
    finally:
        await conn.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    await _ensure_test_database()
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def _truncate_tables(test_engine: AsyncEngine) -> AsyncGenerator[None, None]:
    """Truncate every table after each test for isolation."""
    yield
    async with test_engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f'TRUNCATE TABLE "{table.name}" CASCADE'))
        await conn.commit()


@pytest_asyncio.fixture
async def client(test_engine: AsyncEngine) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client; each request gets a fresh AsyncSession bound to the test engine."""
    Session = async_sessionmaker(test_engine, expire_on_commit=False)

    async def _override():
        async with Session() as session:
            yield session

    app.dependency_overrides[get_db] = _override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
