"""Request ID middleware.

Reads ``X-Request-ID`` from the incoming request (or generates a UUID4) and
echoes it back on the response. Bound to structlog's context so every log
line in the request scope carries the same id — easy to grep, easy to
correlate with downstream services.
"""

from __future__ import annotations

import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a stable request id to every request/response pair."""

    async def dispatch(self, request: Request, call_next) -> Response:
        req_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        request.state.request_id = req_id

        structlog.contextvars.bind_contextvars(request_id=req_id)
        try:
            response = await call_next(request)
        finally:
            structlog.contextvars.unbind_contextvars("request_id")

        response.headers[REQUEST_ID_HEADER] = req_id
        return response
