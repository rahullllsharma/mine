"""Remove unused observation fields

Revision ID: dbb1276bc2bc
Revises: a47435d20579
Create Date: 2022-04-20 10:48:27.759106

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "dbb1276bc2bc"
down_revision = "a47435d20579"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("observations", "longitude")
    op.drop_column("observations", "centroid_source")
    op.drop_column("observations", "latitude")
    op.drop_column("observations", "client_id")
    op.execute("DROP TYPE centroidtype")


def downgrade():
    op.execute(
        """
    CREATE TYPE public.centroidtype AS ENUM (
        'centroid_from_client',
        'centroid_from_geocoder',
        'centroid_from_polygo',
        'centroid_from_bounding_box'
    );
    """
    )
    op.add_column(
        "observations",
        sa.Column("client_id", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "observations",
        sa.Column(
            "latitude",
            postgresql.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "observations",
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
        "observations",
        sa.Column(
            "longitude",
            postgresql.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=True,
        ),
    )
