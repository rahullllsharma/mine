"""Tenant to DivisionRelativePrecursorRisk

Revision ID: 4e55e95cd288
Revises: 62e9ba7f1433
Create Date: 2022-10-13 10:28:56.754265

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "4e55e95cd288"
down_revision = "62e9ba7f1433"
branch_labels = None
depends_on = None


def upgrade():
    # Adding tenant_id shouldn't fail because no data exists on this table, but,
    # if exists, because of some downgrade, clear table entries and try the migration again
    op.add_column(
        "rm_division_relative_precursor_risk",
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
    )

    op.drop_index(
        "rm_division_relative_precursor_risk_entity_idx",
        table_name="rm_division_relative_precursor_risk",
    )
    op.create_index(
        "rm_division_relative_precursor_risk_entity_idx",
        "rm_division_relative_precursor_risk",
        ["tenant_id", "division_id"],
        unique=False,
    )
    op.create_foreign_key(
        "rm_division_relative_precursor_risk_tenant_id_fkey",
        "rm_division_relative_precursor_risk",
        "tenants",
        ["tenant_id"],
        ["id"],
    )

    # Create primary key with tenant
    op.drop_constraint(
        "rm_division_relative_precursor_risk_pkey",
        "rm_division_relative_precursor_risk",
        type_="primary",
    )
    op.create_primary_key(
        "rm_division_relative_precursor_risk_pkey",
        "rm_division_relative_precursor_risk",
        columns=["calculated_at", "tenant_id", "division_id"],
    )


def downgrade():
    op.drop_constraint(
        "rm_division_relative_precursor_risk_pkey",
        "rm_division_relative_precursor_risk",
        type_="primary",
    )
    op.drop_constraint(
        "rm_division_relative_precursor_risk_tenant_id_fkey",
        "rm_division_relative_precursor_risk",
        type_="foreignkey",
    )
    op.drop_index(
        "rm_division_relative_precursor_risk_entity_idx",
        table_name="rm_division_relative_precursor_risk",
    )
    op.create_index(
        "rm_division_relative_precursor_risk_entity_idx",
        "rm_division_relative_precursor_risk",
        ["division_id"],
        unique=False,
    )
    op.drop_column("rm_division_relative_precursor_risk", "tenant_id")
    op.create_primary_key(
        "rm_division_relative_precursor_risk_pkey",
        "rm_division_relative_precursor_risk",
        columns=["calculated_at", "division_id"],
    )
