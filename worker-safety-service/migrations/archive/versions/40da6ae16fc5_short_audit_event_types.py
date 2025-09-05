"""Short audit event types

Revision ID: 40da6ae16fc5
Revises: 303a4ae027ac
Create Date: 2022-07-13 19:28:17.474411

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "40da6ae16fc5"
down_revision = "303a4ae027ac"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'task_created'"
    )
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'task_updated'"
    )
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'task_archived'"
    )
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'site_condition_created'"
    )
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'site_condition_updated'"
    )
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'site_condition_archived'"
    )
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'site_condition_evaluated'"
    )


def downgrade():
    pass
