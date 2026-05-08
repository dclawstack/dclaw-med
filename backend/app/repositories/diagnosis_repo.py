"""Diagnosis repository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.diagnosis import Diagnosis
from app.schemas.diagnosis import DiagnosisCreate, DiagnosisUpdate


class DiagnosisRepository:
    """Diagnosis data access repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_diagnoses(
        self, patient_id: UUID | None = None, page: int = 1, page_size: int = 20
    ) -> tuple[list[Diagnosis], int]:
        """List diagnoses with optional patient filter."""
        stmt = select(func.count()).select_from(Diagnosis)
        if patient_id:
            stmt = stmt.where(Diagnosis.patient_id == patient_id)
        total_result = await self.db.execute(stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(Diagnosis)
            .order_by(Diagnosis.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        if patient_id:
            stmt = stmt.where(Diagnosis.patient_id == patient_id)

        result = await self.db.execute(stmt)
        diagnoses = list(result.scalars().all())
        return diagnoses, total

    async def get_by_id(self, diagnosis_id: UUID) -> Diagnosis | None:
        """Get a diagnosis by ID."""
        result = await self.db.execute(
            select(Diagnosis).where(Diagnosis.id == diagnosis_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: DiagnosisCreate) -> Diagnosis:
        """Create a new diagnosis."""
        diagnosis = Diagnosis(
            patient_id=data.patient_id,
            icd10_code=data.icd10_code,
            name=data.name,
            description=data.description,
            confidence=data.confidence,
            differential=data.differential,
            status=data.status,
        )
        self.db.add(diagnosis)
        await self.db.commit()
        await self.db.refresh(diagnosis)
        return diagnosis

    async def update(self, diagnosis: Diagnosis, data: DiagnosisUpdate) -> Diagnosis:
        """Update a diagnosis."""
        if data.icd10_code is not None:
            diagnosis.icd10_code = data.icd10_code
        if data.name is not None:
            diagnosis.name = data.name
        if data.description is not None:
            diagnosis.description = data.description
        if data.confidence is not None:
            diagnosis.confidence = data.confidence
        if data.differential is not None:
            diagnosis.differential = data.differential
        if data.status is not None:
            diagnosis.status = data.status

        await self.db.commit()
        await self.db.refresh(diagnosis)
        return diagnosis

    async def delete(self, diagnosis: Diagnosis) -> None:
        """Delete a diagnosis."""
        await self.db.delete(diagnosis)
        await self.db.commit()
