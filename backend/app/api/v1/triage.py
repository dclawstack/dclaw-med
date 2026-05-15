"""Symptom-triage endpoint.

Lives at /api/v1/triage (top-level, not under /med) because it's a routing
tool — open to any authenticated user including the patient role — rather
than a clinical-record access path. Keeping it outside /med matches the
RBAC line the rest of the platform draws.
"""

from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.symptom import TriageRequest, TriageResponse
from app.services.symptom_analyzer import triage

router = APIRouter()


@router.post("", response_model=TriageResponse)
async def triage_endpoint(
    request: TriageRequest,
    _current: User = Depends(get_current_user),
) -> TriageResponse:
    """Triage a free-text symptom description.

    Available to any authenticated user (including patient role) so a patient
    can self-triage before booking. Returns urgency, suggested department,
    red flags, recommended tests, and short guidance.
    """
    return await triage(request)
