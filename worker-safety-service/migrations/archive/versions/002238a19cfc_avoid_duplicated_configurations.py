"""Avoid duplicated configurations

Revision ID: 002238a19cfc
Revises: 051b8006f050
Create Date: 2022-10-27 18:24:42.134521

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "002238a19cfc"
down_revision = "051b8006f050"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "name",
        "configurations",
        ["name"],
        unique=True,
        postgresql_where="tenant_id IS NULL",
    )


def downgrade():
    op.drop_index(
        "name", table_name="configurations", postgresql_where="tenant_id IS NULL"
    )
