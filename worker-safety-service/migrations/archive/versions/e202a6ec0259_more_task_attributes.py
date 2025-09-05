"""more task attributes

Revision ID: e202a6ec0259
Revises: 417407ce174c
Create Date: 2022-02-01 14:00:01.965457

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e202a6ec0259"
down_revision = "8a9128b10a0d"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("library_tasks", sa.Column("hesp", sa.Integer(), nullable=True))
    op.execute("UPDATE library_tasks SET hesp = 0")
    op.alter_column("library_tasks", "hesp", nullable=False)

    op.add_column("library_tasks", sa.Column("category", sa.String(), nullable=True))

    op.add_column(
        "library_tasks", sa.Column("unique_task_id", sa.String(), nullable=True)
    )


def downgrade():
    op.drop_column("library_tasks", "hesp")
    op.drop_column("library_tasks", "category")
    op.drop_column("library_tasks", "unique_task_id")
