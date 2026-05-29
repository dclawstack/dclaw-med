"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.routes import health
from app.api.v1 import audit as audit_router
from app.api.v1 import auth as auth_router
from app.api.v1 import demo as demo_router
from app.api.v1 import patient_portal as patient_portal_router
from app.api.v1 import triage as triage_router
from app.api.v1.med import router as med_router
from app.core.audit_middleware import AuditMiddleware
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.rate_limit import limiter
from app.core.request_id import RequestIDMiddleware

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler.

    Prod uses Alembic for schema. SQLite dev mode skips Alembic and creates
    tables on first boot so ``make dev`` works without any extra steps.
    """
    from app.core.dialect import IS_SQLITE

    if IS_SQLITE:
        from app.core.database import init_db

        await init_db()
    yield


app = FastAPI(
    title="DClaw Med",
    description="Clinical intelligence API",
    version="0.1.0",
    lifespan=lifespan,
)

from app.core.database import engine as _engine
app.state.engine = _engine

# Rate limiting. SlowAPIMiddleware applies the default limit to every route;
# per-route @limiter.limit decorators tighten it on sensitive endpoints.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuditMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SlowAPIMiddleware)

app.include_router(health.router, tags=["Health"])
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(audit_router.router, prefix="/api/v1/audit", tags=["Audit"])
app.include_router(
    patient_portal_router.router,
    prefix="/api/v1/patient-portal",
    tags=["Patient Portal"],
)
app.include_router(triage_router.router, prefix="/api/v1/triage", tags=["Triage"])
app.include_router(demo_router.router, prefix="/api/v1/demo", tags=["Demo"])
app.include_router(med_router, prefix="/api/v1/med")
