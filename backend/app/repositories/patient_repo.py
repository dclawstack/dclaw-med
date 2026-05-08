"""Patient repository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate


class PatientRepository:
    """Patient data access repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_patients(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[Patient], int]:
        """List patients with pagination. Returns (patients, total_count)."""
        total_result = await self.db.execute(select(func.count()).select_from(Patient))
        total = total_result.scalar() or 0

        result = await self.db.execute(
            select(Patient)
            .order_by(Patient.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        patients = list(result.scalars().all())
        return patients, total

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
