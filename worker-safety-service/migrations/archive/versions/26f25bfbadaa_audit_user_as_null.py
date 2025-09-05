"""Audit user as NULL

Revision ID: 26f25bfbadaa
Revises: 8fd95d29a41e
Create Date: 2022-04-27 17:33:47.580902

"""
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "26f25bfbadaa"
down_revision = "8fd95d29a41e"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "audit_events", "user_id", existing_type=postgresql.UUID(), nullable=True
    )


def downgrade():
    # If we have audit_events.user_id = NULL it will fail
    # but we don't have a good way to define urbint user
    op.alter_column(
        "audit_events", "user_id", existing_type=postgresql.UUID(), nullable=False
    )
