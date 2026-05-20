"""Demo dataset service.

Powers the public /api/v1/demo/* endpoints that the landing page uses
to populate a small sample dataset for a logged-out visitor.

Identification:
- Demo patients all use MRN prefix ``DEMO-`` (see :data:`DEMO_MRN_PREFIX`).
- The demo clinician account has the email :data:`DEMO_USER_EMAIL`.

``reset_demo()`` is scoped to *only* delete rows that match these markers,
so it can never touch real patient data even if someone enables the
feature flag on a populated instance by mistake.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.models.prescription import Prescription
from app.models.diagnosis import Diagnosis
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate

DEMO_MRN_PREFIX = "DEMO-"
DEMO_USER_EMAIL = "demo@dclaw.dev"
DEMO_USER_PASSWORD = "DemoPass123!"
DEMO_USER_NAME = "Demo Doctor"


@dataclass(frozen=True)
class _DemoPatient:
    mrn_suffix: str
    name: str
    dob: date
    gender: str
    diagnosis_code: str
    diagnosis_name: str
    diagnosis_confidence: float
    rx_medication: str
    rx_dosage: str
    rx_frequency: str
    rx_route: str


_DEMO_PATIENTS: tuple[_DemoPatient, ...] = (
    _DemoPatient(
        "1", "Anna Park", date(1985, 4, 12), "female",
        "E11.9", "Type 2 diabetes mellitus", 0.92,
        "Metformin", "500 mg", "twice daily", "oral",
    ),
    _DemoPatient(
        "2", "Ben Carter", date(1962, 8, 23), "male",
        "I10", "Essential (primary) hypertension", 0.95,
        "Lisinopril", "10 mg", "once daily", "oral",
    ),
    _DemoPatient(
        "3", "Clara Diaz", date(1990, 11, 5), "female",
        "G43.909", "Migraine, unspecified", 0.74,
        "Sumatriptan", "50 mg", "as needed", "oral",
    ),
    _DemoPatient(
        "4", "Daniel Wu", date(1948, 2, 17), "male",
        "I50.9", "Heart failure, unspecified", 0.88,
        "Furosemide", "40 mg", "once daily", "oral",
    ),
    _DemoPatient(
        "5", "Elena Ross", date(1978, 6, 30), "female",
        "J45.901", "Asthma with acute exacerbation", 0.81,
        "Albuterol inhaler", "90 mcg", "as needed", "inhalation",
    ),
)


@dataclass
class DemoStatus:
    enabled: bool
    seeded: bool
    patient_count: int


async def get_demo_status(db: AsyncSession, *, enabled: bool) -> DemoStatus:
    count = await _count_demo_patients(db)
    return DemoStatus(enabled=enabled, seeded=count > 0, patient_count=count)


async def seed_demo(db: AsyncSession) -> DemoStatus:
    """Create the demo dataset. Idempotent — re-running adds nothing new."""
    # Demo clinician account.
    user_repo = UserRepository(db)
    if not await user_repo.get_by_email(DEMO_USER_EMAIL):
        await user_repo.create(
            UserCreate(
                email=DEMO_USER_EMAIL,
                password=DEMO_USER_PASSWORD,
                full_name=DEMO_USER_NAME,
                role="doctor",
            )
        )

    existing_mrns = await _existing_demo_mrns(db)
    today = date.today()

    for spec in _DEMO_PATIENTS:
        mrn = f"{DEMO_MRN_PREFIX}{spec.mrn_suffix}"
        if mrn in existing_mrns:
            continue
        patient = Patient(
            name=spec.name,
            date_of_birth=spec.dob,
            gender=spec.gender,
            medical_record_number=mrn,
            contact_info={"email": f"{mrn.lower()}@example.org"},
        )
        db.add(patient)
        await db.flush()  # populate patient.id

        db.add(
            Diagnosis(
                patient_id=patient.id,
                icd10_code=spec.diagnosis_code,
                name=spec.diagnosis_name,
                confidence=spec.diagnosis_confidence,
                status="confirmed",
            )
        )
        db.add(
            Prescription(
                patient_id=patient.id,
                medication_name=spec.rx_medication,
                dosage=spec.rx_dosage,
                frequency=spec.rx_frequency,
                route=spec.rx_route,
                start_date=today - timedelta(days=30),
                status="active",
            )
        )

    await db.commit()
    return await get_demo_status(db, enabled=True)


async def reset_demo(db: AsyncSession) -> DemoStatus:
    """Delete every demo patient (cascades to symptoms/diagnoses/etc.) plus
    the demo clinician account. Never touches non-demo rows."""
    # Patients first — CASCADE on the FK handles child rows.
    await db.execute(
        delete(Patient).where(
            Patient.medical_record_number.startswith(DEMO_MRN_PREFIX)
        )
    )
    # Demo user is independent of the patient delete (it's a clinician).
    await db.execute(delete(User).where(User.email == DEMO_USER_EMAIL))
    await db.commit()
    return await get_demo_status(db, enabled=True)


async def _count_demo_patients(db: AsyncSession) -> int:
    res = await db.execute(
        select(func.count())
        .select_from(Patient)
        .where(Patient.medical_record_number.startswith(DEMO_MRN_PREFIX))
    )
    return int(res.scalar() or 0)


async def _existing_demo_mrns(db: AsyncSession) -> set[str]:
    res = await db.execute(
        select(Patient.medical_record_number).where(
            Patient.medical_record_number.startswith(DEMO_MRN_PREFIX)
        )
    )
    return {row[0] for row in res.all()}
