"""jsb recommeded selections revert

Revision ID: e47da3706b1f
Revises: 3fab9d535707
Create Date: 2024-11-19 11:18:44.029556

"""

import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e47da3706b1f"
down_revision = "3fab9d535707"
branch_labels = None
depends_on = None


def upgrade() -> None:
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

    for index, row in enumerate(rows):
        print(f"{index}:jsb_id = {row.id}")
        # Revert the "control_assessment_selections" items to their original structure
        for item in row.contents.get("control_assessment_selections") or []:
            if "control_selections" in item:
                print("item ==", item.get("control_selections"))
                del item["control_selections"]

        # Update the "task_selections" field in the "contents" JSON with the orginal structure
        for item in row.contents.get("task_selections") or []:
            item.pop("recommended", None)
            item.pop("selected", None)

        # Update the row with the modified JSON data
        connection.execute(
            sa.text("UPDATE public.jsbs SET contents = :new_contents WHERE id = :id"),
            {"new_contents": json.dumps(row.contents), "id": row.id},
        )


def downgrade() -> None:
    pass
