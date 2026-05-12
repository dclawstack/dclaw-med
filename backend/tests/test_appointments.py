"""Tests for /api/v1/med/appointments + provider list endpoint."""

import pytest
from httpx import AsyncClient


async def _provider_id(client: AsyncClient, headers: dict[str, str]) -> str:
    me = await client.get("/api/v1/auth/me", headers=headers)
    return me.json()["id"]


def _payload(patient_id: str, provider_id: str, **overrides):
    base = {
        "patient_id": patient_id,
        "provider_id": provider_id,
        "scheduled_at": "2026-06-01T10:00:00Z",
        "duration_minutes": 30,
        "status": "scheduled",
        "location": "Clinic Room 1",
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_create_appointment_as_receptionist(
    client: AsyncClient,
    receptionist_headers: dict[str, str],
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    provider_id = await _provider_id(client, doctor_headers)
    res = await client.post(
        "/api/v1/med/appointments",
        headers=receptionist_headers,
        json=_payload(patient_id, provider_id),
    )
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["status"] == "scheduled"
    assert body["duration_minutes"] == 30


@pytest.mark.asyncio
async def test_create_appointment_denied_for_nurse(
    client: AsyncClient,
    nurse_headers: dict[str, str],
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    provider_id = await _provider_id(client, doctor_headers)
    res = await client.post(
        "/api/v1/med/appointments",
        headers=nurse_headers,
        json=_payload(patient_id, provider_id),
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_overlapping_appointment_409(
    client: AsyncClient,
    receptionist_headers: dict[str, str],
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    provider_id = await _provider_id(client, doctor_headers)
    a = await client.post(
        "/api/v1/med/appointments",
        headers=receptionist_headers,
        json=_payload(patient_id, provider_id, scheduled_at="2026-06-01T10:00:00Z"),
    )
    assert a.status_code == 201
    # 30-min appt at 10:00, then another at 10:15 should overlap
    b = await client.post(
        "/api/v1/med/appointments",
        headers=receptionist_headers,
        json=_payload(patient_id, provider_id, scheduled_at="2026-06-01T10:15:00Z"),
    )
    assert b.status_code == 409


@pytest.mark.asyncio
async def test_back_to_back_appointment_allowed(
    client: AsyncClient,
    receptionist_headers: dict[str, str],
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    provider_id = await _provider_id(client, doctor_headers)
    await client.post(
        "/api/v1/med/appointments",
        headers=receptionist_headers,
        json=_payload(patient_id, provider_id, scheduled_at="2026-06-01T10:00:00Z"),
    )
    # 30-min at 10:00 ends at 10:30; another at exactly 10:30 should be fine
    res = await client.post(
        "/api/v1/med/appointments",
        headers=receptionist_headers,
        json=_payload(patient_id, provider_id, scheduled_at="2026-06-01T10:30:00Z"),
    )
    assert res.status_code == 201


@pytest.mark.asyncio
async def test_list_appointments_by_date(
    client: AsyncClient,
    receptionist_headers: dict[str, str],
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    provider_id = await _provider_id(client, doctor_headers)
    await client.post(
        "/api/v1/med/appointments",
        headers=receptionist_headers,
        json=_payload(patient_id, provider_id, scheduled_at="2026-06-02T09:00:00Z"),
    )
    await client.post(
        "/api/v1/med/appointments",
        headers=receptionist_headers,
        json=_payload(patient_id, provider_id, scheduled_at="2026-06-03T09:00:00Z"),
    )
    res = await client.get(
        "/api/v1/med/appointments?date=2026-06-02", headers=receptionist_headers
    )
    assert res.status_code == 200
    rows = res.json()
    assert len(rows) == 1
    assert rows[0]["scheduled_at"].startswith("2026-06-02")


@pytest.mark.asyncio
async def test_cancel_appointment_frees_slot(
    client: AsyncClient,
    receptionist_headers: dict[str, str],
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    provider_id = await _provider_id(client, doctor_headers)
    created = await client.post(
        "/api/v1/med/appointments",
        headers=receptionist_headers,
        json=_payload(patient_id, provider_id, scheduled_at="2026-06-04T10:00:00Z"),
    )
    appt_id = created.json()["id"]
    cancel = await client.put(
        f"/api/v1/med/appointments/{appt_id}",
        headers=receptionist_headers,
        json={"status": "cancelled"},
    )
    assert cancel.status_code == 200
    # Cancelled slot is not active → a new appointment at the same time is allowed
    res = await client.post(
        "/api/v1/med/appointments",
        headers=receptionist_headers,
        json=_payload(patient_id, provider_id, scheduled_at="2026-06-04T10:00:00Z"),
    )
    assert res.status_code == 201


@pytest.mark.asyncio
async def test_providers_endpoint_returns_doctors_and_admins(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    nurse_headers: dict[str, str],
) -> None:
    # any authenticated user can call /providers
    res = await client.get("/api/v1/auth/providers", headers=nurse_headers)
    assert res.status_code == 200
    rows = res.json()
    roles = {r["role"] for r in rows}
    assert roles <= {"doctor", "admin"}
    # the doctor fixture's user should appear
    me = await client.get("/api/v1/auth/me", headers=doctor_headers)
    doctor_id = me.json()["id"]
    assert any(r["id"] == doctor_id for r in rows)


@pytest.mark.asyncio
async def test_appointments_list_requires_auth(client: AsyncClient) -> None:
    res = await client.get("/api/v1/med/appointments")
    assert res.status_code == 401
