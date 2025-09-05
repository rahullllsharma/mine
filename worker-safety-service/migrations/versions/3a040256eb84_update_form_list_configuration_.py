"""update_form_list_configuration_attributes

Revision ID: 3a040256eb84
Revises: 2e9cf52704e6
Create Date: 2024-04-16 19:41:08.855033

"""

import json

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "3a040256eb84"
down_revision = "2e9cf52704e6"
branch_labels = None
depends_on = None


FORM_LIST_ATTRIBUTES_CONFIG_NAME = "APP.FORM_LIST.ATTRIBUTES"

form_list_updated_fields_config = [
    {
        "key": "completedOn",
        "label": "Completed On",
        "labelPlural": "Completed On",
        "visible": False,
        "required": False,
        "filterable": False,
        "mappings": None,
    },
    {
        "key": "date",
        "label": "Report Date",
        "labelPlural": "Report Date",
        "visible": False,
        "required": False,
        "filterable": False,
        "mappings": None,
    },
]


def upgrade() -> None:
    conn = op.get_bind()

    for config in conn.execute(
        text(
            f"SELECT id, value FROM public.configurations WHERE name = '{FORM_LIST_ATTRIBUTES_CONFIG_NAME}'"
        )
    ):
        config_value = json.loads(config.value)
        config_value["attributes"].extend(form_list_updated_fields_config)
        op.get_bind().execute(
            text(
                f"UPDATE public.configurations SET value = '{json.dumps(config_value)}' WHERE id = '{config.id}'"
            )
        )


def downgrade() -> None:
    conn = op.get_bind()

    for config in conn.execute(
        text(
            f"SELECT id, value FROM public.configurations WHERE name = '{FORM_LIST_ATTRIBUTES_CONFIG_NAME}'"
        )
    ):
        config_value = json.loads(config.value)
        config_value["attributes"] = list(
            filter(
                lambda attribute: attribute["key"] not in ["completedOn", "date"],
                config_value["attributes"],
            )
        )
        op.get_bind().execute(
            text(
                f"UPDATE public.configurations SET value = '{json.dumps(config_value)}' WHERE id = '{config.id}'"
            )
        )
