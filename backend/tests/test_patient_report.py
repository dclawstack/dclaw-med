"""Tests for the patient PDF report endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_report_returns_pdf(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    # Sprinkle in some related records so the template exercises every section.
    await client.post(
        "/api/v1/med/allergies",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "allergen": "Penicillin",
            "severity": "severe",
            "reaction": "hives",
        },
    )
    await client.post(
        "/api/v1/med/diagnoses",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "icd10_code": "I10",
            "name": "Essential hypertension",
            "status": "confirmed",
        },
    )
    await client.post(
        "/api/v1/med/prescriptions",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "medication_name": "Lisinopril",
            "dosage": "10mg",
            "frequency": "daily",
            "route": "oral",
            "start_date": "2026-05-15",
        },
    )
    await client.post(
        "/api/v1/med/lab-results",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "test_name": "Hemoglobin A1c",
            "test_category": "Chemistry",
            "result_value": "5.4",
            "unit": "%",
            "reference_range": "<6.5",
            "status": "final",
            "ordered_at": "2026-05-15T10:00:00Z",
            "resulted_at": "2026-05-15T11:00:00Z",
        },
    )
    await client.post(
        "/api/v1/med/notes",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "note_type": "progress",
            "content": "Patient stable on current regimen.",
        },
    )

    res = await client.get(
        f"/api/v1/med/patients/{patient_id}/report", headers=doctor_headers
    )
    assert res.status_code == 200, res.text
    assert res.headers["content-type"].startswith("application/pdf")
    assert "filename=" in res.headers.get("content-disposition", "")
    # Real PDFs start with the %PDF- magic bytes
    assert res.content[:5] == b"%PDF-"
    # Plausible body size — a near-empty template still produces a few KB
    assert len(res.content) > 1000


@pytest.mark.asyncio
async def test_report_for_minimal_patient(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    """No related records → template still renders the 'empty' fallbacks."""
    res = await client.get(
        f"/api/v1/med/patients/{patient_id}/report", headers=doctor_headers
    )
    assert res.status_code == 200
    assert res.content[:5] == b"%PDF-"


@pytest.mark.asyncio
async def test_report_unknown_patient_is_404(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    res = await client.get(
        "/api/v1/med/patients/00000000-0000-0000-0000-000000000000/report",
        headers=doctor_headers,
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_report_requires_auth(client: AsyncClient, patient_id: str) -> None:
    res = await client.get(f"/api/v1/med/patients/{patient_id}/report")
    assert res.status_code == 401
