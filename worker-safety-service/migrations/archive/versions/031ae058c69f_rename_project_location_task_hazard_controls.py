"""Rename project_location_task_hazard_controls

Revision ID: 031ae058c69f
Revises: 625d291ad702
Create Date: 2022-07-07 22:57:59.264797

"""
import json

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "031ae058c69f"
down_revision = "625d291ad702"
branch_labels = None
depends_on = None


def update_audit(
    old_object_type: str, new_object_type: str, from_column: str, to_column: str
) -> None:
    for record in op.get_bind().execute(
        text(
            f"SELECT id, old_values, new_values FROM public.audit_event_diffs WHERE object_type = '{old_object_type}'"
        )
    ):
        to_update = {}
        if record.old_values and from_column in record.old_values:
            record.old_values[to_column] = record.old_values.pop(from_column)
            to_update["old_values"] = json.dumps(record.old_values)
        if record.new_values and from_column in record.new_values:
            record.new_values[to_column] = record.new_values.pop(from_column)
            to_update["new_values"] = json.dumps(record.new_values)
        if to_update:
            to_update["object_type"] = new_object_type
            update_columns = ", ".join(
                f"{column} = :{column}" for column in to_update.keys()
            )
            query = f"UPDATE public.audit_event_diffs SET {update_columns} WHERE id = '{record.id}'"
            op.get_bind().execute(text(query), to_update)

    op.execute(
        f"UPDATE public.audit_event_diffs SET object_type = '{new_object_type}' WHERE object_type = '{old_object_type}'"
    )


def upgrade():
    # Task controls table
    op.execute(
        "ALTER TABLE public.project_location_task_hazard_controls RENAME COLUMN project_location_task_hazard_id TO task_hazard_id"
    )
    op.execute(
        'ALTER TABLE public.project_location_task_hazard_controls RENAME CONSTRAINT "project_location_task_hazard_controls_pkey" TO "task_controls_pkey"'
    )
    op.execute(
        'ALTER TABLE public.project_location_task_hazard_controls RENAME CONSTRAINT "fk-project_location_task_hazard_controls-user" TO "fk-task_controls-user"'
    )
    op.execute(
        'ALTER TABLE public.project_location_task_hazard_controls RENAME CONSTRAINT "project_location_task_hazard__project_location_task_hazard_fkey" TO "task_controls_task_hazard_id_fkey"'
    )
    op.execute(
        'ALTER TABLE public.project_location_task_hazard_controls RENAME CONSTRAINT "project_location_task_hazard_controls_library_control_id_fkey" TO "task_controls_library_control_id_fkey"'
    )
    op.execute(
        "ALTER TABLE public.project_location_task_hazard_controls RENAME TO task_controls"
    )

    # Audit
    update_audit(
        "project_location_task_hazard_control",
        "task_control",
        "project_location_task_hazard_id",
        "task_hazard_id",
    )


def downgrade():
    op.execute(
        "ALTER TABLE public.task_controls RENAME COLUMN task_hazard_id TO project_location_task_hazard_id"
    )
    op.execute(
        'ALTER TABLE public.task_controls RENAME CONSTRAINT "task_controls_pkey" TO "project_location_task_hazard_controls_pkey"'
    )
    op.execute(
        'ALTER TABLE public.task_controls RENAME CONSTRAINT "fk-task_controls-user" TO "fk-project_location_task_hazard_controls-user"'
    )
    op.execute(
        'ALTER TABLE public.task_controls RENAME CONSTRAINT "task_controls_task_hazard_id_fkey" TO "project_location_task_hazard__project_location_task_hazard_fkey"'
    )
    op.execute(
        'ALTER TABLE public.task_controls RENAME CONSTRAINT "task_controls_library_control_id_fkey" TO "project_location_task_hazard_controls_library_control_id_fkey"'
    )
    op.execute(
        "ALTER TABLE public.task_controls RENAME TO project_location_task_hazard_controls"
    )

    # Audit
    update_audit(
        "task_control",
        "project_location_task_hazard_control",
        "task_hazard_id",
        "project_location_task_hazard_id",
    )
