"""Diagnosis endpoints."""

from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import DIAGNOSIS_WRITE, CLINICIAN_READ
from app.core.database import get_db
from app.repositories.diagnosis_repo import DiagnosisRepository
from app.schemas.diagnosis import DiagnosisCreate, DiagnosisResponse, DiagnosisUpdate

router = APIRouter()


@router.get("", response_model=list[DiagnosisResponse], dependencies=[CLINICIAN_READ])
async def list_diagnoses(
    patient_id: UUID | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> Sequence[DiagnosisResponse]:
    """List diagnoses with optional patient filter."""
    repo = DiagnosisRepository(db)
    diagnoses, _ = await repo.list_diagnoses(
        patient_id=patient_id, page=page, page_size=page_size
    )
    return [DiagnosisResponse.model_validate(d) for d in diagnoses]


@router.post(
    "",
    response_model=DiagnosisResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[DIAGNOSIS_WRITE],
)
async def create_diagnosis(
    data: DiagnosisCreate,
    db: AsyncSession = Depends(get_db),
) -> DiagnosisResponse:
    """Create a new diagnosis."""
    repo = DiagnosisRepository(db)
    diagnosis = await repo.create(data)
    return DiagnosisResponse.model_validate(diagnosis)


@router.get("/{diagnosis_id}", response_model=DiagnosisResponse, dependencies=[CLINICIAN_READ])
async def get_diagnosis(
    diagnosis_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> DiagnosisResponse:
    """Get a diagnosis by ID."""
    repo = DiagnosisRepository(db)
    diagnosis = await repo.get_by_id(diagnosis_id)
    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Diagnosis not found"
        )
    return DiagnosisResponse.model_validate(diagnosis)


@router.put(
    "/{diagnosis_id}", response_model=DiagnosisResponse, dependencies=[DIAGNOSIS_WRITE]
)
async def update_diagnosis(
    diagnosis_id: UUID,
    data: DiagnosisUpdate,
    db: AsyncSession = Depends(get_db),
) -> DiagnosisResponse:
    """Update a diagnosis."""
    repo = DiagnosisRepository(db)
    diagnosis = await repo.get_by_id(diagnosis_id)
    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Diagnosis not found"
        )
    diagnosis = await repo.update(diagnosis, data)
    return DiagnosisResponse.model_validate(diagnosis)


@router.delete(
    "/{diagnosis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[DIAGNOSIS_WRITE],
)
async def delete_diagnosis(
    diagnosis_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a diagnosis."""
    repo = DiagnosisRepository(db)
    diagnosis = await repo.get_by_id(diagnosis_id)
    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Diagnosis not found"
        )
    await repo.delete(diagnosis)
