"""TotalActivityRiskScore

Revision ID: 62e9ba7f1433
Revises: 74646a1de43e
Create Date: 2022-10-12 18:42:13.206258

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "62e9ba7f1433"
down_revision = "74646a1de43e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "rm_total_activity_risk_score",
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
        "rm_total_activity_risk_score_entity_idx",
        "rm_total_activity_risk_score",
        ["activity_id", "date"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "rm_total_activity_risk_score_entity_idx",
        table_name="rm_total_activity_risk_score",
    )
    op.drop_table("rm_total_activity_risk_score")
