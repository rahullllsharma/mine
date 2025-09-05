"""Update contents column in jsbs table to add 'operating_hq' in work_location for latest users

Revision ID: f097801131a1
Revises: 3eb8473971e2
Create Date: 2025-02-04 11:54:49.653471

"""

import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f097801131a1"
down_revision = "3eb8473971e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # Find the latest `jsbs` entry for each unique `created_by_id`
    latest_jsbs_subquery = """
        WITH latest_jobs AS (
            SELECT DISTINCT ON (created_by_id) id, contents
            FROM jsbs
            ORDER BY created_by_id, created_at DESC
        )
        SELECT id, contents FROM latest_jobs
    """

    latest_jsbs = conn.execute(sa.text(latest_jsbs_subquery)).fetchall()

    for row in latest_jsbs:
        jsb_id = row.id
        contents = row.contents

        if contents and isinstance(contents, dict):
            # Ensure 'work_location' exists and update it
            if contents.get("work_location") is not None and (
                contents["work_location"].get("operating_hq") is None
            ):
                contents["work_location"]["operating_hq"] = ""

            # Update the row with modified contents
            update_query = sa.text(
                """
                UPDATE jsbs
                SET contents = :new_contents
                WHERE id = :jsb_id
            """
            )
            conn.execute(
                update_query, {"new_contents": json.dumps(contents), "jsb_id": jsb_id}
            )


def downgrade() -> None:
    pass  # No safe downgrade possible since JSON structure changes
