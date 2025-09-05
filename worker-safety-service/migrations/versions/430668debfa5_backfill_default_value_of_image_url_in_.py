"""backfill default value of image_url in library hazards table

Revision ID: 430668debfa5
Revises: be21d4124545
Create Date: 2023-10-17 15:15:59.520609

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "430668debfa5"
down_revision = "be21d4124545"
branch_labels = None
depends_on = None


def upgrade():
    # Update the values in the 'image_url' column
    op.execute(
        "UPDATE library_hazards SET image_url = 'https://storage.googleapis.com/worker-safety-public-icons/DefaultHazardIcon.svg' WHERE image_url = 'https://restore-build-artefacts.s3.amazonaws.com/default_image.svg'"
    )


def downgrade():
    # No need to undo this action
    pass
