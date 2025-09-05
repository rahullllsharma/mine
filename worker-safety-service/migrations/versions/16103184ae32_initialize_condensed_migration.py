"""Initialize Condensed Migration

Revision ID: 16103184ae32
Revises:
Create Date: 2023-07-19 15:06:07.328314

"""
from pathlib import Path

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "16103184ae32"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    fixture_dir = Path("./migrations/fixtures")
    schema_file = fixture_dir / "2-condensed-baseline-migration-schema.sql"
    data_file = fixture_dir / "2-condensed-baseline-migration-data.sql"

    with schema_file.open() as fp:
        query = ""
        for line in fp.readlines():
            if line:
                if line.strip().startswith("--"):
                    if query == "":
                        continue
                    else:
                        op.get_bind().execute(text(query))
                        query = ""
                else:
                    query += line

                pass
            pass
    with data_file.open() as fp:
        query = ""
        for line in fp.readlines():
            if line:
                query += line
                if line.strip().endswith(";"):
                    op.get_bind().execute(text(query))
                    query = ""
    pass


def downgrade():
    pass
