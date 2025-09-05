"""add ranking defaults for total task and task specific risk scores

Revision ID: ec0cb4b6d8ad
Revises: ce1e0947692b
Create Date: 2022-02-07 14:51:22.705794

"""
from alembic import op

# revision identifiers, used by Alembic.
from sqlalchemy import column, delete, insert, table, text

# revision identifiers, used by Alembic.
revision = "ec0cb4b6d8ad"
down_revision = "ce1e0947692b"
branch_labels = None
depends_on = None

config_table_name = "rm_calc_parameters"
data = [
    ("total_task_risk_score_ranking_low", "85.0"),
    ("total_task_risk_score_ranking_medium", "210.0"),
    ("task_specific_risk_score_ranking_low", "85.0"),
    ("task_specific_risk_score_ranking_medium", "210.0"),
]


def upgrade():
    # Add values to the params
    for n, v in data:
        op.execute(
            insert(table(config_table_name, column("name"), column("value"))).values(
                name=n, value=v
            )
        )


def downgrade():
    # Remove defaults
    for name, value in data:
        op.execute(
            delete(table(config_table_name))
            .where(column("name") == name)
            .where(text("tenant IS NULL"))
        )
