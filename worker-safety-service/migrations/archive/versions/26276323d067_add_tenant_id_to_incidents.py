"""Add tenant id to incidents

Revision ID: 26276323d067
Revises: 2aa18ff45c11
Create Date: 2022-04-06 14:57:40.628982

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "26276323d067"
down_revision = "2aa18ff45c11"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "incidents", sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=True)
    )
    op.create_foreign_key(
        "incidents_tenant_id_fkey", "incidents", "tenants", ["tenant_id"], ["id"]
    )


def downgrade():
    op.drop_constraint("incidents_tenant_id_fkey", "incidents", type_="foreignkey")
    op.drop_column("incidents", "tenant_id")
