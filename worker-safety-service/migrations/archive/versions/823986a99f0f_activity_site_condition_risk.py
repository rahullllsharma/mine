"""Activity site condition risk

Revision ID: 823986a99f0f
Revises: 94dce1d4ce24
Create Date: 2022-10-10 19:16:15.238307

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "823986a99f0f"
down_revision = "94dce1d4ce24"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "rm_stochastic_activity_sc_relative_precursor_risk_score",
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
        "rm_stochastic_activity_sc_entity_idx",
        "rm_stochastic_activity_sc_relative_precursor_risk_score",
        ["activity_id", "date"],
        unique=False,
    )


def downgrade():
    op.drop_table("rm_stochastic_activity_sc_relative_precursor_risk_score")
