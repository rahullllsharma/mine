"""Add jsb audit values

Revision ID: 16103184ae32
Revises: 69f56b80e6da
Create Date: 2023-06-26 15:24:41.852827

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "16103184ae32"
down_revision = "69f56b80e6da"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'job_safety_briefing_created'"
    )
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'job_safety_briefing_updated'"
    )
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'job_safety_briefing_archived'"
    )
    op.execute(
        "ALTER TYPE public.audit_object_type ADD VALUE IF NOT EXISTS 'job_safety_briefing'"
    )
    pass


def downgrade():
    pass
