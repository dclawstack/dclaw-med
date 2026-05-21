"""Tests for patient CRUD edges not covered by test_patients_search.py.

Search, DOB filter, and the search-by-diagnosis path live in
test_patients_search.py — this file fills in the gaps: create / get /
update / list / delete smoke, MRN-uniqueness 409 on create, and
MRN-uniqueness 409 on update.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


PATIENTS = "/api/v1/med/patients"


@pytest.mark.asyncio
async def test_patient_crud_smoke(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    """create → get → update → list contains → delete → 404."""
    create = await client.post(
        PATIENTS,
        headers=doctor_headers,
        json={
            "name": "Smoke Test",
            "date_of_birth": "1990-01-01",
            "gender": "female",
            "medical_record_number": "MRN-SMOKE-1",
        },
    )
    assert create.status_code == 201, create.text
    pid = create.json()["id"]
    assert create.json()["medical_record_number"] == "MRN-SMOKE-1"

    got = await client.get(f"{PATIENTS}/{pid}", headers=doctor_headers)
    assert got.status_code == 200
    assert got.json()["medical_record_number"] == "MRN-SMOKE-1"

    upd = await client.put(
        f"{PATIENTS}/{pid}",
        headers=doctor_headers,
        json={"name": "Smoke Updated"},
    )
    assert upd.status_code == 200, upd.text
    assert upd.json()["name"] == "Smoke Updated"

    listing = await client.get(PATIENTS, headers=doctor_headers)
    assert listing.status_code == 200
    assert any(p["id"] == pid for p in listing.json())

    delete = await client.delete(f"{PATIENTS}/{pid}", headers=doctor_headers)
    assert delete.status_code in (200, 204), delete.text

    gone = await client.get(f"{PATIENTS}/{pid}", headers=doctor_headers)
    assert gone.status_code == 404


@pytest.mark.asyncio
async def test_update_patient_mrn(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    """PUT can change a patient's medical_record_number — regression
    for the bug where ``PatientUpdate`` was missing the field."""
    create = await client.post(
        PATIENTS,
        headers=doctor_headers,
        json={
            "name": "MRN Change",
            "date_of_birth": "1990-01-01",
            "gender": "other",
            "medical_record_number": "MRN-OLD-1",
        },
    )
    pid = create.json()["id"]

    upd = await client.put(
        f"{PATIENTS}/{pid}",
        headers=doctor_headers,
        json={"medical_record_number": "MRN-NEW-1"},
    )
    assert upd.status_code == 200, upd.text
    assert upd.json()["medical_record_number"] == "MRN-NEW-1"


@pytest.mark.asyncio
async def test_update_patient_to_existing_mrn_409(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    """Updating Patient A's MRN to collide with Patient B's MRN → 409."""
    a = await client.post(
        PATIENTS,
        headers=doctor_headers,
        json={
            "name": "A",
            "date_of_birth": "1990-01-01",
            "gender": "other",
            "medical_record_number": "MRN-UPD-A",
        },
    )
    b = await client.post(
        PATIENTS,
        headers=doctor_headers,
        json={
            "name": "B",
            "date_of_birth": "1990-01-01",
            "gender": "other",
            "medical_record_number": "MRN-UPD-B",
        },
    )
    a_id = a.json()["id"]
    res = await client.put(
        f"{PATIENTS}/{a_id}",
        headers=doctor_headers,
        json={"medical_record_number": b.json()["medical_record_number"]},
    )
    assert res.status_code == 409, res.text


@pytest.mark.asyncio
async def test_create_patient_rejects_duplicate_mrn_409(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    body = {
        "name": "First",
        "date_of_birth": "1990-01-01",
        "gender": "other",
        "medical_record_number": "MRN-DUP-1",
    }
    first = await client.post(PATIENTS, headers=doctor_headers, json=body)
    assert first.status_code == 201, first.text

    dup = await client.post(
        PATIENTS,
        headers=doctor_headers,
        json={**body, "name": "Second"},
    )
    assert dup.status_code == 409, dup.text


@pytest.mark.asyncio
async def test_get_unknown_patient_404(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    res = await client.get(
        f"{PATIENTS}/00000000-0000-0000-0000-000000000000",
        headers=doctor_headers,
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_delete_unknown_patient_404(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    res = await client.delete(
        f"{PATIENTS}/00000000-0000-0000-0000-000000000000",
        headers=doctor_headers,
    )
    assert res.status_code == 404
