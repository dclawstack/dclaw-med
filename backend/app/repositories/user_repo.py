"""User repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    """User data access repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get a user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Get a user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, data: UserCreate) -> User:
        """Create a new user with hashed password."""
        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            role=data.role,
            is_active=True,
            patient_id=data.patient_id,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def set_patient_link(
        self, user: User, patient_id: UUID | None
    ) -> User:
        """Set or clear the patient link on an existing user."""
        user.patient_id = patient_id
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def list_providers(self) -> list[User]:
        """List active users eligible to be assigned as appointment providers."""
        result = await self.db.execute(
            select(User)
            .where(User.is_active.is_(True))
            .where(User.role.in_(("doctor", "admin")))
            .order_by(User.full_name)
        )
        return list(result.scalars().all())

    async def list_users(self, role: str | None = None) -> list[User]:
        """List all users, optionally filtered by role. Newest first."""
        stmt = select(User).order_by(User.created_at.desc())
        if role is not None:
            stmt = stmt.where(User.role == role)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
