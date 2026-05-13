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
    # Audit middleware reads the engine from app.state to allow test isolation.
    prev_engine = getattr(app.state, "engine", None)
    app.state.engine = test_engine
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
    app.state.engine = prev_engine


async def _auth_headers(
    client: AsyncClient, engine: AsyncEngine, role: str
) -> dict[str, str]:
    """Create a user directly (bypassing the admin-only register endpoint) and log in."""
    from app.repositories.user_repo import UserRepository
    from app.schemas.user import UserCreate

    email = f"{role}@example.com"
    password = "test-password-1"
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as db:
        repo = UserRepository(db)
        if not await repo.get_by_email(email):
            await repo.create(
                UserCreate(
                    email=email,
                    password=password,
                    full_name=f"{role.title()} User",
                    role=role,
                )
            )
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(
    client: AsyncClient, test_engine: AsyncEngine
) -> dict[str, str]:
    return await _auth_headers(client, test_engine, "admin")


@pytest_asyncio.fixture
async def doctor_headers(
    client: AsyncClient, test_engine: AsyncEngine
) -> dict[str, str]:
    return await _auth_headers(client, test_engine, "doctor")


@pytest_asyncio.fixture
async def nurse_headers(
    client: AsyncClient, test_engine: AsyncEngine
) -> dict[str, str]:
    return await _auth_headers(client, test_engine, "nurse")


@pytest_asyncio.fixture
async def receptionist_headers(
    client: AsyncClient, test_engine: AsyncEngine
) -> dict[str, str]:
    return await _auth_headers(client, test_engine, "receptionist")


@pytest_asyncio.fixture
async def patient_id(client: AsyncClient, doctor_headers: dict[str, str]) -> str:
    """A patient created by a doctor; useful for medical-record tests."""
    res = await client.post(
        "/api/v1/med/patients",
        headers=doctor_headers,
        json={
            "name": "Test Patient",
            "date_of_birth": "1990-01-01",
            "gender": "other",
            "medical_record_number": "MRN-TEST-001",
        },
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]
