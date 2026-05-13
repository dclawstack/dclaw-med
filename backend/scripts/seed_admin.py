"""Bootstrap script: create the first admin user.

Usage (inside the backend container):

    docker compose exec backend python -m scripts.seed_admin \
        --email admin@example.com --password 'strong-pass' --name 'Site Admin'

Or via env vars (useful in CI/init containers):

    SEED_ADMIN_EMAIL=... SEED_ADMIN_PASSWORD=... SEED_ADMIN_NAME=... \
        python -m scripts.seed_admin

Idempotent: if a user with the given email already exists, exits 0 without
changing anything. Always sets `role=admin` and `is_active=true`.
"""

import argparse
import asyncio
import os
import sys

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.database import engine
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate


async def main(email: str, password: str, full_name: str) -> int:
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as db:
        repo = UserRepository(db)
        if await repo.get_by_email(email):
            print(f"User {email} already exists; nothing to do.")
            return 0
        await repo.create(
            UserCreate(
                email=email,
                password=password,
                full_name=full_name,
                role="admin",
            )
        )
        print(f"Created admin user: {email}")
        return 0


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--email", default=os.environ.get("SEED_ADMIN_EMAIL"))
    p.add_argument("--password", default=os.environ.get("SEED_ADMIN_PASSWORD"))
    p.add_argument("--name", default=os.environ.get("SEED_ADMIN_NAME", "Site Admin"))
    args = p.parse_args()
    if not args.email or not args.password:
        p.error(
            "--email and --password are required "
            "(or SEED_ADMIN_EMAIL / SEED_ADMIN_PASSWORD env vars)"
        )
    return args


if __name__ == "__main__":
    args = _parse_args()
    sys.exit(asyncio.run(main(args.email, args.password, args.name)))
