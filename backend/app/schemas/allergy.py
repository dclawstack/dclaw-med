"""Allergy schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

ALLERGY_SEVERITY_PATTERN = "^(mild|moderate|severe|anaphylaxis)$"


class AllergyBase(BaseModel):
    """Base allergy fields."""

    allergen: str = Field(..., min_length=1, max_length=255)
    severity: str = Field(..., pattern=ALLERGY_SEVERITY_PATTERN)
    reaction: str | None = None


class AllergyCreate(AllergyBase):
    """Schema for creating an allergy."""

    patient_id: UUID


class AllergyUpdate(BaseModel):
    """Schema for updating an allergy."""

    allergen: str | None = Field(default=None, min_length=1, max_length=255)
    severity: str | None = Field(default=None, pattern=ALLERGY_SEVERITY_PATTERN)
    reaction: str | None = None


class AllergyResponse(AllergyBase):
    """Allergy response schema."""

    id: UUID
    patient_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AllergyWarning(BaseModel):
    """A matched allergy returned alongside a new prescription."""

    allergy_id: UUID
    allergen: str
    severity: str
    reaction: str | None = None
