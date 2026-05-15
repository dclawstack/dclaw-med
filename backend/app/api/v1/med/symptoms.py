"""Symptom analysis endpoints."""

from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CLINICAL_TOOL, CLINICIAN_READ, SYMPTOM_WRITE, get_current_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.symptom_repo import SymptomRepository
from app.schemas.symptom import (
    SymptomAnalysisRequest,
    SymptomAnalysisResponse,
    SymptomCreate,
    SymptomResponse,
    SymptomUpdate,
    TriageRequest,
    TriageResponse,
)
from app.services.symptom_analyzer import analyze_symptoms, triage

router = APIRouter()


@router.post(
    "/analyze",
    response_model=SymptomAnalysisResponse,
    dependencies=[CLINICAL_TOOL],
)
async def analyze_symptoms_endpoint(
    request: SymptomAnalysisRequest,
) -> SymptomAnalysisResponse:
    """Analyze symptoms and return differential diagnosis."""
    return await analyze_symptoms(request)


@router.post("/triage", response_model=TriageResponse)
async def triage_endpoint(
    request: TriageRequest,
    _current: User = Depends(get_current_user),
) -> TriageResponse:
    """Triage a free-text symptom description.

    Available to any authenticated user (including patient role) so a patient
    can self-triage before booking. Returns urgency, suggested department,
    red flags, recommended tests, and a short guidance line.
    """
    return await triage(request)


@router.get("", response_model=list[SymptomResponse], dependencies=[CLINICIAN_READ])
async def list_symptoms(
    patient_id: UUID | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> Sequence[SymptomResponse]:
    """List symptoms with optional patient filter."""
    repo = SymptomRepository(db)
    symptoms, _ = await repo.list_symptoms(
        patient_id=patient_id, page=page, page_size=page_size
    )
    return [SymptomResponse.model_validate(s) for s in symptoms]


@router.post(
    "",
    response_model=SymptomResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[SYMPTOM_WRITE],
)
async def create_symptom(
    data: SymptomCreate,
    db: AsyncSession = Depends(get_db),
) -> SymptomResponse:
    """Create a new symptom record."""
    repo = SymptomRepository(db)
    symptom = await repo.create(data)
    return SymptomResponse.model_validate(symptom)


@router.get("/{symptom_id}", response_model=SymptomResponse, dependencies=[CLINICIAN_READ])
async def get_symptom(
    symptom_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> SymptomResponse:
    """Get a symptom by ID."""
    repo = SymptomRepository(db)
    symptom = await repo.get_by_id(symptom_id)
    if not symptom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symptom not found")
    return SymptomResponse.model_validate(symptom)


@router.put("/{symptom_id}", response_model=SymptomResponse, dependencies=[SYMPTOM_WRITE])
async def update_symptom(
    symptom_id: UUID,
    data: SymptomUpdate,
    db: AsyncSession = Depends(get_db),
) -> SymptomResponse:
    """Update a symptom."""
    repo = SymptomRepository(db)
    symptom = await repo.get_by_id(symptom_id)
    if not symptom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symptom not found")
    symptom = await repo.update(symptom, data)
    return SymptomResponse.model_validate(symptom)


@router.delete(
    "/{symptom_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[SYMPTOM_WRITE],
)
async def delete_symptom(
    symptom_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a symptom."""
    repo = SymptomRepository(db)
    symptom = await repo.get_by_id(symptom_id)
    if not symptom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symptom not found")
    await repo.delete(symptom)
