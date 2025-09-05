"""Set project attributes to as nullable

Revision ID: 9f1d08499876
Revises: 93832a977078
Create Date: 2022-09-12 17:55:37.382497

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "9f1d08499876"
down_revision = "93832a977078"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE projects ALTER COLUMN library_project_type_id DROP NOT NULL"
    )


def downgrade():
    op.execute("ALTER TABLE projects ALTER COLUMN library_project_type_id SET NOT NULL")
