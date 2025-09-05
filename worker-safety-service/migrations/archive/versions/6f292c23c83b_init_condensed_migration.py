"""init condensed migration

Revision ID: 6f292c23c83b
Revises:
Create Date: 2022-04-11 22:19:32.866604

"""
from pathlib import Path

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "6f292c23c83b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    fixture_dir = Path("./migrations/fixtures")
    filenames = [
        fixture_dir / "condensed-baseline-migration-schema.sql",
        fixture_dir / "condensed-baseline-migration-data.sql",
    ]

    for filename in filenames:
        with filename.open() as fp:
            query = ""
            for line in fp.readlines():
                if line:
                    query += line
                    if line.strip().endswith(";"):
                        op.get_bind().execute(text(query))
                        query = ""


def downgrade():
    pass
