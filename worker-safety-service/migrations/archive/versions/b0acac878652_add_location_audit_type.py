"""Add location audit type

Revision ID: b0acac878652
Revises: 194a333ba62f
Create Date: 2023-02-06 13:23:26.174985

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "b0acac878652"
down_revision = "194a333ba62f"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'project_location_created'"
    )
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'project_location_updated'"
    )
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'project_location_archived'"
    )


def downgrade():
    pass
