"""Appointment scheduling endpoints."""

from collections.abc import Sequence
from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import APPOINTMENT_WRITE, READ_ANY
from app.core.database import get_db
from app.repositories.appointment_repo import AppointmentRepository
from app.repositories.user_repo import UserRepository
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
)

router = APIRouter()

PROVIDER_ROLES = ("doctor", "admin")


def _day_range(day: date) -> tuple[datetime, datetime]:
    start = datetime.combine(day, time.min, tzinfo=timezone.utc)
    return start, start + timedelta(days=1)


async def _ensure_valid_provider(db: AsyncSession, provider_id: UUID) -> None:
    user = await UserRepository(db).get_by_id(provider_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provider user not found",
        )
    if not user.is_active or user.role not in PROVIDER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provider must be an active doctor or admin",
        )


@router.get("", response_model=list[AppointmentResponse], dependencies=[READ_ANY])
async def list_appointments(
    patient_id: UUID | None = None,
    provider_id: UUID | None = None,
    date_param: date | None = Query(default=None, alias="date"),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = 1,
    page_size: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> Sequence[AppointmentResponse]:
    """List appointments. ?date=YYYY-MM-DD is a shortcut for the full UTC day."""
    if date_param is not None:
        date_from, date_to = _day_range(date_param)
    repo = AppointmentRepository(db)
    appts, _ = await repo.list_appointments(
        patient_id=patient_id,
        provider_id=provider_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    return [AppointmentResponse.model_validate(a) for a in appts]


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[APPOINTMENT_WRITE],
)
async def create_appointment(
    data: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
) -> AppointmentResponse:
    """Create an appointment. 422 if provider isn't a doctor/admin; 409 on slot overlap."""
    await _ensure_valid_provider(db, data.provider_id)
    repo = AppointmentRepository(db)
    overlap = await repo.find_overlap(
        provider_id=data.provider_id,
        scheduled_at=data.scheduled_at,
        duration_minutes=data.duration_minutes,
    )
    if overlap is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Provider has an overlapping appointment",
        )
    appt = await repo.create(data)
    return AppointmentResponse.model_validate(appt)


@router.get(
    "/{appointment_id}", response_model=AppointmentResponse, dependencies=[READ_ANY]
)
async def get_appointment(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> AppointmentResponse:
    repo = AppointmentRepository(db)
    appt = await repo.get_by_id(appointment_id)
    if appt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found"
        )
    return AppointmentResponse.model_validate(appt)


@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    dependencies=[APPOINTMENT_WRITE],
)
async def update_appointment(
    appointment_id: UUID,
    data: AppointmentUpdate,
    db: AsyncSession = Depends(get_db),
) -> AppointmentResponse:
    repo = AppointmentRepository(db)
    appt = await repo.get_by_id(appointment_id)
    if appt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found"
        )
    # If we're rescheduling or moving providers, re-check overlap.
    new_scheduled = data.scheduled_at or appt.scheduled_at
    new_duration = data.duration_minutes or appt.duration_minutes
    new_provider = data.provider_id or appt.provider_id
    new_status = data.status or appt.status
    if data.provider_id is not None:
        await _ensure_valid_provider(db, data.provider_id)
    if new_status == "scheduled":
        overlap = await repo.find_overlap(
            provider_id=new_provider,
            scheduled_at=new_scheduled,
            duration_minutes=new_duration,
            exclude_id=appt.id,
        )
        if overlap is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Provider has an overlapping appointment",
            )
    appt = await repo.update(appt, data)
    return AppointmentResponse.model_validate(appt)


@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[APPOINTMENT_WRITE],
)
async def delete_appointment(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    repo = AppointmentRepository(db)
    appt = await repo.get_by_id(appointment_id)
    if appt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found"
        )
    await repo.delete(appt)
