"""Fix migrations for all tenants and setting some columns value as true

Revision ID: a1282016fd0c
Revises: 11847eb88386
Create Date: 2025-06-04 16:52:25.291507

"""

import json
from typing import Any, Dict

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "a1282016fd0c"
down_revision = "11847eb88386"
branch_labels = None
depends_on = None

template_form_attributes = {
    "attributes": [
        {
            "key": "formName",
            "label": "Form Name",
            "labelPlural": "Form Names",
            "visible": True,
            "required": True,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "status",
            "label": "Status",
            "labelPlural": "Statuses",
            "visible": True,
            "required": True,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "createdBy",
            "label": "Created By",
            "labelPlural": "Created By",
            "visible": True,
            "required": True,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "createdOn",
            "label": "Created On",
            "labelPlural": "Created On",
            "visible": True,
            "required": True,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "updatedBy",
            "label": "Updated By",
            "labelPlural": "Updated By",
            "visible": True,
            "required": True,
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
            "visible": True,
            "required": True,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "Project",
            "label": "Project",
            "labelPlural": "Projects",
            "visible": True,
            "required": True,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "location",
            "label": "Location",
            "labelPlural": "Locations",
            "visible": True,
            "required": True,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "region",
            "label": "Region",
            "labelPlural": "Regions",
            "visible": True,
            "required": True,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "reportDate",
            "label": "Report Date",
            "labelPlural": "Report Dates",
            "visible": True,
            "required": True,
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
        WHERE name = 'APP.TEMPLATE_FORM.ATTRIBUTES'
    """
    )
    conn.execute(update_query, {"value": json.dumps(template_form_attributes)})


def downgrade() -> None:
    conn = op.get_bind()
    update_query = text(
        """
        UPDATE public.configurations
        SET value = :value
        WHERE name = 'APP.TEMPLATE_FORM.ATTRIBUTES'
    """
    )
    conn.execute(update_query, {"value": json.dumps(old_value)})
