"""Rate limiting behaviour.

The suite disables the limiter globally (see conftest); these tests opt back in
so they can assert the 429 path without affecting other tests.
"""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.core.config import settings
from app.core.rate_limit import limiter


@pytest_asyncio.fixture
async def rate_limiting_on() -> AsyncGenerator[None, None]:
    """Enable the limiter and start from a clean counter for one test."""
    limiter.reset()
    limiter.enabled = True
    try:
        yield
    finally:
        limiter.enabled = False
        limiter.reset()


def _limit_count(limit: str) -> int:
    """Parse the leading request count out of a slowapi limit string."""
    return int(limit.split("/", 1)[0])


@pytest.mark.asyncio
async def test_login_is_rate_limited(
    client: AsyncClient, rate_limiting_on: None
) -> None:
    """The Nth+1 login attempt from one client returns 429."""
    allowed = _limit_count(settings.rate_limit_auth)
    creds = {"username": "nobody@example.com", "password": "wrong"}

    # Wrong creds normally return 401; we only care that the limiter counts them.
    for _ in range(allowed):
        res = await client.post("/api/v1/auth/login", data=creds)
        assert res.status_code != 429, res.text

    res = await client.post("/api/v1/auth/login", data=creds)
    assert res.status_code == 429, res.text


@pytest.mark.asyncio
async def test_health_is_exempt_from_rate_limit(
    client: AsyncClient, rate_limiting_on: None
) -> None:
    """Health checks bypass the limiter so LB probes are never throttled."""
    for _ in range(_limit_count(settings.rate_limit_default) + 5):
        res = await client.get("/health")
        assert res.status_code == 200, res.text
