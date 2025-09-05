"""Store multiple work-type in ebo detail

Revision ID: 9cd8c877e870
Revises: 89559ce5758d
Create Date: 2023-10-31 16:28:38.086474

"""
import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9cd8c877e870"
down_revision = "89559ce5758d"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    # Get all rows with non-null content
    query = "SELECT id, contents FROM public.energy_based_observations WHERE (contents IS NOT NULL AND (contents->'details' IS NOT NULL AND jsonb_typeof(contents->'details') = 'object'));"

    sql = sa.text(query)
    rows = connection.execute(sql)

    for row in rows:
        old_contents = row.contents
        work_type = old_contents["details"]["work_type"]

        # Convert the "work_type" items to the new structure
        new_work_type = [
            {
                "id": None,  # as we have no id currently and the name is also some hardcoded value
                "name": work_type,
            }
        ]

        # Update the "work_type" in details field in the "contents" JSON
        new_contents = old_contents.copy()
        new_contents["details"]["work_type"] = new_work_type

        # Update the row with the modified JSON data
        connection.execute(
            sa.text(
                "UPDATE public.energy_based_observations SET contents = :new_contents WHERE id = :id"
            ),
            {"new_contents": json.dumps(new_contents), "id": row.id},
        )


def downgrade():
    connection = op.get_bind()

    # Get all rows with non-null content
    query = "SELECT id, contents FROM public.energy_based_observations WHERE (contents IS NOT NULL AND (contents->'details' IS NOT NULL AND jsonb_typeof(contents->'details') = 'array'));"
    sql = sa.text(query)
    rows = connection.execute(sql)

    for row in rows:
        old_contents = row.contents
        new_work_type = old_contents["details"][0]["name"]

        # Convert the new "work_type" structure back to the old structure
        work_type = new_work_type

        # Update the "work_type" in details field in the "contents" JSON
        new_contents = old_contents.copy()
        new_contents["details"]["work_type"] = work_type

        # Update the row with the modified JSON data
        connection.execute(
            sa.text(
                "UPDATE public.energy_based_observations SET contents = :new_contents WHERE id = :id"
            ),
            {"new_contents": json.dumps(new_contents), "id": row.id},
        )
