"""add ingestion status table

Revision ID: afb1e5339081
Revises: c13383525e19
Create Date: 2022-11-09 00:46:41.752992

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "afb1e5339081"
down_revision = "97ec238f5a63"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ingestion_process",
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("failed_records", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("ingestion_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("total_record_count", sa.Integer(), nullable=True),
        sa.Column("successful_record_count", sa.Integer(), nullable=True),
        sa.Column("failed_record_count", sa.Integer(), nullable=True),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("ingestion_process")
