"""Admin-only audit trail endpoint."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import ADMIN_ONLY
from app.core.database import get_db
from app.repositories.audit_log_repo import AuditLogRepository
from app.schemas.audit_log import AuditLogResponse

router = APIRouter()


@router.get("", response_model=list[AuditLogResponse], dependencies=[ADMIN_ONLY])
async def list_audit_logs(
    user_id: UUID | None = None,
    entity_type: str | None = None,
    action: str | None = None,
    page: int = 1,
    page_size: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[AuditLogResponse]:
    """List audit log entries, newest first. Admin role only."""
    logs, _ = await AuditLogRepository(db).list_logs(
        user_id=user_id,
        entity_type=entity_type,
        action=action,
        page=page,
        page_size=page_size,
    )
    return [AuditLogResponse.model_validate(log) for log in logs]
