"""Recreate incidents and incident task link

Revision ID: 2aa18ff45c11
Revises: 69c7656bd2ea
Create Date: 2022-04-06 13:57:03.824089

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2aa18ff45c11"
down_revision = "56eca4b5b94b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "incidents",
        sa.Column("timestamp_created", sa.DateTime(timezone=True), nullable=True),
        sa.Column("timestamp_updated", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "centroid_source",
            postgresql.ENUM(
                "centroid_from_client",
                "centroid_from_geocoder",
                "centroid_from_polygo",
                "centroid_from_bounding_box",
                name="centroidtype",
                create_type=False,
            ),
            nullable=True,
        ),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("client_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("incident_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("supervisor_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("project_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("contractor_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("incident_type", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("incident_datetime", sa.DateTime(), nullable=False),
        sa.Column("street_number", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("street", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("city", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("state", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("zipcode", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("address", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("north_latitude", sa.Float(), nullable=True),
        sa.Column("west_longitude", sa.Float(), nullable=True),
        sa.Column("south_latitude", sa.Float(), nullable=True),
        sa.Column("east_longitude", sa.Float(), nullable=True),
        sa.Column(
            "person_impacted_type", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("person_impacted", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "location_description", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("job_type_1", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("job_type_2", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("job_type_3", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "environmental_outcome", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column(
            "person_impacted_severity_outcome",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
        ),
        sa.Column(
            "motor_vehicle_outcome", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column(
            "inferred_work_start_date_confidence",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
        ),
        sa.Column("public_outcome", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("asset_outcome", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("task_type", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.ForeignKeyConstraint(
            ["contractor_id"],
            ["contractor.id"],
        ),
        sa.ForeignKeyConstraint(
            ["supervisor_id"],
            ["supervisor.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.execute(
        "insert into incidents(centroid_source, id, client_id, incident_id, supervisor_id, project_id, timestamp_created, timestamp_updated, incident_type, incident_datetime, street_number, street, city, state, zipcode, address, latitude, longitude, north_latitude, west_longitude, south_latitude, east_longitude, person_impacted_type, person_impacted, location_description, job_type_1, job_type_2, job_type_3, environmental_outcome, person_impacted_severity_outcome, motor_vehicle_outcome, inferred_work_start_date_confidence, public_outcome, asset_outcome, task_type, description, contractor_id) select centroid_source, id::uuid, client_id, incident_id, supervisor_id, project_id, timestamp_created, timestamp_updated, incident_type, incident_datetime, street_number, street, city, state, zipcode, address, latitude, longitude, north_latitude, west_longitude, south_latitude, east_longitude, person_impacted_type, person_impacted, location_description, job_type_1, job_type_2, job_type_3, environmental_outcome, person_impacted_severity_outcome, motor_vehicle_outcome, inferred_work_start_date_confidence, public_outcome, asset_outcome, task_type, description, contractor_id from raw_incidents"
    )

    op.create_table(
        "incident_task_link",
        sa.Column("incident_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("library_task_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["incident_id"],
            ["incidents.id"],
        ),
        sa.ForeignKeyConstraint(
            ["library_task_id"],
            ["library_tasks.id"],
        ),
        sa.PrimaryKeyConstraint("incident_id", "library_task_id"),
    )

    op.execute(
        "insert into incident_task_link (incident_id, library_task_id) select i.id, it.library_task_id from incidents i inner join incident_tasks it on i.incident_id = it.incident_id;"
    )

    op.drop_table("incident_tasks")
    op.drop_table("raw_incidents")


def downgrade():
    pass
    # ### commands auto generated by Alembic - please adjust! ###
    # op.create_table(
    #     "raw_incidents",
    #     sa.Column(
    #         "centroid_source",
    #         postgresql.ENUM(
    #             "centroid_from_client",
    #             "centroid_from_geocoder",
    #             "centroid_from_polygo",
    #             "centroid_from_bounding_box",
    #             name="centroidtype",
    #         ),
    #         autoincrement=False,
    #         nullable=True,
    #     ),
    #     sa.Column("id", sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.Column("client_id", sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.Column("incident_id", sa.VARCHAR(), autoincrement=False, nullable=False),
    #     sa.Column(
    #         "supervisor_id", postgresql.UUID(), autoincrement=False, nullable=True
    #     ),
    #     sa.Column("project_id", sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.Column(
    #         "timestamp_created",
    #         postgresql.TIMESTAMP(timezone=True),
    #         autoincrement=False,
    #         nullable=True,
    #     ),
    #     sa.Column(
    #         "timestamp_updated",
    #         postgresql.TIMESTAMP(timezone=True),
    #         autoincrement=False,
    #         nullable=True,
    #     ),
    #     sa.Column("incident_type", sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.Column(
    #         "incident_datetime",
    #         postgresql.TIMESTAMP(),
    #         autoincrement=False,
    #         nullable=False,
    #     ),
    #     sa.Column("street_number", sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.Column("street", sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.Column("city", sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.Column("state", sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.Column("zipcode", sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.Column("address", sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.Column(
    #         "latitude",
    #         postgresql.DOUBLE_PRECISION(precision=53),
    #         autoincrement=False,
    #         nullable=True,
    #     ),
    #     sa.Column(
    #         "longitude",
    #         postgresql.DOUBLE_PRECISION(precision=53),
    #         autoincrement=False,
    #         nullable=True,
    #     ),
    #     sa.Column(
    #         "north_latitude",
    #         postgresql.DOUBLE_PRECISION(precision=53),
    #         autoincrement=False,
    #         nullable=True,
    #     ),
    #     sa.Column(
    #         "west_longitude",
    #         postgresql.DOUBLE_PRECISION(precision=53),
    #         autoincrement=False,
    #         nullable=True,
    #     ),
    #     sa.Column(
    #         "south_latitude",
    #         postgresql.DOUBLE_PRECISION(precision=53),
    #         autoincrement=False,
    #         nullable=True,
    #     ),
    #     sa.Column(
    #         "east_longitude",
    #         postgresql.DOUBLE_PRECISION(precision=53),
    #         autoincrement=False,
    #         nullable=True,
    #     ),
    #     sa.Column(
    #         "person_impacted_type", sa.VARCHAR(), autoincrement=False, nullable=True
    #     ),
    #     sa.Column("person_impacted", sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.Column(
    #         "location_description", sa.VARCHAR(), autoincrement=False, nullable=True
    #     ),
    #     sa.Column("job_type_1", sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.Column("job_type_2", sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.Column("job_type_3", sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.Column(
    #         "environmental_outcome", sa.VARCHAR(), autoincrement=False, nullable=True
    #     ),
    #     sa.Column(
    #         "person_impacted_severity_outcome",
    #         sa.VARCHAR(),
    #         autoincrement=False,
    #         nullable=True,
    #     ),
    #     sa.Column(
    #         "motor_vehicle_outcome", sa.VARCHAR(), autoincrement=False, nullable=True
    #     ),
    #     sa.Column(
    #         "inferred_work_start_date_confidence",
    #         sa.VARCHAR(),
    #         autoincrement=False,
    #         nullable=True,
    #     ),
    #     sa.Column("public_outcome", sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.Column("asset_outcome", sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.Column("task_type", sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.Column("description", sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.Column(
    #         "contractor_id", postgresql.UUID(), autoincrement=False, nullable=True
    #     ),
    #     sa.ForeignKeyConstraint(
    #         ["contractor_id"],
    #         ["contractor.id"],
    #         name="raw_incidents_contractor_id_fkey",
    #     ),
    #     sa.ForeignKeyConstraint(
    #         ["supervisor_id"],
    #         ["supervisor.id"],
    #         name="raw_incidents_supervisor_id_fkey",
    #     ),
    #     sa.PrimaryKeyConstraint("incident_id", name="raw_incidents_pkey"),
    #     postgresql_ignore_search_path=False,
    # )
    # op.create_table(
    #     "incident_tasks",
    #     sa.Column("incident_id", sa.VARCHAR(), autoincrement=False, nullable=False),
    #     sa.Column(
    #         "library_task_id", postgresql.UUID(), autoincrement=False, nullable=False
    #     ),
    #     sa.ForeignKeyConstraint(
    #         ["incident_id"],
    #         ["raw_incidents.incident_id"],
    #         name="incident_tasks_incident_id_fkey",
    #     ),
    #     sa.ForeignKeyConstraint(
    #         ["library_task_id"],
    #         ["library_tasks.id"],
    #         name="incident_tasks_library_task_id_fkey",
    #     ),
    #     sa.PrimaryKeyConstraint(
    #         "incident_id", "library_task_id", name="incident_tasks_pkey"
    #     ),
    # )
    # op.drop_table("incident_task_link")
    # op.drop_table("incidents")
    # ### end Alembic commands ###
