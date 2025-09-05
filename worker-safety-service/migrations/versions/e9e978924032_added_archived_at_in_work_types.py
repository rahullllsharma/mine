"""added archived at in work types

Revision ID: e9e978924032
Revises: 3e4a21abd72c
Create Date: 2024-06-27 22:02:56.200529

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e9e978924032"
down_revision = "f097801131a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "work_types",
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("work_types", "archived_at")
