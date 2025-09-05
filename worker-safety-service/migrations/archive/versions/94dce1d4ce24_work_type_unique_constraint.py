"""work_type_unique_constraint

Revision ID: 94dce1d4ce24
Revises: bc639a411cc2
Create Date: 2022-10-10 20:04:32.315160

"""

from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "94dce1d4ce24"
down_revision = "bc639a411cc2"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "library_tasks", "work_type_id", existing_type=postgresql.UUID(), nullable=False
    )
    op.create_unique_constraint("work_types_name_key", "work_types", ["name"])


def downgrade():
    op.drop_constraint("work_types_name_key", "work_types", type_="unique")
    op.alter_column(
        "library_tasks", "work_type_id", existing_type=postgresql.UUID(), nullable=True
    )
