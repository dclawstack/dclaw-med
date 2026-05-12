"""Clinical note endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CLINICAL_TOOL, NOTE_WRITE, READ_ANY
from app.core.database import get_db
from app.repositories.clinical_note_repo import ClinicalNoteRepository
from app.schemas.clinical_note import (
    ClinicalNoteCreate,
    ClinicalNoteResponse,
    ClinicalNoteUpdate,
    NoteGenerateRequest,
    NoteGenerateResponse,
)
from app.services.note_generator import generate_note

router = APIRouter()


def _to_response(note) -> ClinicalNoteResponse:
    """Convert ClinicalNote ORM to response schema."""
    return ClinicalNoteResponse.model_validate(note)


@router.post(
    "/generate", response_model=NoteGenerateResponse, dependencies=[CLINICAL_TOOL]
)
async def generate_note_endpoint(
    request: NoteGenerateRequest,
) -> NoteGenerateResponse:
    """Generate a clinical note from patient context."""
    return await generate_note(request)


@router.get("", response_model=list[ClinicalNoteResponse], dependencies=[READ_ANY])
async def list_notes(
    patient_id: UUID | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> list[ClinicalNoteResponse]:
    """List clinical notes with optional patient filter."""
    repo = ClinicalNoteRepository(db)
    notes, _ = await repo.list_notes(
        patient_id=patient_id, page=page, page_size=page_size
    )
    return [_to_response(n) for n in notes]


@router.post(
    "",
    response_model=ClinicalNoteResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[NOTE_WRITE],
)
async def create_note(
    data: ClinicalNoteCreate,
    db: AsyncSession = Depends(get_db),
) -> ClinicalNoteResponse:
    """Create a clinical note."""
    repo = ClinicalNoteRepository(db)
    note = await repo.create(data)
    return _to_response(note)


@router.get("/{note_id}", response_model=ClinicalNoteResponse, dependencies=[READ_ANY])
async def get_note(
    note_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ClinicalNoteResponse:
    """Get a clinical note by ID."""
    repo = ClinicalNoteRepository(db)
    note = await repo.get_by_id(note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    return _to_response(note)


@router.put("/{note_id}", response_model=ClinicalNoteResponse, dependencies=[NOTE_WRITE])
async def update_note(
    note_id: UUID,
    data: ClinicalNoteUpdate,
    db: AsyncSession = Depends(get_db),
) -> ClinicalNoteResponse:
    """Update a clinical note."""
    repo = ClinicalNoteRepository(db)
    note = await repo.get_by_id(note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    note = await repo.update(note, data)
    return _to_response(note)


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[NOTE_WRITE],
)
async def delete_note(
    note_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a clinical note."""
    repo = ClinicalNoteRepository(db)
    note = await repo.get_by_id(note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    await repo.delete(note)
