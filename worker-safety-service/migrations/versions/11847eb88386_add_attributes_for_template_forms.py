"""Add attributes for Template Forms

Revision ID: 11847eb88386
Revises: ac43ac9c07b3
Create Date: 2025-05-26 13:56:32.157498

"""

import json
from typing import Any, Dict

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "11847eb88386"
down_revision = "8f800c7f8aab"
branch_labels = None
depends_on = None

template_form_attributes = {
    "attributes": [
        {
            "key": "formName",
            "label": "Form Name",
            "labelPlural": "Form Names",
            "visible": False,
            "required": False,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "status",
            "label": "Status",
            "labelPlural": "Statuses",
            "visible": False,
            "required": False,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "createdBy",
            "label": "Created By",
            "labelPlural": "Created By",
            "visible": False,
            "required": False,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "createdOn",
            "label": "Created On",
            "labelPlural": "Created On",
            "visible": False,
            "required": False,
            "filterable": False,
            "mappings": None,
        },
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
            "key": "Project",
            "label": "Project",
            "labelPlural": "Projects",
            "visible": False,
            "required": False,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "location",
            "label": "Location",
            "labelPlural": "Locations",
            "visible": False,
            "required": False,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "region",
            "label": "Region",
            "labelPlural": "Regions",
            "visible": False,
            "required": False,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "reportDate",
            "label": "Report Date",
            "labelPlural": "Report Dates",
            "visible": False,
            "required": False,
            "filterable": False,
            "mappings": None,
        },
    ]
}

old_value: Dict[str, Any] = {"attributes": []}


def upgrade() -> None:
    conn = op.get_bind()
    update_query = text(
        """
        UPDATE public.configurations
        SET value = :value
        WHERE name = 'APP.TEMPLATE_FORM.ATTRIBUTES' AND tenant_id IS NULL
    """
    )
    conn.execute(update_query, {"value": json.dumps(template_form_attributes)})


def downgrade() -> None:
    conn = op.get_bind()
    update_query = text(
        """
        UPDATE public.configurations
        SET value = :value
        WHERE name = 'APP.TEMPLATE_FORM.ATTRIBUTES' AND tenant_id IS NULL
    """
    )
    conn.execute(update_query, {"value": json.dumps(old_value)})
