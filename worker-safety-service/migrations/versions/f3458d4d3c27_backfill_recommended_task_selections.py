"""backfill recommended_task_selections

Revision ID: f3458d4d3c27
Revises: fe708de1addc
Create Date: 2024-12-03 16:47:13.470328

"""
import json

import sqlalchemy as sa
from alembic import op

from worker_safety_service.models import RiskLevel

# revision identifiers, used by Alembic.
revision = "f3458d4d3c27"
down_revision = "fe708de1addc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Backfill the data for all rows in the "jsbs" table with the new structure.
    connection = op.get_bind()

    query = """
    SELECT id, contents
    FROM public.jsbs
    WHERE
      (contents->'control_assessment_selections' IS NOT NULL
       OR contents->'task_selections' IS NOT NULL)
      AND contents->'recommended_task_selections' IS NULL -- Skip if recommended_task_selections already present
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
                    {"id": id, "recommended": None, "selected": True}
                    for id in item.get("control_ids")
                ]

        # Skip rows where both task_selections and recommended_task_selections are present
        if (
            "task_selections" in row.contents
            and "recommended_task_selections" in row.contents
        ):
            continue

        # Backfill "recommended_task_selections" based on "task_selections"
        recommended_task_selections = []
        for task in row.contents.get("task_selections") or []:
            recommended_task_selections.append(
                {
                    "id": task.get("id"),
                    "name": task.get("name", None),
                    "risk_level": task.get(
                        "risk_level",
                        RiskLevel.UNKNOWN,
                    ),
                    "from_work_order": task.get("from_work_order", None),
                    "selected": True,
                    "recommended": None,
                }
            )

        # Update the "recommended_task_selections" field in the JSON
        row.contents["recommended_task_selections"] = recommended_task_selections

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

    # Fetch rows where "control_assessment_selections" or "recommended_task_selections" is not null
    query = """
    SELECT id, contents
    FROM public.jsbs
    WHERE
      (contents->'control_assessment_selections' IS NOT NULL
       OR contents->'recommended_task_selections' IS NOT NULL)
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

        # Remove the "recommended_task_selections" field
        row.contents.pop("recommended_task_selections", None)

        # Update the "task_selections" field in the "contents" JSON to the original structure
        for item in row.contents.get("task_selections") or []:
            item.pop("recommended", None)
            item.pop("selected", None)

        # Update the row with the modified JSON data
        connection.execute(
            sa.text("UPDATE public.jsbs SET contents = :new_contents WHERE id = :id"),
            {"new_contents": json.dumps(row.contents), "id": row.id},
        )
