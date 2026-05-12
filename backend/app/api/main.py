"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health
from app.api.v1 import auth as auth_router
from app.api.v1.med import router as med_router
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler. Schema is managed by Alembic."""
    yield


app = FastAPI(
    title="DClaw Med",
    description="Clinical intelligence API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(med_router, prefix="/api/v1/med")
