"""add attribute supervisor for template form

Revision ID: 0c8ee09a52ae
Revises: 27139fc98cde
Create Date: 2025-06-23 11:51:44.666600

"""

import json

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "0c8ee09a52ae"
down_revision = "27139fc98cde"
branch_labels = None
depends_on = None


ATTRIBUTES_CONFIG_NAME = "APP.TEMPLATE_FORM.ATTRIBUTES"

attribute_config_dict = {
    "key": "supervisor",
    "label": "Supervisor",
    "labelPlural": "Supervisors",
    "visible": False,
    "required": False,
    "filterable": False,
    "mappings": None,
}

attribute_key = "supervisor"


def upgrade() -> None:
    """Add supervisor attribute to existing template form configurations for all tenants"""
    conn = op.get_bind()

    # Update the default configuration (tenant_id IS NULL) which applies to all tenants
    for config in conn.execute(
        text(
            f"SELECT id, name, tenant_id, value FROM public.configurations WHERE name = '{ATTRIBUTES_CONFIG_NAME}' AND tenant_id IS NULL"
        )
    ):
        config_value = json.loads(config.value)

        # Check if supervisor attribute already exists
        existing_superviors = any(
            attr.get("key") == attribute_key
            for attr in config_value.get("attributes", [])
        )

        if not existing_superviors:
            config_value["attributes"].append(attribute_config_dict)

            conn.execute(
                text(
                    "UPDATE public.configurations SET value = :config_value WHERE id = :config_id"
                ),
                {"config_value": json.dumps(config_value), "config_id": config.id},
            )

    # Also update any tenant-specific configurations that might already exist
    for config in conn.execute(
        text(
            f"SELECT id, name, tenant_id, value FROM public.configurations WHERE name = '{ATTRIBUTES_CONFIG_NAME}' AND tenant_id IS NOT NULL"
        )
    ):
        config_value = json.loads(config.value)

        # Check if workTypes attribute already exists
        existing_supervisor = any(
            attr.get("key") == attribute_key
            for attr in config_value.get("attributes", [])
        )

        if not existing_supervisor:
            config_value["attributes"].append(attribute_config_dict)

            conn.execute(
                text(
                    "UPDATE public.configurations SET value = :config_value WHERE id = :config_id"
                ),
                {"config_value": json.dumps(config_value), "config_id": config.id},
            )


def downgrade() -> None:
    """Remove supervisor attribute from template form configurations for all tenants"""
    conn = op.get_bind()

    # Remove from default configuration (tenant_id IS NULL)
    for config in conn.execute(
        text(
            f"SELECT id, name, tenant_id, value FROM public.configurations WHERE name = '{ATTRIBUTES_CONFIG_NAME}' AND tenant_id IS NULL"
        )
    ):
        config_value = json.loads(config.value)
        config_value["attributes"] = [
            attr
            for attr in config_value.get("attributes", [])
            if attr.get("key") != attribute_key
        ]

        conn.execute(
            text(
                "UPDATE public.configurations SET value = :config_value WHERE id = :config_id"
            ),
            {"config_value": json.dumps(config_value), "config_id": config.id},
        )

    # Remove from any tenant-specific configurations
    for config in conn.execute(
        text(
            f"SELECT id, name, tenant_id, value FROM public.configurations WHERE name = '{ATTRIBUTES_CONFIG_NAME}' AND tenant_id IS NOT NULL"
        )
    ):
        config_value = json.loads(config.value)
        config_value["attributes"] = [
            attr
            for attr in config_value.get("attributes", [])
            if attr.get("key") != attribute_key
        ]

        conn.execute(
            text(
                "UPDATE public.configurations SET value = :config_value WHERE id = :config_id"
            ),
            {"config_value": json.dumps(config_value), "config_id": config.id},
        )
