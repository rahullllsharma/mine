"""Add email to user

Revision ID: c764e56958d7
Revises: 406dc2dab455
Create Date: 2022-02-22 21:36:57.836774

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "c764e56958d7"
down_revision = "406dc2dab455"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column(
            "email",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
            server_default="",
        ),
    )


def downgrade():
    op.drop_column("users", "email")
