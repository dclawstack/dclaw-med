"""Appointment repository with overlap detection."""

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate

ACTIVE_STATUSES = ("scheduled", "completed")


class AppointmentRepository:
    """Appointment data access repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_appointments(
        self,
        patient_id: UUID | None = None,
        provider_id: UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> tuple[list[Appointment], int]:
        filters = []
        if patient_id is not None:
            filters.append(Appointment.patient_id == patient_id)
        if provider_id is not None:
            filters.append(Appointment.provider_id == provider_id)
        if date_from is not None:
            filters.append(Appointment.scheduled_at >= date_from)
        if date_to is not None:
            filters.append(Appointment.scheduled_at < date_to)

        count_stmt = select(func.count()).select_from(Appointment)
        for f in filters:
            count_stmt = count_stmt.where(f)
        total = (await self.db.execute(count_stmt)).scalar() or 0

        stmt = select(Appointment).order_by(Appointment.scheduled_at)
        for f in filters:
            stmt = stmt.where(f)
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_by_id(self, appointment_id: UUID) -> Appointment | None:
        result = await self.db.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        return result.scalar_one_or_none()

    async def find_overlap(
        self,
        provider_id: UUID,
        scheduled_at: datetime,
        duration_minutes: int,
        exclude_id: UUID | None = None,
    ) -> Appointment | None:
        """Return any existing active appointment that overlaps this slot for the provider."""
        end = scheduled_at + timedelta(minutes=duration_minutes)
        # Overlap iff existing.start < new.end AND new.start < existing.start + duration
        # We compute existing.end via a computed expression.
        existing_end = Appointment.scheduled_at + (
            func.cast(Appointment.duration_minutes, type_=__import__("sqlalchemy").Integer) * func.cast("1 minute", type_=__import__("sqlalchemy").Interval)  # type: ignore
        )
        # Simpler: use SQL interval arithmetic via raw expression.
        from sqlalchemy import text

        stmt = (
            select(Appointment)
            .where(Appointment.provider_id == provider_id)
            .where(Appointment.status.in_(ACTIVE_STATUSES))
            .where(
                and_(
                    Appointment.scheduled_at < end,
                    text(
                        "appointments.scheduled_at + (appointments.duration_minutes || ' minutes')::interval > :new_start"
                    ).bindparams(new_start=scheduled_at),
                )
            )
        )
        if exclude_id is not None:
            stmt = stmt.where(Appointment.id != exclude_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create(self, data: AppointmentCreate) -> Appointment:
        appt = Appointment(
            patient_id=data.patient_id,
            provider_id=data.provider_id,
            scheduled_at=data.scheduled_at,
            duration_minutes=data.duration_minutes,
            status=data.status,
            location=data.location,
            notes=data.notes,
        )
        self.db.add(appt)
        await self.db.commit()
        await self.db.refresh(appt)
        return appt

    async def update(
        self, appt: Appointment, data: AppointmentUpdate
    ) -> Appointment:
        if data.scheduled_at is not None:
            appt.scheduled_at = data.scheduled_at
        if data.duration_minutes is not None:
            appt.duration_minutes = data.duration_minutes
        if data.status is not None:
            appt.status = data.status
        if data.location is not None:
            appt.location = data.location
        if data.notes is not None:
            appt.notes = data.notes
        if data.provider_id is not None:
            appt.provider_id = data.provider_id
        await self.db.commit()
        await self.db.refresh(appt)
        return appt

    async def delete(self, appt: Appointment) -> None:
        await self.db.delete(appt)
        await self.db.commit()
