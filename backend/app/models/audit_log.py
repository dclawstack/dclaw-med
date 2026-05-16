"""Audit log model for HIPAA-compliant access trails."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.dialect import JSONType, UUIDType
from app.models.base import Base, UUIDMixin


class AuditLog(Base, UUIDMixin):
    """Immutable record of a user action against a medical record."""

    __tablename__ = "audit_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(), nullable=True, index=True
    )
    old_value: Mapped[dict[str, Any] | None] = mapped_column(JSONType(), nullable=True)
    new_value: Mapped[dict[str, Any] | None] = mapped_column(JSONType(), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
