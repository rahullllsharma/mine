"""add_form_filters_to_user_preferences

Revision ID: ff29dc0c207d
Revises: 98fabf1f8311
Create Date: 2024-05-14 00:17:17.093788

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "ff29dc0c207d"
down_revision = "98fabf1f8311"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(text("ALTER TYPE userpreferenceentitytype ADD VALUE 'form_filters'"))


def downgrade() -> None:
    pass
