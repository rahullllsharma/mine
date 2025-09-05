"""add ranking defaults for project and project location risk scores

Revision ID: 691d5d20b43a
Revises: ec0cb4b6d8ad
Create Date: 2022-02-10 11:59:05.619370

"""
from alembic import op
from sqlalchemy import column, delete, insert, table, text

# revision identifiers, used by Alembic.
revision = "691d5d20b43a"
down_revision = "d7cd809a77f9"
branch_labels = None
depends_on = None


config_table_name = "rm_calc_parameters"
data = [
    ("project_risk_score_ranking_low", "100.0"),
    ("project_risk_score_ranking_medium", "250.0"),
    ("project_location_risk_score_ranking_low", "100.0"),
    ("project_location_risk_score_ranking_medium", "250.0"),
]


def upgrade():
    for n, v in data:
        op.execute(
            insert(table(config_table_name, column("name"), column("value"))).values(
                name=n, value=v
            )
        )


def downgrade():
    for name, value in data:
        op.execute(
            delete(table(config_table_name))
            .where(column("name") == name)
            .where(text("tenant IS NULL"))
        )
