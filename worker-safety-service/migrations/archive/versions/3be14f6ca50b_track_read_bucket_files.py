"""track read bucket files

Revision ID: 3be14f6ca50b
Revises: deca299cc7f2
Create Date: 2022-03-11 10:39:26.768934

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3be14f6ca50b"
down_revision = "deca299cc7f2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "parsed_files",
        sa.Column("timestamp_processed", sa.DateTime(timezone=True), nullable=False),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("file_path"),
    )


def downgrade() -> None:
    op.drop_table("parsed_files")
