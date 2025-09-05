"""Link historical incidents to tasks

Revision ID: d692695d0949
Revises: da6d716526d1
Create Date: 2022-02-15 16:32:11.152840

"""
import os

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d692695d0949"
down_revision = "da6d716526d1"
branch_labels = None
depends_on = None


def upgrade():
    directory = os.fsencode("migrations/fixtures/")
    included_fixtures = [
        b"d692695d0949_link_historical_incidents_to_tasks.sql",
    ]
    for filename in included_fixtures:
        filepath = os.path.join(directory, filename)
        with open(filepath) as file:
            escaped_sql = sa.text(file.read())
        op.execute(escaped_sql)


def downgrade():
    op.execute(sa.text("TRUNCATE TABLE public.incident_tasks;"))
