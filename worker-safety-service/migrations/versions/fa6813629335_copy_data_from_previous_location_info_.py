"""copy data from previous location info for new field in Location information

Revision ID: fa6813629335
Revises: 7a5cf66a8c85
Create Date: 2025-03-19 14:11:53.377445

"""
import datetime
import json
import uuid
from typing import Dict, Optional

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fa6813629335"
down_revision = "2835336ccda3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    # Get all rows with non-null content
    query = "SELECT id, contents FROM public.natgrid_jsbs WHERE contents IS NOT NULL AND contents->>'work_location' IS NOT NULL;"
    sql = sa.text(query)
    rows = connection.execute(sql)
    for row in rows:
        contents = row.contents
        if isinstance(contents, str):
            contents = json.loads(contents)
        if contents:
            work_location = contents.get("work_location", None)
            voltage_information = contents.get("voltage_info", None)
            gps_coordinates = contents.get("gps_coordinates", None)
            medical_information = contents.get("medical_information", None)
            if work_location:
                new_work_location = []
                new_work_location_json = {
                    "created_at": datetime.datetime.now().isoformat(),
                    "city": work_location.get("city", None),
                    "state": work_location.get("state", None),
                    "address": work_location.get("address", None),
                    "landmark": work_location.get("landmark", None),
                    "operating_hq": work_location.get("operating_hq", None),
                }
                if voltage_information:
                    new_work_location_json["circuit"] = voltage_information.get(
                        "circuit", None
                    )
                    voltage_information_json = {
                        "voltage": {
                            "id": str(uuid.uuid4()),
                            "value": voltage_information.get("voltages", None),
                            "other": True,
                        },
                        "minimum_approach_distance": {
                            "phase_to_phase": work_location.get(
                                "minimum_approach_distance", None
                            ),
                            "phase_to_ground": None,
                        },
                    }
                    new_work_location_json[
                        "voltage_information"
                    ] = voltage_information_json

                gps_coordinates_json: Optional[Dict[str, float]] = None
                if gps_coordinates:
                    gps_coordinates_json = {}
                    for item in gps_coordinates:
                        latitude = item.get("latitude")
                        longitude = item.get("longitude")
                        if not latitude or not longitude:
                            gps_coordinates_json = None
                            break
                        gps_coordinates_json = {
                            "latitude": latitude,
                            "longitude": longitude,
                        }
                    new_work_location_json["gps_coordinates"] = gps_coordinates_json
                new_work_location.append(new_work_location_json)
                contents["work_location_with_voltage_info"] = new_work_location
                if work_location["vehicle_number"]:
                    medical_information["vehicle_number"] = work_location[
                        "vehicle_number"
                    ]
                    contents["medical_information"] = medical_information
                updated_contents = json.dumps(contents)
                connection.execute(
                    sa.text(
                        "UPDATE public.natgrid_jsbs SET contents=:contents WHERE id=:id"
                    ),
                    {"id": row.id, "contents": updated_contents},
                )


def downgrade() -> None:
    query = """
        UPDATE public.natgrid_jsbs
        SET contents = contents - 'work_location_with_voltage_info'
        WHERE contents ? 'work_location_with_voltage_info';
    """
    sql = sa.text(query)
    op.execute(sql)
