"""add tenant id to parsed files table

Revision ID: 2c17e3a05ff9
Revises: 69c7656bd2ea
Create Date: 2022-04-06 13:01:50.577610

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "2c17e3a05ff9"
down_revision = "69c7656bd2ea"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "parsed_files",
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
    )
    op.create_foreign_key(
        "parsed_files_tenant_id_fkey",
        "parsed_files",
        "tenants",
        ["tenant_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_column("parsed_files", "tenant_id")
