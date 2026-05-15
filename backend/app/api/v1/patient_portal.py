"""Patient-portal endpoints — read-only access scoped to the current user's patient_id."""

from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import PORTAL_ONLY, get_current_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.allergy_repo import AllergyRepository
from app.repositories.appointment_repo import AppointmentRepository
from app.repositories.clinical_note_repo import ClinicalNoteRepository
from app.repositories.lab_result_repo import LabResultRepository
from app.repositories.patient_repo import PatientRepository
from app.repositories.prescription_repo import PrescriptionRepository
from app.schemas.allergy import AllergyResponse
from app.schemas.appointment import AppointmentResponse
from app.schemas.clinical_note import ClinicalNoteResponse
from app.schemas.lab_result import LabResultResponse
from app.schemas.patient import PatientResponse
from app.schemas.prescription import PrescriptionResponse

router = APIRouter()


def _ensure_linked(user: User) -> UUID:
    """Resolve the current user's patient_id or raise a clear 403."""
    if user.patient_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is not yet linked to a patient record. "
            "Ask an administrator to complete the link.",
        )
    return user.patient_id


@router.get("/me", response_model=PatientResponse, dependencies=[PORTAL_ONLY])
async def get_my_record(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    pid = _ensure_linked(user)
    patient = await PatientRepository(db).get_by_id(pid)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Linked patient record no longer exists",
        )
    return PatientResponse.model_validate(patient)


@router.get(
    "/me/prescriptions",
    response_model=list[PrescriptionResponse],
    dependencies=[PORTAL_ONLY],
)
async def list_my_prescriptions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Sequence[PrescriptionResponse]:
    pid = _ensure_linked(user)
    items, _ = await PrescriptionRepository(db).list_prescriptions(
        patient_id=pid, page=1, page_size=200
    )
    return [PrescriptionResponse.model_validate(p) for p in items]


@router.get(
    "/me/lab-results",
    response_model=list[LabResultResponse],
    dependencies=[PORTAL_ONLY],
)
async def list_my_lab_results(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Sequence[LabResultResponse]:
    pid = _ensure_linked(user)
    items, _ = await LabResultRepository(db).list_lab_results(
        patient_id=pid, page=1, page_size=200
    )
    return [LabResultResponse.model_validate(l) for l in items]


@router.get(
    "/me/notes",
    response_model=list[ClinicalNoteResponse],
    dependencies=[PORTAL_ONLY],
)
async def list_my_notes(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Sequence[ClinicalNoteResponse]:
    pid = _ensure_linked(user)
    items, _ = await ClinicalNoteRepository(db).list_notes(
        patient_id=pid, page=1, page_size=200
    )
    return [ClinicalNoteResponse.model_validate(n) for n in items]


@router.get(
    "/me/appointments",
    response_model=list[AppointmentResponse],
    dependencies=[PORTAL_ONLY],
)
async def list_my_appointments(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Sequence[AppointmentResponse]:
    pid = _ensure_linked(user)
    items, _ = await AppointmentRepository(db).list_appointments(
        patient_id=pid, page=1, page_size=200
    )
    return [AppointmentResponse.model_validate(a) for a in items]


@router.get(
    "/me/allergies",
    response_model=list[AllergyResponse],
    dependencies=[PORTAL_ONLY],
)
async def list_my_allergies(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Sequence[AllergyResponse]:
    pid = _ensure_linked(user)
    items, _ = await AllergyRepository(db).list_for_patient(
        patient_id=pid, page=1, page_size=200
    )
    return [AllergyResponse.model_validate(a) for a in items]
