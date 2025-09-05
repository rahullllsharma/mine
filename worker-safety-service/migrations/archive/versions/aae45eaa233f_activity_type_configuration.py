"""Activity type configuration

Revision ID: aae45eaa233f
Revises: b10fd24dec56
Create Date: 2022-10-27 19:23:26.348949

"""
import json

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "aae45eaa233f"
down_revision = "b10fd24dec56"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(
        text("UPDATE public.configurations SET value = :value WHERE name = :name"),
        {
            "name": "APP.ACTIVITY.ATTRIBUTES",
            "value": json.dumps(
                {
                    "attributes": [
                        {
                            "key": "name",
                            "label": "Activity Name",
                            "labelPlural": "Activity Names",
                            "visible": True,
                            "required": True,
                            "filterable": True,
                            "mappings": None,
                        },
                        {
                            "key": "startDate",
                            "label": "Start Date",
                            "labelPlural": "Start Dates",
                            "visible": True,
                            "required": True,
                            "filterable": False,
                            "mappings": None,
                        },
                        {
                            "key": "endDate",
                            "label": "End Date",
                            "labelPlural": "End Dates",
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
                            "mappings": {
                                "not_started": ["Not started"],
                                "in_progress": ["In progress"],
                                "complete": ["Complete"],
                                "not_completed": ["Not completed"],
                            },
                        },
                        {
                            "key": "crew",
                            "label": "Crew",
                            "labelPlural": "Crews",
                            "visible": False,
                            "required": False,
                            "filterable": False,
                            "mappings": None,
                        },
                        {
                            "key": "libraryActivityType",
                            "label": "Activity type",
                            "labelPlural": "Activity types",
                            "visible": False,
                            "required": False,
                            "filterable": False,
                            "mappings": None,
                        },
                    ]
                }
            ),
        },
    )


def downgrade():
    pass
