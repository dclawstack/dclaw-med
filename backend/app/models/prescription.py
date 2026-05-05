"""Prescription model."""

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Prescription(Base, UUIDMixin, TimestampMixin):
    """Medication prescription record."""

    __tablename__ = "prescriptions"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    medication_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dosage: Mapped[str] = mapped_column(String(100), nullable=False)
    frequency: Mapped[str] = mapped_column(String(100), nullable=False)
    route: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="active"
    )  # active / completed / discontinued

    patient: Mapped["Patient"] = relationship("Patient", back_populates="prescriptions")
