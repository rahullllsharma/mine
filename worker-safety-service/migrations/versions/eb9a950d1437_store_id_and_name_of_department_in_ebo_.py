"""store id and name of department in EBO detail

Revision ID: eb9a950d1437
Revises: d2b87e1d7c0e
Create Date: 2023-11-30 14:27:28.791010

"""
import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "eb9a950d1437"
down_revision = "d2b87e1d7c0e"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    # Get all rows with non-null content
    query = "SELECT id, contents FROM public.energy_based_observations WHERE contents IS NOT NULL AND contents->>'details' IS NOT NULL;"
    sql = sa.text(query)
    rows = connection.execute(sql)

    for row in rows:
        old_contents = row.contents
        department_observed = old_contents["details"]["department_observed"]

        # Convert the "department_observed" items to the new structure
        new_department_observed = {
            "id": None,  # as we have no id currently and the name is also some hardcoded value
            "name": department_observed,
        }

        # Update the "department_observed" in details field in the "contents" JSON
        new_contents = old_contents.copy()
        new_contents["details"]["department_observed"] = new_department_observed

        # Update the row with the modified JSON data
        connection.execute(
            sa.text(
                "UPDATE public.energy_based_observations SET contents = :new_contents WHERE id = :id"
            ),
            {"new_contents": json.dumps(new_contents), "id": row.id},
        )


def downgrade():
    connection = op.get_bind()
    # Get all rows with non-null content and the updated structure
    query = "SELECT id, contents FROM public.energy_based_observations WHERE contents IS NOT NULL AND contents->'details'->'department_observed' IS NOT NULL;"
    sql = sa.text(query)
    rows = connection.execute(sql)

    for row in rows:
        old_contents = row.contents
        new_department_observed = old_contents["details"]["department_observed"]

        # Revert the "department_observed" field to the original structure
        department_observed = new_department_observed["name"]

        # Update the "department_observed" in details field in the "contents" JSON
        new_contents = old_contents.copy()
        new_contents["details"]["department_observed"] = department_observed

        # Update the row with the modified JSON data
        connection.execute(
            sa.text(
                "UPDATE public.energy_based_observations SET contents = :new_contents WHERE id = :id"
            ),
            {"new_contents": json.dumps(new_contents), "id": row.id},
        )
