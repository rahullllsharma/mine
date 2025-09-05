"""Remove old audit types

Revision ID: 573ca3433695
Revises: 432509e01ddf
Create Date: 2022-07-20 18:35:45.252332

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "573ca3433695"
down_revision = "432509e01ddf"
branch_labels = None
depends_on = None


def upgrade():
    # AuditEventType
    for old_type, new_type in [
        ("project_location_task_created", "task_created"),
        ("project_location_task_updated", "task_updated"),
        ("project_location_task_archived", "task_archived"),
        ("project_location_site_condition_created", "site_condition_created"),
        ("project_location_site_condition_updated", "site_condition_updated"),
        ("project_location_site_condition_archived", "site_condition_archived"),
        ("project_location_site_condition_evaluated", "site_condition_evaluated"),
    ]:
        op.execute(
            f"UPDATE public.audit_events SET event_type = '{new_type}' WHERE event_type = '{old_type}'"
        )
    op.execute(
        """
        CREATE TYPE public.audit_event_type_new AS ENUM (
            'project_created',
            'project_updated',
            'project_archived',
            'task_created',
            'task_updated',
            'task_archived',
            'site_condition_created',
            'site_condition_updated',
            'site_condition_archived',
            'site_condition_evaluated',
            'daily_report_created',
            'daily_report_updated',
            'daily_report_archived'
        )
        """
    )
    op.execute(
        "ALTER TABLE audit_events ALTER COLUMN event_type TYPE audit_event_type_new USING (event_type::text::audit_event_type_new)"
    )
    op.execute("DROP TYPE audit_event_type")
    op.execute("ALTER TYPE audit_event_type_new RENAME TO audit_event_type")

    # AuditObjectType
    for old_type, new_type in [
        ("project_location_task", "task"),
        ("project_location_task_hazard", "task_hazard"),
        ("project_location_task_hazard_control", "task_control"),
        ("project_location_site_condition", "site_condition"),
        ("project_location_site_condition_hazard", "site_condition_hazard"),
        ("project_location_site_condition_hazard_control", "site_condition_control"),
    ]:
        op.execute(
            f"UPDATE public.audit_event_diffs SET object_type = '{new_type}' WHERE object_type = '{old_type}'"
        )
    op.execute(
        """
        CREATE TYPE public.audit_object_type_new AS ENUM (
            'project',
            'project_location',
            'task',
            'task_hazard',
            'task_control',
            'site_condition',
            'site_condition_hazard',
            'site_condition_control',
            'daily_report'
        )
        """
    )
    op.execute(
        "ALTER TABLE audit_event_diffs ALTER COLUMN object_type TYPE audit_object_type_new USING (object_type::text::audit_object_type_new)"
    )
    op.execute("DROP TYPE audit_object_type")
    op.execute("ALTER TYPE audit_object_type_new RENAME TO audit_object_type")


def downgrade():
    # AuditEventType
    for value in [
        "project_location_task_created",
        "project_location_task_updated",
        "project_location_task_archived",
        "project_location_site_condition_created",
        "project_location_site_condition_updated",
        "project_location_site_condition_archived",
        "project_location_site_condition_evaluated",
    ]:
        op.execute(f"ALTER TYPE audit_event_type ADD VALUE IF NOT EXISTS '{value}'")

    # AuditObjectType
    for value in [
        "project_location_task",
        "project_location_task_hazard",
        "project_location_task_hazard_control",
        "project_location_site_condition",
        "project_location_site_condition_hazard",
        "project_location_site_condition_hazard_control",
    ]:
        op.execute(f"ALTER TYPE audit_object_type ADD VALUE IF NOT EXISTS '{value}'")
