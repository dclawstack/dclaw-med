"""Password hashing and JWT helpers."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import settings

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Return an Argon2id hash for the given password."""
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against its stored Argon2id hash."""
    try:
        _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False
    return True


def create_access_token(user_id: UUID, role: str) -> str:
    """Create a signed JWT access token."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expire_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token. Raises jwt.PyJWTError on failure."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
