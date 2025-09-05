"""Update manually added sc index to use new field

Revision ID: 8c5e9568ba61
Revises: c12d391017bc
Create Date: 2023-08-24 14:48:36.238877

"""
from uuid import UUID

from alembic import op
from sqlalchemy import text
from sqlalchemy.engine.row import Row

# revision identifiers, used by Alembic.
revision = "8c5e9568ba61"
down_revision = "c12d391017bc"
branch_labels = None
depends_on = None


def get_locations_with_duplicate_manual_site_conditions() -> list[Row]:
    conn = op.get_bind()
    locations_with_duplicate_site_conditions = conn.execute(
        text(
            """
    SELECT location_id, library_site_condition_id FROM public.site_conditions
    GROUP BY location_id, library_site_condition_id, is_manually_added, archived_at
    HAVING is_manually_added IS TRUE AND archived_at IS NULL AND COUNT(*) > 1;
"""
        )
    )

    return list(locations_with_duplicate_site_conditions)


def archive_duplicate_manual_site_conditions(
    location_id: UUID, library_site_condition_id: UUID
) -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            f"""
    UPDATE public.site_conditions
    SET archived_at = CURRENT_TIMESTAMP
    WHERE id IN (SELECT id
        FROM site_conditions
        WHERE is_manually_added IS TRUE
            AND location_id = '{location_id}'
            AND library_site_condition_id = '{library_site_condition_id}'
            AND archived_at IS NULL
        OFFSET 1);
"""
        )
    )


def upgrade():
    # It is possible that some environments contain duplicate
    # manually added Site Conditions since the definition of a
    # manually added Site Condition has changed. This will clean
    # the data before adding the new constraint
    locations_with_duplicate_site_conditions = (
        get_locations_with_duplicate_manual_site_conditions()
    )

    for row in locations_with_duplicate_site_conditions:
        archive_duplicate_manual_site_conditions(
            row.location_id, row.library_site_condition_id
        )

    op.drop_index("site_conditions_manual_idx", table_name="site_conditions")
    op.drop_index("site_conditions_manually_key", table_name="site_conditions")
    op.create_index(
        "site_condition_manual_idx",
        "site_conditions",
        ["location_id"],
        unique=False,
        postgresql_where="is_manually_added IS TRUE",
    )
    op.create_index(
        "site_condition_manually_key",
        "site_conditions",
        ["location_id", "library_site_condition_id"],
        unique=True,
        postgresql_where=text("is_manually_added IS true AND archived_at IS NULL"),
    )


def downgrade():
    op.drop_index(
        "site_condition_manually_key",
        table_name="site_conditions",
        postgresql_where=text("is_manually_added IS true AND archived_at IS NULL"),
    )
    op.drop_index(
        "site_condition_manual_idx",
        table_name="site_conditions",
        postgresql_where="is_manually_added IS TRUE",
    )
    op.create_index(
        "site_conditions_manually_key",
        "site_conditions",
        ["location_id", "library_site_condition_id"],
        unique=False,
    )
    op.create_index(
        "site_conditions_manual_idx", "site_conditions", ["location_id"], unique=False
    )
