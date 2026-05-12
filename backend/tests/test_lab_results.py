"""Tests for /api/v1/med/lab-results endpoints."""

import pytest
from httpx import AsyncClient


def _lab_payload(patient_id: str, **overrides):
    base = {
        "patient_id": patient_id,
        "test_name": "Hemoglobin A1c",
        "test_category": "Chemistry",
        "result_value": "7.2",
        "unit": "%",
        "reference_range": "<6.5",
        "status": "final",
        "ordered_at": "2026-05-10T09:00:00Z",
        "resulted_at": "2026-05-10T15:30:00Z",
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_create_lab_result_as_doctor(
    client: AsyncClient, doctor_headers: dict[str, str], patient_id: str
) -> None:
    res = await client.post(
        "/api/v1/med/lab-results",
        headers=doctor_headers,
        json=_lab_payload(patient_id),
    )
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["test_name"] == "Hemoglobin A1c"
    assert body["patient_id"] == patient_id
    assert body["status"] == "final"


@pytest.mark.asyncio
async def test_create_lab_result_as_nurse(
    client: AsyncClient, nurse_headers: dict[str, str], patient_id: str
) -> None:
    res = await client.post(
        "/api/v1/med/lab-results",
        headers=nurse_headers,
        json=_lab_payload(patient_id),
    )
    assert res.status_code == 201


@pytest.mark.asyncio
async def test_create_lab_result_denied_for_receptionist(
    client: AsyncClient, receptionist_headers: dict[str, str], patient_id: str
) -> None:
    res = await client.post(
        "/api/v1/med/lab-results",
        headers=receptionist_headers,
        json=_lab_payload(patient_id),
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_list_lab_results_filtered_by_patient(
    client: AsyncClient, doctor_headers: dict[str, str], patient_id: str
) -> None:
    for name in ("Sodium", "Potassium", "Creatinine"):
        await client.post(
            "/api/v1/med/lab-results",
            headers=doctor_headers,
            json=_lab_payload(patient_id, test_name=name),
        )
    res = await client.get(
        f"/api/v1/med/lab-results?patient_id={patient_id}", headers=doctor_headers
    )
    assert res.status_code == 200
    rows = res.json()
    names = {r["test_name"] for r in rows}
    assert {"Sodium", "Potassium", "Creatinine"} <= names


@pytest.mark.asyncio
async def test_list_lab_results_requires_auth(client: AsyncClient) -> None:
    res = await client.get("/api/v1/med/lab-results")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_update_lab_result(
    client: AsyncClient, doctor_headers: dict[str, str], patient_id: str
) -> None:
    created = await client.post(
        "/api/v1/med/lab-results",
        headers=doctor_headers,
        json=_lab_payload(patient_id, status="preliminary"),
    )
    lab_id = created.json()["id"]
    updated = await client.put(
        f"/api/v1/med/lab-results/{lab_id}",
        headers=doctor_headers,
        json={"status": "final", "result_value": "7.5"},
    )
    assert updated.status_code == 200
    body = updated.json()
    assert body["status"] == "final"
    assert body["result_value"] == "7.5"


@pytest.mark.asyncio
async def test_delete_lab_result(
    client: AsyncClient, doctor_headers: dict[str, str], patient_id: str
) -> None:
    created = await client.post(
        "/api/v1/med/lab-results",
        headers=doctor_headers,
        json=_lab_payload(patient_id),
    )
    lab_id = created.json()["id"]
    res = await client.delete(
        f"/api/v1/med/lab-results/{lab_id}", headers=doctor_headers
    )
    assert res.status_code == 204
    after = await client.get(
        f"/api/v1/med/lab-results/{lab_id}", headers=doctor_headers
    )
    assert after.status_code == 404


@pytest.mark.asyncio
async def test_lab_result_invalid_status_rejected(
    client: AsyncClient, doctor_headers: dict[str, str], patient_id: str
) -> None:
    res = await client.post(
        "/api/v1/med/lab-results",
        headers=doctor_headers,
        json=_lab_payload(patient_id, status="bogus"),
    )
    assert res.status_code == 422
