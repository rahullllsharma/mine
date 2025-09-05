"""change voltage value from float to str

Revision ID: 2d650ff48c18
Revises: 50382a11f48d
Create Date: 2024-04-01 15:12:29.217256

"""
import json

import sqlalchemy as sa
from alembic import op

revision = "2d650ff48c18"
down_revision = "50382a11f48d"
branch_labels = None
depends_on = None


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
        # Check if contents is not None
        if contents and "energy_source_control" in contents:
            energy_source_control = contents["energy_source_control"]
            # Check if energy_source_control is not None and contains 'voltages'
            if energy_source_control and "voltages" in energy_source_control:
                for voltage in energy_source_control["voltages"]:
                    # Ensure 'value' exists and is a float or int before converting
                    if "value" in voltage and isinstance(
                        voltage["value"], (float, int)
                    ):
                        voltage["value"] = str(voltage["value"])
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


def is_floatable(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def downgrade():
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
