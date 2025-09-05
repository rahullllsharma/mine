"""added cwf filters entity in user_preferences

Revision ID: a3ee7f1cadbb
Revises: f0c5bb7cf1b7
Create Date: 2025-04-23 13:02:35.538332

"""

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "a3ee7f1cadbb"
down_revision = "f0c5bb7cf1b7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text("ALTER TYPE userpreferenceentitytype ADD VALUE 'cwf_template_filters'")
    )
    conn.execute(
        text(
            "ALTER TYPE userpreferenceentitytype ADD VALUE 'cwf_template_form_filters'"
        )
    )


def downgrade() -> None:
    pass
