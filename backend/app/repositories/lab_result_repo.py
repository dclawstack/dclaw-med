"""Lab result repository."""

from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lab_result import LabResult
from app.schemas.lab_result import LabResultCreate, LabResultUpdate


class LabResultRepository:
    """Lab result data access repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_lab_results(
        self,
        patient_id: UUID | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[LabResult], int]:
        filters = []
        if patient_id is not None:
            filters.append(LabResult.patient_id == patient_id)

        count_stmt = select(func.count()).select_from(LabResult)
        for f in filters:
            count_stmt = count_stmt.where(f)
        total = (await self.db.execute(count_stmt)).scalar() or 0

        stmt = select(LabResult).order_by(desc(LabResult.ordered_at))
        for f in filters:
            stmt = stmt.where(f)
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_by_id(self, lab_result_id: UUID) -> LabResult | None:
        result = await self.db.execute(
            select(LabResult).where(LabResult.id == lab_result_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: LabResultCreate) -> LabResult:
        lab = LabResult(
            patient_id=data.patient_id,
            test_name=data.test_name,
            test_category=data.test_category,
            result_value=data.result_value,
            unit=data.unit,
            reference_range=data.reference_range,
            status=data.status,
            ordered_at=data.ordered_at,
            resulted_at=data.resulted_at,
            notes=data.notes,
        )
        self.db.add(lab)
        await self.db.commit()
        await self.db.refresh(lab)
        return lab

    async def update(self, lab: LabResult, data: LabResultUpdate) -> LabResult:
        if data.test_name is not None:
            lab.test_name = data.test_name
        if data.test_category is not None:
            lab.test_category = data.test_category
        if data.result_value is not None:
            lab.result_value = data.result_value
        if data.unit is not None:
            lab.unit = data.unit
        if data.reference_range is not None:
            lab.reference_range = data.reference_range
        if data.status is not None:
            lab.status = data.status
        if data.ordered_at is not None:
            lab.ordered_at = data.ordered_at
        if data.resulted_at is not None:
            lab.resulted_at = data.resulted_at
        if data.notes is not None:
            lab.notes = data.notes
        await self.db.commit()
        await self.db.refresh(lab)
        return lab

    async def delete(self, lab: LabResult) -> None:
        await self.db.delete(lab)
        await self.db.commit()
