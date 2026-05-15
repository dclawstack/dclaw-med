"""User and auth schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field  # noqa: F401

ROLE_PATTERN = "^(doctor|nurse|admin|receptionist|patient)$"


class UserCreate(BaseModel):
    """Schema for creating a user."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(default="nurse", pattern=ROLE_PATTERN)
    # Only set when role == "patient"; binds the account to a patient record.
    patient_id: UUID | None = None


class UserResponse(BaseModel):
    """User response schema."""

    id: UUID
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    patient_id: UUID | None = None

    model_config = ConfigDict(from_attributes=True)


class UserPatientLinkRequest(BaseModel):
    """Admin request body to (re)link a user account to a patient record."""

    patient_id: UUID | None


class Token(BaseModel):
    """JWT access token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded JWT payload."""

    user_id: UUID
    role: str


class ProviderResponse(BaseModel):
    """Minimal user shape for provider selection on appointments."""

    id: UUID
    full_name: str
    role: str

    model_config = ConfigDict(from_attributes=True)
