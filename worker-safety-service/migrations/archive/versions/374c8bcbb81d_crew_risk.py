"""Crew risk

Revision ID: 374c8bcbb81d
Revises: cbc89b4df39b
Create Date: 2022-09-30 12:21:15.470590

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "374c8bcbb81d"
down_revision = "cbc89b4df39b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "rm_average_crew_risk",
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("inputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("params", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("calculated_at"),
    )
    op.create_index(
        "rm_average_crew_risk_entity_idx",
        "rm_average_crew_risk",
        ["tenant_id"],
        unique=False,
    )
    op.create_table(
        "rm_stddev_crew_risk",
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("inputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("params", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("calculated_at"),
    )
    op.create_index(
        "rm_stddev_crew_risk_entity_idx",
        "rm_stddev_crew_risk",
        ["tenant_id"],
        unique=False,
    )
    op.create_table(
        "rm_crew_risk",
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("inputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("params", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("crew_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["crew_id"],
            ["crew.id"],
        ),
        sa.PrimaryKeyConstraint("calculated_at", "crew_id"),
    )
    op.create_index(
        "rm_crew_risk_entity_idx", "rm_crew_risk", ["crew_id"], unique=False
    )


def downgrade():
    op.drop_index("rm_crew_risk_entity_idx", table_name="rm_crew_risk")
    op.drop_table("rm_crew_risk")
    op.drop_index("rm_stddev_crew_risk_entity_idx", table_name="rm_stddev_crew_risk")
    op.drop_table("rm_stddev_crew_risk")
    op.drop_index("rm_average_crew_risk_entity_idx", table_name="rm_average_crew_risk")
    op.drop_table("rm_average_crew_risk")
