"""Allergy endpoints."""

from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import ALLERGY_WRITE, CLINICIAN_READ
from app.core.database import get_db
from app.repositories.allergy_repo import AllergyRepository
from app.schemas.allergy import AllergyCreate, AllergyResponse, AllergyUpdate

router = APIRouter()


@router.get("", response_model=list[AllergyResponse], dependencies=[CLINICIAN_READ])
async def list_allergies(
    patient_id: UUID = Query(..., description="Patient to list allergies for"),
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
) -> Sequence[AllergyResponse]:
    """List allergies for a patient, newest first."""
    allergies, _ = await AllergyRepository(db).list_for_patient(
        patient_id=patient_id, page=page, page_size=page_size
    )
    return [AllergyResponse.model_validate(a) for a in allergies]


@router.post(
    "",
    response_model=AllergyResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[ALLERGY_WRITE],
)
async def create_allergy(
    data: AllergyCreate,
    db: AsyncSession = Depends(get_db),
) -> AllergyResponse:
    """Record a new allergy for a patient."""
    try:
        allergy = await AllergyRepository(db).create(data)
    except Exception as exc:
        # Unique (patient_id, allergen) constraint guards against duplicates.
        await db.rollback()
        msg = str(exc).lower()
        if "uq_allergies_patient_allergen" in msg or "unique" in msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This allergen is already recorded for the patient.",
            )
        raise
    return AllergyResponse.model_validate(allergy)


@router.get("/{allergy_id}", response_model=AllergyResponse, dependencies=[CLINICIAN_READ])
async def get_allergy(
    allergy_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> AllergyResponse:
    allergy = await AllergyRepository(db).get_by_id(allergy_id)
    if allergy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Allergy not found"
        )
    return AllergyResponse.model_validate(allergy)


@router.put(
    "/{allergy_id}", response_model=AllergyResponse, dependencies=[ALLERGY_WRITE]
)
async def update_allergy(
    allergy_id: UUID,
    data: AllergyUpdate,
    db: AsyncSession = Depends(get_db),
) -> AllergyResponse:
    repo = AllergyRepository(db)
    allergy = await repo.get_by_id(allergy_id)
    if allergy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Allergy not found"
        )
    allergy = await repo.update(allergy, data)
    return AllergyResponse.model_validate(allergy)


@router.delete(
    "/{allergy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[ALLERGY_WRITE],
)
async def delete_allergy(
    allergy_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    repo = AllergyRepository(db)
    allergy = await repo.get_by_id(allergy_id)
    if allergy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Allergy not found"
        )
    await repo.delete(allergy)
