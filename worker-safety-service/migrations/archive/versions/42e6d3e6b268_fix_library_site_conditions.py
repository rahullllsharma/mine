"""Fix library site conditions

Revision ID: 42e6d3e6b268
Revises: 0328b833a037
Create Date: 2022-07-14 20:26:36.668773

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "42e6d3e6b268"
down_revision = "0328b833a037"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO library_site_conditions (id, name, handle_code) VALUES
            ('47ca3dc1-5daa-469e-a09c-4728e60aed35', 'Wet or Frozen Ground', 'wet_or_frozen_ground'),
            ('f8ce7095-2ec1-438d-81e4-fb4d67cb0240', 'High Winds', 'high_winds'),
            ('1e1d229b-1836-422f-b55a-63e09db28250', 'Fugitive Dust', 'fugitive_dust'),
            ('e010935b-10d8-42ba-b1ce-a88ad9f2d49e', 'Air Quality Index', 'air_quality_index'),
            ('4e733c79-a258-4a8c-9362-e676741a4aa8', 'Building Density', 'building_density')
        ON CONFLICT DO NOTHING;
        """
    )
    op.execute(
        "UPDATE library_site_conditions SET name = 'Roadway closed for work' WHERE name = 'Roadway closed for work (roadclosed)'"
    )
    op.execute(
        "UPDATE library_site_conditions SET name = 'Work near regulator station' WHERE name = 'Work near regulator station '"
    )
    op.execute(
        "UPDATE library_site_conditions SET name = 'Working at night' WHERE name = 'Working at night '"
    )


def downgrade():
    pass
