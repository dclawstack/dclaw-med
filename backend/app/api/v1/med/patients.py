"""Patient CRUD endpoints."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import PATIENT_WRITE, READ_ANY
from app.core.database import get_db
from app.repositories.patient_repo import PatientRepository
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate
from app.services.report_service import render_patient_pdf

router = APIRouter()


def _to_response(patient) -> PatientResponse:
    """Convert Patient ORM to response schema."""
    return PatientResponse.model_validate(patient)


@router.get("", response_model=list[PatientResponse], dependencies=[READ_ANY])
async def list_patients(
    page: int = 1,
    page_size: int = Query(default=20, ge=1, le=200),
    q: str | None = Query(default=None, description="Search by name (tsvector) or MRN substring"),
    dob_from: date | None = Query(default=None, description="Inclusive lower bound on date of birth"),
    dob_to: date | None = Query(default=None, description="Inclusive upper bound on date of birth"),
    diagnosis_code: str | None = Query(default=None, description="Filter to patients with a diagnosis at this ICD-10 code"),
    db: AsyncSession = Depends(get_db),
) -> list[PatientResponse]:
    """List patients with pagination + optional search filters."""
    repo = PatientRepository(db)
    patients, _total = await repo.list_patients(
        page=page,
        page_size=page_size,
        q=q,
        dob_from=dob_from,
        dob_to=dob_to,
        diagnosis_code=diagnosis_code,
    )
    return [_to_response(p) for p in patients]


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[PATIENT_WRITE],
)
async def create_patient(
    data: PatientCreate,
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    """Create a new patient."""
    repo = PatientRepository(db)

    # Check for duplicate MRN
    existing = await repo.get_by_mrn(data.medical_record_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Medical record number already exists",
        )

    patient = await repo.create(data)
    return _to_response(patient)


@router.get("/{patient_id}", response_model=PatientResponse, dependencies=[READ_ANY])
async def get_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    """Get a patient by ID."""
    repo = PatientRepository(db)
    patient = await repo.get_by_id(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    return _to_response(patient)


@router.put("/{patient_id}", response_model=PatientResponse, dependencies=[PATIENT_WRITE])
async def update_patient(
    patient_id: UUID,
    data: PatientUpdate,
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    """Update a patient."""
    repo = PatientRepository(db)
    patient = await repo.get_by_id(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    # Check MRN uniqueness if being updated
    if data.medical_record_number is not None:
        existing = await repo.get_by_mrn(data.medical_record_number)
        if existing and existing.id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Medical record number already exists",
            )

    patient = await repo.update(patient, data)
    return _to_response(patient)


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[PATIENT_WRITE],
)
async def delete_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a patient."""
    repo = PatientRepository(db)
    patient = await repo.get_by_id(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    await repo.delete(patient)


@router.get(
    "/{patient_id}/report",
    dependencies=[READ_ANY],
    responses={200: {"content": {"application/pdf": {}}}},
)
async def get_patient_report(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Generate a printable PDF report for a patient."""
    repo = PatientRepository(db)
    patient = await repo.get_for_report(patient_id)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    pdf_bytes = render_patient_pdf(patient)
    filename = f"patient-{patient.medical_record_number}-report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.get("/{patient_id}/history", dependencies=[READ_ANY])
async def get_patient_history(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get patient medical history timeline."""
    repo = PatientRepository(db)
    patient = await repo.get_by_id(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    timeline = [
        {
            "type": "registration",
            "date": patient.created_at.isoformat(),
            "description": f"Patient {patient.name} registered",
        },
    ]

    for note in patient.clinical_notes:
        timeline.append({
            "type": "note",
            "date": note.created_at.isoformat(),
            "description": f"{note.note_type.capitalize()} note created",
        })

    for diagnosis in patient.diagnoses:
        timeline.append({
            "type": "diagnosis",
            "date": diagnosis.created_at.isoformat(),
            "description": f"Diagnosed with {diagnosis.name}",
        })

    # Sort timeline by date
    timeline.sort(key=lambda x: x["date"])

    return {
        "patient_id": str(patient_id),
        "patient": _to_response(patient).model_dump(),
        "timeline": timeline,
        "symptoms": [
            {
                "id": str(s.id),
                "description": s.description,
                "severity": s.severity,
                "onset_date": s.onset_date.isoformat() if s.onset_date else None,
            }
            for s in patient.symptoms
        ],
        "diagnoses": [
            {
                "id": str(d.id),
                "name": d.name,
                "icd10_code": d.icd10_code,
                "confidence": d.confidence,
            }
            for d in patient.diagnoses
        ],
        "prescriptions": [
            {
                "id": str(p.id),
                "medication_name": p.medication_name,
                "dosage": p.dosage,
                "status": p.status,
            }
            for p in patient.prescriptions
        ],
        "clinical_notes": [
            {
                "id": str(n.id),
                "note_type": n.note_type,
                "content": n.content,
                "generated_by": n.generated_by,
                "created_at": n.created_at.isoformat(),
            }
            for n in patient.clinical_notes
        ],
    }
