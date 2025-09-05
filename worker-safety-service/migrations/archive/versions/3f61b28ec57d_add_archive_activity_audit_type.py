"""add_archive_activity_audit_type

Revision ID: 3f61b28ec57d
Revises: 7e98f0dc21b4
Create Date: 2022-09-06 13:22:44.215074

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "3f61b28ec57d"
down_revision = "7e98f0dc21b4"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TYPE audit_event_type ADD VALUE IF NOT EXISTS 'activity_archived'"
    )


def downgrade():
    pass
