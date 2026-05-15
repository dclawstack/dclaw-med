"""Patient model."""

import uuid
from datetime import date
from typing import TYPE_CHECKING, Any

from sqlalchemy import Computed, Date, Index, JSON, String
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.allergy import Allergy
    from app.models.appointment import Appointment
    from app.models.clinical_note import ClinicalNote
    from app.models.diagnosis import Diagnosis
    from app.models.lab_result import LabResult
    from app.models.prescription import Prescription
    from app.models.symptom import Symptom


class Patient(Base, UUIDMixin, TimestampMixin):
    """Patient record with medical history."""

    __tablename__ = "patients"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    medical_record_number: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    contact_info: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    # Generated tsvector for full-text search on name. Stored so the GIN index can use it.
    name_tsv: Mapped[str | None] = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('english', coalesce(name, ''))", persisted=True),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_patients_name_tsv", "name_tsv", postgresql_using="gin"),
    )

    symptoms: Mapped[list["Symptom"]] = relationship(
        "Symptom", back_populates="patient", lazy="selectin", cascade="all, delete-orphan"
    )
    diagnoses: Mapped[list["Diagnosis"]] = relationship(
        "Diagnosis", back_populates="patient", lazy="selectin", cascade="all, delete-orphan"
    )
    prescriptions: Mapped[list["Prescription"]] = relationship(
        "Prescription", back_populates="patient", lazy="selectin", cascade="all, delete-orphan"
    )
    clinical_notes: Mapped[list["ClinicalNote"]] = relationship(
        "ClinicalNote", back_populates="patient", lazy="selectin", cascade="all, delete-orphan"
    )
    lab_results: Mapped[list["LabResult"]] = relationship(
        "LabResult", back_populates="patient", lazy="selectin", cascade="all, delete-orphan"
    )
    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment", back_populates="patient", lazy="selectin", cascade="all, delete-orphan"
    )
    allergies: Mapped[list["Allergy"]] = relationship(
        "Allergy", back_populates="patient", lazy="selectin", cascade="all, delete-orphan"
    )
