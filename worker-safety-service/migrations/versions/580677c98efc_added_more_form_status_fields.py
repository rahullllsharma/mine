"""added_more_form_status_fields

Revision ID: 580677c98efc
Revises: 66804db6decc
Create Date: 2024-06-21 13:40:01.069607

"""
from alembic import op

revision = "580677c98efc"
down_revision = "66804db6decc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE public.form_status ADD VALUE IF NOT EXISTS 'pending_post_job_brief'"
    )
    op.execute(
        "ALTER TYPE public.form_status ADD VALUE IF NOT EXISTS 'pending_sign_off'"
    )


def downgrade() -> None:
    pass
