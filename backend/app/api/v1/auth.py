"""Authentication endpoints: register, login, current user."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, require_role
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import ProviderResponse, Token, UserCreate, UserResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _current: User = Depends(require_role("admin")),
) -> UserResponse:
    """Create a new user. Admin-only — for bootstrap, see `scripts/seed_admin.py`."""
    repo = UserRepository(db)
    existing = await repo.get_by_email(data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user = await repo.create(data)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Exchange email (username field) + password for a JWT access token."""
    repo = UserRepository(db)
    user = await repo.get_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )
    return Token(access_token=create_access_token(user.id, user.role))


@router.get("/me", response_model=UserResponse)
async def read_me(current: User = Depends(get_current_user)) -> UserResponse:
    """Return the current authenticated user."""
    return UserResponse.model_validate(current)


@router.get("/providers", response_model=list[ProviderResponse])
async def list_providers(
    db: AsyncSession = Depends(get_db),
    _current: User = Depends(get_current_user),
) -> list[ProviderResponse]:
    """Return active doctors and admins, for appointment provider pickers."""
    providers = await UserRepository(db).list_providers()
    return [ProviderResponse.model_validate(p) for p in providers]
