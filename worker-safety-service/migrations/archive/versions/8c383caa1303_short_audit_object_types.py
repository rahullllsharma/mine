"""Short audit object types

Revision ID: 8c383caa1303
Revises: 3d5b6f908bcf
Create Date: 2022-07-08 00:25:29.134485

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "8c383caa1303"
down_revision = "3d5b6f908bcf"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE public.audit_object_type ADD VALUE IF NOT EXISTS 'task'")
    op.execute(
        "ALTER TYPE public.audit_object_type ADD VALUE IF NOT EXISTS 'task_hazard'"
    )
    op.execute(
        "ALTER TYPE public.audit_object_type ADD VALUE IF NOT EXISTS 'task_control'"
    )
    op.execute(
        "ALTER TYPE public.audit_object_type ADD VALUE IF NOT EXISTS 'site_condition'"
    )
    op.execute(
        "ALTER TYPE public.audit_object_type ADD VALUE IF NOT EXISTS 'site_condition_hazard'"
    )
    op.execute(
        "ALTER TYPE public.audit_object_type ADD VALUE IF NOT EXISTS 'site_condition_control'"
    )


def downgrade():
    pass
