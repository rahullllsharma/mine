CREATE TYPE public.audit_diff_type AS ENUM (
    'created',
    'updated',
    'deleted',
    'archived'
);



CREATE TYPE public.audit_event_type AS ENUM (
    'project_created',
    'project_updated',
    'project_location_task_created',
    'project_location_task_updated',
    'project_location_task_archived',
    'project_location_site_condition_created',
    'project_location_site_condition_updated',
    'project_location_site_condition_archived',
    'daily_report_created',
    'daily_report_updated',
    'daily_report_archived'
);



CREATE TYPE public.audit_object_type AS ENUM (
    'project',
    'project_location',
    'project_location_task',
    'project_location_task_hazard',
    'project_location_task_hazard_control',
    'project_location_site_condition',
    'project_location_site_condition_hazard',
    'project_location_site_condition_hazard_control',
    'daily_report'
);



CREATE TYPE public.centroidtype AS ENUM (
    'centroid_from_client',
    'centroid_from_geocoder',
    'centroid_from_polygo',
    'centroid_from_bounding_box'
);



CREATE TYPE public.daily_report_status AS ENUM (
    'in_progress',
    'complete'
);



CREATE TYPE public.project_status AS ENUM (
    'pending',
    'active',
    'completed'
);



CREATE TYPE public.task_status AS ENUM (
    'not_started',
    'in_progress',
    'complete',
    'not_completed'
);


SET default_tablespace = '';

SET default_table_access_method = heap;



CREATE TABLE public.audit_event_diffs (
    diff_type public.audit_diff_type NOT NULL,
    object_type public.audit_object_type NOT NULL,
    old_values jsonb,
    new_values jsonb,
    id uuid NOT NULL,
    created_at timestamp with time zone NOT NULL,
    event_id uuid NOT NULL,
    object_id uuid NOT NULL
);



CREATE TABLE public.audit_events (
    event_type public.audit_event_type NOT NULL,
    id uuid NOT NULL,
    created_at timestamp with time zone NOT NULL,
    user_id uuid NOT NULL
);



CREATE TABLE public.calculated_project_location_site_condition (
    date date,
    calculated_at timestamp with time zone,
    id uuid NOT NULL,
    project_location_id uuid NOT NULL,
    library_site_condition_id uuid NOT NULL,
    alert boolean NOT NULL,
    details jsonb,
    multiplier double precision DEFAULT '0'::double precision NOT NULL
);



CREATE TABLE public.contractor (
    id uuid NOT NULL,
    name character varying NOT NULL,
    tenant_id uuid,
    needs_review boolean NOT NULL
);



CREATE TABLE public.contractor_aliases (
    contractor_id uuid NOT NULL,
    alias character varying,
    tenant_id uuid,
    id uuid NOT NULL
);



CREATE TABLE public.daily_reports (
    id uuid NOT NULL,
    project_location_id uuid NOT NULL,
    date_for date NOT NULL,
    created_at timestamp with time zone NOT NULL,
    status public.daily_report_status NOT NULL,
    sections jsonb,
    created_by_id uuid NOT NULL,
    archived_at timestamp with time zone,
    completed_at timestamp with time zone,
    completed_by_id uuid
);



CREATE TABLE public.google_cloud_storage_blob (
    id character varying NOT NULL,
    bucket_name character varying NOT NULL,
    file_name character varying,
    mimetype character varying,
    md5 character varying,
    crc32c character varying
);



CREATE TABLE public.incident_task_link (
    incident_id uuid NOT NULL,
    library_task_id uuid NOT NULL
);



CREATE TABLE public.incidents (
    timestamp_created timestamp with time zone,
    timestamp_updated timestamp with time zone,
    centroid_source public.centroidtype,
    id uuid NOT NULL,
    client_id character varying,
    incident_id character varying NOT NULL,
    supervisor_id uuid,
    project_id character varying,
    contractor_id uuid,
    incident_type character varying,
    incident_datetime timestamp without time zone NOT NULL,
    street_number character varying,
    street character varying,
    city character varying,
    state character varying,
    zipcode character varying,
    address character varying,
    latitude double precision,
    longitude double precision,
    north_latitude double precision,
    west_longitude double precision,
    south_latitude double precision,
    east_longitude double precision,
    person_impacted_type character varying,
    person_impacted character varying,
    location_description character varying,
    job_type_1 character varying,
    job_type_2 character varying,
    job_type_3 character varying,
    environmental_outcome character varying,
    person_impacted_severity_outcome character varying,
    motor_vehicle_outcome character varying,
    inferred_work_start_date_confidence character varying,
    public_outcome character varying,
    asset_outcome character varying,
    task_type character varying,
    description character varying,
    tenant_id uuid
);



CREATE TABLE public.ingestion_settings (
    tenant_id uuid NOT NULL,
    bucket_name character varying NOT NULL,
    folder_name character varying NOT NULL
);



CREATE TABLE public.library_controls (
    id uuid NOT NULL,
    name character varying NOT NULL,
    for_tasks boolean NOT NULL,
    for_site_conditions boolean NOT NULL
);



CREATE TABLE public.library_divisions (
    id uuid NOT NULL,
    name character varying NOT NULL
);



CREATE TABLE public.library_hazards (
    id uuid NOT NULL,
    name character varying NOT NULL,
    for_tasks boolean NOT NULL,
    for_site_conditions boolean NOT NULL
);



CREATE TABLE public.library_project_types (
    id uuid NOT NULL,
    name character varying NOT NULL
);



CREATE TABLE public.library_regions (
    id uuid NOT NULL,
    name character varying NOT NULL
);



CREATE TABLE public.library_site_condition_recommendations (
    library_site_condition_id uuid NOT NULL,
    library_hazard_id uuid NOT NULL,
    library_control_id uuid NOT NULL
);



CREATE TABLE public.library_site_conditions (
    id uuid NOT NULL,
    name character varying NOT NULL,
    handle_code character varying
);



CREATE TABLE public.library_task_recommendations (
    library_task_id uuid NOT NULL,
    library_hazard_id uuid NOT NULL,
    library_control_id uuid NOT NULL
);



CREATE TABLE public.library_task_site_conditions (
    library_site_condition_id uuid NOT NULL,
    library_task_id uuid NOT NULL
);



CREATE TABLE public.library_tasks (
    id uuid NOT NULL,
    name character varying NOT NULL,
    hesp integer NOT NULL,
    category character varying,
    unique_task_id character varying
);



CREATE TABLE public.observations (
    timestamp_created timestamp with time zone,
    timestamp_updated timestamp with time zone,
    centroid_source public.centroidtype,
    id uuid NOT NULL,
    observation_id character varying NOT NULL,
    observation_datetime timestamp without time zone,
    action_datetime timestamp without time zone,
    response_specific_action_datetime timestamp without time zone,
    client_id character varying,
    supervisor_id uuid,
    contractor_involved_id uuid,
    project_id character varying,
    action_id character varying,
    response_specific_id character varying,
    observation_type character varying,
    person_type_reporting character varying,
    location_name character varying,
    street character varying,
    city character varying,
    state character varying,
    address character varying,
    latitude double precision,
    longitude double precision,
    job_type_1 character varying,
    job_type_2 character varying,
    job_type_3 character varying,
    task_type character varying,
    task_detail character varying,
    observation_comments character varying,
    action_type character varying,
    action_category character varying,
    action_topic character varying,
    response character varying,
    response_specific_action_comments character varying,
    tenant_id uuid
);



CREATE TABLE public.parsed_files (
    timestamp_processed timestamp with time zone NOT NULL,
    file_path character varying NOT NULL,
    tenant_id uuid,
    id uuid NOT NULL
);



CREATE TABLE public.project_location_site_condition_hazard_controls (
    id uuid NOT NULL,
    project_location_site_condition_hazard_id uuid NOT NULL,
    library_control_id uuid NOT NULL,
    user_id uuid,
    is_applicable boolean NOT NULL,
    "position" integer NOT NULL,
    archived_at timestamp with time zone
);



CREATE TABLE public.project_location_site_condition_hazards (
    id uuid NOT NULL,
    project_location_site_condition_id uuid NOT NULL,
    library_hazard_id uuid NOT NULL,
    user_id uuid,
    is_applicable boolean NOT NULL,
    "position" integer NOT NULL,
    archived_at timestamp with time zone
);



CREATE TABLE public.project_location_site_conditions (
    id uuid NOT NULL,
    project_location_id uuid NOT NULL,
    library_site_condition_id uuid NOT NULL,
    archived_at timestamp with time zone
);



CREATE TABLE public.project_location_task_hazard_controls (
    id uuid NOT NULL,
    project_location_task_hazard_id uuid NOT NULL,
    library_control_id uuid NOT NULL,
    user_id uuid,
    is_applicable boolean NOT NULL,
    "position" integer NOT NULL,
    archived_at timestamp with time zone
);



CREATE TABLE public.project_location_task_hazards (
    id uuid NOT NULL,
    project_location_task_id uuid NOT NULL,
    library_hazard_id uuid NOT NULL,
    user_id uuid,
    is_applicable boolean NOT NULL,
    "position" integer NOT NULL,
    archived_at timestamp with time zone
);



CREATE TABLE public.project_location_tasks (
    id uuid NOT NULL,
    project_location_id uuid NOT NULL,
    library_task_id uuid NOT NULL,
    start_date date,
    end_date date,
    status public.task_status NOT NULL,
    archived_at timestamp with time zone
);



CREATE TABLE public.project_locations (
    id uuid NOT NULL,
    name character varying NOT NULL,
    project_id uuid NOT NULL,
    latitude character varying NOT NULL,
    longitude character varying NOT NULL,
    archived_at timestamp with time zone,
    supervisor_id uuid NOT NULL,
    additional_supervisor_ids uuid[] NOT NULL
);



CREATE TABLE public.projects (
    id uuid NOT NULL,
    name character varying NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    status public.project_status NOT NULL,
    number character varying NOT NULL,
    description character varying,
    library_region_id uuid NOT NULL,
    library_division_id uuid NOT NULL,
    library_project_type_id uuid NOT NULL,
    manager_id uuid NOT NULL,
    supervisor_id uuid NOT NULL,
    additional_supervisor_ids uuid[] NOT NULL,
    contractor_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    archived_at timestamp with time zone
);



CREATE TABLE public.rm_average_contractor_safety_score (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    tenant_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_average_supervisor_engagement_factor (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    tenant_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_calc_parameters (
    name character varying NOT NULL,
    value character varying NOT NULL,
    tenant_id uuid
);



CREATE TABLE public.rm_contractor_project_execution (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    contractor_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_contractor_safety_history (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    contractor_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_contractor_safety_rating (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    contractor_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_contractor_safety_score (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    contractor_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_gbl_contractor_project_history_bsl (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    inputs jsonb,
    tenant_id uuid NOT NULL,
    params jsonb
);



CREATE TABLE public.rm_gbl_contractor_project_history_bsl_stddev (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    inputs jsonb,
    tenant_id uuid NOT NULL,
    params jsonb
);



CREATE TABLE public.rm_manually_added_site_conditions (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_location_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_project_location_safety_climate_multiplier (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_location_id uuid NOT NULL,
    contractor_id uuid,
    supervisor_id uuid,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_project_location_total_task_risk_score (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_location_id uuid NOT NULL,
    date date NOT NULL,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_project_site_conditions_multiplier (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_location_id uuid NOT NULL,
    date date NOT NULL,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_project_total_task_risk_score (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_id uuid NOT NULL,
    date date NOT NULL,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_stddev_contractor_safety_score (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    tenant_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_stddev_supervisor_engagement_factor (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    tenant_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_supervisor_engagement_factor (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    supervisor_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_surface_project_project_location_risk_scores (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_id uuid,
    project_location_id uuid,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_surface_total_task_task_specific_risk_ranking (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_id uuid,
    project_task_id uuid,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_task_specific_risk_score (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_task_id uuid NOT NULL,
    date date NOT NULL,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_task_specific_safety_climate_multiplier (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    library_task_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_task_specific_site_conditions_multiplier (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_task_id uuid NOT NULL,
    date date NOT NULL,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_total_project_location_risk_score (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_location_id uuid NOT NULL,
    date date NOT NULL,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.rm_total_project_risk_score (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_id uuid NOT NULL,
    date date NOT NULL,
    inputs jsonb,
    params jsonb
);



CREATE TABLE public.supervisor (
    id uuid NOT NULL,
    name character varying NOT NULL,
    tenant_id uuid,
    user_id uuid
);



CREATE TABLE public.tenants (
    id uuid NOT NULL,
    tenant_name character varying NOT NULL,
    auth_realm_name character varying NOT NULL
);



CREATE TABLE public.users (
    id uuid NOT NULL,
    keycloak_id uuid NOT NULL,
    first_name character varying NOT NULL,
    last_name character varying NOT NULL,
    role character varying,
    email character varying DEFAULT ''::character varying NOT NULL,
    tenant_id uuid NOT NULL
);




ALTER TABLE ONLY public.audit_event_diffs
    ADD CONSTRAINT audit_event_diffs_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.audit_events
    ADD CONSTRAINT audit_events_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.calculated_project_location_site_condition
    ADD CONSTRAINT calculated_project_location_site_condition_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.contractor_aliases
    ADD CONSTRAINT contractor_aliases_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.contractor
    ADD CONSTRAINT contractor_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.daily_reports
    ADD CONSTRAINT daily_reports_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.google_cloud_storage_blob
    ADD CONSTRAINT google_cloud_storage_blob_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.incident_task_link
    ADD CONSTRAINT incident_task_link_pkey PRIMARY KEY (incident_id, library_task_id);



ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.ingestion_settings
    ADD CONSTRAINT ingestion_settings_pkey PRIMARY KEY (tenant_id);



ALTER TABLE ONLY public.library_controls
    ADD CONSTRAINT library_controls_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.library_divisions
    ADD CONSTRAINT library_divisions_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.library_hazards
    ADD CONSTRAINT library_hazards_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.library_project_types
    ADD CONSTRAINT library_project_types_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.library_regions
    ADD CONSTRAINT library_regions_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.library_site_condition_recommendations
    ADD CONSTRAINT library_site_condition_recommendations_pkey PRIMARY KEY (library_site_condition_id, library_hazard_id, library_control_id);



ALTER TABLE ONLY public.library_site_conditions
    ADD CONSTRAINT library_site_conditions_handle_code_unique UNIQUE (handle_code);



ALTER TABLE ONLY public.library_site_conditions
    ADD CONSTRAINT library_site_conditions_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.library_task_recommendations
    ADD CONSTRAINT library_task_recommendations_pkey PRIMARY KEY (library_task_id, library_hazard_id, library_control_id);



ALTER TABLE ONLY public.library_task_site_conditions
    ADD CONSTRAINT library_task_site_conditions_pkey PRIMARY KEY (library_site_condition_id, library_task_id);



ALTER TABLE ONLY public.library_tasks
    ADD CONSTRAINT library_tasks_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.observations
    ADD CONSTRAINT observations_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.parsed_files
    ADD CONSTRAINT parsed_files_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.project_location_site_condition_hazard_controls
    ADD CONSTRAINT project_location_site_condition_hazard_controls_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.project_location_site_condition_hazards
    ADD CONSTRAINT project_location_site_condition_hazards_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.project_location_site_conditions
    ADD CONSTRAINT project_location_site_conditions_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.project_location_task_hazard_controls
    ADD CONSTRAINT project_location_task_hazard_controls_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.project_location_task_hazards
    ADD CONSTRAINT project_location_task_hazards_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.project_location_tasks
    ADD CONSTRAINT project_location_tasks_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.project_locations
    ADD CONSTRAINT project_locations_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.rm_average_contractor_safety_score
    ADD CONSTRAINT rm_average_contractor_safety_score_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.rm_average_supervisor_engagement_factor
    ADD CONSTRAINT rm_average_supervisor_engagement_factor_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.rm_calc_parameters
    ADD CONSTRAINT rm_calc_parameters_pkey PRIMARY KEY (name);



ALTER TABLE ONLY public.rm_contractor_project_execution
    ADD CONSTRAINT rm_contractor_project_execution_pkey PRIMARY KEY (calculated_at, contractor_id);



ALTER TABLE ONLY public.rm_contractor_safety_history
    ADD CONSTRAINT rm_contractor_safety_history_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.rm_contractor_safety_rating
    ADD CONSTRAINT rm_contractor_safety_rating_pkey PRIMARY KEY (calculated_at, contractor_id);



ALTER TABLE ONLY public.rm_contractor_safety_score
    ADD CONSTRAINT rm_contractor_safety_score_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.rm_gbl_contractor_project_history_bsl
    ADD CONSTRAINT rm_gbl_contractor_project_history_bsl_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.rm_gbl_contractor_project_history_bsl_stddev
    ADD CONSTRAINT rm_gbl_contractor_project_history_bsl_stddev_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.rm_manually_added_site_conditions
    ADD CONSTRAINT rm_manually_added_site_conditions_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.rm_project_location_safety_climate_multiplier
    ADD CONSTRAINT rm_project_location_safety_climate_multiplier_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.rm_project_location_total_task_risk_score
    ADD CONSTRAINT rm_project_location_total_task_risk_score_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.rm_project_site_conditions_multiplier
    ADD CONSTRAINT rm_project_site_conditions_multiplier_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.rm_project_total_task_risk_score
    ADD CONSTRAINT rm_project_total_task_risk_score_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.rm_stddev_contractor_safety_score
    ADD CONSTRAINT rm_stddev_contractor_safety_score_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.rm_stddev_supervisor_engagement_factor
    ADD CONSTRAINT rm_stddev_supervisor_engagement_factor_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.rm_supervisor_engagement_factor
    ADD CONSTRAINT rm_supervisor_engagement_factor_pkey PRIMARY KEY (calculated_at, supervisor_id);



ALTER TABLE ONLY public.rm_surface_project_project_location_risk_scores
    ADD CONSTRAINT rm_surface_project_project_location_risk_scores_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.rm_surface_total_task_task_specific_risk_ranking
    ADD CONSTRAINT rm_surface_total_task_task_specific_risk_ranking_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.rm_task_specific_risk_score
    ADD CONSTRAINT rm_task_specific_risk_score_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.rm_task_specific_safety_climate_multiplier
    ADD CONSTRAINT rm_task_specific_safety_climate_multiplier_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.rm_task_specific_site_conditions_multiplier
    ADD CONSTRAINT rm_task_specific_site_conditions_multiplier_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.rm_total_project_location_risk_score
    ADD CONSTRAINT rm_total_project_location_risk_score_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.rm_total_project_risk_score
    ADD CONSTRAINT rm_total_project_risk_score_pkey PRIMARY KEY (calculated_at);



ALTER TABLE ONLY public.supervisor
    ADD CONSTRAINT supervisor_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);



CREATE UNIQUE INDEX ix_tenants_tenant_name ON public.tenants USING btree (tenant_name);



CREATE INDEX ix_users_keycloak_id ON public.users USING btree (keycloak_id);



CREATE INDEX ix_users_tenant_id ON public.users USING btree (tenant_id);



CREATE UNIQUE INDEX users_tenant_keycloak_idx ON public.users USING btree (tenant_id, keycloak_id);



ALTER TABLE ONLY public.audit_event_diffs
    ADD CONSTRAINT audit_event_diffs_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.audit_events(id);



ALTER TABLE ONLY public.audit_events
    ADD CONSTRAINT audit_events_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);



ALTER TABLE ONLY public.calculated_project_location_site_condition
    ADD CONSTRAINT calculated_project_location_site_condi_project_location_id_fkey FOREIGN KEY (project_location_id) REFERENCES public.project_locations(id);



ALTER TABLE ONLY public.calculated_project_location_site_condition
    ADD CONSTRAINT calculated_project_location_site_library_site_condition_id_fkey FOREIGN KEY (library_site_condition_id) REFERENCES public.library_site_conditions(id);



ALTER TABLE ONLY public.contractor_aliases
    ADD CONSTRAINT contractor_aliases_contractor_id_fkey FOREIGN KEY (contractor_id) REFERENCES public.contractor(id);



ALTER TABLE ONLY public.contractor_aliases
    ADD CONSTRAINT contractor_aliases_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);



ALTER TABLE ONLY public.contractor
    ADD CONSTRAINT contractor_tenenat_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);



ALTER TABLE ONLY public.daily_reports
    ADD CONSTRAINT created_by_fk FOREIGN KEY (created_by_id) REFERENCES public.users(id);



ALTER TABLE ONLY public.daily_reports
    ADD CONSTRAINT daily_reports_project_location_id_fkey FOREIGN KEY (project_location_id) REFERENCES public.project_locations(id);



ALTER TABLE ONLY public.daily_reports
    ADD CONSTRAINT daily_reports_project_task_completed_by_id_fkey FOREIGN KEY (completed_by_id) REFERENCES public.users(id);



ALTER TABLE ONLY public.project_location_site_condition_hazard_controls
    ADD CONSTRAINT "fk-project_location_site_condition_hazard_controls-user" FOREIGN KEY (user_id) REFERENCES public.users(id);



ALTER TABLE ONLY public.project_location_site_condition_hazards
    ADD CONSTRAINT "fk-project_location_site_condition_hazards-user" FOREIGN KEY (user_id) REFERENCES public.users(id);



ALTER TABLE ONLY public.project_location_task_hazard_controls
    ADD CONSTRAINT "fk-project_location_task_hazard_controls-user" FOREIGN KEY (user_id) REFERENCES public.users(id);



ALTER TABLE ONLY public.project_location_task_hazards
    ADD CONSTRAINT "fk-project_location_task_hazards-user" FOREIGN KEY (user_id) REFERENCES public.users(id);



ALTER TABLE ONLY public.projects
    ADD CONSTRAINT "fk-projects-tenants" FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);



ALTER TABLE ONLY public.users
    ADD CONSTRAINT "fk-users-tenants" FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);



ALTER TABLE ONLY public.incident_task_link
    ADD CONSTRAINT incident_task_link_incident_id_fkey FOREIGN KEY (incident_id) REFERENCES public.incidents(id);



ALTER TABLE ONLY public.incident_task_link
    ADD CONSTRAINT incident_task_link_library_task_id_fkey FOREIGN KEY (library_task_id) REFERENCES public.library_tasks(id);



ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_contractor_id_fkey FOREIGN KEY (contractor_id) REFERENCES public.contractor(id);



ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_supervisor_id_fkey FOREIGN KEY (supervisor_id) REFERENCES public.supervisor(id);



ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);



ALTER TABLE ONLY public.ingestion_settings
    ADD CONSTRAINT ingestion_settings_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);



ALTER TABLE ONLY public.library_site_condition_recommendations
    ADD CONSTRAINT library_site_condition_recommend_library_site_condition_id_fkey FOREIGN KEY (library_site_condition_id) REFERENCES public.library_site_conditions(id);



ALTER TABLE ONLY public.library_site_condition_recommendations
    ADD CONSTRAINT library_site_condition_recommendations_library_control_id_fkey FOREIGN KEY (library_control_id) REFERENCES public.library_controls(id);



ALTER TABLE ONLY public.library_site_condition_recommendations
    ADD CONSTRAINT library_site_condition_recommendations_library_hazard_id_fkey FOREIGN KEY (library_hazard_id) REFERENCES public.library_hazards(id);



ALTER TABLE ONLY public.library_task_recommendations
    ADD CONSTRAINT library_task_recommendations_library_control_id_fkey FOREIGN KEY (library_control_id) REFERENCES public.library_controls(id);



ALTER TABLE ONLY public.library_task_recommendations
    ADD CONSTRAINT library_task_recommendations_library_hazard_id_fkey FOREIGN KEY (library_hazard_id) REFERENCES public.library_hazards(id);



ALTER TABLE ONLY public.library_task_recommendations
    ADD CONSTRAINT library_task_recommendations_library_task_id_fkey FOREIGN KEY (library_task_id) REFERENCES public.library_tasks(id);



ALTER TABLE ONLY public.library_task_site_conditions
    ADD CONSTRAINT library_task_site_conditions_library_site_condition_id_fkey FOREIGN KEY (library_site_condition_id) REFERENCES public.library_site_conditions(id);



ALTER TABLE ONLY public.library_task_site_conditions
    ADD CONSTRAINT library_task_site_conditions_library_task_id_fkey FOREIGN KEY (library_task_id) REFERENCES public.library_tasks(id);



ALTER TABLE ONLY public.observations
    ADD CONSTRAINT observations_contractor_involved_id_fkey FOREIGN KEY (contractor_involved_id) REFERENCES public.contractor(id);



ALTER TABLE ONLY public.observations
    ADD CONSTRAINT observations_supervisor_id_fkey FOREIGN KEY (supervisor_id) REFERENCES public.supervisor(id);



ALTER TABLE ONLY public.observations
    ADD CONSTRAINT observations_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);



ALTER TABLE ONLY public.parsed_files
    ADD CONSTRAINT parsed_files_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);



ALTER TABLE ONLY public.project_location_site_condition_hazard_controls
    ADD CONSTRAINT project_location_site_condit_project_location_site_condit_fkey1 FOREIGN KEY (project_location_site_condition_hazard_id) REFERENCES public.project_location_site_condition_hazards(id);



ALTER TABLE ONLY public.project_location_site_condition_hazards
    ADD CONSTRAINT project_location_site_conditi_project_location_site_condit_fkey FOREIGN KEY (project_location_site_condition_id) REFERENCES public.project_location_site_conditions(id);



ALTER TABLE ONLY public.project_location_site_condition_hazard_controls
    ADD CONSTRAINT project_location_site_condition_hazard__library_control_id_fkey FOREIGN KEY (library_control_id) REFERENCES public.library_controls(id);



ALTER TABLE ONLY public.project_location_site_condition_hazards
    ADD CONSTRAINT project_location_site_condition_hazards_library_hazard_id_fkey FOREIGN KEY (library_hazard_id) REFERENCES public.library_hazards(id);



ALTER TABLE ONLY public.project_location_site_conditions
    ADD CONSTRAINT project_location_site_conditions_library_site_condition_id_fkey FOREIGN KEY (library_site_condition_id) REFERENCES public.library_site_conditions(id);



ALTER TABLE ONLY public.project_location_site_conditions
    ADD CONSTRAINT project_location_site_conditions_project_location_id_fkey FOREIGN KEY (project_location_id) REFERENCES public.project_locations(id);



ALTER TABLE ONLY public.project_location_task_hazard_controls
    ADD CONSTRAINT project_location_task_hazard__project_location_task_hazard_fkey FOREIGN KEY (project_location_task_hazard_id) REFERENCES public.project_location_task_hazards(id);



ALTER TABLE ONLY public.project_location_task_hazard_controls
    ADD CONSTRAINT project_location_task_hazard_controls_library_control_id_fkey FOREIGN KEY (library_control_id) REFERENCES public.library_controls(id);



ALTER TABLE ONLY public.project_location_task_hazards
    ADD CONSTRAINT project_location_task_hazards_library_hazard_id_fkey FOREIGN KEY (library_hazard_id) REFERENCES public.library_hazards(id);



ALTER TABLE ONLY public.project_location_task_hazards
    ADD CONSTRAINT project_location_task_hazards_project_location_task_id_fkey FOREIGN KEY (project_location_task_id) REFERENCES public.project_location_tasks(id);



ALTER TABLE ONLY public.project_location_tasks
    ADD CONSTRAINT project_location_tasks_library_task_id_fkey FOREIGN KEY (library_task_id) REFERENCES public.library_tasks(id);



ALTER TABLE ONLY public.project_location_tasks
    ADD CONSTRAINT project_location_tasks_project_location_id_fkey FOREIGN KEY (project_location_id) REFERENCES public.project_locations(id);



ALTER TABLE ONLY public.project_locations
    ADD CONSTRAINT project_locations_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);



ALTER TABLE ONLY public.project_locations
    ADD CONSTRAINT project_locations_supervisor_id_fkey FOREIGN KEY (supervisor_id) REFERENCES public.users(id);



ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_contractor_id_fkey FOREIGN KEY (contractor_id) REFERENCES public.contractor(id);



ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_library_division_id_fkey FOREIGN KEY (library_division_id) REFERENCES public.library_divisions(id);



ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_library_project_type_id_fkey FOREIGN KEY (library_project_type_id) REFERENCES public.library_project_types(id);



ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_library_region_id_fkey FOREIGN KEY (library_region_id) REFERENCES public.library_regions(id);



ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.users(id);



ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_supervisor_id_fkey FOREIGN KEY (supervisor_id) REFERENCES public.users(id);



ALTER TABLE ONLY public.rm_calc_parameters
    ADD CONSTRAINT rm_calc_parameters_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);



ALTER TABLE ONLY public.rm_manually_added_site_conditions
    ADD CONSTRAINT rm_manually_added_site_conditions_project_location_id_fkey FOREIGN KEY (project_location_id) REFERENCES public.project_locations(id);



ALTER TABLE ONLY public.rm_project_location_safety_climate_multiplier
    ADD CONSTRAINT rm_project_location_safety_climate_mul_project_location_id_fkey FOREIGN KEY (project_location_id) REFERENCES public.project_locations(id);



ALTER TABLE ONLY public.rm_project_location_total_task_risk_score
    ADD CONSTRAINT rm_project_location_total_task_risk_sc_project_location_id_fkey FOREIGN KEY (project_location_id) REFERENCES public.project_locations(id);



ALTER TABLE ONLY public.rm_project_site_conditions_multiplier
    ADD CONSTRAINT rm_project_site_conditions_multiplier_project_location_id_fkey FOREIGN KEY (project_location_id) REFERENCES public.project_locations(id);



ALTER TABLE ONLY public.rm_project_total_task_risk_score
    ADD CONSTRAINT rm_project_total_task_risk_score_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);



ALTER TABLE ONLY public.rm_surface_project_project_location_risk_scores
    ADD CONSTRAINT rm_surface_project_project_location_ri_project_location_id_fkey FOREIGN KEY (project_location_id) REFERENCES public.project_locations(id);



ALTER TABLE ONLY public.rm_surface_project_project_location_risk_scores
    ADD CONSTRAINT rm_surface_project_project_location_risk_scores_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);



ALTER TABLE ONLY public.rm_surface_total_task_task_specific_risk_ranking
    ADD CONSTRAINT rm_surface_total_task_task_specific_risk_r_project_task_id_fkey FOREIGN KEY (project_task_id) REFERENCES public.project_location_tasks(id);



ALTER TABLE ONLY public.rm_surface_total_task_task_specific_risk_ranking
    ADD CONSTRAINT rm_surface_total_task_task_specific_risk_rankin_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);



ALTER TABLE ONLY public.rm_task_specific_risk_score
    ADD CONSTRAINT rm_task_specific_risk_score_project_task_id_fkey FOREIGN KEY (project_task_id) REFERENCES public.project_location_tasks(id);



ALTER TABLE ONLY public.rm_task_specific_safety_climate_multiplier
    ADD CONSTRAINT rm_task_specific_safety_climate_multiplier_library_task_id_fkey FOREIGN KEY (library_task_id) REFERENCES public.library_tasks(id);



ALTER TABLE ONLY public.rm_task_specific_site_conditions_multiplier
    ADD CONSTRAINT rm_task_specific_site_conditions_multiplie_project_task_id_fkey FOREIGN KEY (project_task_id) REFERENCES public.project_location_tasks(id);



ALTER TABLE ONLY public.rm_total_project_location_risk_score
    ADD CONSTRAINT rm_total_project_location_risk_score_project_location_id_fkey FOREIGN KEY (project_location_id) REFERENCES public.project_locations(id);



ALTER TABLE ONLY public.rm_total_project_risk_score
    ADD CONSTRAINT rm_total_project_risk_score_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);



ALTER TABLE ONLY public.supervisor
    ADD CONSTRAINT supervisor_tenenat_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);



ALTER TABLE ONLY public.supervisor
    ADD CONSTRAINT supervisors_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
