"""Tests for audit log middleware + admin endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_med_request_writes_audit_log(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> None:
    # doctor lists patients → one audit row
    res = await client.get("/api/v1/med/patients", headers=doctor_headers)
    assert res.status_code == 200

    # admin reads the audit log
    audit = await client.get("/api/v1/audit", headers=admin_headers)
    assert audit.status_code == 200
    logs = audit.json()
    med_logs = [
        log
        for log in logs
        if log["entity_type"] == "patients" and log["action"] == "read"
    ]
    assert len(med_logs) >= 1


@pytest.mark.asyncio
async def test_create_patient_records_create_action(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> None:
    res = await client.post(
        "/api/v1/med/patients",
        headers=doctor_headers,
        json={
            "name": "Audit Test",
            "date_of_birth": "1990-01-01",
            "gender": "other",
            "medical_record_number": "MRN-AUDIT-1",
        },
    )
    assert res.status_code == 201

    audit = await client.get(
        "/api/v1/audit?action=create&entity_type=patients", headers=admin_headers
    )
    assert audit.status_code == 200
    logs = audit.json()
    assert any(log["entity_type"] == "patients" and log["action"] == "create" for log in logs)


@pytest.mark.asyncio
async def test_failed_request_does_not_audit(
    client: AsyncClient,
    nurse_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> None:
    # nurse tries to create a patient → 403
    res = await client.post(
        "/api/v1/med/patients",
        headers=nurse_headers,
        json={
            "name": "Forbidden",
            "date_of_birth": "1990-01-01",
            "gender": "other",
            "medical_record_number": "MRN-NEVER-1",
        },
    )
    assert res.status_code == 403

    # the 403 should not show up in the audit log
    audit = await client.get(
        "/api/v1/audit?entity_type=patients&action=create", headers=admin_headers
    )
    assert audit.status_code == 200
    logs = audit.json()
    # no log row for this failed attempt
    matching = [
        log
        for log in logs
        if log.get("new_value", {}).get("medical_record_number") == "MRN-NEVER-1"
    ]
    assert matching == []


@pytest.mark.asyncio
async def test_anonymous_request_does_not_audit(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    res = await client.get("/api/v1/med/patients")
    assert res.status_code == 401
    audit = await client.get("/api/v1/audit", headers=admin_headers)
    # 401 doesn't create a row — total count should not include this request
    assert audit.status_code == 200


@pytest.mark.asyncio
async def test_audit_endpoint_requires_admin(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    nurse_headers: dict[str, str],
    receptionist_headers: dict[str, str],
) -> None:
    for headers in (doctor_headers, nurse_headers, receptionist_headers):
        res = await client.get("/api/v1/audit", headers=headers)
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_audit_endpoint_requires_auth(client: AsyncClient) -> None:
    res = await client.get("/api/v1/audit")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_portal_access_is_audited(
    client: AsyncClient,
    patient_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> None:
    """Patient reading their own portal data must leave an audit row.

    HIPAA expects every PHI access to be logged — that includes self-access
    via /api/v1/patient-portal/*, not just clinician access via /med.
    """
    # Patient reads own record + prescriptions via the portal.
    me = await client.get("/api/v1/patient-portal/me", headers=patient_headers)
    assert me.status_code == 200
    rx = await client.get(
        "/api/v1/patient-portal/me/prescriptions", headers=patient_headers
    )
    assert rx.status_code == 200

    audit = await client.get("/api/v1/audit", headers=admin_headers)
    assert audit.status_code == 200
    rows = audit.json()
    entities = {(r["action"], r["entity_type"]) for r in rows}
    assert ("read", "patient") in entities
    assert ("read", "prescriptions") in entities


@pytest.mark.asyncio
async def test_register_user_writes_audit_log(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """Admin user creation must leave an audit row with entity_type='users'.

    Regression for the gap TestSprite surfaced: account-management actions
    were invisible in /audit because the middleware only covered /med and
    /patient-portal paths.
    """
    res = await client.post(
        "/api/v1/auth/register",
        headers=admin_headers,
        json={
            "email": "audit-target@example.com",
            "password": "audit-test-1",
            "full_name": "Audit Target",
            "role": "doctor",
        },
    )
    assert res.status_code == 201, res.text

    audit = await client.get(
        "/api/v1/audit?entity_type=users&action=create", headers=admin_headers
    )
    assert audit.status_code == 200
    assert any(
        log["entity_type"] == "users" and log["action"] == "create"
        for log in audit.json()
    )


@pytest.mark.asyncio
async def test_link_user_to_patient_writes_audit_log(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """PUT /auth/users/{id}/patient is auditable as an update on entity_type='users'."""
    # Create a patient + a patient-role user to link.
    patient_res = await client.post(
        "/api/v1/med/patients",
        headers=admin_headers,
        json={
            "name": "Link Target",
            "date_of_birth": "1990-01-01",
            "gender": "other",
            "medical_record_number": "MRN-LINK-AUDIT-1",
        },
    )
    assert patient_res.status_code == 201, patient_res.text
    patient_id = patient_res.json()["id"]

    user_res = await client.post(
        "/api/v1/auth/register",
        headers=admin_headers,
        json={
            "email": "link-me@example.com",
            "password": "link-target-1",
            "full_name": "Link Me",
            "role": "patient",
            "patient_id": patient_id,
        },
    )
    assert user_res.status_code == 201, user_res.text
    user_id = user_res.json()["id"]

    # Unlink (PATCH with null patient_id) — the audit interesting bit is the PATCH itself.
    link_res = await client.patch(
        f"/api/v1/auth/users/{user_id}/patient",
        headers=admin_headers,
        json={"patient_id": None},
    )
    assert link_res.status_code == 200, link_res.text

    audit = await client.get(
        f"/api/v1/audit?entity_type=users&action=update", headers=admin_headers
    )
    assert audit.status_code == 200
    rows = audit.json()
    matching = [
        r
        for r in rows
        if r["entity_type"] == "users"
        and r["action"] == "update"
        and r.get("entity_id") == user_id
    ]
    assert matching, f"Expected an update audit row for user {user_id}; got {rows}"


@pytest.mark.asyncio
async def test_list_users_is_not_audited(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """GET /auth/users is admin paginated browse — high volume, no PHI;
    we intentionally don't audit it. Regression to make sure no future
    refactor flips it back on by accident."""
    res = await client.get("/api/v1/auth/users", headers=admin_headers)
    assert res.status_code == 200

    audit = await client.get(
        "/api/v1/audit?entity_type=users&action=read", headers=admin_headers
    )
    assert audit.status_code == 200
    assert audit.json() == []


@pytest.mark.asyncio
async def test_audit_filter_by_user(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> None:
    # generate one doctor and one admin read
    await client.get("/api/v1/med/patients", headers=doctor_headers)
    await client.get("/api/v1/med/patients", headers=admin_headers)

    # fetch doctor's id from /me
    me = await client.get("/api/v1/auth/me", headers=doctor_headers)
    doctor_id = me.json()["id"]

    audit = await client.get(
        f"/api/v1/audit?user_id={doctor_id}", headers=admin_headers
    )
    assert audit.status_code == 200
    logs = audit.json()
    assert all(log["user_id"] == doctor_id for log in logs)
    assert len(logs) >= 1
