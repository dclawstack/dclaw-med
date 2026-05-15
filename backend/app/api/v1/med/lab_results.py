"""Lab result endpoints."""

from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import LAB_WRITE, CLINICIAN_READ
from app.core.database import get_db
from app.repositories.lab_result_repo import LabResultRepository
from app.schemas.lab_result import LabResultCreate, LabResultResponse, LabResultUpdate

router = APIRouter()


@router.get("", response_model=list[LabResultResponse], dependencies=[CLINICIAN_READ])
async def list_lab_results(
    patient_id: UUID | None = None,
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
) -> Sequence[LabResultResponse]:
    """List lab results with optional patient filter, newest-ordered first."""
    repo = LabResultRepository(db)
    labs, _ = await repo.list_lab_results(
        patient_id=patient_id, page=page, page_size=page_size
    )
    return [LabResultResponse.model_validate(lab) for lab in labs]


@router.post(
    "",
    response_model=LabResultResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[LAB_WRITE],
)
async def create_lab_result(
    data: LabResultCreate,
    db: AsyncSession = Depends(get_db),
) -> LabResultResponse:
    """Create a new lab result."""
    repo = LabResultRepository(db)
    lab = await repo.create(data)
    return LabResultResponse.model_validate(lab)


@router.get(
    "/{lab_result_id}", response_model=LabResultResponse, dependencies=[CLINICIAN_READ]
)
async def get_lab_result(
    lab_result_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> LabResultResponse:
    """Get a lab result by ID."""
    repo = LabResultRepository(db)
    lab = await repo.get_by_id(lab_result_id)
    if lab is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lab result not found"
        )
    return LabResultResponse.model_validate(lab)


@router.put(
    "/{lab_result_id}", response_model=LabResultResponse, dependencies=[LAB_WRITE]
)
async def update_lab_result(
    lab_result_id: UUID,
    data: LabResultUpdate,
    db: AsyncSession = Depends(get_db),
) -> LabResultResponse:
    """Update a lab result."""
    repo = LabResultRepository(db)
    lab = await repo.get_by_id(lab_result_id)
    if lab is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lab result not found"
        )
    lab = await repo.update(lab, data)
    return LabResultResponse.model_validate(lab)


@router.delete(
    "/{lab_result_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[LAB_WRITE],
)
async def delete_lab_result(
    lab_result_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a lab result."""
    repo = LabResultRepository(db)
    lab = await repo.get_by_id(lab_result_id)
    if lab is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lab result not found"
        )
    await repo.delete(lab)
