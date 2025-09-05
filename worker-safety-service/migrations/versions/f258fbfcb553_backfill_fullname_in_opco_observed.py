"""backfill fullname in opco observed

Revision ID: f258fbfcb553
Revises: f49079be7db1
Create Date: 2024-04-12 14:55:31.073827

"""

import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f258fbfcb553"
down_revision = "f49079be7db1"
branch_labels = None
depends_on = None

opco_name_mapping = {
    "BGE": "Baltimore Gas & Electric Co",
    "ComEd": "ComEd",
    "Corporate": "Exelon Business Servcs Co, LLC",
    "PECO": "PECO Energy Company",
    "PHI": "PHI Service Company",
    "ACE": "Atlantic City Electric Co",
    "DPL": "Delmarva Power & Light Co",
    "PEP": "Potomac Electric Power Co",
}


def upgrade():
    connection = op.get_bind()
    query = """
    SELECT id, contents
    FROM public.energy_based_observations;
    """

    sql = sa.text(query)
    rows = connection.execute(sql)

    for row in rows:
        contents = row.contents
        if isinstance(contents, str):
            contents = json.loads(contents)
        if contents:
            details = contents.get("details", {}) or {}
            opco_observed = details.get("opco_observed", None)
            if opco_observed and "name" in opco_observed:
                name = opco_observed["name"]
                full_name = opco_name_mapping.get(name)
                if full_name:
                    opco_observed["full_name"] = full_name
                    updated_contents = json.dumps(contents)
                    connection.execute(
                        sa.text(
                            "UPDATE public.energy_based_observations SET contents=:contents WHERE id=:id"
                        ),
                        {"id": row.id, "contents": updated_contents},
                    )


def downgrade():
    connection = op.get_bind()
    query = """
    SELECT id, contents
    FROM public.energy_based_observations;
    """

    sql = sa.text(query)
    rows = connection.execute(sql)

    for row in rows:
        contents = row.contents
        if isinstance(contents, str):
            contents = json.loads(contents)
        if contents:
            details = contents.get("details", {}) or {}
            opco_observed = details.get("opco_observed", None)
            if opco_observed and "full_name" in opco_observed:
                del opco_observed["full_name"]
                updated_contents = json.dumps(contents)
                connection.execute(
                    sa.text(
                        "UPDATE public.energy_based_observations SET contents=:contents WHERE id=:id"
                    ),
                    {"id": row.id, "contents": updated_contents},
                )
