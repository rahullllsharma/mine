"""jsb control assessment selections update

Revision ID: 5c0dba7e8c42
Revises: 0465884fe67b
Create Date: 2024-02-22 11:00:53.228995

"""

import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5c0dba7e8c42"
down_revision = "0465884fe67b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Backfill the data for all rows in the "jsbs" table with the new structure.
    connection = op.get_bind()

    query = """
    SELECT id, contents
    FROM public.jsbs
    WHERE
      (contents->'control_assessment_selections' IS NOT NULL OR contents->'task_selections' IS NOT NULL)
      AND jsonb_typeof(contents) = 'object' -- Ensure contents is a JSON object
      AND contents <> '{}' -- Check if contents is not an empty JSON object;
    """

    sql = sa.text(query)
    rows = connection.execute(sql)

    for row in rows:
        # Convert the "control_assessment_selections" items to the new structure
        for item in row.contents.get("control_assessment_selections") or []:
            if (
                item.get("control_selections") is None
                and item.get("control_ids") is not None
            ):
                item["control_selections"] = [
                    {"id": id, "recommended": None, "selected": None}
                    for id in item.get("control_ids")
                ]

        # Update the "task_selections" field in the "contents" JSON
        row.contents["task_selections"] = [
            {"recommended": None, "selected": None, **item}
            for item in row.contents.get("task_selections") or []
        ]

        # Update the row with the modified JSON data
        connection.execute(
            sa.text("UPDATE public.jsbs SET contents = :new_contents WHERE id = :id"),
            {"new_contents": json.dumps(row.contents), "id": row.id},
        )


def downgrade() -> None:
    # Restore the original structure of the "control_assessment_selections" field in the "contents" JSON.
    connection = op.get_bind()

    # Fetch rows where "control_assessment_selections" is not null
    query = """
    SELECT id, contents
    FROM public.jsbs
    WHERE
      (contents->'control_assessment_selections' IS NOT NULL OR contents->'task_selections' IS NOT NULL)
      AND jsonb_typeof(contents) = 'object' -- Ensure contents is a JSON object
      AND contents <> '{}' -- Check if contents is not an empty JSON object;
    """

    sql = sa.text(query)
    rows = connection.execute(sql)

    for row in rows:
        # Revert the "control_assessment_selections" items to their original structure
        for item in row.contents.get("control_assessment_selections") or []:
            item["control_ids"] = [
                control_selection["id"]
                for control_selection in item.get("control_selections", [])
            ]
            item["control_selections"] = None

        # Update the "task_selections" field in the "contents" JSON with the orginal structure
        for item in row.contents.get("task_selections") or []:
            item.pop("recommended", None)
            item.pop("selected", None)

        # Update the row with the modified JSON data
        connection.execute(
            sa.text("UPDATE public.jsbs SET contents = :new_contents WHERE id = :id"),
            {"new_contents": json.dumps(row.contents), "id": row.id},
        )
