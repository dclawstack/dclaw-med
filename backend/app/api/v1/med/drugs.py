"""Drug interaction endpoints."""

from fastapi import APIRouter

from app.core.auth import CLINICAL_TOOL
from app.schemas.prescription import DrugInteractionRequest, DrugInteractionResponse
from app.services.drug_service import check_interactions

router = APIRouter()


@router.post(
    "/interactions",
    response_model=DrugInteractionResponse,
    dependencies=[CLINICAL_TOOL],
)
async def check_drug_interactions(
    request: DrugInteractionRequest,
) -> DrugInteractionResponse:
    """Check for interactions between medications."""
    return check_interactions(request)
