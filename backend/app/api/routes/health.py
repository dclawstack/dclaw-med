"""Health check endpoint."""

from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import engine
from app.core.rate_limit import limiter
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
@limiter.exempt
async def health_check() -> HealthResponse:
    """Return health status. Pings the DB so unhealthy pods get rescheduled."""
    db_status = "ok"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "unreachable"

    overall = "ok" if db_status == "ok" else "degraded"
    return HealthResponse(status=overall, database=db_status)
