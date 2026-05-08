"""Prescription endpoints."""

from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.prescription_repo import PrescriptionRepository
from app.schemas.prescription import (
    PrescriptionCreate,
    PrescriptionResponse,
    PrescriptionUpdate,
)

router = APIRouter()


@router.get("", response_model=list[PrescriptionResponse])
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


@router.post("", response_model=PrescriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_prescription(
    data: PrescriptionCreate,
    db: AsyncSession = Depends(get_db),
) -> PrescriptionResponse:
    """Create a new prescription."""
    repo = PrescriptionRepository(db)
    prescription = await repo.create(data)
    return PrescriptionResponse.model_validate(prescription)


@router.get("/{prescription_id}", response_model=PrescriptionResponse)
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


@router.put("/{prescription_id}", response_model=PrescriptionResponse)
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


@router.delete("/{prescription_id}", status_code=status.HTTP_204_NO_CONTENT)
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
