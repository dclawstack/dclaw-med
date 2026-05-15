"""Add users.patient_id FK for patient-portal accounts

Revision ID: 2026_05_15_0008
Revises: 2026_05_15_0007
Create Date: 2026-05-15 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "2026_05_15_0008"
down_revision: Union[str, None] = "2026_05_15_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_users_patient_id_patients"),
        "users",
        "patients",
        ["patient_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(op.f("ix_users_patient_id"), "users", ["patient_id"])

    # Allow the new 'patient' role in the existing CHECK constraint.
    # IF EXISTS guards fresh DBs that never carried the old constraint.
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS ck_users_role")
    op.create_check_constraint(
        "ck_users_role",
        "users",
        "role IN ('doctor', 'nurse', 'admin', 'receptionist', 'patient')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.create_check_constraint(
        "ck_users_role",
        "users",
        "role IN ('doctor', 'nurse', 'admin', 'receptionist')",
    )
    op.drop_index(op.f("ix_users_patient_id"), table_name="users")
    op.drop_constraint(
        op.f("fk_users_patient_id_patients"), "users", type_="foreignkey"
    )
    op.drop_column("users", "patient_id")
