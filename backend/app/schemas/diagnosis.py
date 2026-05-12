"""Diagnosis and ICD-10 schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class DiagnosisBase(BaseModel):
    """Base diagnosis fields."""

    icd10_code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    status: str = Field(default="provisional", pattern="^(provisional|confirmed|ruled_out)$")


class DiagnosisCreate(DiagnosisBase):
    """Schema for creating a diagnosis."""

    patient_id: UUID
    differential: list[dict[str, Any]] | None = None


class DiagnosisUpdate(BaseModel):
    """Schema for updating a diagnosis."""

    icd10_code: str | None = Field(default=None, min_length=1, max_length=20)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    status: str | None = Field(default=None, pattern="^(provisional|confirmed|ruled_out)$")
    differential: list[dict[str, Any]] | None = None


class DiagnosisResponse(DiagnosisBase):
    """Diagnosis response schema."""

    id: UUID
    patient_id: UUID
    differential: list[dict[str, Any]] | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ICD10Code(BaseModel):
    """Single ICD-10 code entry."""

    code: str
    description: str
    category: str
    billable: bool = True


class ICD10LookupRequest(BaseModel):
    """Request to search ICD-10 codes."""

    query: str = Field(..., min_length=1, description="Search term for ICD-10 code or description")
    max_results: int = Field(default=10, ge=1, le=50)


class ICD10LookupResponse(BaseModel):
    """Response with ICD-10 search results."""

    query: str
    results: list[ICD10Code]
    total_found: int
