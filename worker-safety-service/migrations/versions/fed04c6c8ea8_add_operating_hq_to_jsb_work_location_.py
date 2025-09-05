"""add_operating_hq_to_jsb_work_location_and_backfill

Revision ID: fed04c6c8ea8
Revises: 6abeb62b1f5c
Create Date: 2024-06-12 13:33:55.087852

"""
import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fed04c6c8ea8"
down_revision = "6abeb62b1f5c"
branch_labels = None
depends_on = None


def library_region_name_from_project_location_id(id):
    connection = op.get_bind()
    library_region = connection.execute(
        sa.text(
            """
            SELECT lr.name
            FROM public.project_locations pl
            JOIN public.projects p ON pl.project_id = p.id
            JOIN public.library_regions lr ON p.library_region_id = lr.id
            WHERE pl.id=:id
        """
        ),
        {"id": id},
    ).first()

    return library_region[0] if library_region else None


def upgrade():
    connection = op.get_bind()

    jsbs = connection.execute(
        sa.text("SELECT id,project_location_id,contents FROM public.jsbs")
    )

    for jsb in jsbs:
        if jsb.project_location_id:
            operating_hq = library_region_name_from_project_location_id(
                jsb.project_location_id
            )

            if not operating_hq:
                continue

            contents = jsb.contents
            if "work_location" not in contents or not contents["work_location"]:
                contents["work_location"] = {}
            contents["work_location"]["operating_hq"] = operating_hq
            raw_contents = json.dumps(contents)
            connection.execute(
                sa.text("UPDATE public.jsbs SET contents=:contents WHERE id=:id"),
                {"id": jsb.id, "contents": raw_contents},
            )


def downgrade():
    connection = op.get_bind()

    jsbs = connection.execute(
        sa.text("SELECT id,project_location_id,contents FROM public.jsbs")
    )

    for jsb in jsbs:
        contents = jsb.contents
        if (
            jsb.project_location_id
            and "work_location" in contents
            and contents["work_location"]
            and "operating_hq" in contents["work_location"]
        ):
            del contents["work_location"]["operating_hq"]
            raw_contents = json.dumps(contents)
            connection.execute(
                sa.text("UPDATE public.jsbs SET contents=:contents WHERE id=:id"),
                {"id": jsb.id, "contents": raw_contents},
            )
