"""location geom

Revision ID: c13383525e19
Revises: 5d26653c64aa
Create Date: 2022-11-03 22:56:50.294339

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c13383525e19"
down_revision = "5d26653c64aa"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE project_locations ADD COLUMN geom geometry('POINT')")
    op.execute(
        "UPDATE project_locations SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)"
    )
    op.execute("ALTER TABLE project_locations ALTER COLUMN geom SET NOT NULL")
    op.drop_column("project_locations", "longitude")
    op.drop_column("project_locations", "latitude")


def downgrade():
    op.add_column(
        "project_locations",
        sa.Column(
            "latitude",
            sa.NUMERIC(precision=14, scale=12),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "project_locations",
        sa.Column(
            "longitude",
            sa.NUMERIC(precision=15, scale=12),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.execute(
        "UPDATE project_locations SET longitude = st_x(geom), latitude = st_y(geom)"
    )
    op.execute("ALTER TABLE project_locations ALTER COLUMN latitude SET NOT NULL")
    op.execute("ALTER TABLE project_locations ALTER COLUMN longitude SET NOT NULL")
    op.drop_column("project_locations", "geom")
