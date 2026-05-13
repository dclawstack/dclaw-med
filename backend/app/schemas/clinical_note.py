"""Clinical note schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ClinicalNoteBase(BaseModel):
    """Base clinical note fields."""

    note_type: str = Field(
        ..., pattern="^(progress|admission|discharge|procedure)$"
    )
    content: str = Field(..., min_length=1)
    generated_by: str = Field(default="user", pattern="^(user|ai)$")
    template_used: str | None = None


class ClinicalNoteCreate(ClinicalNoteBase):
    """Schema for creating a clinical note."""

    patient_id: UUID


class ClinicalNoteUpdate(BaseModel):
    """Schema for updating a clinical note."""

    note_type: str | None = Field(default=None, pattern="^(progress|admission|discharge|procedure)$")
    content: str | None = Field(default=None, min_length=1)
    template_used: str | None = None


class ClinicalNoteResponse(ClinicalNoteBase):
    """Clinical note response schema."""

    id: UUID
    patient_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NoteGenerateRequest(BaseModel):
    """Request to generate a clinical note."""

    patient_id: UUID
    note_type: str = Field(
        ..., pattern="^(progress|admission|discharge|procedure)$"
    )
    context: str = Field(
        ..., min_length=1, description="Clinical context or prompt for note generation"
    )
    include_history: bool = True


class NoteGenerateResponse(BaseModel):
    """Response with generated clinical note."""

    patient_id: UUID
    note_type: str
    generated_content: str
    generated_by: str = "ai"
    template_used: str | None = None
    word_count: int
    disclaimer: str = (
        "AI-generated notes should be reviewed and approved by a qualified "
        "healthcare professional before inclusion in the medical record."
    )
