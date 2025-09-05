"""Timestamp with TZ

Revision ID: d33a76a64654
Revises: 3be14f6ca50b
Create Date: 2022-03-10 16:32:26.581634

"""
import datetime

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "d33a76a64654"
down_revision = "3be14f6ca50b"
branch_labels = None
depends_on = None

TO_TS_WITH_TZ: list[tuple[str, str]] = [
    ("audit_event_diffs", "created_at"),
    ("audit_events", "created_at"),
    ("observation", "timestamp_created"),
    ("observation", "timestamp_updated"),
    ("raw_incidents", "timestamp_created"),
    ("raw_incidents", "timestamp_updated"),
    ("daily_reports", "created_at"),
]


def upgrade():
    for tablename, column in TO_TS_WITH_TZ:
        op.execute(
            f"ALTER TABLE {tablename} ALTER COLUMN {column} TYPE timestamptz USING {column} AT TIME ZONE 'UTC'"
        )

    now = datetime.datetime.now(datetime.timezone.utc)
    connection = op.get_bind()
    connection.execute(
        text(
            "UPDATE audit_event_diffs SET created_at = :value WHERE created_at IS NULL"
        ),
        value=now,
    )
    connection.execute(
        text("UPDATE audit_events SET created_at = :value WHERE created_at IS NULL"),
        value=now,
    )

    op.execute("ALTER TABLE audit_event_diffs ALTER COLUMN created_at SET NOT NULL")
    op.execute("ALTER TABLE audit_events ALTER COLUMN created_at SET NOT NULL")


def downgrade():
    for tablename, column in TO_TS_WITH_TZ:
        op.execute(f"ALTER TABLE {tablename} ALTER COLUMN {column} TYPE timestamp")

    op.execute("ALTER TABLE audit_event_diffs ALTER COLUMN created_at DROP NOT NULL")
    op.execute("ALTER TABLE audit_events ALTER COLUMN created_at DROP NOT NULL")
