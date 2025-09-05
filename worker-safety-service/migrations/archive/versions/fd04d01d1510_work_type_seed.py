"""work_type seed

Revision ID: fd04d01d1510
Revises: 275fe2e9e4bc
Create Date: 2022-10-06 15:57:27.757162

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "fd04d01d1510"
down_revision = "275fe2e9e4bc"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(
        text(
            """INSERT INTO work_types(id, name) VALUES ('5f12b55b-710f-4613-92f6-48bf0448c025', 'Gas Transmission Construction') ON CONFLICT (id) DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO work_types(id, name) VALUES ('43974dda-0338-4e76-9856-2a76a472fda5', 'General') ON CONFLICT (id) DO NOTHING;"""
        )
    )


def downgrade():
    pass
