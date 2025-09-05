"""add MAD values corresponding to voltages for N

Revision ID: f0c5bb7cf1b7
Revises: fa6813629335
Create Date: 2025-03-25 12:03:58.758494

"""
import json
import uuid

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f0c5bb7cf1b7"
down_revision = "fa6813629335"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    location_ny = "New York"
    location_ne = "New England"
    mad = [
        {
            "location": location_ny,
            "id": str(uuid.uuid4()),
            "voltages": "NY 50 V - 300 V",
            "phase_to_ground": "Avoid Contact",
            "phase_to_phase": "Avoid Contact",
        },
        {
            "location": location_ny,
            "id": str(uuid.uuid4()),
            "voltages": "NY 301 V - 750 V",
            "phase_to_ground": '12"',
            "phase_to_phase": '12"',
        },
        {
            "location": location_ny,
            "id": str(uuid.uuid4()),
            "voltages": "NY 751 V - 1 KV",
            "phase_to_ground": '24"',
            "phase_to_phase": '24"',
        },
        {
            "location": location_ny,
            "id": str(uuid.uuid4()),
            "voltages": "NY 1,001 V - 15 KV",
            "phase_to_ground": '26"',
            "phase_to_phase": '27"',
        },
        {
            "location": location_ny,
            "id": str(uuid.uuid4()),
            "voltages": "NY 23 KV",
            "phase_to_ground": "3'",
            "phase_to_phase": "3'",
        },
        {
            "location": location_ny,
            "id": str(uuid.uuid4()),
            "voltages": "NY 34.5 KV",
            "phase_to_ground": "3'",
            "phase_to_phase": "3'",
        },
        {
            "location": location_ny,
            "id": str(uuid.uuid4()),
            "voltages": "NY 46 KV",
            "phase_to_ground": "4'",
            "phase_to_phase": "4'",
        },
        {
            "location": location_ny,
            "id": str(uuid.uuid4()),
            "voltages": "NY 69 KV",
            "phase_to_ground": "4'",
            "phase_to_phase": "4'",
        },
        {
            "location": location_ny,
            "id": str(uuid.uuid4()),
            "voltages": "NY 115 KV*",
            "phase_to_ground": "5'",
            "phase_to_phase": "5'",
        },
        {
            "location": location_ny,
            "id": str(uuid.uuid4()),
            "voltages": "NY 230 KV*",
            "phase_to_ground": "7'",
            "phase_to_phase": "7'6\"",
        },
        {
            "location": location_ny,
            "id": str(uuid.uuid4()),
            "voltages": "NY 345 KV*",
            "phase_to_ground": "9'",
            "phase_to_phase": "12'6\"",
        },
        {
            "location": location_ne,
            "id": str(uuid.uuid4()),
            "voltages": "NE 50 – 300",
            "phase_to_ground": "Avoid Contact",
            "phase_to_phase": "Avoid Contact",
        },
        {
            "location": location_ne,
            "id": str(uuid.uuid4()),
            "voltages": "NE 301 – 750",
            "phase_to_ground": '13" (1\'-1")',
            "phase_to_phase": '13" (1\'-1")',
        },
        {
            "location": location_ne,
            "id": str(uuid.uuid4()),
            "voltages": "NE 751 – 15,000",
            "phase_to_ground": '26" (2\'-2")',
            "phase_to_phase": '27" (2\'-3")',
        },
        {
            "location": location_ne,
            "id": str(uuid.uuid4()),
            "voltages": "NE 15,001 – 36,000",
            "phase_to_ground": '31" (2\'-7")',
            "phase_to_phase": '35" (2\'-11")',
        },
        {
            "location": location_ne,
            "id": str(uuid.uuid4()),
            "voltages": "NE 36,001 – 46,000",
            "phase_to_ground": '34" (2\'-10")',
            "phase_to_phase": '39" (3\'-3")',
        },
        {
            "location": location_ne,
            "id": str(uuid.uuid4()),
            "voltages": "NE 46,001 – 72,500",
            "phase_to_ground": '40" (3\'-4")',
            "phase_to_phase": '48" (4\'-0")',
        },
        {
            "location": location_ne,
            "id": str(uuid.uuid4()),
            "voltages": "NE 72,500 – 121,000",
            "phase_to_ground": '38" (3\'-2")',
            "phase_to_phase": '51" (4\'-3")',
        },
        {
            "location": location_ne,
            "id": str(uuid.uuid4()),
            "voltages": "NE 230,000 – 242,000",
            "phase_to_ground": '63" (5\'3")',
            "phase_to_phase": '90" (7\'-6")',
        },
        {
            "location": location_ne,
            "id": str(uuid.uuid4()),
            "voltages": "NE 345,000 – 362,000",
            "phase_to_ground": '102" (8\'-6")',
            "phase_to_phase": '150" (12\'-6")',
        },
    ]
    mad_links = [
        {
            "url": "https://storage.googleapis.com/worker-safety-public-bucket/natgrid/pdf/jsb/NE%20MAD%20Tables%20-%20Employee%20Safety%20Handbook_final.pdf",
            "description": "New England MAD Table",
            "id": str(uuid.uuid4()),
        },
        {
            "url": "https://storage.googleapis.com/worker-safety-public-bucket/natgrid/pdf/jsb/NY%20MAD%20Tables%20-%20Employee%20Safety%20Handbook_final.pdf",
            "description": "New York MAD Table",
            "id": str(uuid.uuid4()),
        },
    ]
    query = """
            SELECT id, contents
            FROM uiconfigs
            WHERE form_type = 'natgrid_job_safety_briefing';
        """
    sql = sa.text(query)
    rows = connection.execute(sql)
    for r in rows:
        contents = r.contents
        if isinstance(contents, str):
            contents = json.loads(contents)
        if contents:
            contents["minimum_approach_distances"] = mad
            contents["minimum_approach_distances_links"] = mad_links
            updated_contents = json.dumps(contents)
            connection.execute(
                sa.text("UPDATE uiconfigs SET contents=:contents WHERE id=:id"),
                {"id": r.id, "contents": updated_contents},
            )


def downgrade() -> None:
    op.execute(
        """
            UPDATE uiconfigs
            SET contents = contents - 'minimum_approach_distances' - 'minimum_approach_distances_links'
            WHERE form_type = 'natgrid_job_safety_briefing';
        """
    )
