"""Add manually created column to site conditions

Revision ID: 4cda3781cae3
Revises: 4169cdce32ba
Create Date: 2023-06-12 14:36:51.729907

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4cda3781cae3"
down_revision = "37fa31f1211a"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "site_conditions", sa.Column("is_manually_added", sa.Boolean(), nullable=True)
    )
    op.execute(
        "UPDATE site_conditions SET is_manually_added = True WHERE user_id IS NOT NULL"
    )
    op.execute(
        "UPDATE site_conditions SET is_manually_added = False WHERE user_id IS NULL"
    )
    op.alter_column("site_conditions", "is_manually_added", nullable=False)
    # ### end Alembic commands ###


def downgrade():
    op.drop_column("site_conditions", "is_manually_added")
