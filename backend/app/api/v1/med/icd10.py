"""ICD-10 lookup endpoints."""

from fastapi import APIRouter

from app.schemas.diagnosis import ICD10LookupRequest, ICD10LookupResponse
from app.services.icd10_service import lookup_icd10

router = APIRouter()


@router.post("/lookup", response_model=ICD10LookupResponse)
async def lookup_icd10_endpoint(
    request: ICD10LookupRequest,
) -> ICD10LookupResponse:
    """Search ICD-10 codes by term."""
    return lookup_icd10(request)
