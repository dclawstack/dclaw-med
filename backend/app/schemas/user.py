"""User and auth schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

ROLE_PATTERN = "^(doctor|nurse|admin|receptionist)$"


class UserCreate(BaseModel):
    """Schema for creating a user."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(default="nurse", pattern=ROLE_PATTERN)


class UserResponse(BaseModel):
    """User response schema."""

    id: UUID
    email: EmailStr
    full_name: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """JWT access token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded JWT payload."""

    user_id: UUID
    role: str
