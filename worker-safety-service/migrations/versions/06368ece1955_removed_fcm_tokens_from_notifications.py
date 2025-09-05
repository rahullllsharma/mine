"""removed fcm_tokens from notifications

Revision ID: 06368ece1955
Revises: 85579292418f
Create Date: 2024-11-04 12:27:12.193700

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "06368ece1955"
down_revision = "85579292418f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("notifications", "fcm_token")


def downgrade() -> None:
    pass
