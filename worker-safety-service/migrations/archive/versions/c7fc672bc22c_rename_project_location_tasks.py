"""Rename project_location_tasks

Revision ID: c7fc672bc22c
Revises: e0641cdc19d3
Create Date: 2022-07-13 16:17:49.757159

"""
import json

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "c7fc672bc22c"
down_revision = "e0641cdc19d3"
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
    # Task table
    op.execute(
        "ALTER TABLE public.project_location_tasks RENAME COLUMN project_location_id TO location_id"
    )
    op.execute(
        'ALTER TABLE public.project_location_tasks RENAME CONSTRAINT "project_location_tasks_pkey" TO "tasks_pkey"'
    )
    op.execute(
        'ALTER TABLE public.project_location_tasks RENAME CONSTRAINT "project_location_tasks_library_task_id_fkey" TO "tasks_library_task_id_fkey"'
    )
    op.execute(
        'ALTER TABLE public.project_location_tasks RENAME CONSTRAINT "project_location_tasks_project_location_id_fkey" TO "tasks_project_location_id_fkey"'
    )
    op.execute("ALTER INDEX project_location_tasks_lt_fkey RENAME TO tasks_pl_fkey")
    op.execute("ALTER INDEX project_location_tasks_pl_fkey RENAME TO tasks_lt_fkey")
    op.execute("ALTER TABLE public.project_location_tasks RENAME TO tasks")

    # Audit
    update_audit(
        "project_location_task",
        "task",
        "project_location_id",
        "location_id",
    )


def downgrade():
    # Task table
    op.execute(
        "ALTER TABLE public.tasks RENAME COLUMN location_id TO project_location_id"
    )
    op.execute(
        'ALTER TABLE public.tasks RENAME CONSTRAINT "tasks_pkey" TO "project_location_tasks_pkey"'
    )
    op.execute(
        'ALTER TABLE public.tasks RENAME CONSTRAINT "tasks_library_task_id_fkey" TO "project_location_tasks_library_task_id_fkey"'
    )
    op.execute(
        'ALTER TABLE public.tasks RENAME CONSTRAINT "tasks_project_location_id_fkey" TO "project_location_tasks_project_location_id_fkey"'
    )
    op.execute("ALTER INDEX tasks_pl_fkey RENAME TO project_location_tasks_lt_fkey")
    op.execute("ALTER INDEX tasks_lt_fkey RENAME TO project_location_tasks_pl_fkey")
    op.execute("ALTER TABLE public.tasks RENAME TO project_location_tasks")

    # Audit
    update_audit(
        "task",
        "project_location_task",
        "location_id",
        "project_location_id",
    )
