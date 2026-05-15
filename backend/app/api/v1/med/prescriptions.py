"""Prescription endpoints."""

from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import PRESCRIPTION_WRITE, READ_ANY
from app.core.database import get_db
from app.repositories.allergy_repo import AllergyRepository
from app.repositories.prescription_repo import PrescriptionRepository
from app.schemas.allergy import AllergyWarning
from app.schemas.prescription import (
    PrescriptionCreate,
    PrescriptionCreateResponse,
    PrescriptionResponse,
    PrescriptionUpdate,
)

router = APIRouter()


@router.get("", response_model=list[PrescriptionResponse], dependencies=[READ_ANY])
async def list_prescriptions(
    patient_id: UUID | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> Sequence[PrescriptionResponse]:
    """List prescriptions with optional patient filter."""
    repo = PrescriptionRepository(db)
    prescriptions, _ = await repo.list_prescriptions(
        patient_id=patient_id, page=page, page_size=page_size
    )
    return [PrescriptionResponse.model_validate(p) for p in prescriptions]


@router.post(
    "",
    response_model=PrescriptionCreateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[PRESCRIPTION_WRITE],
)
async def create_prescription(
    data: PrescriptionCreate,
    db: AsyncSession = Depends(get_db),
) -> PrescriptionCreateResponse:
    """Create a new prescription. Returns matching allergy warnings if any."""
    matches = await AllergyRepository(db).match_for_medication(
        patient_id=data.patient_id, medication_name=data.medication_name
    )
    warnings = [
        AllergyWarning(
            allergy_id=a.id,
            allergen=a.allergen,
            severity=a.severity,
            reaction=a.reaction,
        )
        for a in matches
    ]
    prescription = await PrescriptionRepository(db).create(data)
    response = PrescriptionCreateResponse.model_validate(prescription)
    response.allergy_warnings = warnings
    return response


@router.get(
    "/{prescription_id}", response_model=PrescriptionResponse, dependencies=[READ_ANY]
)
async def get_prescription(
    prescription_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> PrescriptionResponse:
    """Get a prescription by ID."""
    repo = PrescriptionRepository(db)
    prescription = await repo.get_by_id(prescription_id)
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found"
        )
    return PrescriptionResponse.model_validate(prescription)


@router.put(
    "/{prescription_id}",
    response_model=PrescriptionResponse,
    dependencies=[PRESCRIPTION_WRITE],
)
async def update_prescription(
    prescription_id: UUID,
    data: PrescriptionUpdate,
    db: AsyncSession = Depends(get_db),
) -> PrescriptionResponse:
    """Update a prescription."""
    repo = PrescriptionRepository(db)
    prescription = await repo.get_by_id(prescription_id)
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found"
        )
    prescription = await repo.update(prescription, data)
    return PrescriptionResponse.model_validate(prescription)


@router.delete(
    "/{prescription_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[PRESCRIPTION_WRITE],
)
async def delete_prescription(
    prescription_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a prescription."""
    repo = PrescriptionRepository(db)
    prescription = await repo.get_by_id(prescription_id)
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found"
        )
    await repo.delete(prescription)
