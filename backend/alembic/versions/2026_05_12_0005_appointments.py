"""Add appointments table

Revision ID: 2026_05_12_0005
Revises: 2026_05_12_0004
Create Date: 2026-05-12 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "2026_05_12_0005"
down_revision: Union[str, None] = "2026_05_12_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "appointments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="scheduled"),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"], ["patients.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["provider_id"], ["users.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_appointments")),
        sa.CheckConstraint(
            "status IN ('scheduled', 'completed', 'cancelled', 'no_show')",
            name=op.f("ck_appointments_status"),
        ),
        sa.CheckConstraint(
            "duration_minutes BETWEEN 5 AND 480",
            name=op.f("ck_appointments_duration"),
        ),
    )
    op.create_index(
        op.f("ix_appointments_patient_id"), "appointments", ["patient_id"]
    )
    op.create_index(
        op.f("ix_appointments_provider_id"), "appointments", ["provider_id"]
    )
    op.create_index(
        op.f("ix_appointments_scheduled_at"), "appointments", ["scheduled_at"]
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_appointments_scheduled_at"), table_name="appointments")
    op.drop_index(op.f("ix_appointments_provider_id"), table_name="appointments")
    op.drop_index(op.f("ix_appointments_patient_id"), table_name="appointments")
    op.drop_table("appointments")
