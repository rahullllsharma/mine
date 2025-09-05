"""SupervisorRelativePrecursorRisk

Revision ID: 1ea0af372706
Revises: 78b1a059fc85
Create Date: 2022-09-19 11:23:28.386906

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "1ea0af372706"
down_revision = "78b1a059fc85"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "rm_supervisor_relative_precursor_risk",
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("inputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("params", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("supervisor_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.PrimaryKeyConstraint("calculated_at", "supervisor_id"),
    )
    op.create_index(
        "rm_supervisor_relative_precursor_risk_entity_idx",
        "rm_supervisor_relative_precursor_risk",
        ["supervisor_id"],
        unique=False,
    )
    op.create_table(
        "rm_average_supervisor_relative_precursor_risk",
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
        "rm_average_supervisor_relative_precursor_risk_entity_idx",
        "rm_average_supervisor_relative_precursor_risk",
        ["tenant_id"],
        unique=False,
    )
    op.create_table(
        "rm_stddev_supervisor_relative_precursor_risk",
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
        "rm_stddev_supervisor_relative_precursor_risk_entity_idx",
        "rm_stddev_supervisor_relative_precursor_risk",
        ["tenant_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "rm_stddev_supervisor_relative_precursor_risk_entity_idx",
        table_name="rm_stddev_supervisor_relative_precursor_risk",
    )
    op.drop_table("rm_stddev_supervisor_relative_precursor_risk")
    op.drop_index(
        "rm_average_supervisor_relative_precursor_risk_entity_idx",
        table_name="rm_average_supervisor_relative_precursor_risk",
    )
    op.drop_table("rm_average_supervisor_relative_precursor_risk")
    op.drop_index(
        "rm_supervisor_relative_precursor_risk_entity_idx",
        table_name="rm_supervisor_relative_precursor_risk",
    )
    op.drop_table("rm_supervisor_relative_precursor_risk")
