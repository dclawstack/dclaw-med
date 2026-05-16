"""User model."""

import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.dialect import UUIDType
from app.models.base import Base, TimestampMixin, UUIDMixin

ROLES = ("doctor", "nurse", "admin", "receptionist", "patient")
CLINICIAN_ROLES = ("doctor", "nurse", "admin", "receptionist")


class User(Base, UUIDMixin, TimestampMixin):
    """User account with role-based access."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # Set when role == "patient" to bind the account to a patient record.
    # SET NULL on patient delete so the account survives — admins can re-link.
    patient_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(),
        ForeignKey("patients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
