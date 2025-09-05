"""Change default value for hazards image_url

Revision ID: be21d4124545
Revises: cdea177e28c6
Create Date: 2023-10-16 15:36:09.331345

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "be21d4124545"
down_revision = "cdea177e28c6"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "library_hazards",
        "image_url",
        existing_type=sa.String(),
        nullable=False,
        server_default="https://storage.googleapis.com/worker-safety-public-icons/DefaultHazardIcon.svg",
    )


def downgrade():
    # No need to undo this action
    pass
