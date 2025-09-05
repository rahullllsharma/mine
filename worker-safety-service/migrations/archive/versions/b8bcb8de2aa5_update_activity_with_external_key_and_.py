"""update activity with external key and meta

Revision ID: b8bcb8de2aa5
Revises: ac7981af9db2
Create Date: 2023-03-06 19:49:56.157918

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "b8bcb8de2aa5"
down_revision = "ac7981af9db2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "activities",
        sa.Column(
            "meta_attributes", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
    )
    op.add_column(
        "activities",
        sa.Column("external_key", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )


def downgrade():
    op.drop_column("activities", "external_key")
    op.drop_column("activities", "meta_attributes")
