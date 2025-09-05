"""LibrarySiteConditionRelativePrecursorRisk

Revision ID: 45f84adb634a
Revises: 823986a99f0f
Create Date: 2022-10-11 11:45:28.365705

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "45f84adb634a"
down_revision = "823986a99f0f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "rm_library_site_condition_relative_precursor_risk",
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("inputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("params", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column(
            "library_site_condition_id", sqlmodel.sql.sqltypes.GUID(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["library_site_condition_id"],
            ["library_site_conditions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint(
            "calculated_at", "tenant_id", "library_site_condition_id"
        ),
    )
    op.create_index(
        "rm_library_site_condition_relative_precursor_risk_entity_idx",
        "rm_library_site_condition_relative_precursor_risk",
        ["tenant_id", "library_site_condition_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "rm_library_site_condition_relative_precursor_risk_entity_idx",
        table_name="rm_library_site_condition_relative_precursor_risk",
    )
    op.drop_table("rm_library_site_condition_relative_precursor_risk")
