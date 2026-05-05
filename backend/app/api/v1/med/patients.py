"""Patient CRUD endpoints."""

from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate

router = APIRouter()

# In-memory store for mock
MOCK_PATIENTS: dict[UUID, dict] = {}


def _to_response(p: dict) -> PatientResponse:
    """Convert dict to PatientResponse."""
    return PatientResponse(
        id=p["id"],
        name=p["name"],
        date_of_birth=p["date_of_birth"],
        gender=p["gender"],
        medical_record_number=p["medical_record_number"],
        contact_info=p.get("contact_info"),
        created_at=p["created_at"],
        updated_at=p["updated_at"],
    )


@router.get("", response_model=list[PatientResponse])
async def list_patients(
    page: int = 1,
    page_size: int = 20,
) -> list[PatientResponse]:
    """List all patients."""
    all_patients = list(MOCK_PATIENTS.values())
    start = (page - 1) * page_size
    end = start + page_size
    return [_to_response(p) for p in all_patients[start:end]]


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(data: PatientCreate) -> PatientResponse:
    """Create a new patient."""
    now = datetime.now(timezone.utc).isoformat()
    patient_id = uuid4()
    record = {
        "id": patient_id,
        "name": data.name,
        "date_of_birth": data.date_of_birth.isoformat() if hasattr(data.date_of_birth, "isoformat") else str(data.date_of_birth),
        "gender": data.gender,
        "medical_record_number": data.medical_record_number,
        "contact_info": data.contact_info,
        "created_at": now,
        "updated_at": now,
    }
    MOCK_PATIENTS[patient_id] = record
    return _to_response(record)


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: UUID) -> PatientResponse:
    """Get a patient by ID."""
    patient = MOCK_PATIENTS.get(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    return _to_response(patient)


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: UUID,
    data: PatientUpdate,
) -> PatientResponse:
    """Update a patient."""
    patient = MOCK_PATIENTS.get(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    if data.name is not None:
        patient["name"] = data.name
    if data.date_of_birth is not None:
        patient["date_of_birth"] = str(data.date_of_birth)
    if data.gender is not None:
        patient["gender"] = data.gender
    if data.contact_info is not None:
        patient["contact_info"] = data.contact_info
    patient["updated_at"] = datetime.now(timezone.utc).isoformat()
    return _to_response(patient)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(patient_id: UUID) -> None:
    """Delete a patient."""
    if patient_id not in MOCK_PATIENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    del MOCK_PATIENTS[patient_id]


@router.get("/{patient_id}/history")
async def get_patient_history(patient_id: UUID) -> dict:
    """Get patient medical history timeline."""
    patient = MOCK_PATIENTS.get(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    return {
        "patient_id": patient_id,
        "patient": _to_response(patient).model_dump(),
        "timeline": [
            {
                "type": "registration",
                "date": patient["created_at"],
                "description": f"Patient {patient['name']} registered",
            },
        ],
        "symptoms": [],
        "diagnoses": [],
        "prescriptions": [],
        "clinical_notes": [],
    }
