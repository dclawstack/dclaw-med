"""Patient drug/allergy record."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.dialect import UUIDType
from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.patient import Patient


class Allergy(Base, UUIDMixin, TimestampMixin):
    """A known allergen for a patient (drugs, foods, environmental)."""

    __tablename__ = "allergies"
    __table_args__ = (
        UniqueConstraint("patient_id", "allergen", name="uq_allergies_patient_allergen"),
        CheckConstraint(
            "severity IN ('mild', 'moderate', 'severe', 'anaphylaxis')",
            name="ck_allergies_severity",
        ),
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    allergen: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    reaction: Mapped[str | None] = mapped_column(Text, nullable=True)

    patient: Mapped["Patient"] = relationship(
        "Patient", back_populates="allergies", lazy="selectin"
    )
