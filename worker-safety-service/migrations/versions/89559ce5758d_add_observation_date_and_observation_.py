"""Add observation date and observation time to observation detail

Revision ID: 89559ce5758d
Revises: a715ce6008f2
Create Date: 2023-10-31 12:40:30.077374

"""
import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "89559ce5758d"
down_revision = "a715ce6008f2"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    # Get all rows with non-null content

    query = "SELECT id, created_at, contents FROM public.energy_based_observations WHERE (contents IS NOT NULL AND (contents->'details' IS NOT NULL AND jsonb_typeof(contents->'details') = 'object'));"
    sql = sa.text(query)
    rows = connection.execute(sql)

    for row in rows:
        created_at = row.created_at
        observation_date = created_at.date().isoformat()
        observation_time = created_at.time().isoformat()

        # Update the contents dictionary
        contents = row.contents
        if contents["details"] is not None:  # additional check
            contents["details"]["observation_date"] = observation_date
            contents["details"]["observation_time"] = observation_time

        contents_json = json.dumps(contents)

        # Update the row with the modified content
        connection.execute(
            sa.text(
                "UPDATE public.energy_based_observations SET contents = :contents WHERE id = :id"
            ),
            {"contents": contents_json, "id": row.id},
        )


def downgrade():
    connection = op.get_bind()
    # Get all rows with non-null content
    query = "SELECT id, contents FROM public.energy_based_observations WHERE contents IS NOT NULL;"
    sql = sa.text(query)
    rows = connection.execute(sql)

    for row in rows:
        # Get the original contents dictionary
        contents = row.contents

        # Remove the 'observation_date' and 'observation_time' fields from the 'details' dictionary
        if "details" in contents and contents["details"] is not None:
            if "observation_date" in contents["details"]:
                del contents["details"]["observation_date"]
            if "observation_time" in contents["details"]:
                del contents["details"]["observation_time"]

        contents_json = json.dumps(contents)

        # Update the row with the modified content
        connection.execute(
            sa.text(
                "UPDATE public.energy_based_observations SET contents = :contents WHERE id = :id"
            ),
            {"contents": contents_json, "id": row.id},
        )
