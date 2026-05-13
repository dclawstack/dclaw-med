"""Tests for /api/v1/auth endpoints."""

import pytest
from httpx import AsyncClient


REGISTER_PAYLOAD = {
    "email": "newdoc@example.com",
    "password": "secret-pass-1",
    "full_name": "Dr. Doc",
    "role": "doctor",
}


@pytest.mark.asyncio
async def test_register_requires_authentication(client: AsyncClient) -> None:
    res = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_register_denied_for_doctor(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    res = await client.post(
        "/api/v1/auth/register", headers=doctor_headers, json=REGISTER_PAYLOAD
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_register_denied_for_nurse(
    client: AsyncClient, nurse_headers: dict[str, str]
) -> None:
    res = await client.post(
        "/api/v1/auth/register", headers=nurse_headers, json=REGISTER_PAYLOAD
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_register_creates_user(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    res = await client.post(
        "/api/v1/auth/register", headers=admin_headers, json=REGISTER_PAYLOAD
    )
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == REGISTER_PAYLOAD["email"]
    assert body["role"] == "doctor"
    assert body["is_active"] is True
    assert "password" not in body
    assert "password_hash" not in body


@pytest.mark.asyncio
async def test_register_rejects_duplicate_email(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    await client.post(
        "/api/v1/auth/register", headers=admin_headers, json=REGISTER_PAYLOAD
    )
    res = await client.post(
        "/api/v1/auth/register", headers=admin_headers, json=REGISTER_PAYLOAD
    )
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_register_rejects_invalid_role(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    bad = {**REGISTER_PAYLOAD, "role": "superuser"}
    res = await client.post("/api/v1/auth/register", headers=admin_headers, json=bad)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_register_rejects_short_password(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    bad = {**REGISTER_PAYLOAD, "password": "short"}
    res = await client.post("/api/v1/auth/register", headers=admin_headers, json=bad)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_login_returns_token(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    await client.post(
        "/api/v1/auth/register", headers=admin_headers, json=REGISTER_PAYLOAD
    )
    res = await client.post(
        "/api/v1/auth/login",
        data={
            "username": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and len(body["access_token"]) > 20


@pytest.mark.asyncio
async def test_login_wrong_password(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    await client.post(
        "/api/v1/auth/register", headers=admin_headers, json=REGISTER_PAYLOAD
    )
    res = await client.post(
        "/api/v1/auth/login",
        data={"username": REGISTER_PAYLOAD["email"], "password": "wrong-password"},
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_user(client: AsyncClient) -> None:
    res = await client.post(
        "/api/v1/auth/login",
        data={"username": "ghost@example.com", "password": "irrelevant"},
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_token(client: AsyncClient) -> None:
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_current_user(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    res = await client.get("/api/v1/auth/me", headers=doctor_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "doctor@example.com"


@pytest.mark.asyncio
async def test_me_rejects_bad_token(client: AsyncClient) -> None:
    res = await client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-jwt"}
    )
    assert res.status_code == 401
