"""Prescription repository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prescription import Prescription
from app.schemas.prescription import PrescriptionCreate, PrescriptionUpdate


class PrescriptionRepository:
    """Prescription data access repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_prescriptions(
        self, patient_id: UUID | None = None, page: int = 1, page_size: int = 20
    ) -> tuple[list[Prescription], int]:
        """List prescriptions with optional patient filter."""
        stmt = select(func.count()).select_from(Prescription)
        if patient_id:
            stmt = stmt.where(Prescription.patient_id == patient_id)
        total_result = await self.db.execute(stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(Prescription)
            .order_by(Prescription.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        if patient_id:
            stmt = stmt.where(Prescription.patient_id == patient_id)

        result = await self.db.execute(stmt)
        prescriptions = list(result.scalars().all())
        return prescriptions, total

    async def get_by_id(self, prescription_id: UUID) -> Prescription | None:
        """Get a prescription by ID."""
        result = await self.db.execute(
            select(Prescription).where(Prescription.id == prescription_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: PrescriptionCreate) -> Prescription:
        """Create a new prescription."""
        prescription = Prescription(
            patient_id=data.patient_id,
            medication_name=data.medication_name,
            dosage=data.dosage,
            frequency=data.frequency,
            route=data.route,
            start_date=data.start_date,
            end_date=data.end_date,
            instructions=data.instructions,
            status=data.status,
        )
        self.db.add(prescription)
        await self.db.commit()
        await self.db.refresh(prescription)
        return prescription

    async def update(
        self, prescription: Prescription, data: PrescriptionUpdate
    ) -> Prescription:
        """Update a prescription."""
        if data.medication_name is not None:
            prescription.medication_name = data.medication_name
        if data.dosage is not None:
            prescription.dosage = data.dosage
        if data.frequency is not None:
            prescription.frequency = data.frequency
        if data.route is not None:
            prescription.route = data.route
        if data.start_date is not None:
            prescription.start_date = data.start_date
        if data.end_date is not None:
            prescription.end_date = data.end_date
        if data.instructions is not None:
            prescription.instructions = data.instructions
        if data.status is not None:
            prescription.status = data.status

        await self.db.commit()
        await self.db.refresh(prescription)
        return prescription

    async def delete(self, prescription: Prescription) -> None:
        """Delete a prescription."""
        await self.db.delete(prescription)
        await self.db.commit()
