"""ingestion settings

Revision ID: 070209b211c7
Revises: 2acf99e204f6
Create Date: 2022-03-22 13:17:34.591030

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "070209b211c7"
down_revision = "d9143e2dcc11"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ingestion_settings",
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("bucket_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("folder_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("tenant_id"),
    )


def downgrade():
    op.drop_table("ingestion_settings")
