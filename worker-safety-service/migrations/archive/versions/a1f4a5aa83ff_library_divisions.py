"""Library divisions

Revision ID: a1f4a5aa83ff
Revises: 057d8e8234d5
Create Date: 2022-01-20 13:45:57.750464

"""
import uuid

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "a1f4a5aa83ff"
down_revision = "057d8e8234d5"
branch_labels = None
depends_on = None


def upgrade():
    table = op.create_table(
        "library_divisions",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.bulk_insert(
        table,
        [
            {"id": uuid.uuid4(), "name": "Gas"},
            {"id": uuid.uuid4(), "name": "Electric"},
        ],
    )


def downgrade():
    op.drop_table("library_divisions")
