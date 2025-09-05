"""Relax Supervisor constraints

Revision ID: 56eca4b5b94b
Revises: 2c17e3a05ff9
Create Date: 2022-04-06 14:50:01.028494

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "56eca4b5b94b"
down_revision = "2c17e3a05ff9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # supervisor.id is already the primary key
    # TODO: later on, add unique constraint for name+tenant
    op.drop_constraint("supervisor_name_key", "supervisor", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint("supervisor_name_key", "supervisor", ["name"])
