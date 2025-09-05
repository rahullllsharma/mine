"""Rename project_location_site_conditions

Revision ID: e0641cdc19d3
Revises: 442d80146ccb
Create Date: 2022-07-13 11:50:30.107798

"""
import json

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "e0641cdc19d3"
down_revision = "442d80146ccb"
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
    # Site condition table
    op.execute(
        "ALTER TABLE public.project_location_site_conditions RENAME COLUMN project_location_id TO location_id"
    )
    op.execute(
        'ALTER TABLE public.project_location_site_conditions RENAME CONSTRAINT "project_location_site_conditions_library_site_condition_id_fkey" TO "site_conditions_library_site_condition_id_fkey"'
    )
    op.execute(
        'ALTER TABLE public.project_location_site_conditions RENAME CONSTRAINT "project_location_site_conditions_project_location_id_fkey" TO "site_conditions_project_location_id_fkey"'
    )
    op.execute(
        'ALTER TABLE public.project_location_site_conditions RENAME CONSTRAINT "project_location_site_conditions_user_id_fkey" TO "site_conditions_user_id_fkey"'
    )
    op.execute(
        'ALTER TABLE public.project_location_site_conditions RENAME CONSTRAINT "project_location_site_conditions_pkey" TO "site_conditions_pkey"'
    )
    op.execute(
        'ALTER TABLE public.project_location_site_conditions RENAME CONSTRAINT "project_location_site_conditions_evaluated_key" TO "site_conditions_evaluated_key"'
    )
    op.execute(
        "ALTER INDEX project_location_site_conditions_evaluated_idx RENAME TO site_conditions_evaluated_idx"
    )
    op.execute(
        "ALTER INDEX project_location_site_conditions_lsc_fkey RENAME TO site_conditions_lsc_fkey"
    )
    op.execute(
        "ALTER INDEX project_location_site_conditions_manual_idx RENAME TO site_conditions_manual_idx"
    )
    op.execute(
        "ALTER INDEX project_location_site_conditions_manually_key RENAME TO site_conditions_manually_key"
    )
    op.execute(
        "ALTER TABLE public.project_location_site_conditions RENAME TO site_conditions"
    )

    # Audit
    update_audit(
        "project_location_site_condition",
        "site_condition",
        "project_location_id",
        "location_id",
    )


def downgrade():
    op.execute(
        "ALTER TABLE public.site_conditions RENAME COLUMN location_id TO project_location_id"
    )
    op.execute(
        'ALTER TABLE public.site_conditions RENAME CONSTRAINT "site_conditions_library_site_condition_id_fkey" TO "project_location_site_conditions_library_site_condition_id_fkey"'
    )
    op.execute(
        'ALTER TABLE public.site_conditions RENAME CONSTRAINT "site_conditions_project_location_id_fkey" TO "project_location_site_conditions_project_location_id_fkey"'
    )
    op.execute(
        'ALTER TABLE public.site_conditions RENAME CONSTRAINT "site_conditions_user_id_fkey" TO "project_location_site_conditions_user_id_fkey"'
    )
    op.execute(
        'ALTER TABLE public.site_conditions RENAME CONSTRAINT "site_conditions_pkey" TO "project_location_site_conditions_pkey"'
    )
    op.execute(
        'ALTER TABLE public.site_conditions RENAME CONSTRAINT "site_conditions_evaluated_key" TO "project_location_site_conditions_evaluated_key"'
    )
    op.execute(
        "ALTER INDEX site_conditions_evaluated_idx RENAME TO project_location_site_conditions_evaluated_idx"
    )
    op.execute(
        "ALTER INDEX site_conditions_lsc_fkey RENAME TO project_location_site_conditions_lsc_fkey"
    )
    op.execute(
        "ALTER INDEX site_conditions_manual_idx RENAME TO project_location_site_conditions_manual_idx"
    )
    op.execute(
        "ALTER INDEX site_conditions_manually_key RENAME TO project_location_site_conditions_manually_key"
    )
    op.execute(
        "ALTER TABLE public.site_conditions RENAME TO project_location_site_conditions"
    )

    # Audit
    update_audit(
        "site_condition",
        "project_location_site_condition",
        "location_id",
        "project_location_id",
    )
