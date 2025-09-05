"""added workos table

Revision ID: 7ab5c51ff683
Revises: 9de57db0c808
Create Date: 2024-10-16 09:59:07.929314

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "7ab5c51ff683"
down_revision = "9de57db0c808"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workos",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("workos_org_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "workos_directory_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_workos_workos_directory_id"),
        "workos",
        ["workos_directory_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_workos_workos_org_id"), "workos", ["workos_org_id"], unique=True
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_workos_workos_org_id"), table_name="workos")
    op.drop_index(op.f("ix_workos_workos_directory_id"), table_name="workos")
    op.drop_table("workos")
