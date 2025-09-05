"""Create StochasticLocationTotalTaskRiskScoreModel table

Revision ID: 2a8f86bb1a32
Revises: 2b50925ddde1
Create Date: 2022-10-07 14:47:37.575038

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2a8f86bb1a32"
down_revision = "0795d933ec63"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "rm_stochastic_location_total_task_risk_score",
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("inputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("params", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("project_location_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_location_id"],
            ["project_locations.id"],
        ),
        sa.PrimaryKeyConstraint("calculated_at"),
    )
    op.create_index(
        "rm_stochastic_location_total_task_risk_score_entity_idx",
        "rm_stochastic_location_total_task_risk_score",
        ["project_location_id", "date"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "rm_stochastic_location_total_task_risk_score_entity_idx",
        table_name="rm_stochastic_location_total_task_risk_score",
    )
    op.drop_table("rm_stochastic_location_total_task_risk_score")
