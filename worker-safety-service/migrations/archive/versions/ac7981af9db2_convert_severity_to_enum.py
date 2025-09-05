"""convert severity to enum

Revision ID: ac7981af9db2
Revises: b0acac878652
Create Date: 2023-02-14 19:06:09.847146

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "ac7981af9db2"
down_revision = "ef6d6330d23c"
branch_labels = None
depends_on = None

severities = [
    "Not Applicable",
    "Other non-occupational",
    "First Aid Only",
    "Report Purposes Only",
    "Restriction or job transfer",
    "Lost Time",
    "Near deaths",
    "Deaths",
]

conversion_map = {
    "not_applicable": "Not Applicable",
    "near_miss": "Other non-occupational",
    "first_aid": "First Aid Only",
    "recordable": "Report Purposes Only",
    "restricted": "Restriction or job transfer",
    "lost_time": "Lost Time",
    "p_sif": "Near deaths",
    "sif": "Deaths",
}


def upgrade():
    # create new enum data and column
    severities_str = ", ".join(map(lambda x: f"'{x}'", severities))
    op.execute(f"create type incident_severity_types as ENUM({severities_str})")
    op.execute(
        "alter table incidents add column severity_swap incident_severity_types;"
    )

    # convert existing data
    for key, value in conversion_map.items():
        op.execute(
            f"update incidents set severity_swap='{value}' where severity='{key}';"
        )

    # drop severities table data
    op.execute("alter table incidents drop column severity_id cascade;")
    op.execute("drop table incident_severities")

    # swap enum for old column name
    op.execute("alter table incidents drop column severity cascade;")
    op.execute("alter table incidents rename severity_swap to severity;")


def downgrade():
    # recreate old severities
    op.add_column(
        "incidents", sa.Column("severity_swap", sqlmodel.sql.sqltypes.AutoString())
    )
    for key, value in conversion_map.items():
        # swap key & value position to reverse the update
        op.execute(
            f"update incidents set severity_swap='{key}' where severity='{value}';"
        )

    # swap back
    op.execute("alter table incidents drop column severity cascade;")
    op.execute("drop type incident_severity_types")
    op.execute("alter table incidents rename severity_swap to severity")

    # recreate severities table & data
    op.create_table(
        "incident_severities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("weight", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(
        """
        INSERT INTO incident_severities (id, code, name, weight)
        VALUES
            (1, 'sif', 'Deaths', 10),
            (2, 'p_sif', 'Near Deaths', 20),
            (3, 'lost_time', 'Lost Time', 30),
            (4, 'restricted', 'Restriction or job transfer', 40),
            (5, 'recordable', 'Report Purposes Only', 50),
            (6, 'first_aid', 'First Aid Only', 60),
            (7, 'near_miss', 'Other Non-occupational', 70),
            (8, 'not_applicable', 'Not Applicable', 80)
        """
    )
    op.add_column("incidents", sa.Column("severity_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "incidents_severity_id_fk",
        "incidents",
        "incident_severities",
        ["severity_id"],
        ["id"],
    )
    op.create_index(
        "incidents_severity_id_ix", "incidents", ["severity_id"], unique=False
    )

    op.execute("update incidents set severity_id=1 where severity='sif';")
    op.execute("update incidents set severity_id=2 where severity='p_sif';")
    op.execute("update incidents set severity_id=3 where severity='lost_time';")
    op.execute("update incidents set severity_id=4 where severity='restricted';")
    op.execute("update incidents set severity_id=5 where severity='recordable';")
    op.execute("update incidents set severity_id=6 where severity='first_aid';")
    op.execute("update incidents set severity_id=7 where severity='near_miss';")
    op.execute("update incidents set severity_id=8 where severity='not_applicable';")
