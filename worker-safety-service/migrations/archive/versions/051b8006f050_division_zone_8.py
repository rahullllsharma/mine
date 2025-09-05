"""Division Zone 8

Revision ID: 051b8006f050
Revises: 8bfdcdfb64d2
Create Date: 2022-10-26 16:16:50.830616

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "051b8006f050"
down_revision = "8bfdcdfb64d2"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO library_divisions (id, name)
        VALUES
            ('eba82bf6-ca14-487e-b8bc-0b15211841f7', 'Zone 8')
        ON CONFLICT DO NOTHING
        """
    )


def downgrade():
    pass
