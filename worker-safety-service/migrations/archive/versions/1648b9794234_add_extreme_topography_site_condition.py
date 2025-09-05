"""add extreme topography site condition

Revision ID: 1648b9794234
Revises: b9e24c5dd6b6
Create Date: 2022-02-21 16:05:55.788714

"""
import os

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1648b9794234"
down_revision = "b9e24c5dd6b6"
branch_labels = None
depends_on = None


def upgrade():
    fixture_path = os.fsencode(
        "migrations/fixtures/1648b9794234_add_extreme_topography_site_condition.sql"
    )
    with open(fixture_path) as file:
        escaped_sql = sa.text(file.read())
    op.execute(escaped_sql)


def downgrade():
    op.execute(
        "DELETE FROM public.library_site_conditions WHERE handle_code = 'extreme_topography'"
    )
