"""Update audit_events.user to be required

Revision ID: ce1e0947692b
Revises: 4cedd5425652
Create Date: 2022-02-08 17:19:39.149401

"""
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "ce1e0947692b"
down_revision = "254ce3767087"
branch_labels = None
depends_on = None


def upgrade():
    # clean up some invalid events
    # drop diffs on events without users
    op.execute(
        """
        DELETE FROM audit_event_diffs WHERE event_id in
        (SELECT id FROM audit_events WHERE user_id is NULL);
    """
    )
    # drop events without users
    op.execute("DELETE FROM audit_events WHERE user_id is NULL;")

    op.alter_column(
        "audit_events", "user_id", existing_type=postgresql.UUID(), nullable=False
    )


def downgrade():
    op.alter_column(
        "audit_events", "user_id", existing_type=postgresql.UUID(), nullable=True
    )
