"""Symptom schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SymptomBase(BaseModel):
    """Base symptom fields."""

    description: str = Field(..., min_length=1)
    onset_date: datetime | None = None
    severity: int = Field(default=5, ge=1, le=10)
    body_system: str | None = None
    notes: str | None = None


class SymptomCreate(SymptomBase):
    """Schema for creating a symptom."""

    patient_id: UUID


class SymptomUpdate(BaseModel):
    """Schema for updating a symptom."""

    description: str | None = None
    onset_date: datetime | None = None
    severity: int | None = Field(default=None, ge=1, le=10)
    body_system: str | None = None
    notes: str | None = None


class SymptomResponse(SymptomBase):
    """Symptom response schema."""

    id: UUID
    patient_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DifferentialDiagnosis(BaseModel):
    """A single differential diagnosis result."""

    condition: str
    icd10_code: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str


class SymptomAnalysisRequest(BaseModel):
    """Request to analyze symptoms."""

    patient_id: UUID
    symptoms: str = Field(..., min_length=1, description="Comma-separated symptom descriptions")
    include_differential: bool = True
    max_results: int = Field(default=5, ge=1, le=10)


class SymptomAnalysisResponse(BaseModel):
    """Response from symptom analysis."""

    patient_id: UUID
    primary_symptoms: list[str]
    differential_diagnoses: list[DifferentialDiagnosis]
    recommended_tests: list[str]
    urgency_level: str  # low / medium / high / critical
    disclaimer: str = (
        "This analysis is for informational purposes only and does not constitute "
        "medical advice. Always consult a qualified healthcare professional."
    )


class TriageRequest(BaseModel):
    """Free-text triage request. Works without a patient_id so it can be used
    by patients (or anonymous-ish staff) before a registered record exists."""

    symptoms: str = Field(..., min_length=1, description="Free-text symptom description")
    patient_id: UUID | None = None
    age: int | None = Field(default=None, ge=0, le=130)
    sex: str | None = Field(default=None, pattern="^(male|female|other|unknown)$")


class TriageResponse(BaseModel):
    """Triage routing recommendation."""

    urgency_level: str  # low / medium / high / critical
    suggested_department: str  # e.g. "Emergency Department", "Primary Care"
    recommended_tests: list[str]
    red_flags: list[str]
    differential_diagnoses: list[DifferentialDiagnosis]
    summary: str  # human-readable guidance — what to do next
    disclaimer: str = (
        "Triage is for routing only and does not replace clinical evaluation. "
        "If symptoms are severe, worsening, or include any red flags listed "
        "above, seek emergency care immediately."
    )
