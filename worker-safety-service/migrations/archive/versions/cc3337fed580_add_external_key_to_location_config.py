"""add external key to location config

Revision ID: cc3337fed580
Revises: 997bec38bb0b
Create Date: 2022-12-05 14:53:16.530149

"""
import json

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "cc3337fed580"
down_revision = "12673078d1fd"
branch_labels = None
depends_on = None

LOCATION_CONFIG_NAME = "APP.LOCATION.ATTRIBUTES"
location_external_key_config = {
    "key": "externalKey",
    "label": "External Reference ID",
    "labelPlural": "External Reference IDs",
    "visible": False,
    "required": False,
    "filterable": False,
    "mappings": None,
}


def upgrade():
    for config in op.get_bind().execute(
        text(
            f"SELECT id, name, tenant_id, value FROM public.configurations WHERE name = '{LOCATION_CONFIG_NAME}'"
        )
    ):
        config_value = json.loads(config.value)
        config_value["attributes"].append(location_external_key_config)
        op.get_bind().execute(
            text(
                f"UPDATE public.configurations SET value = '{json.dumps(config_value)}' WHERE id = '{config.id}' "
            )
        )


def downgrade():
    for config in op.get_bind().execute(
        text(
            f"SELECT id, name, tenant_id, value FROM public.configurations WHERE name = '{LOCATION_CONFIG_NAME}'"
        )
    ):
        config_value = json.loads(config.value)
        config_value["attributes"] = list(
            filter(
                lambda attribute: attribute["key"] != "externalKey",
                config_value["attributes"],
            )
        )
        op.get_bind().execute(
            text(
                f"UPDATE public.configurations SET value = '{json.dumps(config_value)}' WHERE id = '{config.id}' "
            )
        )
