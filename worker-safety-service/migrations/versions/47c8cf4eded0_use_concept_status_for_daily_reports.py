"""use concept status for daily reports

Revision ID: 47c8cf4eded0
Revises: 189f9c571f80
Create Date: 2023-07-26 10:29:46.016633

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "47c8cf4eded0"
down_revision = "189f9c571f80"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE public.daily_reports ALTER COLUMN status SET DATA TYPE public.conceptstatus USING status::text::public.conceptstatus;"
    )


def downgrade():
    # We won't need to ever undo this op
    pass
