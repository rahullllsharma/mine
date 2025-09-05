"""remove concept status add form status

Revision ID: 0c2a36b3ea1a
Revises: 47c8cf4eded0
Create Date: 2023-07-28 14:50:02.222158

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "0c2a36b3ea1a"
down_revision = "47c8cf4eded0"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE TYPE public.form_status AS ENUM ('in_progress', 'complete');")
    op.execute(
        "ALTER TABLE public.daily_reports ALTER COLUMN status SET DATA TYPE public.form_status USING status::text::public.form_status;"
    )
    op.execute(
        "ALTER TABLE public.jsbs ALTER COLUMN status SET DATA TYPE public.form_status USING status::text::public.form_status;"
    )


def downgrade():
    # No need to undo this action
    pass
