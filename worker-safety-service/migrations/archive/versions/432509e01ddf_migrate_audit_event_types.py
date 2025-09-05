"""Migrate audit event types

Revision ID: 432509e01ddf
Revises: 40da6ae16fc5
Create Date: 2022-07-13 19:33:20.428138

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "432509e01ddf"
down_revision = "40da6ae16fc5"
branch_labels = None
depends_on = None

UPDATE_TYPES = [
    ("project_location_task_created", "task_created"),
    ("project_location_task_updated", "task_updated"),
    ("project_location_task_archived", "task_archived"),
    ("project_location_site_condition_created", "site_condition_created"),
    ("project_location_site_condition_updated", "site_condition_updated"),
    ("project_location_site_condition_archived", "site_condition_archived"),
    ("project_location_site_condition_evaluated", "site_condition_evaluated"),
]


def upgrade():
    for old_name, new_name in UPDATE_TYPES:
        op.execute(
            f"UPDATE public.audit_events SET event_type = '{new_name}' WHERE event_type = '{old_name}'"
        )


def downgrade():
    for old_name, new_name in UPDATE_TYPES:
        op.execute(
            f"UPDATE public.audit_events SET event_type = '{old_name}' WHERE event_type = '{new_name}'"
        )
