"""Add back alert column in integration

Revision ID: 2b7410fda034
Revises: a88e18b5ead8
Create Date: 2023-08-07 12:32:21.870239

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2b7410fda034"
down_revision = "a88e18b5ead8"
branch_labels = None
depends_on = None


def column_exists_on_table(table_name, column_name):
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = inspector.get_columns(table_name)
    for column in columns:
        if column["name"] == column_name:
            return True


def upgrade():
    # https://urbint.atlassian.net/browse/WORK-737
    # This column was orininally removed in 189f9c571f80_remove_alert_column.py as part of WORK-737.
    # We later decided to revert this however the migration was already run in integration.
    # Before it was run in any other environment, we decided to remove the migration.
    # This migration ensures that the column is added back in integration and in dev environments.
    # This migration will be a no-op in any other environments.
    if not column_exists_on_table("site_conditions", "alert"):
        op.add_column(
            "site_conditions",
            sa.Column("alert", sa.BOOLEAN(), autoincrement=False, nullable=True),
        )


def downgrade():
    pass
