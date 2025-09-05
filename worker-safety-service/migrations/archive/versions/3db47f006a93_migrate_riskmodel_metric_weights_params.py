"""Migrate RiskModel Metric Weights params

Revision ID: 3db47f006a93
Revises: acc00e36ed56
Create Date: 2022-10-06 22:34:49.271423

"""
import json
import uuid

from alembic import op

# revision identifiers, used by Alembic.
from sqlalchemy import text

revision = "3db47f006a93"
down_revision = "acc00e36ed56"
branch_labels = None
depends_on = None

weight_labels = [
    (
        "total_project_risk_score_weight",
        "RISK_MODEL.TOTAL_PROJECT_RISK_SCORE_METRIC_CLASS.WEIGHTS",
    ),
    (
        "total_task_risk_score_weight",
        "RISK_MODEL.PROJECT_TOTAL_TASK_RISK_SCORE_METRIC_CLASS.WEIGHTS",
    ),
    (
        "total_task_risk_score_weight",
        "RISK_MODEL.PROJECT_LOCATION_TOTAL_TASK_RISK_SCORE_METRIC_CLASS.WEIGHTS",
    ),
]


def upgrade():
    conn = op.get_bind()

    query = text(
        "SELECT value FROM public.rm_calc_parameters WHERE name = :name and tenant_id is NULL;"
    )

    # Gather to STORE values in an array
    to_store = []
    for old_label, new_label in weight_labels:
        low_label = f"{old_label}_low"
        medium_label = f"{old_label}_medium"
        high_label = f"{old_label}_high"

        low = conn.scalar(query, {"name": low_label})
        medium = conn.scalar(query, {"name": medium_label})
        high = conn.scalar(query, {"name": high_label})

        _dict = {
            "low": float(low),
            "medium": float(medium),
            "high": float(high),
        }

        as_json = json.dumps(_dict)
        to_store.append((new_label, as_json))

    count_query = text(
        "SELECT COUNT(*) FROM public.configurations WHERE name = :name and tenant_id is NULL;"
    )
    insert_query = text(
        "INSERT INTO public.configurations (id, name, value) VALUES (:id, :name, :value)"
    )
    for to_store_tuple in to_store:
        params = {
            "id": uuid.uuid4(),
            "name": to_store_tuple[0],
            "value": to_store_tuple[1],
        }

        # Check if already exists a configuration
        n_records_found = conn.scalar(count_query, params)
        # Insert if does not exist
        if n_records_found == 0:
            conn.execute(insert_query, params)


def downgrade():
    pass
