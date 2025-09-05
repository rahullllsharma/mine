"""Library project types

Revision ID: 5a9b48692d08
Revises: 6dca56cd422e
Create Date: 2022-01-20 14:12:00.829662

"""
import uuid

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "5a9b48692d08"
down_revision = "6dca56cd422e"
branch_labels = None
depends_on = None


def upgrade():
    table = op.create_table(
        "library_project_types",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    table = op.bulk_insert(
        table,
        [
            {"id": uuid.uuid4(), "name": "LNG/CNG"},
            {"id": uuid.uuid4(), "name": "Distribution"},
            {"id": uuid.uuid4(), "name": "Lining"},
            {"id": uuid.uuid4(), "name": "Reg Stations / Heaters"},
            {"id": uuid.uuid4(), "name": "Transmission"},
            {"id": uuid.uuid4(), "name": "Facilities"},
            {"id": uuid.uuid4(), "name": "Other"},
        ],
    )


def downgrade():
    op.drop_table("library_project_types")
