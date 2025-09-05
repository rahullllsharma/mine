"""add applicability columns

Revision ID: 7781a9cbe140
Revises: 747ea3663220
Create Date: 2022-01-21 17:41:59.762277

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7781a9cbe140"
down_revision = "e43f87ea27ff"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # this assumes all existing hazards and controls to be applicable for Tasks
    op.add_column(
        "library_hazards", sa.Column("for_tasks", sa.Boolean(), nullable=True)
    )
    op.execute("UPDATE library_hazards SET for_tasks = true")
    op.alter_column("library_hazards", "for_tasks", nullable=False)
    op.add_column(
        "library_hazards",
        sa.Column("for_site_conditions", sa.Boolean(), nullable=True),
    )
    op.execute("UPDATE library_hazards SET for_site_conditions = false")
    op.alter_column("library_hazards", "for_site_conditions", nullable=False)

    op.add_column(
        "library_controls", sa.Column("for_tasks", sa.Boolean(), nullable=True)
    )
    op.execute("UPDATE library_controls SET for_tasks = true")
    op.alter_column("library_controls", "for_tasks", nullable=False)
    op.add_column(
        "library_controls",
        sa.Column("for_site_conditions", sa.Boolean(), nullable=True),
    )
    op.execute("UPDATE library_controls SET for_site_conditions = false")
    op.alter_column("library_controls", "for_site_conditions", nullable=False)


def downgrade() -> None:
    op.drop_column("library_hazards", "for_tasks")
    op.drop_column("library_hazards", "for_site_conditions")

    op.drop_column("library_controls", "for_tasks")
    op.drop_column("library_controls", "for_site_conditions")
