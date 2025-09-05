"""Migrate risk model threshold to the configurations

Revision ID: 246e1a537082
Revises: 4b2fef494feb
Create Date: 2022-10-05 13:56:27.601079

"""
import json
import uuid

from alembic import op

# revision identifiers, used by Alembic.
from sqlalchemy import text

revision = "246e1a537082"
down_revision = "4b2fef494feb"
branch_labels = None
depends_on = None


threshold_labels = [
    (
        "project_risk_score_ranking",
        "RISK_MODEL.TOTAL_PROJECT_RISK_SCORE_METRIC_CLASS.THRESHOLDS",
    ),
    (
        "project_location_risk_score_ranking",
        "RISK_MODEL.TOTAL_PROJECT_LOCATION_RISK_SCORE_METRIC_CLASS.THRESHOLDS",
    ),
    (
        "total_task_risk_score_ranking",
        "RISK_MODEL.PROJECT_TOTAL_TASK_RISK_SCORE_METRIC_CLASS.THRESHOLDS",
    ),
    (
        "total_task_risk_score_ranking",
        "RISK_MODEL.PROJECT_LOCATION_TOTAL_TASK_RISK_SCORE_METRIC_CLASS.THRESHOLDS",
    ),
    (
        "task_specific_risk_score_ranking",
        "RISK_MODEL.TASK_SPECIFIC_RISK_SCORE_METRIC_CLASS.THRESHOLDS",
    ),
]


def upgrade():
    conn = op.get_bind()

    query = text(
        "SELECT value FROM public.rm_calc_parameters WHERE name = :name and tenant_id is NULL;"
    )

    # Gather to STORE values in an array
    to_store = []
    for old_threshold_label, new_threshold_label in threshold_labels:
        low_label = f"{old_threshold_label}_low"
        medium_label = f"{old_threshold_label}_medium"

        low = conn.scalar(query, {"name": low_label})

        medium = conn.scalar(query, {"name": medium_label})

        _dict = {
            "low": float(low),
            "medium": float(medium),
        }

        as_json = json.dumps(_dict)
        to_store.append((new_threshold_label, as_json))

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
