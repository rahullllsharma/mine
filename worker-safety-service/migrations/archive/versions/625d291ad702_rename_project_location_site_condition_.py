"""Rename project_location_site_condition_hazard_controls

Revision ID: 625d291ad702
Revises: 8c383caa1303
Create Date: 2022-07-08 00:03:35.979521

"""
import json

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "625d291ad702"
down_revision = "8c383caa1303"
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
    # Site condition controls table
    op.execute(
        "ALTER TABLE public.project_location_site_condition_hazard_controls RENAME COLUMN project_location_site_condition_hazard_id TO site_condition_hazard_id"
    )
    op.execute(
        'ALTER TABLE public.project_location_site_condition_hazard_controls RENAME CONSTRAINT "project_location_site_condition_hazard_controls_pkey" TO "site_condition_controls_pkey"'
    )
    op.execute(
        'ALTER TABLE public.project_location_site_condition_hazard_controls RENAME CONSTRAINT "fk-project_location_site_condition_hazard_controls-user" TO "fk-site_condition_controls-user"'
    )
    op.execute(
        'ALTER TABLE public.project_location_site_condition_hazard_controls RENAME CONSTRAINT "project_location_site_condit_project_location_site_condit_fkey1" TO "site_condition_controls_site_condition_hazard_id_fkey"'
    )
    op.execute(
        'ALTER TABLE public.project_location_site_condition_hazard_controls RENAME CONSTRAINT "project_location_site_condition_hazard__library_control_id_fkey" TO "site_condition_controls_library_control_id_fkey"'
    )
    op.execute(
        "ALTER TABLE public.project_location_site_condition_hazard_controls RENAME TO site_condition_controls"
    )

    # Audit
    update_audit(
        "project_location_site_condition_hazard_control",
        "site_condition_control",
        "project_location_site_condition_hazard_id",
        "site_condition_hazard_id",
    )


def downgrade():
    op.execute(
        "ALTER TABLE public.site_condition_controls RENAME COLUMN site_condition_hazard_id TO project_location_site_condition_hazard_id"
    )
    op.execute(
        'ALTER TABLE public.site_condition_controls RENAME CONSTRAINT "site_condition_controls_pkey" TO "project_location_site_condition_hazard_controls_pkey"'
    )
    op.execute(
        'ALTER TABLE public.site_condition_controls RENAME CONSTRAINT "fk-site_condition_controls-user" TO "fk-project_location_site_condition_hazard_controls-user"'
    )
    op.execute(
        'ALTER TABLE public.site_condition_controls RENAME CONSTRAINT "site_condition_controls_site_condition_hazard_id_fkey" TO "project_location_site_condit_project_location_site_condit_fkey1"'
    )
    op.execute(
        'ALTER TABLE public.site_condition_controls RENAME CONSTRAINT "site_condition_controls_library_control_id_fkey" TO "project_location_site_condition_hazard__library_control_id_fkey"'
    )
    op.execute(
        "ALTER TABLE public.site_condition_controls RENAME TO project_location_site_condition_hazard_controls"
    )

    # Audit
    update_audit(
        "site_condition_control",
        "project_location_site_condition_hazard_control",
        "site_condition_hazard_id",
        "project_location_site_condition_hazard_id",
    )
