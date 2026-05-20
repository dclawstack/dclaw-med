"""Public demo dataset endpoints.

Gated by ``settings.enable_demo_mode``. When off, every endpoint returns 403
so the routes can still be wired and discoverable in ``/docs`` but won't
accept calls in production.

Authentication is intentionally absent — the landing page user is logged
out by definition, and the entire surface is bounded by the feature flag
and by the DEMO_ markers in :mod:`app.services.demo_service`.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.services.demo_service import (
    DEMO_USER_EMAIL,
    DEMO_USER_PASSWORD,
    get_demo_status,
    reset_demo,
    seed_demo,
)

router = APIRouter()


class DemoStatusResponse(BaseModel):
    enabled: bool
    seeded: bool
    patient_count: int
    model_config = ConfigDict(from_attributes=True)


class DemoCredentials(BaseModel):
    email: str
    password: str


class DemoSeedResponse(DemoStatusResponse):
    """Seed response carries the demo credentials so the frontend can sign
    the visitor in without making them retype anything."""

    demo_credentials: DemoCredentials


def _require_enabled() -> None:
    if not settings.enable_demo_mode:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo mode is disabled (set ENABLE_DEMO_MODE=true).",
        )


@router.get("/status", response_model=DemoStatusResponse)
async def status_endpoint(
    db: AsyncSession = Depends(get_db),
) -> DemoStatusResponse:
    """Whether demo mode is enabled and how many demo patients exist."""
    s = await get_demo_status(db, enabled=settings.enable_demo_mode)
    return DemoStatusResponse(**s.__dict__)


@router.post(
    "/seed",
    response_model=DemoSeedResponse,
    status_code=status.HTTP_200_OK,
)
async def seed_endpoint(
    db: AsyncSession = Depends(get_db),
) -> DemoSeedResponse:
    """Create the demo dataset and return sign-in credentials.

    Idempotent — calling this twice does not duplicate the patients.
    """
    _require_enabled()
    s = await seed_demo(db)
    return DemoSeedResponse(
        enabled=s.enabled,
        seeded=s.seeded,
        patient_count=s.patient_count,
        demo_credentials=DemoCredentials(
            email=DEMO_USER_EMAIL,
            password=DEMO_USER_PASSWORD,
        ),
    )


@router.delete("/reset", response_model=DemoStatusResponse)
async def reset_endpoint(
    db: AsyncSession = Depends(get_db),
) -> DemoStatusResponse:
    """Remove every demo patient (and the demo clinician account)."""
    _require_enabled()
    s = await reset_demo(db)
    return DemoStatusResponse(**s.__dict__)
