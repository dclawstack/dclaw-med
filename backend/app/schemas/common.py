"""Common schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str = "0.1.0"


class PaginatedResponse(BaseModel):
    """Paginated list response."""

    total: int = 0
    page: int = 1
    page_size: int = 20
