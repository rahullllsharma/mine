"""add_hydro_one_work_types

Revision ID: eacb03e5092f
Revises: 21970df807d8
Create Date: 2022-10-12 12:44:10.906288

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "eacb03e5092f"
down_revision = "c6f3e5b02c12"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(
        text(
            """INSERT INTO work_types(id, name) VALUES ('33377fa1-dfc5-4149-94a7-feefb6467e75', 'Electric Distribution') ON CONFLICT DO NOTHING;"""
        )
    )


def downgrade():
    pass
