"""add supervisor activity link table

Revision ID: 044961a93ea1
Revises: 8a1638c0a53b
Create Date: 2022-10-17 15:37:07.598127

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "044961a93ea1"
down_revision = "8a1638c0a53b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "activity_supervisor_link",
        sa.Column("activity_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("supervisor_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["activity_id"],
            ["activities.id"],
        ),
        sa.ForeignKeyConstraint(
            ["supervisor_id"],
            ["supervisor.id"],
        ),
        sa.PrimaryKeyConstraint("activity_id", "supervisor_id"),
    )


def downgrade():
    op.drop_table("activity_supervisor_link")
