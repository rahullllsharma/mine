"""Postgis extension

Revision ID: 5d26653c64aa
Revises: 5677617a96e8
Create Date: 2022-11-03 17:06:13.484163

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "5d26653c64aa"
down_revision = "5677617a96e8"
branch_labels = None
depends_on = None


def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS "postgis"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "postgis_raster"')


def downgrade():
    pass
