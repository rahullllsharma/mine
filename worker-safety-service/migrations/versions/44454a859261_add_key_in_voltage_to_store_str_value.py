"""add key in voltage to store str value

Revision ID: 44454a859261
Revises: 301a45dcab41
Create Date: 2024-05-03 02:28:06.849619

"""
import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "44454a859261"
down_revision = "301a45dcab41"
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
        contents = row["contents"]  # Assuming this is already a dictionary
        if contents and "energy_source_control" in contents:
            energy_source_control = contents["energy_source_control"]
            if energy_source_control and "voltages" in energy_source_control:
                for voltage in energy_source_control["voltages"]:
                    # Copy existing value to value_str
                    voltage["value_str"] = voltage.get("value", "")

                    # Update value to be a float or 0 if not convertible
                    if "value" in voltage:
                        if isinstance(voltage["value"], str) and is_floatable(
                            voltage["value"]
                        ):
                            voltage["value"] = float(voltage["value"])
                        else:
                            voltage["value"] = 0

                # Serialize the modified contents back to a string (if needed)
                updated_contents = row[
                    "contents"
                ]  # Assuming direct modification is reflected
                if isinstance(updated_contents, dict):
                    updated_contents = json.dumps(updated_contents)

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
    connection = op.get_bind()
    query = """
    SELECT id, contents
    FROM public.jsbs
    WHERE contents IS NOT NULL;
    """
    result = connection.execute(sa.text(query))
    for row in result:
        contents = row["contents"]  # Assuming this is already a dictionary
        if contents and "energy_source_control" in contents:
            energy_source_control = contents["energy_source_control"]
            if energy_source_control and "voltages" in energy_source_control:
                for voltage in energy_source_control["voltages"]:
                    if "value_str" in voltage:
                        # Here, we decide not to revert 'value' changes because original string might have been lost
                        # Remove the value_str key
                        del voltage["value_str"]

                # Serialize the modified contents back to a string
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
