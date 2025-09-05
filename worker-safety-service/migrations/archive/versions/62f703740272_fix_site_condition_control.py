"""Fix site_condition_control

Revision ID: 62f703740272
Revises: c7fc672bc22c
Create Date: 2022-07-13 19:45:30.130825

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "62f703740272"
down_revision = "c7fc672bc22c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "UPDATE public.audit_event_diffs SET object_type = 'site_condition_control' WHERE object_type = 'project_location_site_condition_hazard_control'"
    )


def downgrade():
    op.execute(
        "UPDATE public.audit_event_diffs SET object_type = 'project_location_site_condition_hazard_control' WHERE object_type = 'site_condition_control'"
    )
