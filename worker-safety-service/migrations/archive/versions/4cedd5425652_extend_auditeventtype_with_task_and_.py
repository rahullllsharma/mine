"""Extend AuditEventType with task and site_condition crud

Revision ID: 4cedd5425652
Revises: 2c6b1a7014dc
Create Date: 2022-02-07 13:32:51.531766

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "4cedd5425652"
down_revision = "2c6b1a7014dc"
branch_labels = None
depends_on = None

old_types = [
    "project_created",
    "project_updated",
]

new_types = [
    "project_location_task_created",
    "project_location_task_updated",
    "project_location_task_archived",
    "project_location_site_condition_created",
    "project_location_site_condition_updated",
    "project_location_site_condition_archived",
]


def upgrade():
    for t in new_types:
        op.execute(f"ALTER TYPE audit_event_type ADD VALUE IF NOT EXISTS '{t}'")


def downgrade():
    op.execute("ALTER TYPE audit_event_type RENAME TO audit_event_type_old")

    # recreate the old type
    old_types_str = ", ".join(map(lambda x: f"'{x}'", old_types))
    op.execute(f"CREATE TYPE audit_event_type AS ENUM({old_types_str})")

    new_types_str = ", ".join(map(lambda x: f"'{x}'", old_types))
    # poor man's cascade delete
    # drop no-longer supported diffs
    op.execute(
        f"""
        DELETE FROM audit_event_diffs WHERE event_id in
        (SELECT id FROM audit_events WHERE event_type in ({new_types_str}));
    """
    )
    # drop no-longer supported events
    op.execute(f"DELETE FROM audit_events WHERE event_type in ({new_types_str});")

    # update the table's column type
    op.execute(
        (
            "ALTER TABLE audit_events ALTER COLUMN event_type TYPE audit_event_type USING "
            "event_type::text::audit_event_type"
        )
    )
    op.execute("DROP TYPE audit_event_type_old")
