"""Add ebo audit events

Revision ID: 82c53cce39a8
Revises: 2b7410fda034
Create Date: 2023-08-03 15:48:36.345603

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "82c53cce39a8"
down_revision = "2b7410fda034"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'energy_based_observation_created'"
    )
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'energy_based_observation_updated'"
    )
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'energy_based_observation_archived'"
    )
    op.execute(
        "ALTER TYPE public.audit_object_type ADD VALUE IF NOT EXISTS 'energy_based_observation'"
    )


def downgrade():
    pass
