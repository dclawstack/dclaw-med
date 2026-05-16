"""Dialect-aware helpers so the same models work on Postgres (prod) and SQLite (dev)."""

import os
from urllib.parse import urlparse

from sqlalchemy import JSON, Uuid as SAUuid
from sqlalchemy.dialects.postgresql import JSONB


def _scheme() -> str:
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        return "postgresql"
    return urlparse(url.split("+", 1)[0] if "+" in url else url).scheme or url.split(":", 1)[0]


IS_SQLITE: bool = _scheme().startswith("sqlite")
IS_POSTGRES: bool = _scheme().startswith("postgres")


def UUIDType() -> SAUuid:
    """Cross-dialect UUID column type.

    SQLAlchemy 2.0's Uuid emits ``UUID`` on Postgres and ``CHAR(32)`` on SQLite,
    so the same model definitions work in both environments.
    """
    return SAUuid(as_uuid=True)


def JSONType() -> JSON:
    """Cross-dialect JSON column type.

    Uses ``JSONB`` on Postgres for query performance and ``JSON`` elsewhere.
    """
    return JSON().with_variant(JSONB(), "postgresql")
