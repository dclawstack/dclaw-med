"""Audit middleware: log every successful authenticated /api/v1/med/* request."""

import re
import structlog
from typing import Optional
from uuid import UUID

import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings
from app.models.audit_log import AuditLog

logger = structlog.get_logger(__name__)

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)

_METHOD_TO_ACTION = {
    "GET": "read",
    "POST": "create",
    "PUT": "update",
    "PATCH": "update",
    "DELETE": "delete",
}

_MED_PREFIX = "/api/v1/med/"
_PORTAL_PREFIX = "/api/v1/patient-portal/"

# Map the trailing path segment of a portal route to the entity_type stored
# on the audit row, so a patient reading their own labs becomes a recognizable
# (action=read, entity_type=lab_results) row.
_PORTAL_ENTITY = {
    "me": "patient",
    "prescriptions": "prescriptions",
    "lab-results": "lab_results",
    "notes": "notes",
    "appointments": "appointments",
    "allergies": "allergies",
}


def _user_id_from_token(request: Request) -> Optional[UUID]:
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        return None
    token = auth.split(None, 1)[1]
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None


def _parse_med_path(path: str) -> tuple[Optional[str], Optional[UUID]]:
    """Return (entity_type, entity_id) for /api/v1/med/{entity}[/{uuid}][/...]."""
    rest = path[len(_MED_PREFIX):].strip("/")
    if not rest:
        return None, None
    parts = rest.split("/")
    entity_type = parts[0]
    if len(parts) > 1 and _UUID_RE.match(parts[1]):
        try:
            return entity_type, UUID(parts[1])
        except ValueError:
            pass
    return entity_type, None


def _parse_portal_path(path: str) -> tuple[Optional[str], Optional[UUID]]:
    """Return (entity_type, entity_id) for /api/v1/patient-portal/me[/<resource>].

    Portal routes are always `/me` or `/me/<resource>`. entity_id is always
    None — the resource is implicitly the current user's patient_id, which
    the audit log carries via user_id.
    """
    rest = path[len(_PORTAL_PREFIX):].strip("/")
    if not rest:
        return None, None
    parts = rest.split("/")
    if parts[0] != "me":
        return None, None
    # /me alone reads the patient record; /me/<resource> reads a collection.
    segment = parts[1] if len(parts) > 1 else "me"
    return _PORTAL_ENTITY.get(segment), None


class AuditMiddleware(BaseHTTPMiddleware):
    """Append-only access log for /api/v1/med/* and /api/v1/patient-portal/*.

    HIPAA expects every PHI access to leave a trail — that includes a patient
    reading their own record via the portal, not just clinician access via
    /med. Skips non-medical paths and failed (4xx/5xx) requests.
    """

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        path = request.url.path
        if path.startswith(_MED_PREFIX):
            entity_type, entity_id = _parse_med_path(path)
        elif path.startswith(_PORTAL_PREFIX):
            entity_type, entity_id = _parse_portal_path(path)
        else:
            return response

        if response.status_code >= 400:
            return response

        user_id = _user_id_from_token(request)
        if user_id is None:
            return response

        action = _METHOD_TO_ACTION.get(request.method)
        if entity_type is None or action is None:
            return response

        try:
            engine = request.app.state.engine
            async with AsyncSession(engine, expire_on_commit=False) as db:
                db.add(
                    AuditLog(
                        user_id=user_id,
                        action=action,
                        entity_type=entity_type,
                        entity_id=entity_id,
                    )
                )
                await db.commit()
        except Exception as exc:
            # Never let audit failure break a real request — log and continue.
            logger.warning("audit_write_failed", error=str(exc), path=path)

        return response
