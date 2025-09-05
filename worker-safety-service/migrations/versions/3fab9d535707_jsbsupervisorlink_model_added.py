"""JSBSupervisorLink Model Added

Revision ID: 3fab9d535707
Revises: 06368ece1955
Create Date: 2024-11-11 11:34:01.851552

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "3fab9d535707"
down_revision = "e9c7c128ff6c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "jsb_supervisor_link",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("manager_name", sa.String(), nullable=True),
        sa.Column("manager_email", sa.String(), nullable=True),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("jsb_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("manager_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["jsb_id"],
            ["jsbs.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "jsb_id_supervisor_id_unique",
        "jsb_supervisor_link",
        ["jsb_id", "manager_id"],
        unique=True,
    )
    op.create_unique_constraint(
        "jsb_id_supervisor_id_contraint_unique",
        "jsb_supervisor_link",
        ["jsb_id", "manager_id"],
    )


def downgrade() -> None:
    op.drop_index("jsb_id_supervisor_id_unique", table_name="jsb_supervisor_link")
    op.drop_constraint(
        "jsb_id_supervisor_id_contraint_unique", table_name="jsb_supervisor_link"
    )
    op.drop_table("jsb_supervisor_link")
