"""create archived_at column for users

Revision ID: d5769b9ff60d
Revises: 937444637855
Create Date: 2024-02-09 14:58:32.021775

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d5769b9ff60d"
down_revision = "002d39b4f281"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users", sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade():
    op.drop_column("users", "archived_at")
