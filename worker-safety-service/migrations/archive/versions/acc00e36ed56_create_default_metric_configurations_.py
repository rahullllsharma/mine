"""Create default metric configurations for ranked metrics

Revision ID: acc00e36ed56
Revises: 246e1a537082
Create Date: 2022-10-06 12:36:17.263241

"""
import json
import uuid

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
from sqlalchemy import text

revision = "acc00e36ed56"
down_revision = "246e1a537082"
branch_labels = None
depends_on = None

labels = [
    "RISK_MODEL.TOTAL_PROJECT_RISK_SCORE_METRIC_CLASS",
    "RISK_MODEL.TOTAL_PROJECT_LOCATION_RISK_SCORE_METRIC_CLASS",
    "RISK_MODEL.PROJECT_TOTAL_TASK_RISK_SCORE_METRIC_CLASS",
    "RISK_MODEL.PROJECT_LOCATION_TOTAL_TASK_RISK_SCORE_METRIC_CLASS",
    "RISK_MODEL.TASK_SPECIFIC_RISK_SCORE_METRIC_CLASS",
]
value = "RULE_BASED_ENGINE"


def upgrade():
    conn = op.get_bind()
    for label in labels:
        conn.execute(
            sa.text(
                "INSERT INTO public.configurations(id, name, tenant_id, value) VALUES (:id, :name, null, :value);"
            ),
            {
                "id": uuid.uuid4(),
                "name": label,
                "value": json.dumps(value),
            },
        )


def downgrade():
    conn = op.get_bind()
    for label in labels:
        conn.execute(
            text(
                "DELETE FROM public.configurations WHERE name = :name and tenant_id is NULL;"
            ),
            {
                "name": label,
            },
        )
