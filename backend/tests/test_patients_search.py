"""Tests for patient list search + filters."""

import pytest
from httpx import AsyncClient


async def _create_patient(
    client: AsyncClient,
    headers: dict[str, str],
    name: str,
    mrn: str,
    dob: str,
    gender: str = "other",
) -> str:
    res = await client.post(
        "/api/v1/med/patients",
        headers=headers,
        json={
            "name": name,
            "date_of_birth": dob,
            "gender": gender,
            "medical_record_number": mrn,
        },
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]


@pytest.mark.asyncio
async def test_search_by_name_full_text(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    await _create_patient(client, doctor_headers, "Alice Anderson", "MRN-S1", "1990-01-01")
    await _create_patient(client, doctor_headers, "Bob Brown", "MRN-S2", "1985-06-15")
    await _create_patient(client, doctor_headers, "Charlie Chen", "MRN-S3", "2000-12-31")

    res = await client.get(
        "/api/v1/med/patients?q=anderson", headers=doctor_headers
    )
    assert res.status_code == 200
    names = [p["name"] for p in res.json()]
    assert names == ["Alice Anderson"]


@pytest.mark.asyncio
async def test_search_by_name_partial_token(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    await _create_patient(client, doctor_headers, "Eleanor Vance", "MRN-S4", "1980-01-01")
    # websearch_to_tsquery treats unquoted tokens as prefix-matched against the index
    res = await client.get(
        "/api/v1/med/patients?q=vance", headers=doctor_headers
    )
    assert res.status_code == 200
    assert any(p["name"] == "Eleanor Vance" for p in res.json())


@pytest.mark.asyncio
async def test_search_by_mrn_substring(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    await _create_patient(client, doctor_headers, "Diana D", "MRN-XYZ-9001", "1990-01-01")
    await _create_patient(client, doctor_headers, "Frank F", "MRN-OTHER-001", "1990-01-01")

    res = await client.get(
        "/api/v1/med/patients?q=XYZ", headers=doctor_headers
    )
    assert res.status_code == 200
    mrns = [p["medical_record_number"] for p in res.json()]
    assert mrns == ["MRN-XYZ-9001"]


@pytest.mark.asyncio
async def test_filter_by_dob_range(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    await _create_patient(client, doctor_headers, "Old Patient", "MRN-D1", "1950-01-01")
    await _create_patient(client, doctor_headers, "Mid Patient", "MRN-D2", "1980-06-15")
    await _create_patient(client, doctor_headers, "Young Patient", "MRN-D3", "2010-12-31")

    res = await client.get(
        "/api/v1/med/patients?dob_from=1970-01-01&dob_to=1999-12-31",
        headers=doctor_headers,
    )
    assert res.status_code == 200
    names = sorted(p["name"] for p in res.json())
    assert names == ["Mid Patient"]


@pytest.mark.asyncio
async def test_filter_by_diagnosis_code(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    pid_a = await _create_patient(
        client, doctor_headers, "Hyper A", "MRN-DX-1", "1990-01-01"
    )
    pid_b = await _create_patient(
        client, doctor_headers, "Hyper B", "MRN-DX-2", "1990-01-01"
    )
    await _create_patient(client, doctor_headers, "No Dx", "MRN-DX-3", "1990-01-01")

    for pid in (pid_a, pid_b):
        res = await client.post(
            "/api/v1/med/diagnoses",
            headers=doctor_headers,
            json={
                "patient_id": pid,
                "icd10_code": "I10",
                "name": "Essential hypertension",
                "status": "confirmed",
            },
        )
        assert res.status_code == 201, res.text

    res = await client.get(
        "/api/v1/med/patients?diagnosis_code=I10", headers=doctor_headers
    )
    assert res.status_code == 200
    names = sorted(p["name"] for p in res.json())
    assert names == ["Hyper A", "Hyper B"]


@pytest.mark.asyncio
async def test_combined_filters(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    pid = await _create_patient(
        client, doctor_headers, "Carol Combo", "MRN-CB-1", "1975-03-10"
    )
    # A patient with the right name but outside the DOB window
    await _create_patient(client, doctor_headers, "Carol Decoy", "MRN-CB-2", "2010-01-01")

    await client.post(
        "/api/v1/med/diagnoses",
        headers=doctor_headers,
        json={
            "patient_id": pid,
            "icd10_code": "E11",
            "name": "Type 2 diabetes",
            "status": "confirmed",
        },
    )

    res = await client.get(
        "/api/v1/med/patients"
        "?q=carol&dob_from=1970-01-01&dob_to=1980-12-31&diagnosis_code=E11",
        headers=doctor_headers,
    )
    assert res.status_code == 200
    names = [p["name"] for p in res.json()]
    assert names == ["Carol Combo"]


@pytest.mark.asyncio
async def test_empty_search_returns_all(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    await _create_patient(client, doctor_headers, "P One", "MRN-E1", "1990-01-01")
    await _create_patient(client, doctor_headers, "P Two", "MRN-E2", "1990-01-01")

    res = await client.get("/api/v1/med/patients", headers=doctor_headers)
    assert res.status_code == 200
    assert len(res.json()) == 2


@pytest.mark.asyncio
async def test_page_size_clamped(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    res = await client.get(
        "/api/v1/med/patients?page_size=500", headers=doctor_headers
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_search_requires_auth(client: AsyncClient) -> None:
    res = await client.get("/api/v1/med/patients?q=alice")
    assert res.status_code == 401
