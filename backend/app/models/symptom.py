"""Symptom model."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Symptom(Base, UUIDMixin, TimestampMixin):
    """Patient symptom record."""

    __tablename__ = "symptoms"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    onset_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    severity: Mapped[int] = mapped_column(Integer, default=5)
    body_system: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    patient: Mapped["Patient"] = relationship(
        "Patient", back_populates="symptoms", lazy="selectin"
    )
