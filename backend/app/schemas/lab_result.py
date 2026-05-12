"""Lab result schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

STATUS_PATTERN = "^(pending|preliminary|final|corrected|cancelled)$"


class LabResultBase(BaseModel):
    """Base lab result fields."""

    test_name: str = Field(..., min_length=1, max_length=255)
    test_category: str = Field(..., min_length=1, max_length=100)
    result_value: str = Field(..., min_length=1, max_length=255)
    unit: str | None = Field(default=None, max_length=50)
    reference_range: str | None = Field(default=None, max_length=100)
    status: str = Field(default="final", pattern=STATUS_PATTERN)
    ordered_at: datetime
    resulted_at: datetime | None = None
    notes: str | None = None


class LabResultCreate(LabResultBase):
    """Schema for creating a lab result."""

    patient_id: UUID


class LabResultUpdate(BaseModel):
    """Schema for updating a lab result."""

    test_name: str | None = Field(default=None, min_length=1, max_length=255)
    test_category: str | None = Field(default=None, min_length=1, max_length=100)
    result_value: str | None = Field(default=None, min_length=1, max_length=255)
    unit: str | None = Field(default=None, max_length=50)
    reference_range: str | None = Field(default=None, max_length=100)
    status: str | None = Field(default=None, pattern=STATUS_PATTERN)
    ordered_at: datetime | None = None
    resulted_at: datetime | None = None
    notes: str | None = None


class LabResultResponse(LabResultBase):
    """Lab result response schema."""

    id: UUID
    patient_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
