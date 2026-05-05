"""Clinical note endpoints."""

from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.clinical_note import ClinicalNote
from app.schemas.clinical_note import (
    ClinicalNoteCreate,
    ClinicalNoteResponse,
    NoteGenerateRequest,
    NoteGenerateResponse,
)
from app.services.note_generator import generate_note

router = APIRouter()


@router.post("/generate", response_model=NoteGenerateResponse)
async def generate_note_endpoint(
    request: NoteGenerateRequest,
) -> NoteGenerateResponse:
    """Generate a clinical note from patient context."""
    return await generate_note(request)


@router.get("", response_model=list[ClinicalNoteResponse])
async def list_notes(
    patient_id: UUID | None = None,
    page: int = 1,
    page_size: int = 20,
) -> Sequence[ClinicalNote]:
    """List clinical notes with optional patient filter."""
    db_gen = get_db()
    session = await db_gen.__anext__()
    try:
        stmt = select(ClinicalNote).offset((page - 1) * page_size).limit(page_size)
        if patient_id:
            stmt = stmt.where(ClinicalNote.patient_id == patient_id)
        result = await session.execute(stmt)
        return result.scalars().all()
    finally:
        await session.close()


@router.post("", response_model=ClinicalNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(data: ClinicalNoteCreate) -> ClinicalNoteResponse:
    """Create a manual clinical note (mock)."""
    from datetime import datetime, timezone

    return ClinicalNoteResponse(
        id=UUID(int=0),
        patient_id=data.patient_id,
        note_type=data.note_type,
        content=data.content,
        generated_by=data.generated_by,
        template_used=data.template_used,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
