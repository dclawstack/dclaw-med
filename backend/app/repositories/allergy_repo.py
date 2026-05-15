"""Allergy repository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.allergy import Allergy
from app.schemas.allergy import AllergyCreate, AllergyUpdate


class AllergyRepository:
    """Allergy data access repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_for_patient(
        self, patient_id: UUID, page: int = 1, page_size: int = 50
    ) -> tuple[list[Allergy], int]:
        """List allergies for a patient."""
        count_stmt = (
            select(func.count())
            .select_from(Allergy)
            .where(Allergy.patient_id == patient_id)
        )
        total = (await self.db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(Allergy)
            .where(Allergy.patient_id == patient_id)
            .order_by(Allergy.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_by_id(self, allergy_id: UUID) -> Allergy | None:
        result = await self.db.execute(select(Allergy).where(Allergy.id == allergy_id))
        return result.scalar_one_or_none()

    async def match_for_medication(
        self, patient_id: UUID, medication_name: str
    ) -> list[Allergy]:
        """Return allergies whose allergen is contained in (or contains) the medication name.

        Case-insensitive substring match on both sides — keeps the matcher simple
        without requiring a drug database. Real-world use should swap this for a
        proper drug-class lookup, but it's enough to surface obvious risks like
        a patient allergic to "penicillin" being prescribed "amoxicillin".
        """
        med = medication_name.strip().lower()
        if not med:
            return []
        stmt = select(Allergy).where(Allergy.patient_id == patient_id)
        result = await self.db.execute(stmt)
        matches: list[Allergy] = []
        for allergy in result.scalars().all():
            allergen = allergy.allergen.strip().lower()
            if not allergen:
                continue
            if allergen in med or med in allergen:
                matches.append(allergy)
        return matches

    async def create(self, data: AllergyCreate) -> Allergy:
        allergy = Allergy(
            patient_id=data.patient_id,
            allergen=data.allergen,
            severity=data.severity,
            reaction=data.reaction,
        )
        self.db.add(allergy)
        await self.db.commit()
        await self.db.refresh(allergy)
        return allergy

    async def update(self, allergy: Allergy, data: AllergyUpdate) -> Allergy:
        if data.allergen is not None:
            allergy.allergen = data.allergen
        if data.severity is not None:
            allergy.severity = data.severity
        if data.reaction is not None:
            allergy.reaction = data.reaction
        await self.db.commit()
        await self.db.refresh(allergy)
        return allergy

    async def delete(self, allergy: Allergy) -> None:
        await self.db.delete(allergy)
        await self.db.commit()
