"""Audit log repository — append-only access trail."""

from typing import Any
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditLogRepository:
    """Read/write access to the audit_logs table. No update/delete by design."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_log(
        self,
        user_id: UUID,
        action: str,
        entity_type: str,
        entity_id: UUID | None = None,
        old_value: dict[str, Any] | None = None,
        new_value: dict[str, Any] | None = None,
    ) -> AuditLog:
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
        )
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def list_logs(
        self,
        user_id: UUID | None = None,
        entity_type: str | None = None,
        action: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[AuditLog], int]:
        filters = []
        if user_id is not None:
            filters.append(AuditLog.user_id == user_id)
        if entity_type is not None:
            filters.append(AuditLog.entity_type == entity_type)
        if action is not None:
            filters.append(AuditLog.action == action)

        count_stmt = select(func.count()).select_from(AuditLog)
        for f in filters:
            count_stmt = count_stmt.where(f)
        total = (await self.db.execute(count_stmt)).scalar() or 0

        stmt = select(AuditLog).order_by(desc(AuditLog.timestamp))
        for f in filters:
            stmt = stmt.where(f)
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total
