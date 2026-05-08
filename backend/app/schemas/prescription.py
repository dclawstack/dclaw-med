"""Prescription and drug interaction schemas."""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class PrescriptionBase(BaseModel):
    """Base prescription fields."""

    medication_name: str = Field(..., min_length=1, max_length=255)
    dosage: str = Field(..., min_length=1, max_length=100)
    frequency: str = Field(..., min_length=1, max_length=100)
    route: str = Field(..., min_length=1, max_length=50)
    start_date: date
    end_date: date | None = None
    instructions: str | None = None
    status: str = Field(default="active", pattern="^(active|completed|discontinued)$")


class PrescriptionCreate(PrescriptionBase):
    """Schema for creating a prescription."""

    patient_id: UUID


class PrescriptionUpdate(BaseModel):
    """Schema for updating a prescription."""

    medication_name: str | None = Field(default=None, min_length=1, max_length=255)
    dosage: str | None = Field(default=None, min_length=1, max_length=100)
    frequency: str | None = Field(default=None, min_length=1, max_length=100)
    route: str | None = Field(default=None, min_length=1, max_length=50)
    start_date: date | None = None
    end_date: date | None = None
    instructions: str | None = None
    status: str | None = Field(default=None, pattern="^(active|completed|discontinued)$")


class PrescriptionResponse(PrescriptionBase):
    """Prescription response schema."""

    id: UUID
    patient_id: UUID
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class DrugInteraction(BaseModel):
    """Single drug interaction result."""

    drug_a: str
    drug_b: str
    severity: str  # minor / moderate / major / contraindicated
    description: str
    mechanism: str | None = None
    recommendation: str | None = None


class DrugInteractionRequest(BaseModel):
    """Request to check drug interactions."""

    drugs: list[str] = Field(..., min_length=2, max_length=20, description="List of medication names")
    patient_id: UUID | None = None


class DrugInteractionResponse(BaseModel):
    """Response with drug interaction analysis."""

    drugs_checked: list[str]
    interactions_found: list[DrugInteraction]
    total_interactions: int
    highest_severity: str | None = None
    summary: str
    disclaimer: str = (
        "Drug interaction data is for reference only. Always verify with a "
        "pharmacist or prescribing physician before making medication decisions."
    )
