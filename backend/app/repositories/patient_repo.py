"""Patient repository."""

from datetime import date
from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.diagnosis import Diagnosis
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate


def _apply_filters(
    stmt: Select,
    q: str | None,
    dob_from: date | None,
    dob_to: date | None,
    diagnosis_code: str | None,
) -> Select:
    """Apply search filters to a Patient select statement."""
    if q:
        # Postgres full-text on name OR case-insensitive substring on MRN — covers both
        # "type a name" and "scan an MRN" usage.
        tsquery = func.websearch_to_tsquery("english", q)
        stmt = stmt.where(
            or_(
                Patient.name_tsv.op("@@")(tsquery),
                Patient.medical_record_number.ilike(f"%{q}%"),
            )
        )
    if dob_from is not None:
        stmt = stmt.where(Patient.date_of_birth >= dob_from)
    if dob_to is not None:
        stmt = stmt.where(Patient.date_of_birth <= dob_to)
    if diagnosis_code:
        stmt = stmt.where(
            Patient.diagnoses.any(Diagnosis.icd10_code == diagnosis_code)
        )
    return stmt


class PatientRepository:
    """Patient data access repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_patients(
        self,
        page: int = 1,
        page_size: int = 20,
        q: str | None = None,
        dob_from: date | None = None,
        dob_to: date | None = None,
        diagnosis_code: str | None = None,
    ) -> tuple[list[Patient], int]:
        """List patients with pagination + optional search filters.

        Returns (patients, total_count).
        """
        count_stmt = _apply_filters(
            select(func.count()).select_from(Patient),
            q,
            dob_from,
            dob_to,
            diagnosis_code,
        )
        total = (await self.db.execute(count_stmt)).scalar() or 0

        stmt = _apply_filters(select(Patient), q, dob_from, dob_to, diagnosis_code)
        stmt = (
            stmt.order_by(Patient.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_by_id(self, patient_id: UUID) -> Patient | None:
        """Get a patient by ID with all related data loaded."""
        result = await self.db.execute(
            select(Patient)
            .options(
                selectinload(Patient.symptoms),
                selectinload(Patient.diagnoses),
                selectinload(Patient.prescriptions),
                selectinload(Patient.clinical_notes),
            )
            .where(Patient.id == patient_id)
        )
        return result.scalar_one_or_none()

    async def get_by_mrn(self, medical_record_number: str) -> Patient | None:
        """Get a patient by medical record number."""
        result = await self.db.execute(
            select(Patient).where(Patient.medical_record_number == medical_record_number)
        )
        return result.scalar_one_or_none()

    async def create(self, data: PatientCreate) -> Patient:
        """Create a new patient."""
        patient = Patient(
            name=data.name,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            medical_record_number=data.medical_record_number,
            contact_info=data.contact_info,
        )
        self.db.add(patient)
        await self.db.commit()
        await self.db.refresh(patient)
        return patient

    async def update(self, patient: Patient, data: PatientUpdate) -> Patient:
        """Update a patient."""
        if data.name is not None:
            patient.name = data.name
        if data.date_of_birth is not None:
            patient.date_of_birth = data.date_of_birth
        if data.gender is not None:
            patient.gender = data.gender
        if data.contact_info is not None:
            patient.contact_info = data.contact_info

        await self.db.commit()
        await self.db.refresh(patient)
        return patient

    async def delete(self, patient: Patient) -> None:
        """Delete a patient."""
        await self.db.delete(patient)
        await self.db.commit()
