"""fixing spelling mistake in configuration of FormList

Revision ID: 78a404d5ccb8
Revises: fe5ef03dbf05
Create Date: 2024-11-29 00:26:50.875065

"""
import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "78a404d5ccb8"
down_revision = "fe5ef03dbf05"
branch_labels = None
depends_on = None


FORMS_ATTRIBUTES_CONFIG_NAME = "APP.FORM_LIST.ATTRIBUTES"

new_attribute = {
    "key": "supervisor",
    "label": "Supervisor",
    "labelPlural": "Supervisors",
    "visible": False,
    "required": False,
    "filterable": False,
    "mappings": None,
}


def upgrade() -> None:
    conn = op.get_bind()

    result = conn.execute(
        sa.text("SELECT id, name, value FROM configurations WHERE name = :name"),
        {"name": FORMS_ATTRIBUTES_CONFIG_NAME},
    )

    for row in result:
        current_value = json.loads(row["value"])

        attributes = current_value.get("attributes", [])

        if not any(attr.get("key") == "supervisor" for attr in attributes):
            attributes.append(new_attribute)

        current_value["attributes"] = attributes

        conn.execute(
            sa.text("UPDATE configurations SET value = :value WHERE id = :id"),
            {"value": json.dumps(current_value), "id": row["id"]},
        )


def downgrade() -> None:
    conn = op.get_bind()

    result = conn.execute(
        sa.text("SELECT id, name, value FROM configurations WHERE name = :name"),
        {"name": FORMS_ATTRIBUTES_CONFIG_NAME},
    )

    for row in result:
        current_value = json.loads(row["value"])

        attributes = current_value.get("attributes", [])

        current_value["attributes"] = [
            attr for attr in attributes if attr.get("key") != "supervisor"
        ]

        conn.execute(
            sa.text("UPDATE configurations SET value = :value WHERE id = :id"),
            {"value": json.dumps(current_value), "id": row["id"]},
        )
