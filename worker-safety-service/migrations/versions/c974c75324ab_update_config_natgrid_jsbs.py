"""update_config_natgrid_jsbs

Revision ID: c974c75324ab
Revises: 9698cecd5c9c
Create Date: 2024-08-02 14:08:40.339226

"""
import json

import sqlalchemy as sa
from alembic import op

revision = "c974c75324ab"
down_revision = "9698cecd5c9c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Update query to add bool field to energy_source_control where form_type is 'natgrid_job_safety_briefing'
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT id, contents FROM uiconfigs WHERE form_type = 'natgrid_job_safety_briefing'"
        )
    )
    for row in result:
        contents = row["contents"]
        if "energy_source_control" in contents:
            for item in contents["energy_source_control"]:
                if item["name"] in ["Reclosers", "Switching Limits"]:
                    item[
                        "description_allowed"
                    ] = True  # Set to True for Reclosers and Switching Limits
                else:
                    item[
                        "description_allowed"
                    ] = False  # Set to False for all other cases
            conn.execute(
                sa.text("UPDATE uiconfigs SET contents = :contents WHERE id = :id"),
                {"contents": json.dumps(contents), "id": row["id"]},
            )


def downgrade() -> None:
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT id, contents FROM uiconfigs WHERE form_type = 'natgrid_job_safety_briefing'"
        )
    )
    for row in result:
        contents = row["contents"]
        if "energy_source_control" in contents:
            for item in contents["energy_source_control"]:
                if "description_allowed" in item:
                    del item["description_allowed"]
            conn.execute(
                sa.text("UPDATE uiconfigs SET contents = :contents WHERE id = :id"),
                {"contents": json.dumps(contents), "id": row["id"]},
            )
