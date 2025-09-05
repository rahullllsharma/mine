"""Activity name

Revision ID: 444fa996c207
Revises: eb0aeaa980e7
Create Date: 2022-08-03 15:53:21.557564

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "444fa996c207"
down_revision = "eb0aeaa980e7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "activities",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    )


def downgrade():
    op.drop_column("activities", "name")
