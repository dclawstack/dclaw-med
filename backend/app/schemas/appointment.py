"""Appointment schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

STATUS_PATTERN = "^(scheduled|completed|cancelled|no_show)$"


class AppointmentBase(BaseModel):
    """Base appointment fields."""

    scheduled_at: datetime
    duration_minutes: int = Field(default=30, ge=5, le=480)
    status: str = Field(default="scheduled", pattern=STATUS_PATTERN)
    location: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class AppointmentCreate(AppointmentBase):
    """Schema for creating an appointment."""

    patient_id: UUID
    provider_id: UUID


class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment."""

    scheduled_at: datetime | None = None
    duration_minutes: int | None = Field(default=None, ge=5, le=480)
    status: str | None = Field(default=None, pattern=STATUS_PATTERN)
    location: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    provider_id: UUID | None = None


class AppointmentResponse(AppointmentBase):
    """Appointment response schema."""

    id: UUID
    patient_id: UUID
    provider_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
