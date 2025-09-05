"""Create StochasticTaskSpecificRiskScoreModel Table

Revision ID: 2b50925ddde1
Revises: 108949d56148
Create Date: 2022-10-07 12:51:32.002522

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2b50925ddde1"
down_revision = "108949d56148"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "rm_stochastic_task_specific_risk_score",
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("inputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("params", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("project_task_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_task_id"],
            ["tasks.id"],
        ),
        sa.PrimaryKeyConstraint("calculated_at", "project_task_id"),
    )
    op.create_index(
        "rm_stochastic_task_specific_risk_score_entity_idx",
        "rm_stochastic_task_specific_risk_score",
        ["project_task_id", "date"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "rm_stochastic_task_specific_risk_score_entity_idx",
        table_name="rm_stochastic_task_specific_risk_score",
    )
    op.drop_table("rm_stochastic_task_specific_risk_score")
