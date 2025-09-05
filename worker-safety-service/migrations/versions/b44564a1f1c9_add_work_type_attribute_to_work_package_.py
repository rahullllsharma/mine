"""add work type attribute to work package config

Revision ID: b44564a1f1c9
Revises: a1282016fd0c
Create Date: 2025-06-06 14:28:53.553534

"""

import json

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "b44564a1f1c9"
down_revision = "a1282016fd0c"
branch_labels = None
depends_on = None


WORK_PACKAGE_ATTRIBUTES_CONFIG_NAME = "APP.WORK_PACKAGE.ATTRIBUTES"

work_types_attribute_config = {
    "key": "workTypes",
    "label": "Work Types",
    "labelPlural": "Work Types",
    "visible": True,
    "required": True,
    "filterable": True,
    "mappings": None,
}


def upgrade() -> None:
    """Add workTypes attribute to existing work package configurations for all tenants"""
    conn = op.get_bind()

    # Update the default configuration (tenant_id IS NULL) which applies to all tenants
    for config in conn.execute(
        text(
            f"SELECT id, name, tenant_id, value FROM public.configurations WHERE name = '{WORK_PACKAGE_ATTRIBUTES_CONFIG_NAME}' AND tenant_id IS NULL"
        )
    ):
        config_value = json.loads(config.value)

        # Check if workTypes attribute already exists
        existing_work_types = any(
            attr.get("key") == "workTypes"
            for attr in config_value.get("attributes", [])
        )

        if not existing_work_types:
            config_value["attributes"].append(work_types_attribute_config)

            conn.execute(
                text(
                    "UPDATE public.configurations SET value = :config_value WHERE id = :config_id"
                ),
                {"config_value": json.dumps(config_value), "config_id": config.id},
            )

    # Also update any tenant-specific configurations that might already exist
    for config in conn.execute(
        text(
            f"SELECT id, name, tenant_id, value FROM public.configurations WHERE name = '{WORK_PACKAGE_ATTRIBUTES_CONFIG_NAME}' AND tenant_id IS NOT NULL"
        )
    ):
        config_value = json.loads(config.value)

        # Check if workTypes attribute already exists
        existing_work_types = any(
            attr.get("key") == "workTypes"
            for attr in config_value.get("attributes", [])
        )

        if not existing_work_types:
            config_value["attributes"].append(work_types_attribute_config)

            conn.execute(
                text(
                    "UPDATE public.configurations SET value = :config_value WHERE id = :config_id"
                ),
                {"config_value": json.dumps(config_value), "config_id": config.id},
            )


def downgrade() -> None:
    """Remove workTypes attribute from work package configurations for all tenants"""
    conn = op.get_bind()

    # Remove from default configuration (tenant_id IS NULL)
    for config in conn.execute(
        text(
            f"SELECT id, name, tenant_id, value FROM public.configurations WHERE name = '{WORK_PACKAGE_ATTRIBUTES_CONFIG_NAME}' AND tenant_id IS NULL"
        )
    ):
        config_value = json.loads(config.value)
        config_value["attributes"] = [
            attr
            for attr in config_value.get("attributes", [])
            if attr.get("key") != "workTypes"
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
            f"SELECT id, name, tenant_id, value FROM public.configurations WHERE name = '{WORK_PACKAGE_ATTRIBUTES_CONFIG_NAME}' AND tenant_id IS NOT NULL"
        )
    ):
        config_value = json.loads(config.value)
        config_value["attributes"] = [
            attr
            for attr in config_value.get("attributes", [])
            if attr.get("key") != "workTypes"
        ]

        conn.execute(
            text(
                "UPDATE public.configurations SET value = :config_value WHERE id = :config_id"
            ),
            {"config_value": json.dumps(config_value), "config_id": config.id},
        )
