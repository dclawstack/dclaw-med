"""Lab result model."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class LabResult(Base, UUIDMixin, TimestampMixin):
    """Laboratory test result for a patient."""

    __tablename__ = "lab_results"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    test_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    test_category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    result_value: Mapped[str] = mapped_column(String(255), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reference_range: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="final"
    )  # pending / preliminary / final / corrected / cancelled
    ordered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resulted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    patient: Mapped["Patient"] = relationship(  # type: ignore[name-defined]
        "Patient", back_populates="lab_results", lazy="selectin"
    )
