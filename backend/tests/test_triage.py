"""Tests for the /api/v1/med/symptoms/triage endpoint."""

import pytest
from httpx import AsyncClient

TRIAGE = "/api/v1/triage"


@pytest.mark.asyncio
async def test_chest_pain_routes_to_ed(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    res = await client.post(
        TRIAGE,
        headers=doctor_headers,
        json={"symptoms": "Crushing chest pain radiating to left arm"},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["urgency_level"] == "high"
    assert body["suggested_department"] == "Emergency Department"
    assert "ECG" in body["recommended_tests"]
    assert any("Pain radiating" in flag for flag in body["red_flags"])
    assert len(body["differential_diagnoses"]) <= 3
    # Summary should reflect "today / urgent" guidance, not the routine line.
    assert "urgent" in body["summary"].lower() or "today" in body["summary"].lower()


@pytest.mark.asyncio
async def test_fever_routes_to_primary_care(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    res = await client.post(
        TRIAGE,
        headers=doctor_headers,
        json={"symptoms": "Mild fever and cough for 2 days"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["urgency_level"] == "medium"
    assert body["suggested_department"] == "Primary Care"
    assert body["red_flags"], "fever pattern must surface red flags"


@pytest.mark.asyncio
async def test_unknown_symptoms_default_routine(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    res = await client.post(
        TRIAGE,
        headers=doctor_headers,
        json={"symptoms": "Occasional left big toe twitch"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["urgency_level"] == "low"
    assert body["suggested_department"] == "Primary Care"
    assert "routine" in body["summary"].lower()


@pytest.mark.asyncio
async def test_patient_role_can_self_triage(
    client: AsyncClient,
    patient_headers: dict[str, str],
) -> None:
    """A patient logged in to the portal can call triage. This is the
    'patient describes symptoms via chat' use case from PLAN-v1.2 #10."""
    res = await client.post(
        TRIAGE,
        headers=patient_headers,
        json={"symptoms": "Shortness of breath when walking upstairs"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["urgency_level"] == "high"
    assert body["suggested_department"] == "Emergency Department"


@pytest.mark.asyncio
async def test_triage_requires_auth(client: AsyncClient) -> None:
    res = await client.post(TRIAGE, json={"symptoms": "headache"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_triage_validates_input(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    res = await client.post(TRIAGE, headers=doctor_headers, json={"symptoms": ""})
    assert res.status_code == 422
