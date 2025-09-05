"""Create TotalActivityRiskScoreDefault Config

Revision ID: b6f903208edd
Revises: 4e55e95cd288
Create Date: 2022-10-13 17:17:49.171279

"""
import json
import uuid

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b6f903208edd"
down_revision = "4e55e95cd288"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "INSERT INTO public.configurations(id, name, tenant_id, value) VALUES (:id, :name, null, :value);"
        ),
        {
            "id": uuid.uuid4(),
            "name": "RISK_MODEL.TOTAL_ACTIVITY_RISK_SCORE_METRIC_CLASS",
            "value": json.dumps(None),
        },
    )


def downgrade():
    op.execute(
        "DELETE FROM public.configurations WHERE name = 'RISK_MODEL.TOTAL_ACTIVITY_RISK_SCORE_METRIC_CLASS'"
    )
