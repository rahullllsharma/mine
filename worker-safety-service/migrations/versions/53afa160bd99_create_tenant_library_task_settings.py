"""Create tenant library task settings

Revision ID: 53afa160bd99
Revises: fed04c6c8ea8
Create Date: 2024-06-16 17:46:27.614995

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "53afa160bd99"
down_revision = "fed04c6c8ea8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_library_task_settings",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("alias", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("library_task_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["library_task_id"],
            ["library_tasks.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("tenant_id", "library_task_id"),
    )
    op.create_index(
        "tenant_library_task_settings_library_task_id_idx",
        "tenant_library_task_settings",
        ["library_task_id"],
        unique=False,
    )
    op.create_index(
        "tenant_library_task_settings_tenant_id_idx",
        "tenant_library_task_settings",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "tenant_library_task_settings_tenant_id_library_task_id_idx",
        "tenant_library_task_settings",
        ["tenant_id", "library_task_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "tenant_library_task_settings_tenant_id_library_task_id_idx",
        table_name="tenant_library_task_settings",
    )
    op.drop_index(
        "tenant_library_task_settings_tenant_id_idx",
        table_name="tenant_library_task_settings",
    )
    op.drop_index(
        "tenant_library_task_settings_library_task_id_idx",
        table_name="tenant_library_task_settings",
    )
    op.drop_table("tenant_library_task_settings")
