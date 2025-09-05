"""Project number and description

Revision ID: dd6bcd96679f
Revises: 8e8721aa3658
Create Date: 2022-01-24 15:00:42.354894

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "dd6bcd96679f"
down_revision = "8e8721aa3658"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "projects",
        sa.Column("number", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.execute("UPDATE projects SET number = '0'")
    op.alter_column("projects", "number", nullable=False)
    op.add_column(
        "projects",
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )


def downgrade():
    op.drop_column("projects", "description")
    op.drop_column("projects", "number")
