"""Fix tasks indexes

Revision ID: 303a4ae027ac
Revises: 62f703740272
Create Date: 2022-07-14 12:33:57.099011

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "303a4ae027ac"
down_revision = "62f703740272"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER INDEX tasks_lt_fkey RENAME TO bad_tasks_lt_fkey")
    op.execute("ALTER INDEX tasks_pl_fkey RENAME TO tasks_lt_fkey")
    op.execute("ALTER INDEX bad_tasks_lt_fkey RENAME TO tasks_pl_fkey")


def downgrade():
    op.execute("ALTER INDEX tasks_lt_fkey RENAME TO bad_tasks_lt_fkey")
    op.execute("ALTER INDEX tasks_pl_fkey RENAME TO tasks_lt_fkey")
    op.execute("ALTER INDEX bad_tasks_lt_fkey RENAME TO tasks_pl_fkey")
