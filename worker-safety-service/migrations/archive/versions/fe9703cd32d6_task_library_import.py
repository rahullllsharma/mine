"""Task Library Import

Revision ID: fe9703cd32d6
Revises: 0847f33ceb8a
Create Date: 2022-01-11 14:13:37.510956

"""
import os

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fe9703cd32d6"
down_revision = "0847f33ceb8a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    directory = os.fsencode("migrations/fixtures/")
    included_fixtures = [
        # model tables
        b"postgres_public_library_tasks.sql",
        b"postgres_public_library_hazards.sql",
        b"postgres_public_library_controls.sql",
        # link tables
        b"postgres_public_library_task_hazards.sql",
        b"postgres_public_library_hazard_controls.sql",
    ]
    for filename in included_fixtures:
        filepath = os.path.join(directory, filename)
        with open(filepath) as file:
            escaped_sql = sa.text(file.read())
        op.execute(escaped_sql)


def downgrade() -> None:
    fixture_tables = [
        # link tables
        "public.library_task_hazards",
        "public.library_hazard_controls",
        # model tables
        "public.library_hazards",
        "public.library_tasks",
        "public.library_controls",
    ]
    for table in fixture_tables:
        escaped_sql = sa.text(f"TRUNCATE TABLE {table} CASCADE;")
        op.execute(escaped_sql)
