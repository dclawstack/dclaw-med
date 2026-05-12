"""Add lab_results table

Revision ID: 2026_05_12_0004
Revises: 2026_05_12_0003
Create Date: 2026-05-12 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "2026_05_12_0004"
down_revision: Union[str, None] = "2026_05_12_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lab_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("test_name", sa.String(length=255), nullable=False),
        sa.Column("test_category", sa.String(length=100), nullable=False),
        sa.Column("result_value", sa.String(length=255), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("reference_range", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="final"),
        sa.Column("ordered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resulted_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_lab_results")),
        sa.CheckConstraint(
            "status IN ('pending', 'preliminary', 'final', 'corrected', 'cancelled')",
            name=op.f("ck_lab_results_status"),
        ),
    )
    op.create_index(
        op.f("ix_lab_results_patient_id"), "lab_results", ["patient_id"], unique=False
    )
    op.create_index(
        op.f("ix_lab_results_test_name"), "lab_results", ["test_name"], unique=False
    )
    op.create_index(
        op.f("ix_lab_results_test_category"),
        "lab_results",
        ["test_category"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_lab_results_test_category"), table_name="lab_results")
    op.drop_index(op.f("ix_lab_results_test_name"), table_name="lab_results")
    op.drop_index(op.f("ix_lab_results_patient_id"), table_name="lab_results")
    op.drop_table("lab_results")
