"""update_form_configuration

Revision ID: 242a74cd0768
Revises: c6ecf3815922
Create Date: 2023-11-14 23:09:18.943545

"""
import json

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "242a74cd0768"
down_revision = "46a64fb28319"
branch_labels = None
depends_on = None


FORMS_ATTRIBUTES_CONFIG_NAME = "APP.FORM_LIST.ATTRIBUTES"

forms_updated_fields_config = [
    {
        "key": "updatedBy",
        "label": "Updated By",
        "labelPlural": "Updated By",
        "visible": False,
        "required": False,
        "filterable": False,
        "mappings": None,
    },
    {
        "key": "updatedOn",
        "label": "Updated On",
        "labelPlural": "Updated On",
        "visible": False,
        "required": False,
        "filterable": False,
        "mappings": None,
    },
]


def upgrade():
    conn = op.get_bind()

    for config in conn.execute(
        text(
            f"SELECT id, name, tenant_id, value FROM public.configurations WHERE name = '{FORMS_ATTRIBUTES_CONFIG_NAME}'"
        )
    ):
        config_value = json.loads(config.value)
        config_value["attributes"].extend(forms_updated_fields_config)
        op.get_bind().execute(
            text(
                f"UPDATE public.configurations SET value = '{json.dumps(config_value)}' WHERE id = '{config.id}' "
            )
        )


def downgrade():
    conn = op.get_bind()

    for config in conn.execute(
        text(
            f"SELECT id, name, tenant_id, value FROM public.configurations WHERE name = '{FORMS_ATTRIBUTES_CONFIG_NAME}'"
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
