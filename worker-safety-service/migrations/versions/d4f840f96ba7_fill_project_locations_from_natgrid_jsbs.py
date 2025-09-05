"""Fill project_locations from natgrid_jsbs

Revision ID: d4f840f96ba7
Revises: 7fb47f093f1a
Create Date: 2025-05-29 21:51:47.396061

"""

import json
import uuid

import sqlalchemy as sa
from alembic import op

from worker_safety_service.models.concepts import FormStatus

# revision identifiers, used by Alembic.
revision = "d4f840f96ba7"
down_revision = "7fb47f093f1a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    result = conn.execute(
        sa.text(
            """
        SELECT id, contents, tenant_id, status
        FROM natgrid_jsbs
    """
        )
    )

    rows = result.fetchall()

    for row in rows:
        contents = row["contents"]
        if isinstance(contents, str):
            contents = json.loads(contents)
        work_locs = contents.get("work_location_with_voltage_info")
        if not work_locs or not isinstance(work_locs, list):
            continue

        # If status is 'complete', get supervisor_id from the nested JSON path
        supervisor_id = None
        if row["status"] == FormStatus.COMPLETE.value:
            try:
                supervisor_id = (
                    contents.get("supervisor_sign_off", {})
                    .get("supervisor", {})
                    .get("supervisor_info", {})
                    .get("id")
                )
            except Exception:
                supervisor_id = None

        tenant_id = row["tenant_id"]

        for work_loc in work_locs:
            name = work_loc.get("address")
            geom = work_loc.get("gps_coordinates")

            if geom and isinstance(geom, dict):
                point_wkt = f"POINT({geom['longitude']} {geom['latitude']})"
            else:
                point_wkt = None

            # Check for existing location with same name, address, and coordinates
            exists = False
            if point_wkt:
                check = conn.execute(
                    sa.text(
                        """
                    SELECT id FROM project_locations
                    WHERE name = :name
                      AND ST_Equals(geom, ST_GeomFromText(:geom, 4326))
                """
                    ),
                    {"name": name, "geom": point_wkt},
                ).fetchone()
                if check:
                    exists = True

            if exists:
                continue

            new_id = str(uuid.uuid4())

            # Checking for non-null constraint should not violate
            if name and geom and tenant_id:
                conn.execute(
                    sa.text(
                        """
                    INSERT INTO project_locations (
                        id, name, project_id, archived_at, supervisor_id, additional_supervisor_ids,
                        geom, external_key, tenant_id, address, clustering, risk
                    ) VALUES (
                        :id, :name, :project_id, NULL, :supervisor_id, :additional_supervisor_ids,
                        ST_GeomFromText(:geom, 4326), :external_key, :tenant_id, :address, :clustering, :risk
                    )
                """
                    ),
                    {
                        "id": new_id,
                        "name": name,
                        "project_id": None,
                        "archived_at": None,
                        "supervisor_id": supervisor_id,
                        "additional_supervisor_ids": [],
                        "geom": point_wkt,
                        "external_key": None,
                        "tenant_id": str(tenant_id),
                        "address": None,
                        "clustering": [None] * 13,
                        "risk": "unknown",
                    },
                )


def downgrade() -> None:
    # Downgrade is not implemented as the data is not reversible.
    pass
