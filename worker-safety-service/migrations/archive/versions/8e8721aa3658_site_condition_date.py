"""Site condition date

Revision ID: 8e8721aa3658
Revises: 7781a9cbe140
Create Date: 2022-01-21 23:15:03.411295

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8e8721aa3658"
down_revision = "7781a9cbe140"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "project_location_site_conditions", sa.Column("date", sa.Date(), nullable=True)
    )
    op.execute("UPDATE project_location_site_conditions SET date = CURRENT_DATE")
    op.alter_column("project_location_site_conditions", "date", nullable=False)


def downgrade():
    op.drop_column("project_location_site_conditions", "date")
