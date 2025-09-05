"""added index on work type

Revision ID: 4e1de636f404
Revises: e9e978924032
Create Date: 2024-07-22 15:15:15.111143

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4e1de636f404"
down_revision = "e9e978924032"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "unique_work_type_name_when_tenant_id_is_null",
        "work_types",
        ["name"],
        unique=True,
        postgresql_where=sa.text("tenant_id IS NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "unique_work_type_name_when_tenant_id_is_null",
        table_name="work_types",
        postgresql_where=sa.text("tenant_id IS NULL"),
    )
