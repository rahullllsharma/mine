"""Supervisor relation precusor config

Revision ID: 672c8c97558a
Revises: 1ea0af372706
Create Date: 2022-09-22 16:45:52.855643

"""
import json
import uuid

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "672c8c97558a"
down_revision = "1ea0af372706"
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
            "name": "RISK_MODEL.SUPERVISOR_METRIC_CLASS",
            "value": json.dumps("SupervisorEngagementFactor"),
        },
    )


def downgrade():
    op.execute(
        "DELETE FROM public.configurations WHERE name = 'RISK_MODEL.SUPERVISOR_METRIC_CLASS'"
    )
