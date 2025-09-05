"""add_operating_hq_in_forms_configuration.py

Revision ID: 7173f34db919
Revises: 580677c98efc
Create Date: 2024-07-01 13:33:23.522758

"""
import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7173f34db919"
down_revision = "580677c98efc"
branch_labels = None
depends_on = None


FORMS_ATTRIBUTES_CONFIG_NAME = "APP.FORM_LIST.ATTRIBUTES"

forms_updated_fields_config = [
    {
        "key": "operatingHQ",
        "label": "Operating HQ",
        "labelPlural": "Operating HQ",
        "visible": False,
        "required": False,
        "filterable": False,
        "mappings": None,
    },
]


def upgrade():
    conn = op.get_bind()

    for config in conn.execute(
        sa.text(
            f"SELECT id, name, tenant_id, value FROM public.configurations WHERE name = '{FORMS_ATTRIBUTES_CONFIG_NAME}'"
        )
    ):
        config_value = json.loads(config.value)
        config_value["attributes"].extend(forms_updated_fields_config)
        op.get_bind().execute(
            sa.text(
                f"UPDATE public.configurations SET value = '{json.dumps(config_value)}' WHERE id = '{config.id}'"
            )
        )


def downgrade():
    conn = op.get_bind()

    for config in conn.execute(
        sa.text(
            f"SELECT id, name, tenant_id, value FROM public.configurations WHERE name = '{FORMS_ATTRIBUTES_CONFIG_NAME}'"
        )
    ):
        config_value = json.loads(config.value)
        config_value["attributes"] = list(
            filter(
                lambda attribute: attribute["key"] == "operatingHQ",
                config_value["attributes"],
            )
        )
        op.get_bind().execute(
            sa.text(
                f"UPDATE public.configurations SET value = '{json.dumps(config_value)}' WHERE id = '{config.id}'"
            )
        )
