"""Add tenant model

Revision ID: aea0cdbfd2cf
Revises: 5a9b48692d08
Create Date: 2022-01-21 13:34:57.482476

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "aea0cdbfd2cf"
down_revision = "5a9b48692d08"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tenants",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("tenant_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "auth_realm_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_tenants_tenant_name"), "tenants", ["tenant_name"], unique=True
    )


def downgrade():
    op.drop_index(op.f("ix_tenants_tenant_name"), table_name="tenants")
    op.drop_table("tenants")
