"""Audit log schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    """A single audit log entry."""

    id: UUID
    user_id: UUID
    action: str
    entity_type: str
    entity_id: UUID | None
    old_value: dict[str, Any] | None
    new_value: dict[str, Any] | None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
