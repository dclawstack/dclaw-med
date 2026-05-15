"""FHIR R4 read-only export endpoints.

Mounted under /api/v1/med/fhir. The resource types follow standard FHIR REST:
- GET /Patient/{id}
- GET /Patient/{id}/$everything   (Bundle of every resource for the patient)
- GET /Condition?patient={id}
- GET /MedicationRequest?patient={id}
- GET /Observation?patient={id}
- GET /AllergyIntolerance?patient={id}

These are clinician-only — see app.core.auth.CLINICIAN_READ. The shape is best
effort FHIR R4 and is intended for interop sanity checks, not strict spec
conformance.
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CLINICIAN_READ
from app.core.database import get_db
from app.repositories.allergy_repo import AllergyRepository
from app.repositories.diagnosis_repo import DiagnosisRepository
from app.repositories.lab_result_repo import LabResultRepository
from app.repositories.patient_repo import PatientRepository
from app.repositories.prescription_repo import PrescriptionRepository
from app.services.fhir_mapper import (
    allergy_to_fhir,
    bundle,
    diagnosis_to_fhir,
    everything_bundle,
    lab_result_to_fhir,
    patient_to_fhir,
    prescription_to_fhir,
)

router = APIRouter()


async def _require_patient(db: AsyncSession, patient_id: UUID):
    repo = PatientRepository(db)
    patient = await repo.get_by_id(patient_id)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    return patient


@router.get("/Patient/{patient_id}", dependencies=[CLINICIAN_READ])
async def get_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    patient = await _require_patient(db, patient_id)
    return patient_to_fhir(patient)


@router.get("/Patient/{patient_id}/$everything", dependencies=[CLINICIAN_READ])
async def get_patient_everything(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Return a Bundle of every resource attached to this patient."""
    patient = await PatientRepository(db).get_for_report(patient_id)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    return everything_bundle(patient)


@router.get("/Condition", dependencies=[CLINICIAN_READ])
async def search_conditions(
    patient: UUID = Query(..., description="Patient FHIR id (UUID)"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await _require_patient(db, patient)
    items, _ = await DiagnosisRepository(db).list_diagnoses(
        patient_id=patient, page=1, page_size=200
    )
    return bundle("Condition", [diagnosis_to_fhir(d) for d in items])


@router.get("/MedicationRequest", dependencies=[CLINICIAN_READ])
async def search_medication_requests(
    patient: UUID = Query(..., description="Patient FHIR id (UUID)"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await _require_patient(db, patient)
    items, _ = await PrescriptionRepository(db).list_prescriptions(
        patient_id=patient, page=1, page_size=200
    )
    return bundle("MedicationRequest", [prescription_to_fhir(rx) for rx in items])


@router.get("/Observation", dependencies=[CLINICIAN_READ])
async def search_observations(
    patient: UUID = Query(..., description="Patient FHIR id (UUID)"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await _require_patient(db, patient)
    items, _ = await LabResultRepository(db).list_lab_results(
        patient_id=patient, page=1, page_size=200
    )
    return bundle("Observation", [lab_result_to_fhir(l) for l in items])


@router.get("/AllergyIntolerance", dependencies=[CLINICIAN_READ])
async def search_allergies(
    patient: UUID = Query(..., description="Patient FHIR id (UUID)"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await _require_patient(db, patient)
    items, _ = await AllergyRepository(db).list_for_patient(
        patient_id=patient, page=1, page_size=200
    )
    return bundle("AllergyIntolerance", [allergy_to_fhir(a) for a in items])
