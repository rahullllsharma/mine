"""updated workos table

Revision ID: fe5ef03dbf05
Revises: c03594b5f406
Create Date: 2024-11-22 17:19:47.078444

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "fe5ef03dbf05"
down_revision = "e47da3706b1f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_workos_workos_directory_id", table_name="workos")
    op.create_index(
        op.f("ix_workos_workos_directory_id"),
        "workos",
        ["workos_directory_id"],
        unique=False,
    )
    op.drop_index("ix_workos_workos_org_id", table_name="workos")
    op.create_index(
        op.f("ix_workos_workos_org_id"), "workos", ["workos_org_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_workos_workos_org_id"), table_name="workos")
    op.create_index("ix_workos_workos_org_id", "workos", ["workos_org_id"], unique=True)
    op.drop_index(op.f("ix_workos_workos_directory_id"), table_name="workos")
    op.create_index(
        "ix_workos_workos_directory_id", "workos", ["workos_directory_id"], unique=True
    )
