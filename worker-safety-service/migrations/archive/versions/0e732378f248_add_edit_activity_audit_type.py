"""add_edit_activity_audit_type

Revision ID: 0e732378f248
Revises: 7683c53a0e8c
Create Date: 2022-08-24 12:19:52.702161

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "0e732378f248"
down_revision = "7683c53a0e8c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE audit_event_type ADD VALUE IF NOT EXISTS 'activity_updated'")


def downgrade():
    pass
