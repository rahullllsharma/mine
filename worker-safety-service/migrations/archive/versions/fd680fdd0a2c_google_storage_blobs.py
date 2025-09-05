"""google-storage-blobs

Revision ID: fd680fdd0a2c
Revises: fb31bc54c5d3
Create Date: 2022-02-03 15:32:15.662167

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "fd680fdd0a2c"
down_revision = "0c7bd349a563"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "google_cloud_storage_blob",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column("bucket_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("file_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("mimetype", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("md5", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("crc32c", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("google_cloud_storage_blob")
