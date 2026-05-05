"""Patient schemas."""

from datetime import date
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class PatientBase(BaseModel):
    """Base patient fields."""

    name: str = Field(..., min_length=1, max_length=255)
    date_of_birth: date
    gender: str = Field(..., pattern="^(male|female|other|unknown)$")
    medical_record_number: str = Field(..., min_length=1, max_length=100)
    contact_info: dict[str, Any] | None = None


class PatientCreate(PatientBase):
    """Schema for creating a patient."""


class PatientUpdate(BaseModel):
    """Schema for updating a patient."""

    name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    contact_info: dict[str, Any] | None = None


class PatientResponse(PatientBase):
    """Patient response schema."""

    id: UUID
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
