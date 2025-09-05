"""Fix unique task ID

Revision ID: 5677617a96e8
Revises: 4e2d737eb5c8
Create Date: 2022-10-27 23:14:42.791726

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "5677617a96e8"
down_revision = "4e2d737eb5c8"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        UPDATE public.library_tasks
        SET unique_task_id = replace(unique_task_id, ' ', '')
        WHERE unique_task_id != replace(unique_task_id, ' ', '')
        """
    )


def downgrade():
    pass
