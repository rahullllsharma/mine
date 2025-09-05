"""added burn kit location type

Revision ID: 10a98c5bdc39
Revises: c974c75324ab
Create Date: 2024-08-22 14:08:52.027282

"""
from alembic import op

revision = "10a98c5bdc39"
down_revision = "c974c75324ab"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE public.location_type ADD VALUE IF NOT EXISTS 'burn_kit_location'"
    )


def downgrade() -> None:
    pass
