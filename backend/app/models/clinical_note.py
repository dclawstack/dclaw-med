"""Clinical note model."""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class ClinicalNote(Base, UUIDMixin, TimestampMixin):
    """Clinical note record."""

    __tablename__ = "clinical_notes"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    note_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # progress / admission / discharge / procedure
    content: Mapped[str] = mapped_column(Text, nullable=False)
    generated_by: Mapped[str] = mapped_column(
        String(20), default="user"
    )  # user / ai
    template_used: Mapped[str | None] = mapped_column(String(100), nullable=True)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="clinical_notes")
