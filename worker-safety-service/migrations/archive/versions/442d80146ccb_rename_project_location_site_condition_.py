"""Rename project_location_site_condition_hazards

Revision ID: 442d80146ccb
Revises: 35df9f804cf7
Create Date: 2022-07-12 18:27:41.185770

"""
import json

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "442d80146ccb"
down_revision = "35df9f804cf7"
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
    # Site condition hazards table
    op.execute(
        "ALTER TABLE public.project_location_site_condition_hazards RENAME COLUMN project_location_site_condition_id TO site_condition_id"
    )
    op.execute(
        'ALTER TABLE public.project_location_site_condition_hazards RENAME CONSTRAINT "project_location_site_condition_hazards_pkey" TO "site_condition_hazards_pkey"'
    )
    op.execute(
        'ALTER TABLE public.project_location_site_condition_hazards RENAME CONSTRAINT "fk-project_location_site_condition_hazards-user" TO "fk-site_condition_hazards-user"'
    )
    op.execute(
        'ALTER TABLE public.project_location_site_condition_hazards RENAME CONSTRAINT "project_location_site_conditi_project_location_site_condit_fkey" TO "site_condition_hazards_site_condition_id_fkey"'
    )
    op.execute(
        'ALTER TABLE public.project_location_site_condition_hazards RENAME CONSTRAINT "project_location_site_condition_hazards_library_hazard_id_fkey" TO "site_condition_hazards_library_hazard_id_fkey"'
    )
    op.execute(
        "ALTER TABLE public.project_location_site_condition_hazards RENAME TO site_condition_hazards"
    )

    # Audit
    update_audit(
        "project_location_site_condition_hazard",
        "site_condition_hazard",
        "project_location_site_condition_id",
        "site_condition_id",
    )


def downgrade():
    op.execute(
        "ALTER TABLE public.site_condition_hazards RENAME COLUMN site_condition_id TO project_location_site_condition_id"
    )
    op.execute(
        'ALTER TABLE public.site_condition_hazards RENAME CONSTRAINT "site_condition_hazards_pkey" TO "project_location_site_condition_hazards_pkey"'
    )
    op.execute(
        'ALTER TABLE public.site_condition_hazards RENAME CONSTRAINT "fk-site_condition_hazards-user" TO "fk-project_location_site_condition_hazards-user"'
    )
    op.execute(
        'ALTER TABLE public.site_condition_hazards RENAME CONSTRAINT "site_condition_hazards_site_condition_id_fkey" TO "project_location_site_conditi_project_location_site_condit_fkey"'
    )
    op.execute(
        'ALTER TABLE public.site_condition_hazards RENAME CONSTRAINT "site_condition_hazards_library_hazard_id_fkey" TO "project_location_site_condition_hazards_library_hazard_id_fkey"'
    )
    op.execute(
        "ALTER TABLE public.site_condition_hazards RENAME TO project_location_site_condition_hazards"
    )

    # Audit
    update_audit(
        "site_condition_hazard",
        "project_location_site_condition_hazard",
        "site_condition_id",
        "project_location_site_condition_id",
    )
