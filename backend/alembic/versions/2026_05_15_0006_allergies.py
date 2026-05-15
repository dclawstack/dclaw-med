"""Add allergies table

Revision ID: 2026_05_15_0006
Revises: 2026_05_12_0005
Create Date: 2026-05-15 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "2026_05_15_0006"
down_revision: Union[str, None] = "2026_05_12_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "allergies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("allergen", sa.String(length=255), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("reaction", sa.Text(), nullable=True),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_allergies")),
        sa.CheckConstraint(
            "severity IN ('mild', 'moderate', 'severe', 'anaphylaxis')",
            name=op.f("ck_allergies_severity"),
        ),
        sa.UniqueConstraint(
            "patient_id",
            "allergen",
            name=op.f("uq_allergies_patient_allergen"),
        ),
    )
    op.create_index(op.f("ix_allergies_patient_id"), "allergies", ["patient_id"])
    op.create_index(op.f("ix_allergies_allergen"), "allergies", ["allergen"])


def downgrade() -> None:
    op.drop_index(op.f("ix_allergies_allergen"), table_name="allergies")
    op.drop_index(op.f("ix_allergies_patient_id"), table_name="allergies")
    op.drop_table("allergies")
