"""Aggregate medical API routers."""

from fastapi import APIRouter

from app.api.v1.med import (
    allergies,
    appointments,
    diagnoses,
    drugs,
    fhir,
    icd10,
    lab_results,
    notes,
    patients,
    prescriptions,
    symptoms,
)

router = APIRouter()
router.include_router(symptoms.router, prefix="/symptoms", tags=["Symptoms"])
router.include_router(diagnoses.router, prefix="/diagnoses", tags=["Diagnoses"])
router.include_router(
    prescriptions.router, prefix="/prescriptions", tags=["Prescriptions"]
)
router.include_router(notes.router, prefix="/notes", tags=["Clinical Notes"])
router.include_router(icd10.router, prefix="/icd10", tags=["ICD-10"])
router.include_router(drugs.router, prefix="/drug", tags=["Drug Interactions"])
router.include_router(
    lab_results.router, prefix="/lab-results", tags=["Lab Results"]
)
router.include_router(
    appointments.router, prefix="/appointments", tags=["Appointments"]
)
router.include_router(allergies.router, prefix="/allergies", tags=["Allergies"])
router.include_router(fhir.router, prefix="/fhir", tags=["FHIR"])
router.include_router(patients.router, prefix="/patients", tags=["Patients"])
