"""update activity configuration attributes

Revision ID: 9c02983e5c8a
Revises: 937444637855
Create Date: 2024-02-06 12:47:26.822150

"""

import json

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "9c02983e5c8a"
down_revision = "937444637855"
branch_labels = None
depends_on = None


ACTIVITY_ATTRIBUTES_CONFIG_NAME = "APP.ACTIVITY.ATTRIBUTES"

activity_updated_fields_config = [
    {
        "key": "criticalActivity",
        "label": "Critical Activity",
        "labelPlural": "Critical Activity",
        "visible": False,
        "required": False,
        "filterable": False,
        "mappings": None,
    }
]


def upgrade() -> None:
    conn = op.get_bind()

    for config in conn.execute(
        text(
            f"SELECT id, name, tenant_id, value FROM public.configurations WHERE name = '{ACTIVITY_ATTRIBUTES_CONFIG_NAME}'"
        )
    ):
        config_value = json.loads(config.value)
        config_value["attributes"].extend(activity_updated_fields_config)
        op.get_bind().execute(
            text(
                f"UPDATE public.configurations SET value = '{json.dumps(config_value)}' WHERE id = '{config.id}' "
            )
        )


def downgrade() -> None:
    conn = op.get_bind()

    for config in conn.execute(
        text(
            f"SELECT id, name, tenant_id, value FROM public.configurations WHERE name = '{ACTIVITY_ATTRIBUTES_CONFIG_NAME}'"
        )
    ):
        config_value = json.loads(config.value)
        config_value["attributes"] = list(
            filter(
                lambda attribute: attribute["key"] not in ["updatedOn", "updatedBy"],
                config_value["attributes"],
            )
        )
        op.get_bind().execute(
            text(
                f"UPDATE public.configurations SET value = '{json.dumps(config_value)}' WHERE id = '{config.id}' "
            )
        )
