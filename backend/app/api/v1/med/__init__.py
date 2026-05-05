"""Aggregate medical API routers."""

from fastapi import APIRouter

from app.api.v1.med import drugs, icd10, notes, patients, symptoms

router = APIRouter()
router.include_router(symptoms.router, prefix="/symptoms", tags=["Symptoms"])
router.include_router(notes.router, prefix="/notes", tags=["Clinical Notes"])
router.include_router(icd10.router, prefix="/icd10", tags=["ICD-10"])
router.include_router(drugs.router, prefix="/drug", tags=["Drug Interactions"])
router.include_router(patients.router, prefix="/patients", tags=["Patients"])
