"""revert primary voltage str changes

Revision ID: f49079be7db1
Revises: 2d650ff48c18
Create Date: 2024-04-03 16:51:31.383091

"""
import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f49079be7db1"
down_revision = "2d650ff48c18"
branch_labels = None
depends_on = None


def is_floatable(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def upgrade():
    connection = op.get_bind()
    query = """
    SELECT id, contents
    FROM public.jsbs
    WHERE contents IS NOT NULL;
    """
    result = connection.execute(sa.text(query))
    for row in result:
        contents = row["contents"]
        if contents and "energy_source_control" in contents:
            energy_source_control = contents["energy_source_control"]
            if energy_source_control and "voltages" in energy_source_control:
                for voltage in energy_source_control["voltages"]:
                    if (
                        "value" in voltage
                        and isinstance(voltage["value"], str)
                        and is_floatable(voltage["value"])
                    ):
                        voltage["value"] = float(voltage["value"])
                updated_contents = json.dumps(contents)
                update_query = """
                UPDATE public.jsbs
                SET contents = :contents
                WHERE id = :id;
                """
                connection.execute(
                    sa.text(update_query),
                    {"id": row["id"], "contents": updated_contents},
                )


def downgrade():
    pass
