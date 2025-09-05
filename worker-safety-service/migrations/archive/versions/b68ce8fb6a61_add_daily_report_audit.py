"""add-daily-report-audit

Revision ID: b68ce8fb6a61
Revises: 0f32f88344f9
Create Date: 2022-03-22 18:31:28.298216

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "b68ce8fb6a61"
down_revision = "554149a9d1e3"
branch_labels = None
depends_on = None

old_objects = [
    "project",
    "project_location",
    "project_location_task",
    "project_location_task_hazard",
    "project_location_task_hazard_control",
    "project_location_site_condition",
    "project_location_site_condition_hazard",
    "project_location_site_condition_hazard_control",
]
old_events = [
    "project_created",
    "project_updated",
    "project_location_task_created",
    "project_location_task_updated",
    "project_location_task_archived",
    "project_location_site_condition_created",
    "project_location_site_condition_updated",
    "project_location_site_condition_archived",
]

new_objects = ["daily_report"]
new_events = [
    "daily_report_archived",
    "daily_report_created",
    "daily_report_updated",
]


def upgrade():
    op.execute("ALTER TYPE audit_object_type ADD VALUE IF NOT EXISTS 'daily_report'")

    for t in new_events:
        op.execute(f"ALTER TYPE audit_event_type ADD VALUE IF NOT EXISTS '{t}'")


def downgrade():
    op.execute("ALTER TYPE audit_event_type RENAME TO audit_event_type_old")
    old_events_str = ", ".join(map(lambda x: f"'{x}'", old_events))
    op.execute(f"CREATE TYPE audit_event_type AS ENUM({old_events_str})")
    new_events_str = ", ".join(map(lambda x: f"'{x}'", new_events))

    op.execute("ALTER TYPE audit_object_type RENAME TO audit_object_type_old")
    old_objects_str = ", ".join(map(lambda x: f"'{x}'", old_objects))
    op.execute(f"CREATE TYPE audit_object_type AS ENUM({old_objects_str})")

    # this should also delete all daily report object types
    op.execute(
        f"""
            DELETE FROM audit_event_diffs WHERE event_id in
            (SELECT id FROM audit_events WHERE event_type in ({new_events_str}))
        """
    )
    op.execute(f"DELETE FROM audit_events WHERE event_Type in ({new_events_str})")
    op.execute(
        "ALTER TABLE audit_events ALTER COLUMN event_type TYPE audit_event_type USING event_type::text::audit_event_type"
    )
    op.execute(
        "ALTER TABLE audit_event_diffs ALTER COLUMN object_type TYPE audit_object_type USING object_type::text::audit_object_type"
    )
    op.execute("DROP TYPE audit_event_type_old")
    op.execute("DROP TYPE audit_object_type_old")
