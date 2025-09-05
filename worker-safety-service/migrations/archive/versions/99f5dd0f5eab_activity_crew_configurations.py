"""Activity crew configurations

Revision ID: 99f5dd0f5eab
Revises: 8fb67d09065f
Create Date: 2022-09-30 15:27:15.671236

"""
import json

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "99f5dd0f5eab"
down_revision = "8fb67d09065f"
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
                            "key": "crew",
                            "label": "Crew",
                            "labelPlural": "Crews",
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
