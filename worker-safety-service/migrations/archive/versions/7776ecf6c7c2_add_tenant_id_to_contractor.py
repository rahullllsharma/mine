"""Add tenant_id to Contractor

Revision ID: 7776ecf6c7c2
Revises: 156a80d386af
Create Date: 2022-02-08 08:14:43.244573

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "7776ecf6c7c2"
down_revision = "156a80d386af"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "contractor",
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
    )
    op.create_foreign_key(
        "contractor_tenenat_id_fkey", "contractor", "tenants", ["tenant_id"], ["id"]
    )


def downgrade():
    op.drop_constraint("contractor_tenenat_id_fkey", "contractor", type_="foreignkey")
    op.drop_column("contractor", "tenant_id")
