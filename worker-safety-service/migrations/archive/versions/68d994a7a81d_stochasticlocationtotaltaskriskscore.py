"""StochasticLocationTotalTaskRiskScore

Revision ID: 68d994a7a81d
Revises: 21970df807d8
Create Date: 2022-10-12 18:32:52.026955

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "68d994a7a81d"
down_revision = "21970df807d8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "rm_stochastic_activity_total_task_risk_score",
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("inputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("params", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("activity_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(
            ["activity_id"],
            ["activities.id"],
        ),
        sa.PrimaryKeyConstraint("calculated_at"),
    )
    op.create_index(
        "rm_stochastic_activity_total_task_risk_score_entity_idx",
        "rm_stochastic_activity_total_task_risk_score",
        ["activity_id", "date"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "rm_stochastic_activity_total_task_risk_score_entity_idx",
        table_name="rm_stochastic_activity_total_task_risk_score",
    )
    op.drop_table("rm_stochastic_activity_total_task_risk_score")
