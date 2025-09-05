"""Add key PRIMARY_FIRE_SUPRESSION_LOCATION in enum for LocationType

Revision ID: db867046a4ba
Revises: 5720436091b0
Create Date: 2025-09-01 13:19:15.632630

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "db867046a4ba"
down_revision = "5720436091b0"
branch_labels = None
depends_on = None


ENUM_TYPE = "location_type"
ENUM_VALUE = "primary_fire_supression_location"


def upgrade() -> None:
    # Add the enum value safely using IF NOT EXISTS
    # This prevents errors if the value already exists
    op.execute(f"ALTER TYPE {ENUM_TYPE} ADD VALUE IF NOT EXISTS '{ENUM_VALUE}'")


def downgrade() -> None:
    # PostgreSQL doesn't support removing enum values directly
    # We need to recreate the enum type without the new value

    # Create new enum type without PRIMARY_FIRE_SUPRESSION_LOCATION
    op.execute(
        f"CREATE TYPE {ENUM_TYPE}_new AS ENUM ('first_aid_location','aed_location', 'burn_kit_location')"
    )

    # Update the table to use the new enum type
    op.execute(
        f"""
            ALTER TABLE first_aid_aed_locations
            ALTER COLUMN location_type TYPE {ENUM_TYPE}_new
            USING location_type::text::{ENUM_TYPE}_new
        """
    )

    # Drop the old enum type and rename the new one
    op.execute(f"DROP TYPE {ENUM_TYPE}")
    op.execute(f"ALTER TYPE {ENUM_TYPE}_new RENAME TO {ENUM_TYPE}")
