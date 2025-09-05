"""add formId in forms_configuration

Revision ID: 33d9764e6f34
Revises: 2dc9254cc26e
Create Date: 2024-07-09 12:28:24.054080

"""
import json

import sqlalchemy as sa
from alembic import op

revision = "33d9764e6f34"
down_revision = "2dc9254cc26e"
branch_labels = None
depends_on = None

FORMS_ATTRIBUTES_CONFIG_NAME = "APP.FORM_LIST.ATTRIBUTES"

new_attribute = {
    "key": "formId",
    "label": "Form Id",
    "labelPlural": "Form Ids",
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

        if not any(attr.get("key") == "formId" for attr in attributes):
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
            attr for attr in attributes if attr.get("key") != "formId"
        ]

        conn.execute(
            sa.text("UPDATE configurations SET value = :value WHERE id = :id"),
            {"value": json.dumps(current_value), "id": row["id"]},
        )
