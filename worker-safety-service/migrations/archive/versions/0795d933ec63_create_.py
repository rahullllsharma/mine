"""Create DivisionRelativePrecursorRiskModel Table

Revision ID: 0795d933ec63
Revises: 45f84adb634a
Create Date: 2022-10-12 11:52:44.350647

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0795d933ec63"
down_revision = "45f84adb634a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "rm_division_relative_precursor_risk",
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("inputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("params", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("division_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["division_id"],
            ["library_divisions.id"],
        ),
        sa.PrimaryKeyConstraint("calculated_at", "division_id"),
    )
    op.create_index(
        "rm_division_relative_precursor_risk_entity_idx",
        "rm_division_relative_precursor_risk",
        ["division_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "rm_division_relative_precursor_risk_entity_idx",
        table_name="rm_division_relative_precursor_risk",
    )
    op.drop_table("rm_division_relative_precursor_risk")
