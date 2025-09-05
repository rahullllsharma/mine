"""added externa_id in user table

Revision ID: e9c7c128ff6c
Revises: 5c0dba7e8c42
Create Date: 2024-11-06 15:32:02.758345

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "e9c7c128ff6c"
down_revision = "5c0dba7e8c42"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("external_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "external_id")
