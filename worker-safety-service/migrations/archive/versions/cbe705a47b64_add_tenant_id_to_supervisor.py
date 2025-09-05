"""Add tenant_id to Supervisor

Revision ID: cbe705a47b64
Revises: 254ce3767087
Create Date: 2022-02-10 11:39:10.541219

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "cbe705a47b64"
down_revision = "ec0cb4b6d8ad"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "supervisor",
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
    )
    op.create_foreign_key(
        "supervisor_tenenat_id_fkey", "supervisor", "tenants", ["tenant_id"], ["id"]
    )


def downgrade():
    op.drop_constraint("supervisor_tenenat_id_fkey", "supervisor", type_="foreignkey")
    op.drop_column("supervisor", "tenant_id")
