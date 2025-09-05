"""rm_calc_parameters tenant

Revision ID: 0f32f88344f9
Revises: 2acf99e204f6
Create Date: 2022-03-22 17:20:29.718664

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "0f32f88344f9"
down_revision = "2acf99e204f6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "rm_calc_parameters",
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
    )
    op.create_foreign_key(
        "rm_calc_parameters_tenant_id_fkey",
        "rm_calc_parameters",
        "tenants",
        ["tenant_id"],
        ["id"],
    )
    op.execute(
        "UPDATE rm_calc_parameters SET tenant_id = tenant::uuid WHERE tenant IS NOT NULL"
    )
    op.drop_column("rm_calc_parameters", "tenant")


def downgrade():
    op.add_column(
        "rm_calc_parameters",
        sa.Column("tenant", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.execute(
        "UPDATE rm_calc_parameters SET tenant = tenant_id::text WHERE tenant_id IS NOT NULL"
    )
    op.drop_constraint(
        "rm_calc_parameters_tenant_id_fkey", "rm_calc_parameters", type_="foreignkey"
    )
    op.drop_column("rm_calc_parameters", "tenant_id")
