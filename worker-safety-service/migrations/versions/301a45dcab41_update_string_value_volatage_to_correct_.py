"""update_string_value_volatage_to_correct_value

Revision ID: 301a45dcab41
Revises: 8da266178d72
Create Date: 2024-04-22 10:45:22.718997

"""
import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "301a45dcab41"
down_revision = "8da266178d72"
branch_labels = None
depends_on = None


def upgrade() -> None:
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
                    if "value" in voltage and voltage["value"].endswith(".0"):
                        voltage["value"] = voltage["value"][:-2]
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


def downgrade() -> None:
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
                    if "value" in voltage:
                        # Convert value to float
                        float_value = float(voltage["value"])
                        # Check if the value is an integer (whole number)
                        if float_value.is_integer():
                            # Add ".0" suffix to whole numbers
                            voltage["value"] += ".0"

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
