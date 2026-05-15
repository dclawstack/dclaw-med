"""Tests for allergy CRUD and prescription allergy alerts."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_allergy(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    res = await client.post(
        "/api/v1/med/allergies",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "allergen": "Penicillin",
            "severity": "severe",
            "reaction": "hives, swelling",
        },
    )
    assert res.status_code == 201, res.text
    assert res.json()["allergen"] == "Penicillin"

    res = await client.get(
        f"/api/v1/med/allergies?patient_id={patient_id}", headers=doctor_headers
    )
    assert res.status_code == 200
    allergies = res.json()
    assert len(allergies) == 1
    assert allergies[0]["severity"] == "severe"


@pytest.mark.asyncio
async def test_duplicate_allergy_rejected(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    body = {
        "patient_id": patient_id,
        "allergen": "Aspirin",
        "severity": "moderate",
    }
    res1 = await client.post(
        "/api/v1/med/allergies", headers=doctor_headers, json=body
    )
    assert res1.status_code == 201
    res2 = await client.post(
        "/api/v1/med/allergies", headers=doctor_headers, json=body
    )
    assert res2.status_code == 409


@pytest.mark.asyncio
async def test_invalid_severity_rejected(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    res = await client.post(
        "/api/v1/med/allergies",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "allergen": "Latex",
            "severity": "extreme",
        },
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_update_and_delete_allergy(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    create = await client.post(
        "/api/v1/med/allergies",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "allergen": "Sulfa drugs",
            "severity": "mild",
        },
    )
    allergy_id = create.json()["id"]

    upd = await client.put(
        f"/api/v1/med/allergies/{allergy_id}",
        headers=doctor_headers,
        json={"severity": "severe", "reaction": "rash"},
    )
    assert upd.status_code == 200
    assert upd.json()["severity"] == "severe"
    assert upd.json()["reaction"] == "rash"

    delete = await client.delete(
        f"/api/v1/med/allergies/{allergy_id}", headers=doctor_headers
    )
    assert delete.status_code == 204

    fetch = await client.get(
        f"/api/v1/med/allergies/{allergy_id}", headers=doctor_headers
    )
    assert fetch.status_code == 404


@pytest.mark.asyncio
async def test_receptionist_cannot_write_allergy(
    client: AsyncClient,
    receptionist_headers: dict[str, str],
    patient_id: str,
) -> None:
    res = await client.post(
        "/api/v1/med/allergies",
        headers=receptionist_headers,
        json={
            "patient_id": patient_id,
            "allergen": "Codeine",
            "severity": "mild",
        },
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_prescription_returns_allergy_warning_on_match(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    await client.post(
        "/api/v1/med/allergies",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "allergen": "Penicillin",
            "severity": "severe",
            "reaction": "anaphylaxis risk",
        },
    )

    # Prescribe a med whose name contains the allergen string.
    res = await client.post(
        "/api/v1/med/prescriptions",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "medication_name": "Penicillin V 500mg",
            "dosage": "500mg",
            "frequency": "twice daily",
            "route": "oral",
            "start_date": "2026-05-15",
        },
    )
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["medication_name"] == "Penicillin V 500mg"
    warnings = body["allergy_warnings"]
    assert len(warnings) == 1
    assert warnings[0]["allergen"] == "Penicillin"
    assert warnings[0]["severity"] == "severe"


@pytest.mark.asyncio
async def test_prescription_no_warning_when_unrelated(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    await client.post(
        "/api/v1/med/allergies",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "allergen": "Penicillin",
            "severity": "severe",
        },
    )

    res = await client.post(
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
    assert res.status_code == 201
    assert res.json()["allergy_warnings"] == []


@pytest.mark.asyncio
async def test_prescription_flags_cross_class_allergen(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    """A 'Penicillin' allergy must flag a script for any other penicillin-class drug."""
    await client.post(
        "/api/v1/med/allergies",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "allergen": "Penicillin",
            "severity": "moderate",
        },
    )
    res = await client.post(
        "/api/v1/med/prescriptions",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "medication_name": "Amoxicillin 250mg",
            "dosage": "250mg",
            "frequency": "tid",
            "route": "oral",
            "start_date": "2026-05-15",
        },
    )
    assert res.status_code == 201
    warnings = res.json()["allergy_warnings"]
    assert len(warnings) == 1
    assert warnings[0]["allergen"] == "Penicillin"


@pytest.mark.asyncio
async def test_prescription_no_cross_class_false_positive(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    """Penicillin allergy should NOT flag a statin — different class."""
    await client.post(
        "/api/v1/med/allergies",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "allergen": "Penicillin",
            "severity": "severe",
        },
    )
    res = await client.post(
        "/api/v1/med/prescriptions",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "medication_name": "Atorvastatin 20mg",
            "dosage": "20mg",
            "frequency": "daily",
            "route": "oral",
            "start_date": "2026-05-15",
        },
    )
    assert res.status_code == 201
    assert res.json()["allergy_warnings"] == []


@pytest.mark.asyncio
async def test_anonymous_cannot_access_allergies(
    client: AsyncClient, patient_id: str
) -> None:
    res = await client.get(f"/api/v1/med/allergies?patient_id={patient_id}")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_patient_id_query_required(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    res = await client.get("/api/v1/med/allergies", headers=doctor_headers)
    assert res.status_code == 422
