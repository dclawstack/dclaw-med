"""Tests for the public demo dataset lifecycle.

Endpoints under test live in :mod:`app.api.v1.demo` and are gated by
``settings.enable_demo_mode``. The conftest truncates tables between
tests, so every test starts from an empty database — there's no risk
of one test's seed leaking into another's reset.

We monkeypatch ``settings.enable_demo_mode = True`` per-test instead of
flipping it globally so the disabled-mode test can also live here.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.services.demo_service import DEMO_USER_EMAIL


@pytest.fixture
def demo_on(monkeypatch: pytest.MonkeyPatch) -> None:
    """Turn the demo feature flag on for the duration of one test."""
    monkeypatch.setattr(settings, "enable_demo_mode", True)


# ---------- status ----------


@pytest.mark.asyncio
async def test_status_when_demo_disabled_reports_disabled(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When the feature flag is off, /status still answers (the
    landing page reads it), but reports ``enabled=False``."""
    monkeypatch.setattr(settings, "enable_demo_mode", False)
    res = await client.get("/api/v1/demo/status")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["enabled"] is False
    assert body["seeded"] is False
    assert body["patient_count"] == 0


@pytest.mark.asyncio
async def test_status_when_demo_enabled_reports_unseeded(
    client: AsyncClient, demo_on: None
) -> None:
    res = await client.get("/api/v1/demo/status")
    assert res.status_code == 200
    body = res.json()
    assert body["enabled"] is True
    assert body["seeded"] is False
    assert body["patient_count"] == 0


# ---------- gating ----------


@pytest.mark.asyncio
async def test_seed_forbidden_when_demo_disabled(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "enable_demo_mode", False)
    res = await client.post("/api/v1/demo/seed")
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_reset_forbidden_when_demo_disabled(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "enable_demo_mode", False)
    res = await client.delete("/api/v1/demo/reset")
    assert res.status_code == 403


# ---------- seed ----------


@pytest.mark.asyncio
async def test_seed_creates_dataset_and_returns_credentials(
    client: AsyncClient, demo_on: None
) -> None:
    res = await client.post("/api/v1/demo/seed")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["enabled"] is True
    assert body["seeded"] is True
    assert body["patient_count"] == 5  # five canonical demo patients
    creds = body["demo_credentials"]
    assert creds["email"] == DEMO_USER_EMAIL
    assert isinstance(creds["password"], str) and len(creds["password"]) >= 8

    # Sign in with the returned credentials — the seeded clinician account
    # really exists and can hit a protected route.
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": creds["email"], "password": creds["password"]},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    me = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me.status_code == 200
    assert me.json()["role"] == "doctor"


@pytest.mark.asyncio
async def test_seed_is_idempotent(client: AsyncClient, demo_on: None) -> None:
    """Hitting /seed twice does not duplicate the demo patients."""
    first = await client.post("/api/v1/demo/seed")
    assert first.status_code == 200
    assert first.json()["patient_count"] == 5

    second = await client.post("/api/v1/demo/seed")
    assert second.status_code == 200
    assert second.json()["patient_count"] == 5

    status = await client.get("/api/v1/demo/status")
    assert status.json()["patient_count"] == 5


# ---------- reset ----------


@pytest.mark.asyncio
async def test_reset_after_seed_returns_to_empty(
    client: AsyncClient, demo_on: None
) -> None:
    await client.post("/api/v1/demo/seed")
    res = await client.delete("/api/v1/demo/reset")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["seeded"] is False
    assert body["patient_count"] == 0

    # Demo clinician account is gone — login fails.
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": DEMO_USER_EMAIL, "password": "DemoPass123!"},
    )
    assert login.status_code == 401


@pytest.mark.asyncio
async def test_reset_only_touches_demo_rows(
    client: AsyncClient,
    demo_on: None,
    doctor_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> None:
    """Reset must not delete non-demo patients or non-demo users."""
    # Seed demo data.
    await client.post("/api/v1/demo/seed")

    # Create a non-demo patient (MRN does NOT start with DEMO-).
    keep_patient = await client.post(
        "/api/v1/med/patients",
        headers=doctor_headers,
        json={
            "name": "Keep Me",
            "date_of_birth": "1990-01-01",
            "gender": "other",
            "medical_record_number": "MRN-KEEP-1",
        },
    )
    assert keep_patient.status_code == 201, keep_patient.text
    keep_id = keep_patient.json()["id"]

    # Create a non-demo user (admin-only register endpoint).
    keep_user_email = "keep-me@example.com"
    keep_user = await client.post(
        "/api/v1/auth/register",
        headers=admin_headers,
        json={
            "email": keep_user_email,
            "password": "keep-password-1",
            "full_name": "Keep User",
            "role": "doctor",
        },
    )
    assert keep_user.status_code == 201, keep_user.text

    # Reset demo.
    reset = await client.delete("/api/v1/demo/reset")
    assert reset.status_code == 200
    assert reset.json()["patient_count"] == 0

    # Non-demo patient survives.
    got = await client.get(
        f"/api/v1/med/patients/{keep_id}", headers=doctor_headers
    )
    assert got.status_code == 200
    assert got.json()["medical_record_number"] == "MRN-KEEP-1"

    # Non-demo user can still log in.
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": keep_user_email, "password": "keep-password-1"},
    )
    assert login.status_code == 200


@pytest.mark.asyncio
async def test_reset_clears_demo_user_audit_rows_but_preserves_real(
    client: AsyncClient,
    demo_on: None,
    admin_headers: dict[str, str],
) -> None:
    """Regression for commit f371fc2: reset must hand-clear the demo
    user's audit rows (audit_logs FK is ON DELETE RESTRICT) without
    touching audit rows for real users."""
    # Real admin generates an audit row by reading patients.
    real_read = await client.get("/api/v1/med/patients", headers=admin_headers)
    assert real_read.status_code == 200

    # Seed + sign in as demo doctor + generate an audit row as the demo user.
    seed = await client.post("/api/v1/demo/seed")
    creds = seed.json()["demo_credentials"]
    demo_login = await client.post(
        "/api/v1/auth/login",
        data={"username": creds["email"], "password": creds["password"]},
    )
    demo_headers = {"Authorization": f"Bearer {demo_login.json()['access_token']}"}
    demo_read = await client.get("/api/v1/med/patients", headers=demo_headers)
    assert demo_read.status_code == 200

    # Reset must succeed despite the demo user's audit FK references.
    reset = await client.delete("/api/v1/demo/reset")
    assert reset.status_code == 200, reset.text

    # Real admin's audit rows survive.
    audit = await client.get("/api/v1/audit", headers=admin_headers)
    assert audit.status_code == 200
    rows = audit.json()
    # At least the admin's earlier read should still be present.
    me = await client.get("/api/v1/auth/me", headers=admin_headers)
    admin_id = me.json()["id"]
    assert any(r["user_id"] == admin_id for r in rows)
