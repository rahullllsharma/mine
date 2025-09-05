"""Unique manually added site conditions

Revision ID: 3acd8e7f9781
Revises: 1b4b3893b602
Create Date: 2022-04-29 18:48:29.431065

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3acd8e7f9781"
down_revision = "1b4b3893b602"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "project_location_site_conditions_manually_key",
        "project_location_site_conditions",
        ["project_location_id", "library_site_condition_id"],
        unique=True,
        postgresql_where=sa.text("user_id IS NOT NULL AND archived_at IS NULL"),
    )


def downgrade():
    op.drop_index(
        "project_location_site_conditions_manually_key",
        table_name="project_location_site_conditions",
        postgresql_where=sa.text("user_id IS NOT NULL AND archived_at IS NULL"),
    )
