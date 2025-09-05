"""Clear tables indexes

Revision ID: 1b1325849463
Revises: b6f966f4d7f7
Create Date: 2022-01-17 17:16:06.194504

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "1b1325849463"
down_revision = "b6f966f4d7f7"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index("ix_observation_action_category", table_name="observation")
    op.drop_index("ix_observation_action_datetime", table_name="observation")
    op.drop_index("ix_observation_action_id", table_name="observation")
    op.drop_index("ix_observation_action_topic", table_name="observation")
    op.drop_index("ix_observation_action_type", table_name="observation")
    op.drop_index("ix_observation_address", table_name="observation")
    op.drop_index("ix_observation_city", table_name="observation")
    op.drop_index("ix_observation_client_id", table_name="observation")
    op.drop_index("ix_observation_contractor_involved", table_name="observation")
    op.drop_index("ix_observation_id", table_name="observation")
    op.drop_index("ix_observation_job_type_1", table_name="observation")
    op.drop_index("ix_observation_job_type_2", table_name="observation")
    op.drop_index("ix_observation_job_type_3", table_name="observation")
    op.drop_index("ix_observation_latitude", table_name="observation")
    op.drop_index("ix_observation_location_name", table_name="observation")
    op.drop_index("ix_observation_longitude", table_name="observation")
    op.drop_index("ix_observation_observation_comments", table_name="observation")
    op.drop_index("ix_observation_observation_datetime", table_name="observation")
    op.drop_index("ix_observation_observation_id", table_name="observation")
    op.drop_index("ix_observation_observation_type", table_name="observation")
    op.drop_index("ix_observation_person_type_reporting", table_name="observation")
    op.drop_index("ix_observation_project_id", table_name="observation")
    op.drop_index("ix_observation_response", table_name="observation")
    op.drop_index(
        "ix_observation_response_specific_action_comments", table_name="observation"
    )
    op.drop_index(
        "ix_observation_response_specific_action_datetime", table_name="observation"
    )
    op.drop_index("ix_observation_response_specific_id", table_name="observation")
    op.drop_index("ix_observation_state", table_name="observation")
    op.drop_index("ix_observation_street", table_name="observation")
    op.drop_index("ix_observation_supervisor_id", table_name="observation")
    op.drop_index("ix_observation_task_detail", table_name="observation")
    op.drop_index("ix_observation_task_type", table_name="observation")
    op.drop_index("ix_observation_timestamp_created", table_name="observation")
    op.drop_index("ix_observation_timestamp_updated", table_name="observation")
    op.drop_index(
        "ix_project_location_site_condition_link_project_location_id",
        table_name="project_location_site_condition_link",
    )
    op.drop_index(
        "ix_project_location_site_condition_link_site_condition_id",
        table_name="project_location_site_condition_link",
    )
    op.drop_index("ix_project_locations_id", table_name="project_locations")
    op.drop_index("ix_project_locations_latitude", table_name="project_locations")
    op.drop_index("ix_project_locations_longitude", table_name="project_locations")
    op.drop_index("ix_project_locations_name", table_name="project_locations")
    op.drop_index("ix_project_locations_project_id", table_name="project_locations")
    op.drop_index("ix_projects_end_date", table_name="projects")
    op.drop_index("ix_projects_id", table_name="projects")
    op.drop_index("ix_projects_name", table_name="projects")
    op.drop_index("ix_projects_start_date", table_name="projects")
    op.drop_index("ix_raw_incidents_address", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_asset_outcome", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_city", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_client_id", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_contractor", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_description", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_east_longitude", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_environmental_outcome", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_id", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_incident_datetime", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_incident_id", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_incident_type", table_name="raw_incidents")
    op.drop_index(
        "ix_raw_incidents_inferred_work_start_date_confidence",
        table_name="raw_incidents",
    )
    op.drop_index("ix_raw_incidents_job_type_1", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_job_type_2", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_job_type_3", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_latitude", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_location_description", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_longitude", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_motor_vehicle_outcome", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_north_latitude", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_person_impacted", table_name="raw_incidents")
    op.drop_index(
        "ix_raw_incidents_person_impacted_severity_outcome", table_name="raw_incidents"
    )
    op.drop_index("ix_raw_incidents_person_impacted_type", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_project_id", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_public_outcome", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_south_latitude", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_state", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_street", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_street_number", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_supervisor_id", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_task_type", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_timestamp_created", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_timestamp_updated", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_west_longitude", table_name="raw_incidents")
    op.drop_index("ix_raw_incidents_zipcode", table_name="raw_incidents")
    op.drop_index("ix_samplemodel_id", table_name="samplemodel")
    op.drop_index("ix_samplemodel_sample_field_1", table_name="samplemodel")
    op.drop_index("ix_samplemodel_sample_field_2", table_name="samplemodel")
    op.drop_index("ix_samplemodel_sample_field_3", table_name="samplemodel")
    op.drop_index("ix_samplemodel_sample_field_4", table_name="samplemodel")
    op.drop_index(
        "ix_site_condition_hazard_link_site_condition_id",
        table_name="site_condition_hazard_link",
    )
    op.drop_index("ix_site_conditions_id", table_name="site_conditions")
    op.drop_index("ix_site_conditions_name", table_name="site_conditions")


def downgrade():
    op.create_index(
        "ix_site_conditions_name", "site_conditions", ["name"], unique=False
    )
    op.create_index("ix_site_conditions_id", "site_conditions", ["id"], unique=False)
    op.create_index(
        "ix_site_condition_hazard_link_site_condition_id",
        "site_condition_hazard_link",
        ["site_condition_id"],
        unique=False,
    )
    op.create_index(
        "ix_samplemodel_sample_field_4", "samplemodel", ["sample_field_4"], unique=False
    )
    op.create_index(
        "ix_samplemodel_sample_field_3", "samplemodel", ["sample_field_3"], unique=False
    )
    op.create_index(
        "ix_samplemodel_sample_field_2", "samplemodel", ["sample_field_2"], unique=False
    )
    op.create_index(
        "ix_samplemodel_sample_field_1", "samplemodel", ["sample_field_1"], unique=False
    )
    op.create_index("ix_samplemodel_id", "samplemodel", ["id"], unique=False)
    op.create_index(
        "ix_raw_incidents_zipcode", "raw_incidents", ["zipcode"], unique=False
    )
    op.create_index(
        "ix_raw_incidents_west_longitude",
        "raw_incidents",
        ["west_longitude"],
        unique=False,
    )
    op.create_index(
        "ix_raw_incidents_timestamp_updated",
        "raw_incidents",
        ["timestamp_updated"],
        unique=False,
    )
    op.create_index(
        "ix_raw_incidents_timestamp_created",
        "raw_incidents",
        ["timestamp_created"],
        unique=False,
    )
    op.create_index(
        "ix_raw_incidents_task_type", "raw_incidents", ["task_type"], unique=False
    )
    op.create_index(
        "ix_raw_incidents_supervisor_id",
        "raw_incidents",
        ["supervisor_id"],
        unique=False,
    )
    op.create_index(
        "ix_raw_incidents_street_number",
        "raw_incidents",
        ["street_number"],
        unique=False,
    )
    op.create_index(
        "ix_raw_incidents_street", "raw_incidents", ["street"], unique=False
    )
    op.create_index("ix_raw_incidents_state", "raw_incidents", ["state"], unique=False)
    op.create_index(
        "ix_raw_incidents_south_latitude",
        "raw_incidents",
        ["south_latitude"],
        unique=False,
    )
    op.create_index(
        "ix_raw_incidents_public_outcome",
        "raw_incidents",
        ["public_outcome"],
        unique=False,
    )
    op.create_index(
        "ix_raw_incidents_project_id", "raw_incidents", ["project_id"], unique=False
    )
    op.create_index(
        "ix_raw_incidents_person_impacted_type",
        "raw_incidents",
        ["person_impacted_type"],
        unique=False,
    )
    op.create_index(
        "ix_raw_incidents_person_impacted_severity_outcome",
        "raw_incidents",
        ["person_impacted_severity_outcome"],
        unique=False,
    )
    op.create_index(
        "ix_raw_incidents_person_impacted",
        "raw_incidents",
        ["person_impacted"],
        unique=False,
    )
    op.create_index(
        "ix_raw_incidents_north_latitude",
        "raw_incidents",
        ["north_latitude"],
        unique=False,
    )
    op.create_index(
        "ix_raw_incidents_motor_vehicle_outcome",
        "raw_incidents",
        ["motor_vehicle_outcome"],
        unique=False,
    )
    op.create_index(
        "ix_raw_incidents_longitude", "raw_incidents", ["longitude"], unique=False
    )
    op.create_index(
        "ix_raw_incidents_location_description",
        "raw_incidents",
        ["location_description"],
        unique=False,
    )
    op.create_index(
        "ix_raw_incidents_latitude", "raw_incidents", ["latitude"], unique=False
    )
    op.create_index(
        "ix_raw_incidents_job_type_3", "raw_incidents", ["job_type_3"], unique=False
    )
    op.create_index(
        "ix_raw_incidents_job_type_2", "raw_incidents", ["job_type_2"], unique=False
    )
    op.create_index(
        "ix_raw_incidents_job_type_1", "raw_incidents", ["job_type_1"], unique=False
    )
    op.create_index(
        "ix_raw_incidents_inferred_work_start_date_confidence",
        "raw_incidents",
        ["inferred_work_start_date_confidence"],
        unique=False,
    )
    op.create_index(
        "ix_raw_incidents_incident_type",
        "raw_incidents",
        ["incident_type"],
        unique=False,
    )
    op.create_index(
        "ix_raw_incidents_incident_id", "raw_incidents", ["incident_id"], unique=False
    )
    op.create_index(
        "ix_raw_incidents_incident_datetime",
        "raw_incidents",
        ["incident_datetime"],
        unique=False,
    )
    op.create_index("ix_raw_incidents_id", "raw_incidents", ["id"], unique=False)
    op.create_index(
        "ix_raw_incidents_environmental_outcome",
        "raw_incidents",
        ["environmental_outcome"],
        unique=False,
    )
    op.create_index(
        "ix_raw_incidents_east_longitude",
        "raw_incidents",
        ["east_longitude"],
        unique=False,
    )
    op.create_index(
        "ix_raw_incidents_description", "raw_incidents", ["description"], unique=False
    )
    op.create_index(
        "ix_raw_incidents_contractor", "raw_incidents", ["contractor"], unique=False
    )
    op.create_index(
        "ix_raw_incidents_client_id", "raw_incidents", ["client_id"], unique=False
    )
    op.create_index("ix_raw_incidents_city", "raw_incidents", ["city"], unique=False)
    op.create_index(
        "ix_raw_incidents_asset_outcome",
        "raw_incidents",
        ["asset_outcome"],
        unique=False,
    )
    op.create_index(
        "ix_raw_incidents_address", "raw_incidents", ["address"], unique=False
    )
    op.create_index("ix_projects_start_date", "projects", ["start_date"], unique=False)
    op.create_index("ix_projects_name", "projects", ["name"], unique=False)
    op.create_index("ix_projects_id", "projects", ["id"], unique=False)
    op.create_index("ix_projects_end_date", "projects", ["end_date"], unique=False)
    op.create_index(
        "ix_project_locations_project_id",
        "project_locations",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        "ix_project_locations_name", "project_locations", ["name"], unique=False
    )
    op.create_index(
        "ix_project_locations_longitude",
        "project_locations",
        ["longitude"],
        unique=False,
    )
    op.create_index(
        "ix_project_locations_latitude", "project_locations", ["latitude"], unique=False
    )
    op.create_index(
        "ix_project_locations_id", "project_locations", ["id"], unique=False
    )
    op.create_index(
        "ix_project_location_site_condition_link_site_condition_id",
        "project_location_site_condition_link",
        ["site_condition_id"],
        unique=False,
    )
    op.create_index(
        "ix_project_location_site_condition_link_project_location_id",
        "project_location_site_condition_link",
        ["project_location_id"],
        unique=False,
    )
    op.create_index(
        "ix_observation_timestamp_updated",
        "observation",
        ["timestamp_updated"],
        unique=False,
    )
    op.create_index(
        "ix_observation_timestamp_created",
        "observation",
        ["timestamp_created"],
        unique=False,
    )
    op.create_index(
        "ix_observation_task_type", "observation", ["task_type"], unique=False
    )
    op.create_index(
        "ix_observation_task_detail", "observation", ["task_detail"], unique=False
    )
    op.create_index(
        "ix_observation_supervisor_id", "observation", ["supervisor_id"], unique=False
    )
    op.create_index("ix_observation_street", "observation", ["street"], unique=False)
    op.create_index("ix_observation_state", "observation", ["state"], unique=False)
    op.create_index(
        "ix_observation_response_specific_id",
        "observation",
        ["response_specific_id"],
        unique=False,
    )
    op.create_index(
        "ix_observation_response_specific_action_datetime",
        "observation",
        ["response_specific_action_datetime"],
        unique=False,
    )
    op.create_index(
        "ix_observation_response_specific_action_comments",
        "observation",
        ["response_specific_action_comments"],
        unique=False,
    )
    op.create_index(
        "ix_observation_response", "observation", ["response"], unique=False
    )
    op.create_index(
        "ix_observation_project_id", "observation", ["project_id"], unique=False
    )
    op.create_index(
        "ix_observation_person_type_reporting",
        "observation",
        ["person_type_reporting"],
        unique=False,
    )
    op.create_index(
        "ix_observation_observation_type",
        "observation",
        ["observation_type"],
        unique=False,
    )
    op.create_index(
        "ix_observation_observation_id", "observation", ["observation_id"], unique=False
    )
    op.create_index(
        "ix_observation_observation_datetime",
        "observation",
        ["observation_datetime"],
        unique=False,
    )
    op.create_index(
        "ix_observation_observation_comments",
        "observation",
        ["observation_comments"],
        unique=False,
    )
    op.create_index(
        "ix_observation_longitude", "observation", ["longitude"], unique=False
    )
    op.create_index(
        "ix_observation_location_name", "observation", ["location_name"], unique=False
    )
    op.create_index(
        "ix_observation_latitude", "observation", ["latitude"], unique=False
    )
    op.create_index(
        "ix_observation_job_type_3", "observation", ["job_type_3"], unique=False
    )
    op.create_index(
        "ix_observation_job_type_2", "observation", ["job_type_2"], unique=False
    )
    op.create_index(
        "ix_observation_job_type_1", "observation", ["job_type_1"], unique=False
    )
    op.create_index("ix_observation_id", "observation", ["id"], unique=False)
    op.create_index(
        "ix_observation_contractor_involved",
        "observation",
        ["contractor_involved"],
        unique=False,
    )
    op.create_index(
        "ix_observation_client_id", "observation", ["client_id"], unique=False
    )
    op.create_index("ix_observation_city", "observation", ["city"], unique=False)
    op.create_index("ix_observation_address", "observation", ["address"], unique=False)
    op.create_index(
        "ix_observation_action_type", "observation", ["action_type"], unique=False
    )
    op.create_index(
        "ix_observation_action_topic", "observation", ["action_topic"], unique=False
    )
    op.create_index(
        "ix_observation_action_id", "observation", ["action_id"], unique=False
    )
    op.create_index(
        "ix_observation_action_datetime",
        "observation",
        ["action_datetime"],
        unique=False,
    )
    op.create_index(
        "ix_observation_action_category",
        "observation",
        ["action_category"],
        unique=False,
    )
