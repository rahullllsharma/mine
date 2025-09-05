"""Lat/lon to decimal

Revision ID: 3d5b6f908bcf
Revises: 0830b21df248
Create Date: 2022-06-22 12:03:17.878005

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "3d5b6f908bcf"
down_revision = "0830b21df248"
branch_labels = None
depends_on = None


def upgrade():
    # Make sure lat/lon are valid
    query = "SELECT id, latitude, longitude FROM project_locations"
    for item in op.get_bind().execute(text(query)).fetchall():
        to_update = {}
        try:
            latitude = float(item.latitude)
            if latitude > 90:
                to_update["latitude"] = "90"
            elif latitude < -90:
                to_update["latitude"] = "-90"
        except:  # noqa: E722 B001
            to_update["latitude"] = "0"

        try:
            longitude = float(item.longitude)
            if longitude > 180:
                to_update["longitude"] = "180"
            elif longitude < -180:
                to_update["longitude"] = "-180"
        except:  # noqa: E722 B001
            to_update["longitude"] = "0"

        if to_update:
            update_columns = ", ".join(
                f"{column} = :{column}" for column in to_update.keys()
            )
            query = (
                f"UPDATE project_locations SET {update_columns} WHERE id = '{item.id}'"
            )
            op.get_bind().execute(text(query), to_update)

    op.execute(
        "ALTER TABLE project_locations ALTER COLUMN latitude TYPE numeric(14,12) USING CAST(latitude as numeric)"
    )
    op.execute(
        "ALTER TABLE project_locations ALTER COLUMN longitude TYPE numeric(15,12) USING CAST(longitude as numeric)"
    )


def downgrade():
    op.execute("ALTER TABLE project_locations ALTER COLUMN latitude TYPE varchar")
    op.execute("ALTER TABLE project_locations ALTER COLUMN longitude TYPE varchar")
