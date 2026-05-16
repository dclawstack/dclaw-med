"""Seed the dev DB with realistic-looking demo data.

Usage:

    DATABASE_URL=sqlite+aiosqlite:///./dev.db python -m scripts.seed_dev

Or via the Makefile:

    make seed

Idempotent: skips records (by MRN / email) that already exist. Safe to run
against either SQLite (dev) or Postgres (prod-like).
"""

from __future__ import annotations

import asyncio
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.database import engine, init_db
from app.core.dialect import IS_SQLITE
from app.models.diagnosis import Diagnosis
from app.models.patient import Patient
from app.models.prescription import Prescription
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate

DEMO_PATIENTS = [
    ("Maria Alvarez", date(1962, 3, 14), "female", "MRN-1001"),
    ("James Okonkwo", date(1978, 11, 2), "male", "MRN-1002"),
    ("Sofia Rossi", date(1990, 7, 21), "female", "MRN-1003"),
    ("Daniel Park", date(1955, 1, 9), "male", "MRN-1004"),
    ("Aisha Khan", date(1986, 5, 30), "female", "MRN-1005"),
    ("Leo Schmidt", date(2002, 9, 4), "male", "MRN-1006"),
    ("Priya Nair", date(1971, 12, 17), "female", "MRN-1007"),
    ("Marcus Reed", date(1948, 6, 25), "male", "MRN-1008"),
    ("Yuki Tanaka", date(1995, 2, 11), "other", "MRN-1009"),
    ("Hannah Cohen", date(1980, 8, 8), "female", "MRN-1010"),
]

DEMO_DIAGNOSES = {
    "MRN-1001": ("I10", "Essential (primary) hypertension", 0.92, "confirmed"),
    "MRN-1002": ("E11.9", "Type 2 diabetes mellitus", 0.88, "confirmed"),
    "MRN-1003": ("G43.909", "Migraine, unspecified", 0.74, "provisional"),
    "MRN-1004": ("I50.9", "Heart failure, unspecified", 0.81, "confirmed"),
    "MRN-1005": ("F41.9", "Anxiety disorder, unspecified", 0.66, "confirmed"),
    "MRN-1007": ("J45.901", "Asthma with acute exacerbation", 0.79, "confirmed"),
}

DEMO_PRESCRIPTIONS = {
    "MRN-1001": ("Lisinopril", "10 mg", "once daily", "oral"),
    "MRN-1002": ("Metformin", "500 mg", "twice daily", "oral"),
    "MRN-1004": ("Furosemide", "40 mg", "once daily", "oral"),
    "MRN-1007": ("Albuterol", "90 mcg", "as needed", "inhalation"),
}


async def _seed_users(Session) -> None:
    async with Session() as db:
        repo = UserRepository(db)
        defaults = [
            ("admin@dclaw.dev", "admin-pass-1", "Site Admin", "admin"),
            ("doctor@dclaw.dev", "doctor-pass-1", "Dr. Jane Stone", "doctor"),
            ("nurse@dclaw.dev", "nurse-pass-1", "Nurse Marie Lee", "nurse"),
        ]
        for email, password, name, role in defaults:
            if await repo.get_by_email(email):
                continue
            await repo.create(
                UserCreate(email=email, password=password, full_name=name, role=role)
            )
            print(f"  + user: {email} ({role})")


async def _seed_patients(Session) -> None:
    async with Session() as db:
        from sqlalchemy import select

        existing = {
            p.medical_record_number: p
            for p in (
                await db.execute(select(Patient).where(Patient.medical_record_number.in_(
                    [m for _, _, _, m in DEMO_PATIENTS]
                )))
            ).scalars().all()
        }

        for name, dob, gender, mrn in DEMO_PATIENTS:
            if mrn in existing:
                continue
            patient = Patient(
                name=name,
                date_of_birth=dob,
                gender=gender,
                medical_record_number=mrn,
                contact_info={"email": f"{mrn.lower()}@example.org"},
            )
            db.add(patient)
            await db.flush()
            existing[mrn] = patient

            if mrn in DEMO_DIAGNOSES:
                code, dx_name, conf, status = DEMO_DIAGNOSES[mrn]
                db.add(Diagnosis(
                    patient_id=patient.id,
                    icd10_code=code,
                    name=dx_name,
                    confidence=conf,
                    status=status,
                ))
            if mrn in DEMO_PRESCRIPTIONS:
                med, dose, freq, route = DEMO_PRESCRIPTIONS[mrn]
                db.add(Prescription(
                    patient_id=patient.id,
                    medication_name=med,
                    dosage=dose,
                    frequency=freq,
                    route=route,
                    start_date=date.today() - timedelta(days=30),
                ))
            print(f"  + patient: {name} ({mrn})")

        await db.commit()


async def main() -> int:
    if IS_SQLITE:
        await init_db()
    Session = async_sessionmaker(engine, expire_on_commit=False)
    print("Seeding users…")
    await _seed_users(Session)
    print("Seeding patients…")
    await _seed_patients(Session)
    print("Done.")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
