"""Per-client rate limiting.

A single shared :class:`slowapi.Limiter` keyed by client IP. A generous
default limit is applied to every route via ``SlowAPIMiddleware`` (wired up in
``app.api.main``); brute-force and expensive endpoints opt into stricter limits
with ``@limiter.limit(...)``.

The in-memory store is per-process, so behind multiple replicas each pod keeps
its own counters. That is intentionally a first line of defence — pair it with
gateway/ingress limits for a hard global cap.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit_default],
    enabled=settings.rate_limit_enabled,
    headers_enabled=True,
)
