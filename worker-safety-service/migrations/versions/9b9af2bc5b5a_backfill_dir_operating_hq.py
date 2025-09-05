"""backfill_DIR_operating_hq

Revision ID: 9b9af2bc5b5a
Revises: 7173f34db919
Create Date: 2024-07-01 13:33:54.186579

"""
import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9b9af2bc5b5a"
down_revision = "7173f34db919"
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

    daily_reports = connection.execute(
        sa.text("SELECT id,project_location_id,sections FROM public.daily_reports")
    )

    for daily_report in daily_reports:
        if daily_report.project_location_id:
            operating_hq = library_region_name_from_project_location_id(
                daily_report.project_location_id
            )

            if not operating_hq:
                continue

            sections = daily_report.sections

            if (
                "additional_information" not in sections
                or not sections["additional_information"]
            ):
                sections["additional_information"] = {}

            sections["additional_information"]["operating_hq"] = operating_hq

            raw_sections = json.dumps(sections)

            connection.execute(
                sa.text(
                    "UPDATE public.daily_reports SET sections=:sections WHERE id=:id"
                ),
                {"id": daily_report.id, "sections": raw_sections},
            )


def downgrade():
    connection = op.get_bind()

    daily_reports = connection.execute(
        sa.text("SELECT id,project_location_id,sections FROM public.daily_reports")
    )

    for daily_report in daily_reports:
        sections = daily_report.sections
        if (
            daily_report.project_location_id
            and "additional_information" in sections
            and sections["additional_information"]
            and "operating_hq" in sections["additional_information"]
        ):
            del sections["additional_information"]["operating_hq"]
            raw_sections = json.dumps(sections)
            connection.execute(
                sa.text(
                    "UPDATE public.daily_reports SET sections=:sections WHERE id=:id"
                ),
                {"id": daily_report.id, "sections": raw_sections},
            )
