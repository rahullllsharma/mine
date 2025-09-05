"""contractor aliases

Revision ID: 9e888d47f36d
Revises: 63180023baac
Create Date: 2022-02-22 15:52:14.412698

"""

import sqlalchemy as sa
from alembic import op
from sqlmodel import sql

# revision identifiers, used by Alembic.
revision = "9e888d47f36d"
down_revision = "63180023baac"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("contractor", sa.Column("needs_review", sa.Boolean(), nullable=True))
    op.execute("UPDATE contractor SET needs_review = false;")
    op.alter_column("contractor", "needs_review", nullable=False)

    op.create_table(
        "contractor_aliases",
        sa.Column("contractor_id", sql.sqltypes.GUID(), nullable=False),
        sa.Column("alias", sql.sqltypes.AutoString(), nullable=False, unique=True),
        sa.ForeignKeyConstraint(
            ["contractor_id"],
            ["contractor.id"],
        ),
    )
    op.execute(
        "INSERT INTO public.contractor_aliases (alias, contractor_id) SELECT name, id FROM public.contractor;"
    )


def downgrade() -> None:
    op.drop_table("contractor_aliases")

    op.drop_column("contractor", "needs_review")
