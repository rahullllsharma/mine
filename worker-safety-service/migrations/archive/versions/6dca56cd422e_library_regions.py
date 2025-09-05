"""Library regions

Revision ID: 6dca56cd422e
Revises: a1f4a5aa83ff
Create Date: 2022-01-20 14:02:37.920396

"""
import uuid

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "6dca56cd422e"
down_revision = "a1f4a5aa83ff"
branch_labels = None
depends_on = None


def upgrade():
    table = op.create_table(
        "library_regions",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.bulk_insert(
        table,
        [
            {"id": uuid.uuid4(), "name": "DNY (Downstate New York)"},
            {"id": uuid.uuid4(), "name": "UNY (Upstate New York)"},
            {"id": uuid.uuid4(), "name": "NE (New England)"},
        ],
    )


def downgrade():
    op.drop_table("library_regions")
