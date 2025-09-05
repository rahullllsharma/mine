"""Activity create audit

Revision ID: 57e96ff6c942
Revises: 444fa996c207
Create Date: 2022-08-03 18:01:51.063113

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "57e96ff6c942"
down_revision = "bb88fd6bc38c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE public.audit_object_type ADD VALUE IF NOT EXISTS 'activity'")
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'activity_created'"
    )


def downgrade():
    pass
