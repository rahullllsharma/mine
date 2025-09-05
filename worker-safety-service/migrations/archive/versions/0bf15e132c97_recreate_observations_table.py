"""Recreate observations table

Revision ID: 0bf15e132c97
Revises: 26276323d067
Create Date: 2022-04-06 15:31:32.420263

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0bf15e132c97"
down_revision = "16dea8b8b9c3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "observations",
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
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("observation_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("observation_datetime", sa.DateTime(), nullable=True),
        sa.Column("action_datetime", sa.DateTime(), nullable=True),
        sa.Column("response_specific_action_datetime", sa.DateTime(), nullable=True),
        sa.Column("client_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("supervisor_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column(
            "contractor_involved_id", sqlmodel.sql.sqltypes.GUID(), nullable=True
        ),
        sa.Column("project_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("action_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "response_specific_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column(
            "observation_type", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column(
            "person_type_reporting", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("location_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("street", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("city", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("state", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("address", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("job_type_1", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("job_type_2", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("job_type_3", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("task_type", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("task_detail", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "observation_comments", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("action_type", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("action_category", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("action_topic", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("response", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "response_specific_action_comments",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
        ),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["contractor_involved_id"],
            ["contractor.id"],
        ),
        sa.ForeignKeyConstraint(
            ["supervisor_id"],
            ["supervisor.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.execute(
        """
insert into observations (timestamp_created, timestamp_updated, centroid_source, id, observation_id,
                          observation_datetime, action_datetime, response_specific_action_datetime, client_id,
                          supervisor_id, contractor_involved_id, project_id, action_id, response_specific_id,
                          observation_type, person_type_reporting, location_name, street, city, state, address,
                          latitude, longitude, job_type_1, job_type_2, job_type_3, task_type, task_detail,
                          observation_comments, action_type, action_category, action_topic, response,
                          response_specific_action_comments)
select timestamp_created,
       timestamp_updated,
       centroid_source,
       id::uuid,
       observation_id,
       observation_datetime,
       action_datetime,
       response_specific_action_datetime,
       client_id,
       supervisor_id,
       contractor_involved_id,
       project_id,
       action_id,
       response_specific_id,
       observation_type,
       person_type_reporting,
       location_name,
       street,
       city,
       state,
       address,
       latitude,
       longitude,
       job_type_1,
       job_type_2,
       job_type_3,
       task_type,
       task_detail,
       observation_comments,
       action_type,
       action_category,
       action_topic,
       response,
       response_specific_action_comments
from observation;
    """
    )

    op.drop_table("observation")


def downgrade():
    op.create_table(
        "observation",
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
        sa.Column("id", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("observation_id", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "timestamp_created",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "timestamp_updated",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "observation_datetime",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "action_datetime",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "response_specific_action_datetime",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("client_id", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "supervisor_id", postgresql.UUID(), autoincrement=False, nullable=True
        ),
        sa.Column("project_id", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("action_id", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "response_specific_id", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
        sa.Column("observation_type", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "person_type_reporting", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
        sa.Column("location_name", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("street", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("city", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("state", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("address", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "latitude",
            postgresql.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "longitude",
            postgresql.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("job_type_1", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("job_type_2", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("job_type_3", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("task_type", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("task_detail", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "observation_comments", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
        sa.Column("action_type", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("action_category", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("action_topic", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("response", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "response_specific_action_comments",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "contractor_involved_id",
            postgresql.UUID(),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["contractor_involved_id"],
            ["contractor.id"],
            name="observation_contractor_involved_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["supervisor_id"], ["supervisor.id"], name="observation_supervisor_id_fkey"
        ),
        sa.PrimaryKeyConstraint("observation_id", name="observation_pkey"),
    )
    op.drop_table("observations")
