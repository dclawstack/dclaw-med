"""Clinical note repository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinical_note import ClinicalNote
from app.schemas.clinical_note import ClinicalNoteCreate, ClinicalNoteUpdate


class ClinicalNoteRepository:
    """Clinical note data access repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_notes(
        self, patient_id: UUID | None = None, page: int = 1, page_size: int = 20
    ) -> tuple[list[ClinicalNote], int]:
        """List clinical notes with optional patient filter."""
        stmt = select(func.count()).select_from(ClinicalNote)
        if patient_id:
            stmt = stmt.where(ClinicalNote.patient_id == patient_id)
        total_result = await self.db.execute(stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(ClinicalNote)
            .order_by(ClinicalNote.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        if patient_id:
            stmt = stmt.where(ClinicalNote.patient_id == patient_id)

        result = await self.db.execute(stmt)
        notes = list(result.scalars().all())
        return notes, total

    async def get_by_id(self, note_id: UUID) -> ClinicalNote | None:
        """Get a clinical note by ID."""
        result = await self.db.execute(
            select(ClinicalNote).where(ClinicalNote.id == note_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: ClinicalNoteCreate) -> ClinicalNote:
        """Create a new clinical note."""
        note = ClinicalNote(
            patient_id=data.patient_id,
            note_type=data.note_type,
            content=data.content,
            generated_by=data.generated_by,
            template_used=data.template_used,
        )
        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def update(
        self, note: ClinicalNote, data: ClinicalNoteUpdate
    ) -> ClinicalNote:
        """Update a clinical note."""
        if data.note_type is not None:
            note.note_type = data.note_type
        if data.content is not None:
            note.content = data.content
        if data.template_used is not None:
            note.template_used = data.template_used

        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def delete(self, note: ClinicalNote) -> None:
        """Delete a clinical note."""
        await self.db.delete(note)
        await self.db.commit()
