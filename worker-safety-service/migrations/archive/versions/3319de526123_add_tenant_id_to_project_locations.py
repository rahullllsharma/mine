"""Add tenant id to project locations

Revision ID: 3319de526123
Revises: c67a195dddfe
Create Date: 2023-01-12 14:39:59.588920

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy import text

revision = "3319de526123"
down_revision = "0715f99ff159"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "project_locations",
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
    )
    op.get_bind().execute(
        text(
            "UPDATE project_locations SET tenant_id=projects.tenant_id FROM projects where project_id=projects.id"
        )
    )
    op.create_foreign_key(
        "project_locations_tenant_id_fkey",
        "project_locations",
        "tenants",
        ["tenant_id"],
        ["id"],
    )
    op.alter_column(
        "project_locations",
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
    )
    op.create_index(
        "project_locations_tenant_id_idx",
        "project_locations",
        ["tenant_id"],
        unique=False,
    )


def downgrade():
    op.drop_index("project_locations_tenant_id_idx", table_name="project_locations")
    op.drop_constraint(
        "project_locations_tenant_id_fkey", "project_locations", type_="foreignkey"
    )
    op.drop_column("project_locations", "tenant_id")
