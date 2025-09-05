"""fixtures for incidents and observations

Revision ID: 254ce3767087
Revises: d068b39629f5
Create Date: 2022-02-09 10:20:11.248427

"""
import os

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "254ce3767087"
down_revision = "d068b39629f5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    directory = os.fsencode("migrations/fixtures/")
    filename = (
        b"254ce3767087_fixtures_for_incidents_observations_contractors_supervisors.sql"
    )
    filepath = os.path.join(directory, filename)
    with open(filepath) as file:
        escaped_sql = sa.text(file.read())
    op.execute(escaped_sql)


def downgrade() -> None:
    fixture_tables = [
        # link tables
        "public.raw_incidents",
        "public.observation",
        "public.supervisor",
        "public.contractor",
    ]
    for table in fixture_tables:
        escaped_sql = sa.text(f"TRUNCATE TABLE {table} CASCADE;")
        op.execute(escaped_sql)

    op.execute("UPDATE public.library_tasks SET hesp = 0")
    op.execute("UPDATE public.library_tasks SET category = NULL")
    op.execute("UPDATE public.library_tasks SET unique_task_id = NULL")
