"""project_location_site_condition_evaluated type

Revision ID: 0e295d2678ff
Revises: 3acd8e7f9781
Create Date: 2022-05-02 17:17:53.117978

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "0e295d2678ff"
down_revision = "3acd8e7f9781"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TYPE audit_event_type ADD VALUE IF NOT EXISTS 'project_location_site_condition_evaluated'"
    )


def downgrade():
    pass
