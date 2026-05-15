"""Tests for the /api/v1/patient-portal/* router and the patient/clinician RBAC split."""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate


async def _make_patient_user(
    client: AsyncClient,
    engine: AsyncEngine,
    email: str,
    patient_id: str | None,
) -> dict[str, str]:
    """Create a patient-role user and return Authorization headers."""
    password = "patient-portal-1"
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as db:
        repo = UserRepository(db)
        existing = await repo.get_by_email(email)
        if existing is None:
            await repo.create(
                UserCreate(
                    email=email,
                    password=password,
                    full_name="Portal User",
                    role="patient",
                    patient_id=patient_id,
                )
            )
        elif existing.patient_id != patient_id:
            await repo.set_patient_link(existing, patient_id)
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest_asyncio.fixture
async def patient_headers(
    client: AsyncClient,
    test_engine: AsyncEngine,
    patient_id: str,
) -> dict[str, str]:
    return await _make_patient_user(
        client, test_engine, "linked-patient@example.com", patient_id
    )


@pytest_asyncio.fixture
async def unlinked_patient_headers(
    client: AsyncClient, test_engine: AsyncEngine
) -> dict[str, str]:
    return await _make_patient_user(
        client, test_engine, "unlinked-patient@example.com", None
    )


@pytest.mark.asyncio
async def test_patient_can_read_own_record(
    client: AsyncClient,
    patient_headers: dict[str, str],
    patient_id: str,
) -> None:
    res = await client.get("/api/v1/patient-portal/me", headers=patient_headers)
    assert res.status_code == 200
    assert res.json()["id"] == patient_id


@pytest.mark.asyncio
async def test_patient_lists_only_own_prescriptions(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_headers: dict[str, str],
    patient_id: str,
) -> None:
    # Create a second patient with their own prescription.
    other = await client.post(
        "/api/v1/med/patients",
        headers=doctor_headers,
        json={
            "name": "Stranger",
            "date_of_birth": "1980-01-01",
            "gender": "other",
            "medical_record_number": "MRN-STRANGER-1",
        },
    )
    other_id = other.json()["id"]
    for pid, med in ((patient_id, "Lisinopril"), (other_id, "Metformin")):
        await client.post(
            "/api/v1/med/prescriptions",
            headers=doctor_headers,
            json={
                "patient_id": pid,
                "medication_name": med,
                "dosage": "10mg",
                "frequency": "daily",
                "route": "oral",
                "start_date": "2026-05-15",
            },
        )

    res = await client.get(
        "/api/v1/patient-portal/me/prescriptions", headers=patient_headers
    )
    assert res.status_code == 200
    meds = [p["medication_name"] for p in res.json()]
    assert meds == ["Lisinopril"]


@pytest.mark.asyncio
async def test_patient_lists_own_allergies_labs_notes_appointments(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    admin_headers: dict[str, str],
    patient_headers: dict[str, str],
    patient_id: str,
) -> None:
    await client.post(
        "/api/v1/med/allergies",
        headers=doctor_headers,
        json={"patient_id": patient_id, "allergen": "Latex", "severity": "moderate"},
    )
    await client.post(
        "/api/v1/med/lab-results",
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "test_name": "HbA1c",
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
            "content": "Doing well.",
        },
    )
    # Appointments need a provider — the admin user works.
    me = await client.get("/api/v1/auth/me", headers=admin_headers)
    provider_id = me.json()["id"]
    await client.post(
        "/api/v1/med/appointments",
        headers=admin_headers,
        json={
            "patient_id": patient_id,
            "provider_id": provider_id,
            "scheduled_at": "2026-06-01T09:00:00Z",
        },
    )

    for path, key in (
        ("/api/v1/patient-portal/me/allergies", "allergen"),
        ("/api/v1/patient-portal/me/lab-results", "test_name"),
        ("/api/v1/patient-portal/me/notes", "content"),
        ("/api/v1/patient-portal/me/appointments", "patient_id"),
    ):
        res = await client.get(path, headers=patient_headers)
        assert res.status_code == 200, (path, res.text)
        assert len(res.json()) == 1, (path, res.json())


@pytest.mark.asyncio
async def test_patient_blocked_from_med_routes(
    client: AsyncClient, patient_headers: dict[str, str], patient_id: str
) -> None:
    for path in (
        "/api/v1/med/patients",
        "/api/v1/med/prescriptions",
        f"/api/v1/med/prescriptions?patient_id={patient_id}",
        "/api/v1/med/allergies?patient_id=" + patient_id,
    ):
        res = await client.get(path, headers=patient_headers)
        assert res.status_code == 403, (path, res.status_code)


@pytest.mark.asyncio
async def test_clinician_cannot_use_portal(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    res = await client.get("/api/v1/patient-portal/me", headers=doctor_headers)
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_unlinked_patient_gets_clear_403(
    client: AsyncClient, unlinked_patient_headers: dict[str, str]
) -> None:
    res = await client.get(
        "/api/v1/patient-portal/me", headers=unlinked_patient_headers
    )
    assert res.status_code == 403
    assert "not yet linked" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_portal_requires_auth(client: AsyncClient) -> None:
    res = await client.get("/api/v1/patient-portal/me")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_register_patient_requires_patient_id(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    res = await client.post(
        "/api/v1/auth/register",
        headers=admin_headers,
        json={
            "email": "needs-link@example.com",
            "password": "password-12",
            "full_name": "Unlinked",
            "role": "patient",
        },
    )
    assert res.status_code == 422
    assert "patient_id is required" in res.json()["detail"]


@pytest.mark.asyncio
async def test_register_clinician_rejects_patient_id(
    client: AsyncClient, admin_headers: dict[str, str], patient_id: str
) -> None:
    res = await client.post(
        "/api/v1/auth/register",
        headers=admin_headers,
        json={
            "email": "weird-doctor@example.com",
            "password": "password-12",
            "full_name": "Weird",
            "role": "doctor",
            "patient_id": patient_id,
        },
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_admin_can_link_user_to_patient(
    client: AsyncClient,
    admin_headers: dict[str, str],
    unlinked_patient_headers: dict[str, str],
    patient_id: str,
) -> None:
    # find the unlinked user's id
    me = await client.get("/api/v1/auth/me", headers=unlinked_patient_headers)
    user_id = me.json()["id"]

    res = await client.patch(
        f"/api/v1/auth/users/{user_id}/patient",
        headers=admin_headers,
        json={"patient_id": patient_id},
    )
    assert res.status_code == 200
    assert res.json()["patient_id"] == patient_id

    # Now they can read /me
    me_after = await client.get(
        "/api/v1/patient-portal/me", headers=unlinked_patient_headers
    )
    assert me_after.status_code == 200


@pytest.mark.asyncio
async def test_non_admin_cannot_link_user(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    res = await client.patch(
        "/api/v1/auth/users/00000000-0000-0000-0000-000000000000/patient",
        headers=doctor_headers,
        json={"patient_id": None},
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_cannot_link_clinician_to_patient(
    client: AsyncClient,
    admin_headers: dict[str, str],
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    doc = await client.get("/api/v1/auth/me", headers=doctor_headers)
    res = await client.patch(
        f"/api/v1/auth/users/{doc.json()['id']}/patient",
        headers=admin_headers,
        json={"patient_id": patient_id},
    )
    assert res.status_code == 422
