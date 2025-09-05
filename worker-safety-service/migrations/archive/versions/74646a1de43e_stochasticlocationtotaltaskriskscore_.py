"""StochasticLocationTotalTaskRiskScore config

Revision ID: 74646a1de43e
Revises: 68d994a7a81d
Create Date: 2022-10-12 18:36:24.924740

"""
import json
import uuid

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "74646a1de43e"
down_revision = "68d994a7a81d"
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
            "name": "RISK_MODEL.ACTIVITY_TOTAL_TASK_RISK_SCORE_METRIC_CLASS",
            "value": json.dumps(None),
        },
    )


def downgrade():
    op.execute(
        "DELETE FROM public.configurations WHERE name = 'RISK_MODEL.ACTIVITY_TOTAL_TASK_RISK_SCORE_METRIC_CLASS'"
    )
