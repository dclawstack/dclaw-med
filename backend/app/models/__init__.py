"""Ensure every model class is registered with SQLAlchemy's mapper.

Importing the package binds the relationship name lookups (e.g. ``"Symptom"``
in ``Patient.symptoms``) so any module that only imports a subset of models
still gets a fully configured registry.
"""

from app.models import (  # noqa: F401
    allergy,
    appointment,
    audit_log,
    base,
    clinical_note,
    diagnosis,
    lab_result,
    patient,
    prescription,
    symptom,
    user,
)
