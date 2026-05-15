"""Add patient search: name_tsv generated column + GIN index + dob index

Revision ID: 2026_05_15_0007
Revises: 2026_05_15_0006
Create Date: 2026-05-15 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "2026_05_15_0007"
down_revision: Union[str, None] = "2026_05_15_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Generated stored tsvector column on patient name.
    # Stored (persisted) so the GIN index can be used directly.
    op.execute(
        "ALTER TABLE patients ADD COLUMN name_tsv tsvector "
        "GENERATED ALWAYS AS (to_tsvector('english', coalesce(name, ''))) STORED"
    )
    op.create_index(
        "ix_patients_name_tsv",
        "patients",
        ["name_tsv"],
        postgresql_using="gin",
    )
    # DOB range filter benefits from a btree index.
    op.create_index(
        op.f("ix_patients_date_of_birth"),
        "patients",
        ["date_of_birth"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_patients_date_of_birth"), table_name="patients")
    op.drop_index("ix_patients_name_tsv", table_name="patients")
    op.drop_column("patients", "name_tsv")
