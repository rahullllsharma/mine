"""add standard operating procedures model

Revision ID: 6abeb62b1f5c
Revises: b50ab610b5e4
Create Date: 2024-05-31 14:34:31.419875

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "6abeb62b1f5c"
down_revision = "b50ab610b5e4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    This function creates new tables and indexes as follows:

    1. Create the `standard_operating_procedures` table with:
        - `name`: Name of the procedure (not nullable).
        - `link`: Link to the procedure (not nullable).
        - `id`: Primary key (GUID, not nullable).
        - `tenant_id`: Foreign key referencing `tenants.id` (GUID, not nullable).

    2. Create an index on the `tenant_id` column in the `standard_operating_procedures` table.

    3. Create the `library_task_standard_operating_procedures` table to link `library_tasks` and `standard_operating_procedures` with:
        - `library_task_id`: Foreign key referencing `library_tasks.id` (GUID, not nullable).
        - `standard_operating_procedure_id`: Foreign key referencing `standard_operating_procedures.id` (GUID, not nullable).
        - Primary key constraint on both `library_task_id` and `standard_operating_procedure_id`.
    """
    op.create_table(
        "standard_operating_procedures",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("link", sa.String(), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_standard_operating_procedures_tenant_id"),
        "standard_operating_procedures",
        ["tenant_id"],
        unique=False,
    )
    op.create_table(
        "library_task_standard_operating_procedures",
        sa.Column("library_task_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column(
            "standard_operating_procedure_id",
            sqlmodel.sql.sqltypes.GUID(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["library_task_id"],
            ["library_tasks.id"],
        ),
        sa.ForeignKeyConstraint(
            ["standard_operating_procedure_id"],
            ["standard_operating_procedures.id"],
        ),
        sa.PrimaryKeyConstraint("library_task_id", "standard_operating_procedure_id"),
    )


def downgrade() -> None:
    """
    This function drops the tables and indexes created during the upgrade:

    1. Drop the `library_task_standard_operating_procedures` table.
    2. Drop the index on the `tenant_id` column in the `standard_operating_procedures` table.
    3. Drop the `standard_operating_procedures` table.
    """
    op.drop_table("library_task_standard_operating_procedures")
    op.drop_index(
        op.f("ix_standard_operating_procedures_tenant_id"),
        table_name="standard_operating_procedures",
    )
    op.drop_table("standard_operating_procedures")
