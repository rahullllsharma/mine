"""Site condition fixtures

Revision ID: 6abc94c81b6c
Revises: 74beb09fc391
Create Date: 2022-01-26 16:16:28.693665

"""
import os

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "6abc94c81b6c"
down_revision = "74beb09fc391"
branch_labels = None
depends_on = None


def upgrade() -> None:
    directory = os.fsencode("migrations/fixtures/")
    included_fixtures = [
        # model tables
        b"postgres_public_library_site_conditions.sql",
        b"postgres_public_library_site_conditions_hazards.sql",
        b"postgres_public_library_site_conditions_controls.sql",
        # link tables
        b"postgres_public_library_site_conditions_recommendations.sql",
    ]
    for filename in included_fixtures:
        filepath = os.path.join(directory, filename)
        with open(filepath) as file:
            escaped_sql = sa.text(file.read())
        op.execute(escaped_sql)


def downgrade() -> None:
    op.execute("DELETE FROM public.library_site_condition_recommendations")
    op.execute(
        "DELETE FROM public.library_controls WHERE for_tasks = false AND for_site_conditions = true"
    )
    op.execute(
        "UPDATE public.library_controls SET for_site_conditions = false WHERE for_site_conditions = true"
    )
    op.execute(
        "DELETE FROM public.library_hazards WHERE for_tasks = false AND for_site_conditions = true"
    )
    op.execute(
        "UPDATE public.library_hazards SET for_site_conditions = false WHERE for_site_conditions = true"
    )
    op.execute("DELETE FROM public.library_site_conditions")
