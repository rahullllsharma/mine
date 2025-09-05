"""geom index

Revision ID: e5d203160101
Revises: af6ade335f11
Create Date: 2022-11-18 22:45:34.197488

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "e5d203160101"
down_revision = "af6ade335f11"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "locations_geom_ix",
        "project_locations",
        ["geom"],
        unique=False,
        postgresql_where="archived_at IS NULL",
        postgresql_include=["id", "project_id"],
        postgresql_using="gist",
    )


def downgrade():
    op.drop_index("locations_geom_ix", table_name="project_locations")
