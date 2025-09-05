"""add display_name field to tenants table

Revision ID: cf74785f909a
Revises: d0c3f1002352
Create Date: 2024-01-12 00:52:57.460632

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "cf74785f909a"
down_revision = "d0c3f1002352"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("display_name", sa.String(), nullable=True))

    # pre populate with the existing value in tenant_name column
    op.execute("UPDATE tenants SET display_name = tenant_name")


def downgrade() -> None:
    op.drop_column("tenants", "display_name")
