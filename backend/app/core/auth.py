"""Authentication and authorization dependencies."""

from typing import Callable
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repo import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Resolve the current user from a bearer JWT. 401 on any failure."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise credentials_exc

    user = await UserRepository(db).get_by_id(user_id)
    if user is None or not user.is_active:
        raise credentials_exc
    return user


def require_role(*allowed_roles: str) -> Callable[[User], User]:
    """Dependency factory that enforces the current user has one of the given roles."""

    async def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(allowed_roles)}",
            )
        return user

    return _check


# Reusable role-group dependencies.
# Centralize policy here so router files declare intent, not raw role lists.

READ_ANY = Depends(get_current_user)
PATIENT_WRITE = Depends(require_role("admin", "doctor", "receptionist"))
SYMPTOM_WRITE = Depends(require_role("admin", "doctor", "nurse"))
DIAGNOSIS_WRITE = Depends(require_role("admin", "doctor"))
PRESCRIPTION_WRITE = Depends(require_role("admin", "doctor"))
NOTE_WRITE = Depends(require_role("admin", "doctor", "nurse"))
LAB_WRITE = Depends(require_role("admin", "doctor", "nurse"))
APPOINTMENT_WRITE = Depends(require_role("admin", "doctor", "receptionist"))
CLINICAL_TOOL = Depends(require_role("admin", "doctor", "nurse"))
ADMIN_ONLY = Depends(require_role("admin"))
