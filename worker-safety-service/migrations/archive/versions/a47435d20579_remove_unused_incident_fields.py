"""Remove unused incident fields

Revision ID: a47435d20579
Revises: 6f292c23c83b
Create Date: 2022-04-20 10:19:31.750234

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a47435d20579"
down_revision = "6f292c23c83b"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("incidents", "east_longitude")
    op.drop_column("incidents", "zipcode")
    op.drop_column("incidents", "project_id")
    op.drop_column("incidents", "client_id")
    op.drop_column("incidents", "longitude")
    op.drop_column("incidents", "west_longitude")
    op.drop_column("incidents", "latitude")
    op.drop_column("incidents", "centroid_source")
    op.drop_column("incidents", "south_latitude")
    op.drop_column("incidents", "north_latitude")
    op.drop_column("incidents", "inferred_work_start_date_confidence")
    op.drop_column("incidents", "address")
    op.drop_column("incidents", "person_impacted")


def downgrade():
    op.add_column(
        "incidents",
        sa.Column("address", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "incidents",
        sa.Column(
            "inferred_work_start_date_confidence",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "incidents",
        sa.Column(
            "north_latitude",
            postgresql.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "incidents",
        sa.Column(
            "south_latitude",
            postgresql.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "incidents",
        sa.Column(
            "centroid_source",
            postgresql.ENUM(
                "centroid_from_client",
                "centroid_from_geocoder",
                "centroid_from_polygo",
                "centroid_from_bounding_box",
                name="centroidtype",
            ),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "incidents",
        sa.Column(
            "latitude",
            postgresql.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "incidents",
        sa.Column(
            "west_longitude",
            postgresql.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "incidents",
        sa.Column(
            "longitude",
            postgresql.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "incidents",
        sa.Column("client_id", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "incidents",
        sa.Column("project_id", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "incidents",
        sa.Column("zipcode", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "incidents",
        sa.Column(
            "east_longitude",
            postgresql.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "incidents",
        sa.Column("person_imacted", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
