"""Rename activity group name

Revision ID: b10fd24dec56
Revises: 9fc19d85a3ce
Create Date: 2022-10-27 17:17:48.733254

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "b10fd24dec56"
down_revision = "9fc19d85a3ce"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE public.activity_groups RENAME COLUMN activity_group_name TO name"
    )
    op.execute(
        "ALTER TABLE public.activity_groups RENAME CONSTRAINT activity_groups_activity_group_name_key TO library_activity_groups_name_key"
    )
    op.execute(
        "ALTER TABLE public.activity_groups RENAME CONSTRAINT activity_groups_pkey TO library_activity_groups_pkey"
    )
    op.execute("ALTER TABLE public.activity_groups RENAME TO library_activity_groups")


def downgrade():
    op.execute("ALTER TABLE public.library_activity_groups RENAME TO activity_groups")
    op.execute(
        "ALTER TABLE public.activity_groups RENAME COLUMN name TO activity_group_name"
    )
    op.execute(
        "ALTER TABLE public.activity_groups RENAME CONSTRAINT library_activity_groups_name_key TO activity_groups_activity_group_name_key"
    )
    op.execute(
        "ALTER TABLE public.activity_groups RENAME CONSTRAINT library_activity_groups_pkey TO activity_groups_pkey"
    )
