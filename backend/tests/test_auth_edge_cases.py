"""Auth edge cases not covered by test_auth.py.

The big one is the inactive-user login path — register an account,
flip ``is_active=False`` directly in the DB, then assert the login
fails with 403 (the explicit "User is inactive" branch in
``app.api.v1.auth.login``).
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from app.repositories.user_repo import UserRepository


@pytest.mark.asyncio
async def test_login_inactive_user_returns_403(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_engine: AsyncEngine,
) -> None:
    """A user with ``is_active=False`` cannot log in even with the right
    password — the login route returns 403 (not 401), so a deactivated
    clinician sees a different error than a typo."""
    email = "inactive-user@example.com"
    password = "active-then-not-1"
    await client.post(
        "/api/v1/auth/register",
        headers=admin_headers,
        json={
            "email": email,
            "password": password,
            "full_name": "Inactive Doc",
            "role": "doctor",
        },
    )

    # Flip the flag directly via the repo — there's no admin endpoint
    # for deactivation today and we don't want to add one just for a test.
    Session = async_sessionmaker(test_engine, expire_on_commit=False)
    async with Session() as db:
        repo = UserRepository(db)
        user = await repo.get_by_email(email)
        assert user is not None
        user.is_active = False
        await db.commit()

    res = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert res.status_code == 403, res.text


@pytest.mark.asyncio
async def test_users_listing_is_admin_only(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    nurse_headers: dict[str, str],
    receptionist_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> None:
    """Sample admin-only route: GET /api/v1/auth/users."""
    for headers in (doctor_headers, nurse_headers, receptionist_headers):
        res = await client.get("/api/v1/auth/users", headers=headers)
        assert res.status_code == 403, res.text

    ok = await client.get("/api/v1/auth/users", headers=admin_headers)
    assert ok.status_code == 200
    assert isinstance(ok.json(), list)
