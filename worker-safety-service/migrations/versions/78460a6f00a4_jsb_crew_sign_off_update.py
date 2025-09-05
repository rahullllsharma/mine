"""jsb crew sign off update

Revision ID: 78460a6f00a4
Revises: 8c5e9568ba61
Create Date: 2023-09-19 10:56:17.156747

"""
import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "78460a6f00a4"
down_revision = "8c5e9568ba61"
branch_labels = None
depends_on = None


def upgrade():
    # Backfill the "crew_sign_off" JSON data for all rows in the "jsbs" table with the new structure.
    connection = op.get_bind()

    # Fetch rows where "crew_sign_off" is not null
    query = """
    SELECT id, contents
    FROM public.jsbs
    WHERE
      contents->'crew_sign_off' IS NOT NULL
      AND jsonb_typeof(contents) = 'object' -- Ensure contents is a JSON object
      AND contents <> '{}' -- Check if contents is not an empty JSON object;
    """

    sql = sa.text(query)
    rows = connection.execute(sql)

    for row in rows:
        old_contents = row.contents
        crew_sign_off = old_contents.get("crew_sign_off", [])

        if crew_sign_off is None:
            continue

        # Convert the "crew_sign_off" items to the new structure
        new_crew_sign_off = [
            {
                "name": item,
                "signature": {
                    "id": "",
                    "md5": None,
                    "url": "",
                    "date": None,
                    "name": "",
                    "size": None,
                    "time": None,
                    "crc32c": None,
                    "category": None,
                    "mimetype": None,
                    "signed_url": None,
                    "display_name": "",
                },
            }
            for item in crew_sign_off
        ]

        # Update the "crew_sign_off" field in the "contents" JSON
        new_contents = old_contents.copy()
        new_contents["crew_sign_off"] = new_crew_sign_off

        # Update the row with the modified JSON data
        connection.execute(
            sa.text("UPDATE public.jsbs SET contents = :new_contents WHERE id = :id"),
            {"new_contents": json.dumps(new_contents), "id": row.id},
        )


def downgrade():
    # Restore the original structure of the "crew_sign_off" field in the "contents" JSON.
    connection = op.get_bind()

    # Fetch rows where "crew_sign_off" is not null
    query = """
    SELECT id, contents
    FROM public.jsbs
    WHERE
      contents->'crew_sign_off' IS NOT NULL
      AND jsonb_typeof(contents) = 'object' -- Ensure contents is a JSON object
      AND contents <> '{}' -- Check if contents is not an empty JSON object;
    """

    sql = sa.text(query)
    rows = connection.execute(sql)

    for row in rows:
        old_contents = row.contents
        crew_sign_off = old_contents.get("crew_sign_off", [])

        # Revert the "crew_sign_off" items to their original structure
        original_crew_sign_off = [item["name"] for item in crew_sign_off]

        # Update the "crew_sign_off" field in the "contents" JSON with the original structure
        new_contents = old_contents.copy()
        new_contents["crew_sign_off"] = original_crew_sign_off

        # Update the row with the modified JSON data
        connection.execute(
            sa.text("UPDATE public.jsbs SET contents = :new_contents WHERE id = :id"),
            {"new_contents": json.dumps(new_contents), "id": row.id},
        )
