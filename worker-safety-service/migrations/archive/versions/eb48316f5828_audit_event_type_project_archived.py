"""audit event type project archived

Revision ID: eb48316f5828
Revises: 0e295d2678ff
Create Date: 2022-05-05 16:08:17.717818

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "eb48316f5828"
down_revision = "0e295d2678ff"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE audit_event_type ADD VALUE IF NOT EXISTS 'project_archived'")


def downgrade():
    # we don't want to lose data, so we keep the existing type and any entries that use it
    pass
