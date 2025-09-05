"""fix-nearest-medical-facility-jsb-data

Revision ID: 474865497419
Revises: e5c34346547a
Create Date: 2024-07-19 17:09:02.059399

"""
import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "474865497419"
down_revision = "e5c34346547a"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()

    jsbs = connection.execute(sa.text("SELECT id,contents FROM public.jsbs"))

    for jsb in jsbs:
        contents = jsb.contents
        if (
            contents
            and "customNearestMedicalFacility" in contents
            and "address" in contents["customNearestMedicalFacility"]
            and (
                contents["customNearestMedicalFacility"]["address"] is None
                or contents["customNearestMedicalFacility"]["address"] == ""
            )
        ):
            raw_contents = json.dumps(contents)
            contents["customNearestMedicalFacility"]["address"] = "Not specified"
            connection.execute(
                sa.text("UPDATE public.jsbs SET contents=:contents WHERE id=:id;"),
                {"id": jsb.id, "contents": raw_contents},
            )


def downgrade():
    pass
