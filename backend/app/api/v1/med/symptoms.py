"""Symptom analysis endpoints."""

from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.symptom import Symptom
from app.schemas.symptom import (
    SymptomAnalysisRequest,
    SymptomAnalysisResponse,
    SymptomCreate,
    SymptomResponse,
)
from app.services.symptom_analyzer import analyze_symptoms

router = APIRouter()


@router.post("/analyze", response_model=SymptomAnalysisResponse)
async def analyze_symptoms_endpoint(
    request: SymptomAnalysisRequest,
) -> SymptomAnalysisResponse:
    """Analyze symptoms and return differential diagnosis."""
    return await analyze_symptoms(request)


@router.get("", response_model=list[SymptomResponse])
async def list_symptoms(
    patient_id: UUID | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = ...,  # type: ignore[assignment]
) -> Sequence[Symptom]:
    """List symptoms with optional patient filter."""
    db_gen = get_db()
    session = await db_gen.__anext__()
    try:
        stmt = select(Symptom).offset((page - 1) * page_size).limit(page_size)
        if patient_id:
            stmt = stmt.where(Symptom.patient_id == patient_id)
        result = await session.execute(stmt)
        return result.scalars().all()
    finally:
        await session.close()


@router.post("", response_model=SymptomResponse, status_code=status.HTTP_201_CREATED)
async def create_symptom(data: SymptomCreate) -> SymptomResponse:
    """Create a new symptom record (mock - returns input)."""
    from datetime import datetime, timezone

    return SymptomResponse(
        id=UUID(int=0),
        patient_id=data.patient_id,
        description=data.description,
        onset_date=data.onset_date,
        severity=data.severity,
        body_system=data.body_system,
        notes=data.notes,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
