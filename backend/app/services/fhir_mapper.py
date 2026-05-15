"""ORM → FHIR R4 dict mappers.

Hand-rolled (no `fhir.resources` dependency). The output dicts conform to FHIR
R4 resource shapes well enough for interoperability sanity checks, but they're
not exhaustive — we only project the fields we actually populate.

Internal IDs go straight through as FHIR `id`s (UUIDs). Resource references
follow the standard `ResourceType/id` form so a Bundle is internally consistent.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from app.models.allergy import Allergy
from app.models.diagnosis import Diagnosis
from app.models.lab_result import LabResult
from app.models.patient import Patient
from app.models.prescription import Prescription

ICD10_SYSTEM = "http://hl7.org/fhir/sid/icd-10-cm"

# FHIR clinical-status / verification-status mapping for our internal
# diagnosis.status enum (provisional / confirmed / ruled_out).
_DIAGNOSIS_STATUS = {
    "provisional": {
        "clinicalStatus": "active",
        "verificationStatus": "provisional",
    },
    "confirmed": {
        "clinicalStatus": "active",
        "verificationStatus": "confirmed",
    },
    "ruled_out": {
        "clinicalStatus": "resolved",
        "verificationStatus": "refuted",
    },
}

_PRESCRIPTION_STATUS = {
    "active": "active",
    "completed": "completed",
    "discontinued": "stopped",
}

_LAB_STATUS = {
    "pending": "registered",
    "preliminary": "preliminary",
    "final": "final",
    "corrected": "corrected",
    "cancelled": "cancelled",
}

_ALLERGY_SEVERITY = {
    "mild": "mild",
    "moderate": "moderate",
    "severe": "severe",
    # "anaphylaxis" isn't a FHIR severity enum value; FHIR uses "severe"
    # with a reaction.manifestation indicating anaphylaxis. We project to
    # "severe" and surface the reaction free-text below.
    "anaphylaxis": "severe",
}


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def _ref(resource_type: str, resource_id: UUID | str) -> dict[str, str]:
    return {"reference": f"{resource_type}/{resource_id}"}


def patient_to_fhir(p: Patient) -> dict[str, Any]:
    """Map a Patient to a FHIR Patient resource."""
    # Naive split on first space — clinical apps usually carry first/last
    # separately, but our model has a single `name` so we approximate.
    parts = p.name.strip().split(None, 1)
    given = [parts[0]] if parts else []
    family = parts[1] if len(parts) > 1 else ""
    return {
        "resourceType": "Patient",
        "id": str(p.id),
        "meta": {"lastUpdated": _iso(p.updated_at)},
        "identifier": [
            {
                "use": "usual",
                "system": "urn:mrn",
                "value": p.medical_record_number,
            }
        ],
        "active": True,
        "name": [{"text": p.name, "family": family, "given": given}],
        "gender": p.gender if p.gender in ("male", "female", "other") else "unknown",
        "birthDate": p.date_of_birth.isoformat(),
    }


def diagnosis_to_fhir(d: Diagnosis) -> dict[str, Any]:
    """Map a Diagnosis to a FHIR Condition resource."""
    status = _DIAGNOSIS_STATUS.get(
        d.status, {"clinicalStatus": "active", "verificationStatus": "unconfirmed"}
    )
    return {
        "resourceType": "Condition",
        "id": str(d.id),
        "meta": {"lastUpdated": _iso(d.updated_at)},
        "clinicalStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": status["clinicalStatus"],
                }
            ]
        },
        "verificationStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                    "code": status["verificationStatus"],
                }
            ]
        },
        "code": {
            "coding": [
                {
                    "system": ICD10_SYSTEM,
                    "code": d.icd10_code,
                    "display": d.name,
                }
            ],
            "text": d.name,
        },
        "subject": _ref("Patient", d.patient_id),
        "recordedDate": _iso(d.created_at),
    }


def prescription_to_fhir(rx: Prescription) -> dict[str, Any]:
    """Map a Prescription to a FHIR MedicationRequest resource."""
    return {
        "resourceType": "MedicationRequest",
        "id": str(rx.id),
        "meta": {"lastUpdated": _iso(rx.updated_at)},
        "status": _PRESCRIPTION_STATUS.get(rx.status, "unknown"),
        "intent": "order",
        "medicationCodeableConcept": {"text": rx.medication_name},
        "subject": _ref("Patient", rx.patient_id),
        "authoredOn": _iso(rx.created_at),
        "dosageInstruction": [
            {
                "text": f"{rx.dosage} · {rx.frequency} · {rx.route}",
                "route": {"text": rx.route},
                "doseAndRate": [{"doseQuantity": {"value": rx.dosage}}],
                **({"patientInstruction": rx.instructions} if rx.instructions else {}),
            }
        ],
        "dispenseRequest": {
            "validityPeriod": {
                "start": rx.start_date.isoformat(),
                **(
                    {"end": rx.end_date.isoformat()}
                    if rx.end_date is not None
                    else {}
                ),
            }
        },
    }


def lab_result_to_fhir(lab: LabResult) -> dict[str, Any]:
    """Map a LabResult to a FHIR Observation resource."""
    return {
        "resourceType": "Observation",
        "id": str(lab.id),
        "meta": {"lastUpdated": _iso(lab.updated_at)},
        "status": _LAB_STATUS.get(lab.status, "unknown"),
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "laboratory",
                        "display": "Laboratory",
                    }
                ],
                "text": lab.test_category,
            }
        ],
        "code": {"text": lab.test_name},
        "subject": _ref("Patient", lab.patient_id),
        "effectiveDateTime": _iso(lab.ordered_at),
        **({"issued": _iso(lab.resulted_at)} if lab.resulted_at else {}),
        "valueString": (
            f"{lab.result_value}{' ' + lab.unit if lab.unit else ''}"
        ),
        **(
            {
                "referenceRange": [
                    {"text": lab.reference_range}
                ]
            }
            if lab.reference_range
            else {}
        ),
    }


def allergy_to_fhir(a: Allergy) -> dict[str, Any]:
    """Map an Allergy to a FHIR AllergyIntolerance resource."""
    return {
        "resourceType": "AllergyIntolerance",
        "id": str(a.id),
        "meta": {"lastUpdated": _iso(a.updated_at)},
        "clinicalStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                    "code": "active",
                }
            ]
        },
        "verificationStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                    "code": "confirmed",
                }
            ]
        },
        "type": "allergy",
        "criticality": (
            "high" if a.severity in ("severe", "anaphylaxis") else "low"
        ),
        "code": {"text": a.allergen},
        "patient": _ref("Patient", a.patient_id),
        "recordedDate": _iso(a.created_at),
        **(
            {
                "reaction": [
                    {
                        "manifestation": [{"text": a.reaction}],
                        "severity": _ALLERGY_SEVERITY.get(a.severity, "moderate"),
                    }
                ]
            }
            if a.reaction
            else {
                "reaction": [
                    {
                        "manifestation": [{"text": a.allergen}],
                        "severity": _ALLERGY_SEVERITY.get(a.severity, "moderate"),
                    }
                ]
            }
        ),
    }


def bundle(
    resource_type: str,
    resources: list[dict[str, Any]],
) -> dict[str, Any]:
    """Wrap a list of FHIR resources in a `searchset` Bundle."""
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(resources),
        "entry": [{"resource": r} for r in resources],
    }


def everything_bundle(patient: Patient) -> dict[str, Any]:
    """Build a FHIR Bundle (type=searchset) of every resource for a patient.

    Caller is responsible for eager-loading every related collection — the
    PatientRepository.get_for_report does this already.
    """
    resources: list[dict[str, Any]] = [patient_to_fhir(patient)]
    resources.extend(diagnosis_to_fhir(d) for d in patient.diagnoses)
    resources.extend(prescription_to_fhir(rx) for rx in patient.prescriptions)
    resources.extend(lab_result_to_fhir(l) for l in patient.lab_results)
    resources.extend(allergy_to_fhir(a) for a in patient.allergies)
    return bundle("Bundle", resources)
