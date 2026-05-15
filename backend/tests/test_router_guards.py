"""Role-based access tests for /api/v1/med routers."""

import pytest
from httpx import AsyncClient


# ---------- 401: unauthenticated requests ----------

@pytest.mark.parametrize(
    "method,path",
    [
        ("GET", "/api/v1/med/patients"),
        ("POST", "/api/v1/med/patients"),
        ("GET", "/api/v1/med/symptoms"),
        ("POST", "/api/v1/med/symptoms"),
        ("GET", "/api/v1/med/diagnoses"),
        ("POST", "/api/v1/med/diagnoses"),
        ("GET", "/api/v1/med/prescriptions"),
        ("POST", "/api/v1/med/prescriptions"),
        ("GET", "/api/v1/med/notes"),
        ("POST", "/api/v1/med/notes"),
        ("POST", "/api/v1/med/icd10/lookup"),
        ("POST", "/api/v1/med/drug/interactions"),
        ("POST", "/api/v1/med/symptoms/analyze"),
        ("POST", "/api/v1/med/notes/generate"),
    ],
)
@pytest.mark.asyncio
async def test_protected_endpoints_reject_anonymous(
    client: AsyncClient, method: str, path: str
) -> None:
    res = await client.request(method, path, json={})
    assert res.status_code == 401, f"{method} {path} → {res.status_code}"


# ---------- Patients: PATIENT_WRITE = admin|doctor|receptionist ----------

@pytest.mark.asyncio
async def test_patients_create_allowed_for_receptionist(
    client: AsyncClient, receptionist_headers: dict[str, str]
) -> None:
    res = await client.post(
        "/api/v1/med/patients",
        headers=receptionist_headers,
        json={
            "name": "R Patient",
            "date_of_birth": "1985-06-15",
            "gender": "female",
            "medical_record_number": "MRN-R-001",
        },
    )
    assert res.status_code == 201


@pytest.mark.asyncio
async def test_patients_create_denied_for_nurse(
    client: AsyncClient, nurse_headers: dict[str, str]
) -> None:
    res = await client.post(
        "/api/v1/med/patients",
        headers=nurse_headers,
        json={
            "name": "N Patient",
            "date_of_birth": "1985-06-15",
            "gender": "female",
            "medical_record_number": "MRN-N-001",
        },
    )
    assert res.status_code == 403


# ---------- Symptoms: SYMPTOM_WRITE = admin|doctor|nurse ----------

@pytest.mark.asyncio
async def test_symptoms_create_allowed_for_nurse(
    client: AsyncClient, nurse_headers: dict[str, str], patient_id: str
) -> None:
    res = await client.post(
        "/api/v1/med/symptoms",
        headers=nurse_headers,
        json={"patient_id": patient_id, "description": "headache", "severity": 4},
    )
    assert res.status_code == 201


@pytest.mark.asyncio
async def test_symptoms_create_denied_for_receptionist(
    client: AsyncClient, receptionist_headers: dict[str, str], patient_id: str
) -> None:
    res = await client.post(
        "/api/v1/med/symptoms",
        headers=receptionist_headers,
        json={"patient_id": patient_id, "description": "headache", "severity": 4},
    )
    assert res.status_code == 403


# ---------- Diagnoses: DIAGNOSIS_WRITE = admin|doctor ----------

@pytest.mark.asyncio
async def test_diagnoses_create_allowed_for_doctor(
    client: AsyncClient, doctor_headers: dict[str, str], patient_id: str
) -> None:
    res = await client.post(
        "/api/v1/med/diagnoses",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "icd10_code": "J00",
            "name": "Common cold",
            "status": "provisional",
        },
    )
    assert res.status_code == 201


@pytest.mark.asyncio
async def test_diagnoses_create_denied_for_nurse(
    client: AsyncClient, nurse_headers: dict[str, str], patient_id: str
) -> None:
    res = await client.post(
        "/api/v1/med/diagnoses",
        headers=nurse_headers,
        json={
            "patient_id": patient_id,
            "icd10_code": "J00",
            "name": "Common cold",
            "status": "provisional",
        },
    )
    assert res.status_code == 403


# ---------- Prescriptions: PRESCRIPTION_WRITE = admin|doctor ----------

@pytest.mark.asyncio
async def test_prescriptions_create_allowed_for_doctor(
    client: AsyncClient, doctor_headers: dict[str, str], patient_id: str
) -> None:
    res = await client.post(
        "/api/v1/med/prescriptions",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "medication_name": "Ibuprofen",
            "dosage": "200mg",
            "frequency": "q8h",
            "route": "oral",
            "start_date": "2026-05-12",
        },
    )
    assert res.status_code == 201


@pytest.mark.asyncio
async def test_prescriptions_create_denied_for_nurse(
    client: AsyncClient, nurse_headers: dict[str, str], patient_id: str
) -> None:
    res = await client.post(
        "/api/v1/med/prescriptions",
        headers=nurse_headers,
        json={
            "patient_id": patient_id,
            "medication_name": "Ibuprofen",
            "dosage": "200mg",
            "frequency": "q8h",
            "route": "oral",
            "start_date": "2026-05-12",
        },
    )
    assert res.status_code == 403


# ---------- Notes: NOTE_WRITE = admin|doctor|nurse ----------

@pytest.mark.asyncio
async def test_notes_create_allowed_for_nurse(
    client: AsyncClient, nurse_headers: dict[str, str], patient_id: str
) -> None:
    res = await client.post(
        "/api/v1/med/notes",
        headers=nurse_headers,
        json={"patient_id": patient_id, "note_type": "progress", "content": "stable"},
    )
    assert res.status_code == 201


@pytest.mark.asyncio
async def test_notes_create_denied_for_receptionist(
    client: AsyncClient, receptionist_headers: dict[str, str], patient_id: str
) -> None:
    res = await client.post(
        "/api/v1/med/notes",
        headers=receptionist_headers,
        json={"patient_id": patient_id, "note_type": "progress", "content": "stable"},
    )
    assert res.status_code == 403


# ---------- ICD-10: CLINICIAN_READ (everyone authenticated) ----------

@pytest.mark.asyncio
async def test_icd10_allowed_for_receptionist(
    client: AsyncClient, receptionist_headers: dict[str, str]
) -> None:
    res = await client.post(
        "/api/v1/med/icd10/lookup",
        headers=receptionist_headers,
        json={"query": "cold"},
    )
    assert res.status_code == 200


# ---------- Drug interactions: CLINICAL_TOOL = admin|doctor|nurse ----------

@pytest.mark.asyncio
async def test_drug_interactions_denied_for_receptionist(
    client: AsyncClient, receptionist_headers: dict[str, str]
) -> None:
    res = await client.post(
        "/api/v1/med/drug/interactions",
        headers=receptionist_headers,
        json={"drugs": ["ibuprofen", "aspirin"]},
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_drug_interactions_allowed_for_nurse(
    client: AsyncClient, nurse_headers: dict[str, str]
) -> None:
    res = await client.post(
        "/api/v1/med/drug/interactions",
        headers=nurse_headers,
        json={"drugs": ["ibuprofen", "aspirin"]},
    )
    assert res.status_code == 200


# ---------- Read-only access universally allowed for authenticated ----------

@pytest.mark.asyncio
async def test_patients_list_allowed_for_nurse(
    client: AsyncClient, nurse_headers: dict[str, str]
) -> None:
    res = await client.get("/api/v1/med/patients", headers=nurse_headers)
    assert res.status_code == 200
