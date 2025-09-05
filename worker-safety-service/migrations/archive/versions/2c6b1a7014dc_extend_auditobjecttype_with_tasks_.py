"""Extend AuditObjectType with tasks, site_conditions, hazards, controls

Revision ID: 2c6b1a7014dc
Revises: 156a80d386af
Create Date: 2022-02-07 13:09:05.082755

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "2c6b1a7014dc"
down_revision = "7776ecf6c7c2"
branch_labels = None
depends_on = None

old_types = [
    "project",
    "project_location",
]

new_types = [
    "project_location_task",
    "project_location_task_hazard",
    "project_location_task_hazard_control",
    "project_location_site_condition",
    "project_location_site_condition_hazard",
    "project_location_site_condition_hazard_control",
]


def upgrade():
    for t in new_types:
        op.execute(f"ALTER TYPE audit_object_type ADD VALUE IF NOT EXISTS '{t}'")


def downgrade():
    op.execute("ALTER TYPE audit_object_type RENAME TO audit_object_type_old")

    # recreate the old type
    old_types_str = ", ".join(map(lambda x: f"'{x}'", old_types))
    op.execute(f"CREATE TYPE audit_object_type AS ENUM({old_types_str})")

    # drop no-longer supported diffs
    new_types_str = ", ".join(map(lambda x: f"'{x}'", old_types))
    op.execute(
        f"""
    DELETE FROM audit_event_diffs WHERE object_type in ({new_types_str})
    """
    )

    # update the table's column type
    op.execute(
        (
            "ALTER TABLE audit_event_diffs ALTER COLUMN object_type TYPE audit_object_type USING "
            "object_type::text::audit_object_type"
        )
    )
    op.execute("DROP TYPE audit_object_type_old")
