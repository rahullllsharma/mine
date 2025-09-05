"""Remove Sample Model

Revision ID: 33a1b906f4a2
Revises: fb673ca347e0
Create Date: 2022-03-07 08:05:40.403422

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "33a1b906f4a2"
down_revision = "fb673ca347e0"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("samplemodel")


def downgrade():
    # Downgrade not needed
    pass
