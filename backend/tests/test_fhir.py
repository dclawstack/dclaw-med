"""Tests for /api/v1/med/fhir/* — FHIR R4 export endpoints."""

import pytest
from httpx import AsyncClient

ICD10 = "http://hl7.org/fhir/sid/icd-10-cm"
FHIR = "/api/v1/med/fhir"


@pytest.mark.asyncio
async def test_get_patient_resource_shape(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    res = await client.get(f"{FHIR}/Patient/{patient_id}", headers=doctor_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["resourceType"] == "Patient"
    assert body["id"] == patient_id
    assert body["gender"] == "other"
    assert body["birthDate"] == "1990-01-01"
    assert body["identifier"][0]["value"] == "MRN-TEST-001"
    # Name shape — single-name model approximated; family may be empty.
    assert body["name"][0]["text"] == "Test Patient"


@pytest.mark.asyncio
async def test_patient_unknown_is_404(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    res = await client.get(
        f"{FHIR}/Patient/00000000-0000-0000-0000-000000000000",
        headers=doctor_headers,
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_condition_search_uses_icd10_system(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
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
    res = await client.get(
        f"{FHIR}/Condition?patient={patient_id}", headers=doctor_headers
    )
    assert res.status_code == 200
    body = res.json()
    assert body["resourceType"] == "Bundle"
    assert body["type"] == "searchset"
    assert body["total"] == 1
    condition = body["entry"][0]["resource"]
    assert condition["resourceType"] == "Condition"
    coding = condition["code"]["coding"][0]
    assert coding["system"] == ICD10
    assert coding["code"] == "I10"
    assert coding["display"] == "Essential hypertension"
    assert condition["subject"]["reference"] == f"Patient/{patient_id}"


@pytest.mark.asyncio
async def test_medication_request_search(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
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
    res = await client.get(
        f"{FHIR}/MedicationRequest?patient={patient_id}", headers=doctor_headers
    )
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 1
    mr = body["entry"][0]["resource"]
    assert mr["resourceType"] == "MedicationRequest"
    assert mr["status"] == "active"
    assert mr["intent"] == "order"
    assert mr["medicationCodeableConcept"]["text"] == "Lisinopril"
    assert mr["subject"]["reference"] == f"Patient/{patient_id}"


@pytest.mark.asyncio
async def test_observation_search(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
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
    res = await client.get(
        f"{FHIR}/Observation?patient={patient_id}", headers=doctor_headers
    )
    assert res.status_code == 200
    obs = res.json()["entry"][0]["resource"]
    assert obs["resourceType"] == "Observation"
    assert obs["status"] == "final"
    assert obs["valueString"] == "5.4 %"
    assert obs["referenceRange"][0]["text"] == "<6.5"
    assert obs["category"][0]["coding"][0]["code"] == "laboratory"


@pytest.mark.asyncio
async def test_allergy_intolerance_search(
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
            "reaction": "hives",
        },
    )
    res = await client.get(
        f"{FHIR}/AllergyIntolerance?patient={patient_id}", headers=doctor_headers
    )
    assert res.status_code == 200
    ai = res.json()["entry"][0]["resource"]
    assert ai["resourceType"] == "AllergyIntolerance"
    assert ai["criticality"] == "high"
    assert ai["code"]["text"] == "Penicillin"
    assert ai["reaction"][0]["manifestation"][0]["text"] == "hives"
    assert ai["reaction"][0]["severity"] == "severe"


@pytest.mark.asyncio
async def test_everything_returns_bundle_of_all_resources(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    # Drop one of each related resource into the patient.
    await client.post(
        "/api/v1/med/diagnoses",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "icd10_code": "E11",
            "name": "Type 2 diabetes",
            "status": "confirmed",
        },
    )
    await client.post(
        "/api/v1/med/prescriptions",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "medication_name": "Metformin",
            "dosage": "500mg",
            "frequency": "bid",
            "route": "oral",
            "start_date": "2026-05-15",
        },
    )
    await client.post(
        "/api/v1/med/lab-results",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "test_name": "HbA1c",
            "test_category": "Chemistry",
            "result_value": "7.2",
            "unit": "%",
            "reference_range": "<6.5",
            "status": "final",
            "ordered_at": "2026-05-15T10:00:00Z",
            "resulted_at": "2026-05-15T11:00:00Z",
        },
    )
    await client.post(
        "/api/v1/med/allergies",
        headers=doctor_headers,
        json={"patient_id": patient_id, "allergen": "Sulfa", "severity": "mild"},
    )

    res = await client.get(
        f"{FHIR}/Patient/{patient_id}/$everything", headers=doctor_headers
    )
    assert res.status_code == 200
    body = res.json()
    assert body["resourceType"] == "Bundle"
    assert body["type"] == "searchset"
    types = sorted(e["resource"]["resourceType"] for e in body["entry"])
    assert types == [
        "AllergyIntolerance",
        "Condition",
        "MedicationRequest",
        "Observation",
        "Patient",
    ]


@pytest.mark.asyncio
async def test_fhir_requires_auth(client: AsyncClient, patient_id: str) -> None:
    res = await client.get(f"{FHIR}/Patient/{patient_id}")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_fhir_rejects_patient_role(
    client: AsyncClient, patient_id: str, test_engine
) -> None:
    """A patient-role account must not access /fhir — that's bulk-export territory."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from app.repositories.user_repo import UserRepository
    from app.schemas.user import UserCreate

    Session = async_sessionmaker(test_engine, expire_on_commit=False)
    async with Session() as db:
        await UserRepository(db).create(
            UserCreate(
                email="fhir-patient@example.com",
                password="fhir-patient-1",
                full_name="P",
                role="patient",
                patient_id=patient_id,
            )
        )
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "fhir-patient@example.com", "password": "fhir-patient-1"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    res = await client.get(f"{FHIR}/Patient/{patient_id}", headers=headers)
    assert res.status_code == 403
