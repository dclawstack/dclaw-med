"""Symptom repository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.symptom import Symptom
from app.schemas.symptom import SymptomCreate, SymptomUpdate


class SymptomRepository:
    """Symptom data access repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_symptoms(
        self, patient_id: UUID | None = None, page: int = 1, page_size: int = 20
    ) -> tuple[list[Symptom], int]:
        """List symptoms with optional patient filter."""
        stmt = select(func.count()).select_from(Symptom)
        if patient_id:
            stmt = stmt.where(Symptom.patient_id == patient_id)
        total_result = await self.db.execute(stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(Symptom)
            .order_by(Symptom.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        if patient_id:
            stmt = stmt.where(Symptom.patient_id == patient_id)

        result = await self.db.execute(stmt)
        symptoms = list(result.scalars().all())
        return symptoms, total

    async def get_by_id(self, symptom_id: UUID) -> Symptom | None:
        """Get a symptom by ID."""
        result = await self.db.execute(
            select(Symptom).where(Symptom.id == symptom_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: SymptomCreate) -> Symptom:
        """Create a new symptom."""
        symptom = Symptom(
            patient_id=data.patient_id,
            description=data.description,
            onset_date=data.onset_date,
            severity=data.severity,
            body_system=data.body_system,
            notes=data.notes,
        )
        self.db.add(symptom)
        await self.db.commit()
        await self.db.refresh(symptom)
        return symptom

    async def update(self, symptom: Symptom, data: SymptomUpdate) -> Symptom:
        """Update a symptom."""
        if data.description is not None:
            symptom.description = data.description
        if data.onset_date is not None:
            symptom.onset_date = data.onset_date
        if data.severity is not None:
            symptom.severity = data.severity
        if data.body_system is not None:
            symptom.body_system = data.body_system
        if data.notes is not None:
            symptom.notes = data.notes

        await self.db.commit()
        await self.db.refresh(symptom)
        return symptom

    async def delete(self, symptom: Symptom) -> None:
        """Delete a symptom."""
        await self.db.delete(symptom)
        await self.db.commit()
