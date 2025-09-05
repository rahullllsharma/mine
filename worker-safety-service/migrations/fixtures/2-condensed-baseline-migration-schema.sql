--
-- Name: tiger; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA IF NOT EXISTS tiger;


--
-- Name: tiger_data; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA IF NOT EXISTS tiger_data;


--
-- Name: topology; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA IF NOT EXISTS topology;


--
-- Name: SCHEMA topology; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA topology IS 'PostGIS Topology schema';


--
-- Name: fuzzystrmatch; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS fuzzystrmatch WITH SCHEMA public;


--
-- Name: EXTENSION fuzzystrmatch; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION fuzzystrmatch IS 'determine similarities and distance between strings';


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- Name: postgis_raster; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis_raster WITH SCHEMA public;


--
-- Name: EXTENSION postgis_raster; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION postgis_raster IS 'PostGIS raster types and functions';


--
-- Name: postgis_tiger_geocoder; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder WITH SCHEMA tiger;


--
-- Name: EXTENSION postgis_tiger_geocoder; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION postgis_tiger_geocoder IS 'PostGIS tiger geocoder and reverse geocoder';


--
-- Name: postgis_topology; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis_topology WITH SCHEMA topology;


--
-- Name: EXTENSION postgis_topology; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION postgis_topology IS 'PostGIS topology spatial types and functions';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: activity_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.activity_status AS ENUM (
    'not_started',
    'in_progress',
    'complete',
    'not_completed'
);


--
-- Name: audit_diff_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.audit_diff_type AS ENUM (
    'created',
    'updated',
    'deleted',
    'archived'
);


--
-- Name: audit_event_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.audit_event_type AS ENUM (
    'project_created',
    'project_updated',
    'project_archived',
    'task_created',
    'task_updated',
    'task_archived',
    'site_condition_created',
    'site_condition_updated',
    'site_condition_archived',
    'site_condition_evaluated',
    'daily_report_created',
    'daily_report_updated',
    'daily_report_archived',
    'activity_created',
    'activity_updated',
    'activity_archived',
    'project_location_created',
    'project_location_updated',
    'project_location_archived',
    'job_safety_briefing_created',
    'job_safety_briefing_updated',
    'job_safety_briefing_archived'
);


--
-- Name: audit_object_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.audit_object_type AS ENUM (
    'project',
    'project_location',
    'task',
    'task_hazard',
    'task_control',
    'site_condition',
    'site_condition_hazard',
    'site_condition_control',
    'daily_report',
    'activity',
    'job_safety_briefing'
);


--
-- Name: conceptstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.conceptstatus AS ENUM (
    'in_progress',
    'complete'
);


--
-- Name: daily_report_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.daily_report_status AS ENUM (
    'in_progress',
    'complete'
);


--
-- Name: formdefinitionstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.formdefinitionstatus AS ENUM (
    'active',
    'inactive'
);


--
-- Name: hazard_energy_levels; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.hazard_energy_levels AS ENUM (
    'High Energy',
    'Low Energy',
    'Not Defined'
);


--
-- Name: hazard_energy_types; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.hazard_energy_types AS ENUM (
    'Biological',
    'Chemical',
    'Electrical',
    'Gravity',
    'Mechanical',
    'Motion',
    'Pressure',
    'Radiation',
    'Sound',
    'Temperature',
    'Not Defined'
);


--
-- Name: incident_severity_types; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.incident_severity_types AS ENUM (
    'Not Applicable',
    'Other non-occupational',
    'First Aid Only',
    'Report Purposes Only',
    'Restriction or job transfer',
    'Lost Time',
    'Near deaths',
    'Deaths'
);


--
-- Name: osha_controls_classification; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.osha_controls_classification AS ENUM (
    'ADMINISTRATIVE_CONTROLS',
    'ELIMINATION',
    'ENGINEERING_CONTROLS',
    'PPE',
    'SUBSTITUTION'
);


--
-- Name: project_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.project_status AS ENUM (
    'pending',
    'active',
    'completed'
);


--
-- Name: task_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.task_status AS ENUM (
    'not_started',
    'in_progress',
    'complete',
    'not_completed'
);


--
-- Name: type_of_control; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.type_of_control AS ENUM (
    'DIRECT',
    'INDIRECT'
);


--
-- Name: activity_external_key_unique_per_tenant(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.activity_external_key_unique_per_tenant() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

        BEGIN
        IF (
            SELECT COUNT(a.id) FROM activities as a
            INNER JOIN project_locations as l on l.id = a.location_id
            INNER JOIN projects as p on p.id = l.project_id
            WHERE a.external_key = NEW.external_key
            AND p.tenant_id = (
                SELECT p.tenant_id FROM projects as p
                join project_locations as l on p.id = l.project_id
                WHERE NEW.location_id = l.id
            )
        ) > 1 THEN
            RAISE EXCEPTION 'ExternalKey must be unique within a Tenant';
        ELSE
            RETURN NEW;
        END IF;
        END;
        $$;


--
-- Name: clustering_0(uuid[]); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.clustering_0(i uuid[]) RETURNS uuid
    LANGUAGE plpgsql IMMUTABLE
    AS $$
            BEGIN
                return i[1];
            END;
            $$;


--
-- Name: clustering_1(uuid[]); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.clustering_1(i uuid[]) RETURNS uuid
    LANGUAGE plpgsql IMMUTABLE
    AS $$
            BEGIN
                return i[2];
            END;
            $$;


--
-- Name: clustering_10(uuid[]); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.clustering_10(i uuid[]) RETURNS uuid
    LANGUAGE plpgsql IMMUTABLE
    AS $$
            BEGIN
                return i[11];
            END;
            $$;


--
-- Name: clustering_11(uuid[]); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.clustering_11(i uuid[]) RETURNS uuid
    LANGUAGE plpgsql IMMUTABLE
    AS $$
            BEGIN
                return i[12];
            END;
            $$;


--
-- Name: clustering_12(uuid[]); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.clustering_12(i uuid[]) RETURNS uuid
    LANGUAGE plpgsql IMMUTABLE
    AS $$
            BEGIN
                return i[13];
            END;
            $$;


--
-- Name: clustering_2(uuid[]); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.clustering_2(i uuid[]) RETURNS uuid
    LANGUAGE plpgsql IMMUTABLE
    AS $$
            BEGIN
                return i[3];
            END;
            $$;


--
-- Name: clustering_3(uuid[]); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.clustering_3(i uuid[]) RETURNS uuid
    LANGUAGE plpgsql IMMUTABLE
    AS $$
            BEGIN
                return i[4];
            END;
            $$;


--
-- Name: clustering_4(uuid[]); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.clustering_4(i uuid[]) RETURNS uuid
    LANGUAGE plpgsql IMMUTABLE
    AS $$
            BEGIN
                return i[5];
            END;
            $$;


--
-- Name: clustering_5(uuid[]); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.clustering_5(i uuid[]) RETURNS uuid
    LANGUAGE plpgsql IMMUTABLE
    AS $$
            BEGIN
                return i[6];
            END;
            $$;


--
-- Name: clustering_6(uuid[]); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.clustering_6(i uuid[]) RETURNS uuid
    LANGUAGE plpgsql IMMUTABLE
    AS $$
            BEGIN
                return i[7];
            END;
            $$;


--
-- Name: clustering_7(uuid[]); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.clustering_7(i uuid[]) RETURNS uuid
    LANGUAGE plpgsql IMMUTABLE
    AS $$
            BEGIN
                return i[8];
            END;
            $$;


--
-- Name: clustering_8(uuid[]); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.clustering_8(i uuid[]) RETURNS uuid
    LANGUAGE plpgsql IMMUTABLE
    AS $$
            BEGIN
                return i[9];
            END;
            $$;


--
-- Name: clustering_9(uuid[]); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.clustering_9(i uuid[]) RETURNS uuid
    LANGUAGE plpgsql IMMUTABLE
    AS $$
            BEGIN
                return i[10];
            END;
            $$;


--
-- Name: external_key_uniqueness_insert(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.external_key_uniqueness_insert() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

        BEGIN
        IF (
            SELECT COUNT(l.id) FROM project_locations as l
            INNER JOIN projects as p on p.id = l.project_id
            WHERE l.external_key = NEW.external_key
            AND p.tenant_id = (
                SELECT tenant_id FROM projects
                WHERE id = NEW.project_id
            )
        ) > 1 THEN
            RAISE EXCEPTION 'ExternalKey must be unique within a Tenant';
        ELSE
            RETURN NEW;
        END IF;
        END;
        $$;


--
-- Name: tilebbox(integer, integer, integer, integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.tilebbox(z integer, x integer, y integer, srid integer DEFAULT 3857) RETURNS public.geometry
    LANGUAGE plpgsql IMMUTABLE
    AS $$
        declare
            max numeric := 20037508.34;
            res numeric := (max*2)/(2^z);
            bbox geometry;
        begin
            bbox := ST_MakeEnvelope(
                -max + (x * res),
                max - (y * res),
                -max + (x * res) + res,
                max - (y * res) - res,
                3857
            );
            if srid = 3857 then
                return bbox;
            else
                return ST_Transform(bbox, srid);
            end if;
        end;
        $$;

--

SET default_tablespace = '';

--

SET default_table_access_method = heap;

--
-- Name: activities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.activities (
    id uuid NOT NULL,
    location_id uuid NOT NULL,
    status public.activity_status NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    archived_at timestamp with time zone,
    name character varying NOT NULL,
    crew_id uuid,
    library_activity_type_id uuid,
    meta_attributes jsonb,
    external_key character varying
);


--
-- Name: activity_supervisor_link; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.activity_supervisor_link (
    activity_id uuid NOT NULL,
    supervisor_id uuid NOT NULL
);


--
-- Name: audit_event_diffs; Type: TABLE; Schema: public; Owner: -
--

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


--
-- Name: audit_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_events (
    event_type public.audit_event_type NOT NULL,
    id uuid NOT NULL,
    created_at timestamp with time zone NOT NULL,
    user_id uuid
);


--
-- Name: compatible_units; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.compatible_units (
    compatible_unit_id character varying NOT NULL,
    tenant_id uuid NOT NULL,
    description character varying,
    element_id uuid
);


--
-- Name: configurations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.configurations (
    id uuid NOT NULL,
    name character varying NOT NULL,
    tenant_id uuid,
    value character varying NOT NULL
);


--
-- Name: contractor; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.contractor (
    id uuid NOT NULL,
    name character varying NOT NULL,
    tenant_id uuid,
    needs_review boolean NOT NULL
);


--
-- Name: contractor_aliases; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.contractor_aliases (
    contractor_id uuid NOT NULL,
    alias character varying,
    tenant_id uuid,
    id uuid NOT NULL
);


--
-- Name: crew; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.crew (
    id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    external_key character varying NOT NULL
);


--
-- Name: daily_reports; Type: TABLE; Schema: public; Owner: -
--

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


--
-- Name: element_library_task_link; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.element_library_task_link (
    element_id uuid NOT NULL,
    library_task_id uuid NOT NULL
);


--
-- Name: elements; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.elements (
    id uuid NOT NULL,
    name character varying NOT NULL
);


--
-- Name: form_definitions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.form_definitions (
    id uuid NOT NULL,
    name character varying NOT NULL,
    status public.formdefinitionstatus NOT NULL,
    external_key character varying NOT NULL,
    tenant_id uuid NOT NULL
);


--
-- Name: google_cloud_storage_blob; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.google_cloud_storage_blob (
    id character varying NOT NULL,
    bucket_name character varying NOT NULL,
    file_name character varying,
    mimetype character varying,
    md5 character varying,
    crc32c character varying
);


--
-- Name: hydro_one_job_type_task_map; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hydro_one_job_type_task_map (
    job_type character varying NOT NULL,
    unique_task_id character varying NOT NULL
);


--
-- Name: incident_task_link; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.incident_task_link (
    incident_id uuid NOT NULL,
    library_task_id uuid NOT NULL
);


--
-- Name: incidents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.incidents (
    timestamp_created timestamp with time zone,
    timestamp_updated timestamp with time zone,
    id uuid NOT NULL,
    incident_id character varying,
    supervisor_id uuid,
    contractor_id uuid,
    incident_type character varying NOT NULL,
    incident_date date NOT NULL,
    street_number character varying,
    street character varying,
    city character varying,
    state character varying,
    person_impacted_type character varying,
    location_description character varying,
    job_type_1 character varying,
    job_type_2 character varying,
    job_type_3 character varying,
    environmental_outcome character varying,
    person_impacted_severity_outcome character varying,
    motor_vehicle_outcome character varying,
    public_outcome character varying,
    asset_outcome character varying,
    task_type character varying,
    description character varying NOT NULL,
    tenant_id uuid NOT NULL,
    meta_attributes jsonb,
    external_key character varying,
    work_type uuid,
    task_type_id uuid,
    severity public.incident_severity_types
);


--
-- Name: ingest_work_package_to_compatible_unit_link; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ingest_work_package_to_compatible_unit_link (
    id uuid NOT NULL,
    work_package_external_key character varying NOT NULL,
    compatible_unit_id character varying NOT NULL,
    tenant_id uuid NOT NULL
);


--
-- Name: ingestion_process; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ingestion_process (
    submitted_at timestamp with time zone,
    failed_records character varying[],
    ingestion_type character varying NOT NULL,
    finished_at timestamp without time zone,
    total_record_count integer,
    successful_record_count integer,
    failed_record_count integer,
    id uuid NOT NULL
);


--
-- Name: ingestion_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ingestion_settings (
    tenant_id uuid NOT NULL,
    bucket_name character varying NOT NULL,
    folder_name character varying NOT NULL
);


--
-- Name: jsbs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.jsbs (
    created_at timestamp with time zone NOT NULL,
    completed_at timestamp with time zone,
    archived_at timestamp with time zone,
    status public.conceptstatus NOT NULL,
    contents jsonb,
    id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    created_by_id uuid NOT NULL,
    project_location_id uuid,
    date_for timestamp with time zone NOT NULL,
    completed_by_id uuid
);


--
-- Name: library_activity_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.library_activity_groups (
    id uuid NOT NULL,
    name character varying NOT NULL,
    archived_at timestamp with time zone
);


--
-- Name: library_activity_type_tenant_link; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.library_activity_type_tenant_link (
    library_activity_type_id uuid NOT NULL,
    tenant_id uuid NOT NULL
);


--
-- Name: library_activity_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.library_activity_types (
    id uuid NOT NULL,
    name character varying NOT NULL
);


--
-- Name: library_asset_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.library_asset_types (
    id uuid NOT NULL,
    name character varying NOT NULL
);


--
-- Name: library_controls; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.library_controls (
    id uuid NOT NULL,
    name character varying NOT NULL,
    for_tasks boolean NOT NULL,
    for_site_conditions boolean NOT NULL,
    archived_at timestamp with time zone,
    type public.type_of_control,
    osha_classification public.osha_controls_classification,
    ppe boolean
);


--
-- Name: library_division_tenant_link; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.library_division_tenant_link (
    library_division_id uuid NOT NULL,
    tenant_id uuid NOT NULL
);


--
-- Name: library_divisions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.library_divisions (
    id uuid NOT NULL,
    name character varying NOT NULL
);


--
-- Name: library_hazards; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.library_hazards (
    id uuid NOT NULL,
    name character varying NOT NULL,
    for_tasks boolean NOT NULL,
    for_site_conditions boolean NOT NULL,
    archived_at timestamp with time zone,
    energy_type public.hazard_energy_types,
    energy_level public.hazard_energy_levels
);


--
-- Name: library_project_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.library_project_types (
    id uuid NOT NULL,
    name character varying NOT NULL
);


--
-- Name: library_region_tenant_link; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.library_region_tenant_link (
    library_region_id uuid NOT NULL,
    tenant_id uuid NOT NULL
);


--
-- Name: library_regions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.library_regions (
    id uuid NOT NULL,
    name character varying NOT NULL
);


--
-- Name: library_site_condition_recommendations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.library_site_condition_recommendations (
    library_site_condition_id uuid NOT NULL,
    library_hazard_id uuid NOT NULL,
    library_control_id uuid NOT NULL
);


--
-- Name: library_site_conditions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.library_site_conditions (
    id uuid NOT NULL,
    name character varying NOT NULL,
    handle_code character varying NOT NULL,
    archived_at timestamp with time zone
);


--
-- Name: library_task_activity_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.library_task_activity_groups (
    activity_group_id uuid NOT NULL,
    library_task_id uuid NOT NULL
);


--
-- Name: library_task_recommendations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.library_task_recommendations (
    library_task_id uuid NOT NULL,
    library_hazard_id uuid NOT NULL,
    library_control_id uuid NOT NULL
);


--
-- Name: library_tasks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.library_tasks (
    id uuid NOT NULL,
    name character varying NOT NULL,
    hesp integer NOT NULL,
    category character varying,
    unique_task_id character varying NOT NULL,
    work_type_id uuid NOT NULL,
    archived_at timestamp with time zone
);


--
-- Name: location_hazard_control_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.location_hazard_control_settings (
    id uuid NOT NULL,
    location_id uuid NOT NULL,
    library_hazard_id uuid NOT NULL,
    library_control_id uuid,
    tenant_id uuid NOT NULL,
    user_id uuid,
    created_at timestamp with time zone NOT NULL,
    disabled boolean NOT NULL
);


--
-- Name: locations_clustering; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.locations_clustering (
    id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    zoom smallint NOT NULL,
    geom public.geometry(Polygon) NOT NULL,
    geom_centroid public.geometry(Point) NOT NULL
);


--
-- Name: observations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.observations (
    timestamp_created timestamp with time zone,
    timestamp_updated timestamp with time zone,
    id uuid NOT NULL,
    observation_id character varying NOT NULL,
    observation_datetime timestamp without time zone,
    action_datetime timestamp without time zone,
    response_specific_action_datetime timestamp without time zone,
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
    tenant_id uuid NOT NULL
);


--
-- Name: parsed_files; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.parsed_files (
    timestamp_processed timestamp with time zone NOT NULL,
    file_path character varying NOT NULL,
    tenant_id uuid,
    id uuid NOT NULL
);


--
-- Name: project_locations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.project_locations (
    id uuid NOT NULL,
    name character varying NOT NULL,
    project_id uuid NOT NULL,
    archived_at timestamp with time zone,
    supervisor_id uuid,
    additional_supervisor_ids uuid[] NOT NULL,
    geom public.geometry(Point) NOT NULL,
    external_key character varying,
    tenant_id uuid NOT NULL,
    address character varying,
    clustering uuid[] NOT NULL
);


--
-- Name: projects; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.projects (
    id uuid NOT NULL,
    name character varying NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    status public.project_status NOT NULL,
    number character varying,
    description character varying,
    library_region_id uuid,
    library_division_id uuid,
    library_project_type_id uuid,
    manager_id uuid,
    supervisor_id uuid,
    additional_supervisor_ids uuid[] NOT NULL,
    contractor_id uuid,
    tenant_id uuid NOT NULL,
    archived_at timestamp with time zone,
    engineer_name character varying,
    project_zip_code character varying,
    contract_reference character varying,
    contract_name character varying,
    library_asset_type_id uuid,
    meta_attributes jsonb,
    customer_status character varying,
    work_package_type character varying
);


--
-- Name: rm_average_contractor_safety_score; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_average_contractor_safety_score (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    tenant_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);


--
-- Name: rm_average_crew_risk; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_average_crew_risk (
    calculated_at timestamp with time zone NOT NULL,
    inputs jsonb,
    params jsonb,
    value double precision NOT NULL,
    tenant_id uuid NOT NULL
);


--
-- Name: rm_average_supervisor_engagement_factor; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_average_supervisor_engagement_factor (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    tenant_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);


--
-- Name: rm_average_supervisor_relative_precursor_risk; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_average_supervisor_relative_precursor_risk (
    calculated_at timestamp with time zone NOT NULL,
    inputs jsonb,
    params jsonb,
    value double precision NOT NULL,
    tenant_id uuid NOT NULL
);


--
-- Name: rm_calc_parameters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_calc_parameters (
    name character varying NOT NULL,
    value character varying NOT NULL,
    tenant_id uuid
);


--
-- Name: rm_contractor_project_execution; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_contractor_project_execution (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    contractor_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);


--
-- Name: rm_contractor_safety_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_contractor_safety_history (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    contractor_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);


--
-- Name: rm_contractor_safety_rating; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_contractor_safety_rating (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    contractor_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);


--
-- Name: rm_contractor_safety_score; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_contractor_safety_score (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    contractor_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);


--
-- Name: rm_crew_risk; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_crew_risk (
    calculated_at timestamp with time zone NOT NULL,
    inputs jsonb,
    params jsonb,
    value double precision NOT NULL,
    crew_id uuid NOT NULL
);


--
-- Name: rm_division_relative_precursor_risk; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_division_relative_precursor_risk (
    calculated_at timestamp with time zone NOT NULL,
    inputs jsonb,
    params jsonb,
    value double precision NOT NULL,
    division_id uuid NOT NULL,
    tenant_id uuid NOT NULL
);


--
-- Name: rm_gbl_contractor_project_history_bsl; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_gbl_contractor_project_history_bsl (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    inputs jsonb,
    tenant_id uuid NOT NULL,
    params jsonb
);


--
-- Name: rm_gbl_contractor_project_history_bsl_stddev; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_gbl_contractor_project_history_bsl_stddev (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    inputs jsonb,
    tenant_id uuid NOT NULL,
    params jsonb
);


--
-- Name: rm_library_site_condition_relative_precursor_risk; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_library_site_condition_relative_precursor_risk (
    calculated_at timestamp with time zone NOT NULL,
    inputs jsonb,
    params jsonb,
    value double precision NOT NULL,
    tenant_id uuid NOT NULL,
    library_site_condition_id uuid NOT NULL
);


--
-- Name: rm_librarytask_relative_precursor_risk; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_librarytask_relative_precursor_risk (
    calculated_at timestamp with time zone NOT NULL,
    inputs jsonb,
    params jsonb,
    value double precision NOT NULL,
    library_task_id uuid NOT NULL
);


--
-- Name: rm_manually_added_site_conditions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_manually_added_site_conditions (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_location_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);


--
-- Name: rm_project_location_safety_climate_multiplier; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_project_location_safety_climate_multiplier (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_location_id uuid NOT NULL,
    contractor_id uuid,
    supervisor_id uuid,
    inputs jsonb,
    params jsonb
);


--
-- Name: rm_project_location_total_task_risk_score; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_project_location_total_task_risk_score (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_location_id uuid NOT NULL,
    date date NOT NULL,
    inputs jsonb,
    params jsonb
);


--
-- Name: rm_project_site_conditions_multiplier; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_project_site_conditions_multiplier (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_location_id uuid NOT NULL,
    date date NOT NULL,
    inputs jsonb,
    params jsonb
);


--
-- Name: rm_project_total_task_risk_score; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_project_total_task_risk_score (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_id uuid NOT NULL,
    date date NOT NULL,
    inputs jsonb,
    params jsonb
);


--
-- Name: rm_stddev_contractor_safety_score; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_stddev_contractor_safety_score (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    tenant_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);


--
-- Name: rm_stddev_crew_risk; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_stddev_crew_risk (
    calculated_at timestamp with time zone NOT NULL,
    inputs jsonb,
    params jsonb,
    value double precision NOT NULL,
    tenant_id uuid NOT NULL
);


--
-- Name: rm_stddev_supervisor_engagement_factor; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_stddev_supervisor_engagement_factor (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    tenant_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);


--
-- Name: rm_stddev_supervisor_relative_precursor_risk; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_stddev_supervisor_relative_precursor_risk (
    calculated_at timestamp with time zone NOT NULL,
    inputs jsonb,
    params jsonb,
    value double precision NOT NULL,
    tenant_id uuid NOT NULL
);


--
-- Name: rm_stochastic_activity_sc_relative_precursor_risk_score; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_stochastic_activity_sc_relative_precursor_risk_score (
    calculated_at timestamp with time zone NOT NULL,
    inputs jsonb,
    params jsonb,
    value double precision NOT NULL,
    activity_id uuid NOT NULL,
    date date NOT NULL
);


--
-- Name: rm_stochastic_activity_total_task_risk_score; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_stochastic_activity_total_task_risk_score (
    calculated_at timestamp with time zone NOT NULL,
    inputs jsonb,
    params jsonb,
    value double precision NOT NULL,
    activity_id uuid NOT NULL,
    date date NOT NULL
);


--
-- Name: rm_stochastic_location_total_task_risk_score; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_stochastic_location_total_task_risk_score (
    calculated_at timestamp with time zone NOT NULL,
    inputs jsonb,
    params jsonb,
    value double precision NOT NULL,
    project_location_id uuid NOT NULL,
    date date NOT NULL
);


--
-- Name: rm_stochastic_task_specific_risk_score; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_stochastic_task_specific_risk_score (
    calculated_at timestamp with time zone NOT NULL,
    inputs jsonb,
    params jsonb,
    value double precision NOT NULL,
    project_task_id uuid NOT NULL,
    date date NOT NULL
);


--
-- Name: rm_stochastic_total_location_risk_score; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_stochastic_total_location_risk_score (
    calculated_at timestamp with time zone NOT NULL,
    inputs jsonb,
    params jsonb,
    value double precision NOT NULL,
    project_location_id uuid NOT NULL,
    date date NOT NULL
);


--
-- Name: rm_stochastic_total_work_package_risk_score; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_stochastic_total_work_package_risk_score (
    calculated_at timestamp with time zone NOT NULL,
    inputs jsonb,
    params jsonb,
    value double precision NOT NULL,
    project_id uuid NOT NULL,
    date date NOT NULL
);


--
-- Name: rm_supervisor_engagement_factor; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_supervisor_engagement_factor (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    supervisor_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);


--
-- Name: rm_supervisor_relative_precursor_risk; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_supervisor_relative_precursor_risk (
    calculated_at timestamp with time zone NOT NULL,
    inputs jsonb,
    params jsonb,
    value double precision NOT NULL,
    supervisor_id uuid NOT NULL
);


--
-- Name: rm_task_specific_risk_score; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_task_specific_risk_score (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_task_id uuid NOT NULL,
    date date NOT NULL,
    inputs jsonb,
    params jsonb
);


--
-- Name: rm_task_specific_safety_climate_multiplier; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_task_specific_safety_climate_multiplier (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    library_task_id uuid NOT NULL,
    inputs jsonb,
    params jsonb
);


--
-- Name: rm_task_specific_site_conditions_multiplier; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_task_specific_site_conditions_multiplier (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_task_id uuid NOT NULL,
    date date NOT NULL,
    inputs jsonb,
    params jsonb
);


--
-- Name: rm_total_activity_risk_score; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_total_activity_risk_score (
    calculated_at timestamp with time zone NOT NULL,
    inputs jsonb,
    params jsonb,
    value double precision NOT NULL,
    activity_id uuid NOT NULL,
    date date NOT NULL
);


--
-- Name: rm_total_project_location_risk_score; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_total_project_location_risk_score (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_location_id uuid NOT NULL,
    date date NOT NULL,
    inputs jsonb,
    params jsonb
);


--
-- Name: rm_total_project_risk_score; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rm_total_project_risk_score (
    calculated_at timestamp with time zone NOT NULL,
    value double precision NOT NULL,
    project_id uuid NOT NULL,
    date date NOT NULL,
    inputs jsonb,
    params jsonb
);


--
-- Name: site_condition_controls; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.site_condition_controls (
    id uuid NOT NULL,
    site_condition_hazard_id uuid NOT NULL,
    library_control_id uuid NOT NULL,
    user_id uuid,
    is_applicable boolean NOT NULL,
    "position" integer NOT NULL,
    archived_at timestamp with time zone
);


--
-- Name: site_condition_hazards; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.site_condition_hazards (
    id uuid NOT NULL,
    site_condition_id uuid NOT NULL,
    library_hazard_id uuid NOT NULL,
    user_id uuid,
    is_applicable boolean NOT NULL,
    "position" integer NOT NULL,
    archived_at timestamp with time zone
);


--
-- Name: site_conditions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.site_conditions (
    id uuid NOT NULL,
    location_id uuid NOT NULL,
    library_site_condition_id uuid NOT NULL,
    archived_at timestamp with time zone,
    user_id uuid,
    date date,
    details jsonb,
    alert boolean,
    multiplier double precision,
    is_manually_added boolean NOT NULL
);


--
-- Name: supervisor; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.supervisor (
    id uuid NOT NULL,
    external_key character varying NOT NULL,
    tenant_id uuid NOT NULL,
    user_id uuid
);


--
-- Name: task_controls; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_controls (
    id uuid NOT NULL,
    task_hazard_id uuid NOT NULL,
    library_control_id uuid NOT NULL,
    user_id uuid,
    is_applicable boolean NOT NULL,
    "position" integer NOT NULL,
    archived_at timestamp with time zone
);


--
-- Name: task_hazards; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_hazards (
    id uuid NOT NULL,
    task_id uuid NOT NULL,
    library_hazard_id uuid NOT NULL,
    user_id uuid,
    is_applicable boolean NOT NULL,
    "position" integer NOT NULL,
    archived_at timestamp with time zone
);


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tasks (
    id uuid NOT NULL,
    location_id uuid NOT NULL,
    library_task_id uuid NOT NULL,
    start_date date,
    end_date date,
    status public.task_status NOT NULL,
    archived_at timestamp with time zone,
    activity_id uuid
);


--
-- Name: tenants; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tenants (
    id uuid NOT NULL,
    tenant_name character varying NOT NULL,
    auth_realm_name character varying NOT NULL
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    keycloak_id uuid NOT NULL,
    first_name character varying NOT NULL,
    last_name character varying NOT NULL,
    role character varying,
    email character varying DEFAULT ''::character varying NOT NULL,
    tenant_id uuid NOT NULL
);


--
-- Name: work_type_tenant_link; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.work_type_tenant_link (
    work_type_id uuid NOT NULL,
    tenant_id uuid NOT NULL
);


--
-- Name: work_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.work_types (
    id uuid NOT NULL,
    name character varying NOT NULL
);


--
-- Name: activities activities_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_pkey PRIMARY KEY (id);


--
-- Name: activity_supervisor_link activity_supervisor_link_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.activity_supervisor_link
    ADD CONSTRAINT activity_supervisor_link_pkey PRIMARY KEY (activity_id, supervisor_id);


--
-- Name: library_activity_types activity_types_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_activity_types
    ADD CONSTRAINT activity_types_name_key UNIQUE (name);


--
-- Name: audit_event_diffs audit_event_diffs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_event_diffs
    ADD CONSTRAINT audit_event_diffs_pkey PRIMARY KEY (id);


--
-- Name: audit_events audit_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_events
    ADD CONSTRAINT audit_events_pkey PRIMARY KEY (id);


--
-- Name: compatible_units compatible_units_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.compatible_units
    ADD CONSTRAINT compatible_units_pkey PRIMARY KEY (compatible_unit_id, tenant_id);


--
-- Name: contractor_aliases contractor_aliases_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contractor_aliases
    ADD CONSTRAINT contractor_aliases_pkey PRIMARY KEY (id);


--
-- Name: contractor contractor_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contractor
    ADD CONSTRAINT contractor_pkey PRIMARY KEY (id);


--
-- Name: crew crew_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.crew
    ADD CONSTRAINT crew_pkey PRIMARY KEY (id);


--
-- Name: daily_reports daily_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.daily_reports
    ADD CONSTRAINT daily_reports_pkey PRIMARY KEY (id);


--
-- Name: element_library_task_link element_library_task_link_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.element_library_task_link
    ADD CONSTRAINT element_library_task_link_pkey PRIMARY KEY (element_id, library_task_id);


--
-- Name: elements elements_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.elements
    ADD CONSTRAINT elements_name_key UNIQUE (name);


--
-- Name: elements elements_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.elements
    ADD CONSTRAINT elements_pkey PRIMARY KEY (id);


--
-- Name: form_definitions form_definitions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.form_definitions
    ADD CONSTRAINT form_definitions_pkey PRIMARY KEY (id);


--
-- Name: google_cloud_storage_blob google_cloud_storage_blob_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.google_cloud_storage_blob
    ADD CONSTRAINT google_cloud_storage_blob_pkey PRIMARY KEY (id);


--
-- Name: hydro_one_job_type_task_map hydro_one_job_type_task_map_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hydro_one_job_type_task_map
    ADD CONSTRAINT hydro_one_job_type_task_map_pkey PRIMARY KEY (job_type, unique_task_id);


--
-- Name: incident_task_link incident_task_link_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_task_link
    ADD CONSTRAINT incident_task_link_pkey PRIMARY KEY (incident_id, library_task_id);


--
-- Name: incidents incidents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_pkey PRIMARY KEY (id);


--
-- Name: ingest_work_package_to_compatible_unit_link ingest_work_package_to_compatible_unit_link_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingest_work_package_to_compatible_unit_link
    ADD CONSTRAINT ingest_work_package_to_compatible_unit_link_pkey PRIMARY KEY (id);


--
-- Name: ingestion_process ingestion_process_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingestion_process
    ADD CONSTRAINT ingestion_process_pkey PRIMARY KEY (id);


--
-- Name: ingestion_settings ingestion_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingestion_settings
    ADD CONSTRAINT ingestion_settings_pkey PRIMARY KEY (tenant_id);


--
-- Name: jsbs jsbs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jsbs
    ADD CONSTRAINT jsbs_pkey PRIMARY KEY (id);


--
-- Name: library_activity_groups library_activity_groups_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_activity_groups
    ADD CONSTRAINT library_activity_groups_name_key UNIQUE (name);


--
-- Name: library_activity_groups library_activity_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_activity_groups
    ADD CONSTRAINT library_activity_groups_pkey PRIMARY KEY (id);


--
-- Name: library_activity_type_tenant_link library_activity_type_tenant_link_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_activity_type_tenant_link
    ADD CONSTRAINT library_activity_type_tenant_link_pkey PRIMARY KEY (library_activity_type_id, tenant_id);


--
-- Name: library_activity_types library_activity_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_activity_types
    ADD CONSTRAINT library_activity_types_pkey PRIMARY KEY (id);


--
-- Name: library_asset_types library_asset_types_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_asset_types
    ADD CONSTRAINT library_asset_types_name_key UNIQUE (name);


--
-- Name: library_asset_types library_asset_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_asset_types
    ADD CONSTRAINT library_asset_types_pkey PRIMARY KEY (id);


--
-- Name: library_controls library_controls_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_controls
    ADD CONSTRAINT library_controls_pkey PRIMARY KEY (id);


--
-- Name: library_division_tenant_link library_division_tenant_link_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_division_tenant_link
    ADD CONSTRAINT library_division_tenant_link_pkey PRIMARY KEY (library_division_id, tenant_id);


--
-- Name: library_divisions library_divisions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_divisions
    ADD CONSTRAINT library_divisions_pkey PRIMARY KEY (id);


--
-- Name: library_hazards library_hazards_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_hazards
    ADD CONSTRAINT library_hazards_pkey PRIMARY KEY (id);


--
-- Name: library_project_types library_project_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_project_types
    ADD CONSTRAINT library_project_types_pkey PRIMARY KEY (id);


--
-- Name: library_region_tenant_link library_region_tenant_link_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_region_tenant_link
    ADD CONSTRAINT library_region_tenant_link_pkey PRIMARY KEY (library_region_id, tenant_id);


--
-- Name: library_regions library_regions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_regions
    ADD CONSTRAINT library_regions_pkey PRIMARY KEY (id);


--
-- Name: library_site_condition_recommendations library_site_condition_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_site_condition_recommendations
    ADD CONSTRAINT library_site_condition_recommendations_pkey PRIMARY KEY (library_site_condition_id, library_hazard_id, library_control_id);


--
-- Name: library_site_conditions library_site_conditions_handle_code_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_site_conditions
    ADD CONSTRAINT library_site_conditions_handle_code_unique UNIQUE (handle_code);


--
-- Name: library_site_conditions library_site_conditions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_site_conditions
    ADD CONSTRAINT library_site_conditions_pkey PRIMARY KEY (id);


--
-- Name: library_task_activity_groups library_task_activity_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_task_activity_groups
    ADD CONSTRAINT library_task_activity_groups_pkey PRIMARY KEY (activity_group_id, library_task_id);


--
-- Name: library_task_recommendations library_task_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_task_recommendations
    ADD CONSTRAINT library_task_recommendations_pkey PRIMARY KEY (library_task_id, library_hazard_id, library_control_id);


--
-- Name: library_tasks library_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_tasks
    ADD CONSTRAINT library_tasks_pkey PRIMARY KEY (id);


--
-- Name: location_hazard_control_settings location_hazard_control_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.location_hazard_control_settings
    ADD CONSTRAINT location_hazard_control_settings_pkey PRIMARY KEY (id);


--
-- Name: locations_clustering locations_clustering_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations_clustering
    ADD CONSTRAINT locations_clustering_pkey PRIMARY KEY (id);


--
-- Name: observations observations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observations
    ADD CONSTRAINT observations_pkey PRIMARY KEY (id);


--
-- Name: parsed_files parsed_files_id_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parsed_files
    ADD CONSTRAINT parsed_files_id_pkey PRIMARY KEY (id);


--
-- Name: project_locations project_locations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_locations
    ADD CONSTRAINT project_locations_pkey PRIMARY KEY (id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: rm_average_contractor_safety_score rm_average_contractor_safety_score_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_average_contractor_safety_score
    ADD CONSTRAINT rm_average_contractor_safety_score_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_average_crew_risk rm_average_crew_risk_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_average_crew_risk
    ADD CONSTRAINT rm_average_crew_risk_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_average_supervisor_engagement_factor rm_average_supervisor_engagement_factor_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_average_supervisor_engagement_factor
    ADD CONSTRAINT rm_average_supervisor_engagement_factor_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_average_supervisor_relative_precursor_risk rm_average_supervisor_relative_precursor_risk_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_average_supervisor_relative_precursor_risk
    ADD CONSTRAINT rm_average_supervisor_relative_precursor_risk_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_calc_parameters rm_calc_parameters_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_calc_parameters
    ADD CONSTRAINT rm_calc_parameters_pkey PRIMARY KEY (name);


--
-- Name: rm_contractor_project_execution rm_contractor_project_execution_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_contractor_project_execution
    ADD CONSTRAINT rm_contractor_project_execution_pkey PRIMARY KEY (calculated_at, contractor_id);


--
-- Name: rm_contractor_safety_history rm_contractor_safety_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_contractor_safety_history
    ADD CONSTRAINT rm_contractor_safety_history_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_contractor_safety_rating rm_contractor_safety_rating_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_contractor_safety_rating
    ADD CONSTRAINT rm_contractor_safety_rating_pkey PRIMARY KEY (calculated_at, contractor_id);


--
-- Name: rm_contractor_safety_score rm_contractor_safety_score_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_contractor_safety_score
    ADD CONSTRAINT rm_contractor_safety_score_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_crew_risk rm_crew_risk_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_crew_risk
    ADD CONSTRAINT rm_crew_risk_pkey PRIMARY KEY (calculated_at, crew_id);


--
-- Name: rm_division_relative_precursor_risk rm_division_relative_precursor_risk_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_division_relative_precursor_risk
    ADD CONSTRAINT rm_division_relative_precursor_risk_pkey PRIMARY KEY (calculated_at, tenant_id, division_id);


--
-- Name: rm_gbl_contractor_project_history_bsl rm_gbl_contractor_project_history_bsl_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_gbl_contractor_project_history_bsl
    ADD CONSTRAINT rm_gbl_contractor_project_history_bsl_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_gbl_contractor_project_history_bsl_stddev rm_gbl_contractor_project_history_bsl_stddev_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_gbl_contractor_project_history_bsl_stddev
    ADD CONSTRAINT rm_gbl_contractor_project_history_bsl_stddev_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_library_site_condition_relative_precursor_risk rm_library_site_condition_relative_precursor_risk_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_library_site_condition_relative_precursor_risk
    ADD CONSTRAINT rm_library_site_condition_relative_precursor_risk_pkey PRIMARY KEY (calculated_at, tenant_id, library_site_condition_id);


--
-- Name: rm_librarytask_relative_precursor_risk rm_librarytask_relative_precursor_risk_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_librarytask_relative_precursor_risk
    ADD CONSTRAINT rm_librarytask_relative_precursor_risk_pkey PRIMARY KEY (calculated_at, library_task_id);


--
-- Name: rm_manually_added_site_conditions rm_manually_added_site_conditions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_manually_added_site_conditions
    ADD CONSTRAINT rm_manually_added_site_conditions_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_project_location_safety_climate_multiplier rm_project_location_safety_climate_multiplier_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_project_location_safety_climate_multiplier
    ADD CONSTRAINT rm_project_location_safety_climate_multiplier_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_project_location_total_task_risk_score rm_project_location_total_task_risk_score_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_project_location_total_task_risk_score
    ADD CONSTRAINT rm_project_location_total_task_risk_score_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_project_site_conditions_multiplier rm_project_site_conditions_multiplier_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_project_site_conditions_multiplier
    ADD CONSTRAINT rm_project_site_conditions_multiplier_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_project_total_task_risk_score rm_project_total_task_risk_score_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_project_total_task_risk_score
    ADD CONSTRAINT rm_project_total_task_risk_score_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_stddev_contractor_safety_score rm_stddev_contractor_safety_score_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stddev_contractor_safety_score
    ADD CONSTRAINT rm_stddev_contractor_safety_score_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_stddev_crew_risk rm_stddev_crew_risk_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stddev_crew_risk
    ADD CONSTRAINT rm_stddev_crew_risk_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_stddev_supervisor_engagement_factor rm_stddev_supervisor_engagement_factor_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stddev_supervisor_engagement_factor
    ADD CONSTRAINT rm_stddev_supervisor_engagement_factor_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_stddev_supervisor_relative_precursor_risk rm_stddev_supervisor_relative_precursor_risk_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stddev_supervisor_relative_precursor_risk
    ADD CONSTRAINT rm_stddev_supervisor_relative_precursor_risk_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_stochastic_activity_sc_relative_precursor_risk_score rm_stochastic_activity_sc_relative_precursor_risk_score_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stochastic_activity_sc_relative_precursor_risk_score
    ADD CONSTRAINT rm_stochastic_activity_sc_relative_precursor_risk_score_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_stochastic_activity_total_task_risk_score rm_stochastic_activity_total_task_risk_score_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stochastic_activity_total_task_risk_score
    ADD CONSTRAINT rm_stochastic_activity_total_task_risk_score_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_stochastic_location_total_task_risk_score rm_stochastic_location_total_task_risk_score_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stochastic_location_total_task_risk_score
    ADD CONSTRAINT rm_stochastic_location_total_task_risk_score_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_stochastic_task_specific_risk_score rm_stochastic_task_specific_risk_score_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stochastic_task_specific_risk_score
    ADD CONSTRAINT rm_stochastic_task_specific_risk_score_pkey PRIMARY KEY (calculated_at, project_task_id);


--
-- Name: rm_stochastic_total_location_risk_score rm_stochastic_total_location_risk_score_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stochastic_total_location_risk_score
    ADD CONSTRAINT rm_stochastic_total_location_risk_score_pkey PRIMARY KEY (calculated_at, project_location_id);


--
-- Name: rm_stochastic_total_work_package_risk_score rm_stochastic_total_work_package_risk_score_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stochastic_total_work_package_risk_score
    ADD CONSTRAINT rm_stochastic_total_work_package_risk_score_pkey PRIMARY KEY (calculated_at, project_id);


--
-- Name: rm_supervisor_engagement_factor rm_supervisor_engagement_factor_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_supervisor_engagement_factor
    ADD CONSTRAINT rm_supervisor_engagement_factor_pkey PRIMARY KEY (calculated_at, supervisor_id);


--
-- Name: rm_supervisor_relative_precursor_risk rm_supervisor_relative_precursor_risk_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_supervisor_relative_precursor_risk
    ADD CONSTRAINT rm_supervisor_relative_precursor_risk_pkey PRIMARY KEY (calculated_at, supervisor_id);


--
-- Name: rm_task_specific_risk_score rm_task_specific_risk_score_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_task_specific_risk_score
    ADD CONSTRAINT rm_task_specific_risk_score_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_task_specific_safety_climate_multiplier rm_task_specific_safety_climate_multiplier_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_task_specific_safety_climate_multiplier
    ADD CONSTRAINT rm_task_specific_safety_climate_multiplier_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_task_specific_site_conditions_multiplier rm_task_specific_site_conditions_multiplier_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_task_specific_site_conditions_multiplier
    ADD CONSTRAINT rm_task_specific_site_conditions_multiplier_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_total_activity_risk_score rm_total_activity_risk_score_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_total_activity_risk_score
    ADD CONSTRAINT rm_total_activity_risk_score_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_total_project_location_risk_score rm_total_project_location_risk_score_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_total_project_location_risk_score
    ADD CONSTRAINT rm_total_project_location_risk_score_pkey PRIMARY KEY (calculated_at);


--
-- Name: rm_total_project_risk_score rm_total_project_risk_score_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_total_project_risk_score
    ADD CONSTRAINT rm_total_project_risk_score_pkey PRIMARY KEY (calculated_at);


--
-- Name: site_condition_controls site_condition_controls_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_condition_controls
    ADD CONSTRAINT site_condition_controls_pkey PRIMARY KEY (id);


--
-- Name: site_condition_hazards site_condition_hazards_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_condition_hazards
    ADD CONSTRAINT site_condition_hazards_pkey PRIMARY KEY (id);


--
-- Name: site_conditions site_conditions_evaluated_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_conditions
    ADD CONSTRAINT site_conditions_evaluated_key UNIQUE (location_id, library_site_condition_id, date);


--
-- Name: site_conditions site_conditions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_conditions
    ADD CONSTRAINT site_conditions_pkey PRIMARY KEY (id);


--
-- Name: supervisor supervisor_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supervisor
    ADD CONSTRAINT supervisor_pkey PRIMARY KEY (id);


--
-- Name: supervisor supervisor_unique_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supervisor
    ADD CONSTRAINT supervisor_unique_name UNIQUE (tenant_id, external_key);


--
-- Name: task_controls task_controls_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_controls
    ADD CONSTRAINT task_controls_pkey PRIMARY KEY (id);


--
-- Name: task_hazards task_hazards_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_hazards
    ADD CONSTRAINT task_hazards_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: tenants tenants_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_pkey PRIMARY KEY (id);


--
-- Name: configurations u_name_tenant_1; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.configurations
    ADD CONSTRAINT u_name_tenant_1 UNIQUE (name, tenant_id);


--
-- Name: crew unique_crew_tenant_external_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.crew
    ADD CONSTRAINT unique_crew_tenant_external_key UNIQUE (tenant_id, external_key);


--
-- Name: library_tasks unique_task_id_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_tasks
    ADD CONSTRAINT unique_task_id_unique UNIQUE (unique_task_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: work_type_tenant_link work_type_tenant_link_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.work_type_tenant_link
    ADD CONSTRAINT work_type_tenant_link_pkey PRIMARY KEY (work_type_id, tenant_id);


--
-- Name: work_types work_types_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.work_types
    ADD CONSTRAINT work_types_name_key UNIQUE (name);


--
-- Name: work_types work_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.work_types
    ADD CONSTRAINT work_types_pkey PRIMARY KEY (id);


--
-- Name: activities_crew_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX activities_crew_id_ix ON public.activities USING btree (crew_id);


--
-- Name: activities_library_activity_type_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX activities_library_activity_type_id_ix ON public.activities USING btree (library_activity_type_id);


--
-- Name: activities_location_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX activities_location_id_ix ON public.activities USING btree (location_id);


--
-- Name: audit_event_diffs_ae_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX audit_event_diffs_ae_fkey ON public.audit_event_diffs USING btree (event_id);


--
-- Name: audit_event_diffs_object_id_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX audit_event_diffs_object_id_fkey ON public.audit_event_diffs USING btree (object_id);


--
-- Name: contractor_aliases_contractor_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX contractor_aliases_contractor_id_ix ON public.contractor_aliases USING btree (contractor_id);


--
-- Name: contractor_aliases_tenant_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX contractor_aliases_tenant_id_ix ON public.contractor_aliases USING btree (tenant_id);


--
-- Name: contractor_tenant_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX contractor_tenant_id_ix ON public.contractor USING btree (tenant_id);


--
-- Name: daily_report_pl_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX daily_report_pl_fkey ON public.daily_reports USING btree (project_location_id);


--
-- Name: daily_reports_completed_by_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX daily_reports_completed_by_id_ix ON public.daily_reports USING btree (completed_by_id);


--
-- Name: daily_reports_created_by_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX daily_reports_created_by_id_ix ON public.daily_reports USING btree (created_by_id);


--
-- Name: form_definitions_tenant_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX form_definitions_tenant_id_ix ON public.form_definitions USING btree (tenant_id);


--
-- Name: incidents_contractor_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX incidents_contractor_id_ix ON public.incidents USING btree (contractor_id);


--
-- Name: incidents_supervisor_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX incidents_supervisor_id_ix ON public.incidents USING btree (supervisor_id);


--
-- Name: incidents_tenant_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX incidents_tenant_id_ix ON public.incidents USING btree (tenant_id);


--
-- Name: ingest_work_package_to_compatible_unit_link_tenant_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ingest_work_package_to_compatible_unit_link_tenant_id_ix ON public.ingest_work_package_to_compatible_unit_link USING btree (tenant_id);


--
-- Name: ix_tenants_tenant_name; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_tenants_tenant_name ON public.tenants USING btree (tenant_name);


--
-- Name: ix_users_keycloak_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_keycloak_id ON public.users USING btree (keycloak_id);


--
-- Name: ix_users_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_tenant_id ON public.users USING btree (tenant_id);


--
-- Name: library_tasks_work_type_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX library_tasks_work_type_id_ix ON public.library_tasks USING btree (work_type_id);


--
-- Name: location_hazard_control_settings_lhc_uk; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX location_hazard_control_settings_lhc_uk ON public.location_hazard_control_settings USING btree (location_id, library_hazard_id, library_control_id);


--
-- Name: locations_clustering_0_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX locations_clustering_0_ix ON public.project_locations USING btree (public.clustering_0(clustering)) WHERE (archived_at IS NULL);


--
-- Name: locations_clustering_10_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX locations_clustering_10_ix ON public.project_locations USING btree (public.clustering_10(clustering)) WHERE (archived_at IS NULL);


--
-- Name: locations_clustering_11_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX locations_clustering_11_ix ON public.project_locations USING btree (public.clustering_11(clustering)) WHERE (archived_at IS NULL);


--
-- Name: locations_clustering_12_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX locations_clustering_12_ix ON public.project_locations USING btree (public.clustering_12(clustering)) WHERE (archived_at IS NULL);


--
-- Name: locations_clustering_1_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX locations_clustering_1_ix ON public.project_locations USING btree (public.clustering_1(clustering)) WHERE (archived_at IS NULL);


--
-- Name: locations_clustering_2_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX locations_clustering_2_ix ON public.project_locations USING btree (public.clustering_2(clustering)) WHERE (archived_at IS NULL);


--
-- Name: locations_clustering_3_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX locations_clustering_3_ix ON public.project_locations USING btree (public.clustering_3(clustering)) WHERE (archived_at IS NULL);


--
-- Name: locations_clustering_4_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX locations_clustering_4_ix ON public.project_locations USING btree (public.clustering_4(clustering)) WHERE (archived_at IS NULL);


--
-- Name: locations_clustering_5_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX locations_clustering_5_ix ON public.project_locations USING btree (public.clustering_5(clustering)) WHERE (archived_at IS NULL);


--
-- Name: locations_clustering_6_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX locations_clustering_6_ix ON public.project_locations USING btree (public.clustering_6(clustering)) WHERE (archived_at IS NULL);


--
-- Name: locations_clustering_7_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX locations_clustering_7_ix ON public.project_locations USING btree (public.clustering_7(clustering)) WHERE (archived_at IS NULL);


--
-- Name: locations_clustering_8_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX locations_clustering_8_ix ON public.project_locations USING btree (public.clustering_8(clustering)) WHERE (archived_at IS NULL);


--
-- Name: locations_clustering_9_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX locations_clustering_9_ix ON public.project_locations USING btree (public.clustering_9(clustering)) WHERE (archived_at IS NULL);


--
-- Name: locations_clustering_geom_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX locations_clustering_geom_ix ON public.locations_clustering USING gist (geom);


--
-- Name: locations_clustering_tenant_id_zoom_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX locations_clustering_tenant_id_zoom_ix ON public.locations_clustering USING btree (tenant_id, zoom);


--
-- Name: locations_geom_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX locations_geom_ix ON public.project_locations USING gist (geom) INCLUDE (id, project_id) WHERE (archived_at IS NULL);


--
-- Name: locations_project_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX locations_project_id_ix ON public.project_locations USING btree (project_id);


--
-- Name: locations_supervisor_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX locations_supervisor_id_ix ON public.project_locations USING btree (supervisor_id);


--
-- Name: name; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX name ON public.configurations USING btree (name) WHERE (tenant_id IS NULL);


--
-- Name: observations_contractor_involved_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX observations_contractor_involved_id_ix ON public.observations USING btree (contractor_involved_id);


--
-- Name: observations_supervisor_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX observations_supervisor_id_ix ON public.observations USING btree (supervisor_id);


--
-- Name: observations_tenant_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX observations_tenant_id_ix ON public.observations USING btree (tenant_id);


--
-- Name: parsed_files_tenant_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX parsed_files_tenant_id_ix ON public.parsed_files USING btree (tenant_id);


--
-- Name: project_locations_tenant_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_locations_tenant_id_idx ON public.project_locations USING btree (tenant_id);


--
-- Name: projects_tenant_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX projects_tenant_status_idx ON public.projects USING btree (tenant_id, status) WHERE (archived_at IS NULL);


--
-- Name: rm_average_contractor_safety_score_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_average_contractor_safety_score_entity_idx ON public.rm_average_contractor_safety_score USING btree (tenant_id);


--
-- Name: rm_average_crew_risk_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_average_crew_risk_entity_idx ON public.rm_average_crew_risk USING btree (tenant_id);


--
-- Name: rm_average_supervisor_engagement_factor_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_average_supervisor_engagement_factor_entity_idx ON public.rm_average_supervisor_engagement_factor USING btree (tenant_id);


--
-- Name: rm_average_supervisor_relative_precursor_risk_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_average_supervisor_relative_precursor_risk_entity_idx ON public.rm_average_supervisor_relative_precursor_risk USING btree (tenant_id);


--
-- Name: rm_contractor_project_execution_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_contractor_project_execution_entity_idx ON public.rm_contractor_project_execution USING btree (contractor_id);


--
-- Name: rm_contractor_safety_history_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_contractor_safety_history_entity_idx ON public.rm_contractor_safety_history USING btree (contractor_id);


--
-- Name: rm_contractor_safety_rating_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_contractor_safety_rating_entity_idx ON public.rm_contractor_safety_rating USING btree (contractor_id);


--
-- Name: rm_contractor_safety_score_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_contractor_safety_score_entity_idx ON public.rm_contractor_safety_score USING btree (contractor_id);


--
-- Name: rm_crew_risk_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_crew_risk_entity_idx ON public.rm_crew_risk USING btree (crew_id);


--
-- Name: rm_division_relative_precursor_risk_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_division_relative_precursor_risk_entity_idx ON public.rm_division_relative_precursor_risk USING btree (tenant_id, division_id);


--
-- Name: rm_gbl_contractor_project_history_bsl_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_gbl_contractor_project_history_bsl_entity_idx ON public.rm_gbl_contractor_project_history_bsl USING btree (tenant_id);


--
-- Name: rm_gbl_contractor_project_history_bsl_stddev_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_gbl_contractor_project_history_bsl_stddev_entity_idx ON public.rm_gbl_contractor_project_history_bsl_stddev USING btree (tenant_id);


--
-- Name: rm_library_site_condition_relative_precursor_risk_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_library_site_condition_relative_precursor_risk_entity_idx ON public.rm_library_site_condition_relative_precursor_risk USING btree (tenant_id, library_site_condition_id);


--
-- Name: rm_librarytask_relative_precursor_risk_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_librarytask_relative_precursor_risk_entity_idx ON public.rm_librarytask_relative_precursor_risk USING btree (library_task_id);


--
-- Name: rm_manually_added_site_conditions_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_manually_added_site_conditions_entity_idx ON public.rm_manually_added_site_conditions USING btree (project_location_id);


--
-- Name: rm_project_location_safety_climate_multiplier_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_project_location_safety_climate_multiplier_entity_idx ON public.rm_project_location_safety_climate_multiplier USING btree (project_location_id);


--
-- Name: rm_project_location_total_task_risk_score_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_project_location_total_task_risk_score_entity_idx ON public.rm_project_location_total_task_risk_score USING btree (project_location_id, date);


--
-- Name: rm_project_site_conditions_multiplier_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_project_site_conditions_multiplier_entity_idx ON public.rm_project_site_conditions_multiplier USING btree (project_location_id, date);


--
-- Name: rm_project_total_task_risk_score_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_project_total_task_risk_score_entity_idx ON public.rm_project_total_task_risk_score USING btree (project_id);


--
-- Name: rm_stddev_contractor_safety_score_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_stddev_contractor_safety_score_entity_idx ON public.rm_stddev_contractor_safety_score USING btree (tenant_id);


--
-- Name: rm_stddev_crew_risk_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_stddev_crew_risk_entity_idx ON public.rm_stddev_crew_risk USING btree (tenant_id);


--
-- Name: rm_stddev_supervisor_engagement_factor_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_stddev_supervisor_engagement_factor_entity_idx ON public.rm_stddev_supervisor_engagement_factor USING btree (tenant_id);


--
-- Name: rm_stddev_supervisor_relative_precursor_risk_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_stddev_supervisor_relative_precursor_risk_entity_idx ON public.rm_stddev_supervisor_relative_precursor_risk USING btree (tenant_id);


--
-- Name: rm_stochastic_activity_sc_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_stochastic_activity_sc_entity_idx ON public.rm_stochastic_activity_sc_relative_precursor_risk_score USING btree (activity_id, date);


--
-- Name: rm_stochastic_activity_total_task_risk_score_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_stochastic_activity_total_task_risk_score_entity_idx ON public.rm_stochastic_activity_total_task_risk_score USING btree (activity_id, date);


--
-- Name: rm_stochastic_location_total_task_risk_score_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_stochastic_location_total_task_risk_score_entity_idx ON public.rm_stochastic_location_total_task_risk_score USING btree (project_location_id, date);


--
-- Name: rm_stochastic_task_specific_risk_score_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_stochastic_task_specific_risk_score_entity_idx ON public.rm_stochastic_task_specific_risk_score USING btree (project_task_id, date);


--
-- Name: rm_stochastic_total_location_risk_score_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_stochastic_total_location_risk_score_entity_idx ON public.rm_stochastic_total_location_risk_score USING btree (project_location_id, date);


--
-- Name: rm_stochastic_total_work_package_risk_score_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_stochastic_total_work_package_risk_score_entity_idx ON public.rm_stochastic_total_work_package_risk_score USING btree (project_id, date);


--
-- Name: rm_supervisor_engagement_factor_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_supervisor_engagement_factor_entity_idx ON public.rm_supervisor_engagement_factor USING btree (supervisor_id);


--
-- Name: rm_supervisor_relative_precursor_risk_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_supervisor_relative_precursor_risk_entity_idx ON public.rm_supervisor_relative_precursor_risk USING btree (supervisor_id);


--
-- Name: rm_task_specific_risk_score_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_task_specific_risk_score_entity_idx ON public.rm_task_specific_risk_score USING btree (project_task_id, date);


--
-- Name: rm_task_specific_safety_climate_multiplier_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_task_specific_safety_climate_multiplier_entity_idx ON public.rm_task_specific_safety_climate_multiplier USING btree (library_task_id);


--
-- Name: rm_task_specific_site_conditions_multiplier_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_task_specific_site_conditions_multiplier_entity_idx ON public.rm_task_specific_site_conditions_multiplier USING btree (project_task_id, date);


--
-- Name: rm_total_activity_risk_score_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_total_activity_risk_score_entity_idx ON public.rm_total_activity_risk_score USING btree (activity_id, date);


--
-- Name: rm_total_project_location_risk_score_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_total_project_location_risk_score_entity_idx ON public.rm_total_project_location_risk_score USING btree (project_location_id, date);


--
-- Name: rm_total_project_risk_score_entity_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rm_total_project_risk_score_entity_idx ON public.rm_total_project_risk_score USING btree (project_id, date);


--
-- Name: site_condition_controls_library_control_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX site_condition_controls_library_control_id_ix ON public.site_condition_controls USING btree (library_control_id);


--
-- Name: site_condition_controls_site_condition_hazard_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX site_condition_controls_site_condition_hazard_id_ix ON public.site_condition_controls USING btree (site_condition_hazard_id);


--
-- Name: site_condition_hazards_library_hazard_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX site_condition_hazards_library_hazard_id_ix ON public.site_condition_hazards USING btree (library_hazard_id);


--
-- Name: site_condition_hazards_site_condition_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX site_condition_hazards_site_condition_id_ix ON public.site_condition_hazards USING btree (site_condition_id);


--
-- Name: site_conditions_evaluated_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX site_conditions_evaluated_idx ON public.site_conditions USING btree (location_id, date);


--
-- Name: site_conditions_lsc_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX site_conditions_lsc_fkey ON public.site_conditions USING btree (library_site_condition_id);


--
-- Name: site_conditions_manual_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX site_conditions_manual_idx ON public.site_conditions USING btree (location_id) WHERE (user_id IS NOT NULL);


--
-- Name: site_conditions_manually_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX site_conditions_manually_key ON public.site_conditions USING btree (location_id, library_site_condition_id) WHERE ((user_id IS NOT NULL) AND (archived_at IS NULL));


--
-- Name: supervisor_tenant_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX supervisor_tenant_id_ix ON public.supervisor USING btree (tenant_id);


--
-- Name: task_controls_library_control_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX task_controls_library_control_id_ix ON public.task_controls USING btree (library_control_id);


--
-- Name: task_controls_task_hazard_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX task_controls_task_hazard_id_ix ON public.task_controls USING btree (task_hazard_id);


--
-- Name: tasks_activity_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX tasks_activity_id_ix ON public.tasks USING btree (activity_id);


--
-- Name: tasks_hazards_library_hazard_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX tasks_hazards_library_hazard_id_ix ON public.task_hazards USING btree (library_hazard_id);


--
-- Name: tasks_hazards_plt_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX tasks_hazards_plt_fkey ON public.task_hazards USING btree (task_id);


--
-- Name: tasks_lt_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX tasks_lt_fkey ON public.tasks USING btree (library_task_id);


--
-- Name: tasks_pl_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX tasks_pl_fkey ON public.tasks USING btree (location_id);


--
-- Name: users_tenant_keycloak_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX users_tenant_keycloak_idx ON public.users USING btree (tenant_id, keycloak_id);


--
-- Name: work_packages_contractor_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX work_packages_contractor_id_ix ON public.projects USING btree (contractor_id);


--
-- Name: work_packages_library_asset_type_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX work_packages_library_asset_type_id_ix ON public.projects USING btree (library_asset_type_id);


--
-- Name: work_packages_library_division_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX work_packages_library_division_id_ix ON public.projects USING btree (library_division_id);


--
-- Name: work_packages_library_project_type_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX work_packages_library_project_type_id_ix ON public.projects USING btree (library_project_type_id);


--
-- Name: work_packages_library_region_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX work_packages_library_region_id_ix ON public.projects USING btree (library_region_id);


--
-- Name: work_packages_manager_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX work_packages_manager_id_ix ON public.projects USING btree (manager_id);


--
-- Name: work_packages_primary_assigned_user_id_ix; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX work_packages_primary_assigned_user_id_ix ON public.projects USING btree (supervisor_id);


--
-- Name: activities verify_external_key_unique_per_tenant_activities; Type: TRIGGER; Schema: public; Owner: -
--

CREATE CONSTRAINT TRIGGER verify_external_key_unique_per_tenant_activities AFTER INSERT OR UPDATE ON public.activities NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE FUNCTION public.activity_external_key_unique_per_tenant();


--
-- Name: project_locations verify_insert_unique_location_external_key; Type: TRIGGER; Schema: public; Owner: -
--

CREATE CONSTRAINT TRIGGER verify_insert_unique_location_external_key AFTER INSERT OR UPDATE ON public.project_locations NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE FUNCTION public.external_key_uniqueness_insert();


--
-- Name: activities activities_crew_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_crew_id_fkey FOREIGN KEY (crew_id) REFERENCES public.crew(id);


--
-- Name: activities activities_library_activity_type_id_pkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_library_activity_type_id_pkey FOREIGN KEY (library_activity_type_id) REFERENCES public.library_activity_types(id);


--
-- Name: activities activities_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.project_locations(id);


--
-- Name: activity_supervisor_link activity_supervisor_link_activity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.activity_supervisor_link
    ADD CONSTRAINT activity_supervisor_link_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES public.activities(id);


--
-- Name: activity_supervisor_link activity_supervisor_link_supervisor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.activity_supervisor_link
    ADD CONSTRAINT activity_supervisor_link_supervisor_id_fkey FOREIGN KEY (supervisor_id) REFERENCES public.supervisor(id);


--
-- Name: audit_event_diffs audit_event_diffs_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_event_diffs
    ADD CONSTRAINT audit_event_diffs_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.audit_events(id);


--
-- Name: audit_events audit_events_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_events
    ADD CONSTRAINT audit_events_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: compatible_units compatible_units_element_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.compatible_units
    ADD CONSTRAINT compatible_units_element_id_fk FOREIGN KEY (element_id) REFERENCES public.elements(id);


--
-- Name: compatible_units compatible_units_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.compatible_units
    ADD CONSTRAINT compatible_units_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: configurations configurations_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.configurations
    ADD CONSTRAINT configurations_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: contractor_aliases contractor_aliases_contractor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contractor_aliases
    ADD CONSTRAINT contractor_aliases_contractor_id_fkey FOREIGN KEY (contractor_id) REFERENCES public.contractor(id);


--
-- Name: contractor_aliases contractor_aliases_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contractor_aliases
    ADD CONSTRAINT contractor_aliases_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: contractor contractor_tenenat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contractor
    ADD CONSTRAINT contractor_tenenat_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: daily_reports created_by_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.daily_reports
    ADD CONSTRAINT created_by_fk FOREIGN KEY (created_by_id) REFERENCES public.users(id);


--
-- Name: crew crew_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.crew
    ADD CONSTRAINT crew_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: daily_reports daily_reports_project_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.daily_reports
    ADD CONSTRAINT daily_reports_project_location_id_fkey FOREIGN KEY (project_location_id) REFERENCES public.project_locations(id);


--
-- Name: daily_reports daily_reports_project_task_completed_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.daily_reports
    ADD CONSTRAINT daily_reports_project_task_completed_by_id_fkey FOREIGN KEY (completed_by_id) REFERENCES public.users(id);


--
-- Name: element_library_task_link element_library_task_link_element_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.element_library_task_link
    ADD CONSTRAINT element_library_task_link_element_id_fkey FOREIGN KEY (element_id) REFERENCES public.elements(id);


--
-- Name: element_library_task_link element_library_task_link_library_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.element_library_task_link
    ADD CONSTRAINT element_library_task_link_library_task_id_fkey FOREIGN KEY (library_task_id) REFERENCES public.library_tasks(id);


--
-- Name: projects fk-projects-tenants; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT "fk-projects-tenants" FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: site_condition_controls fk-site_condition_controls-user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_condition_controls
    ADD CONSTRAINT "fk-site_condition_controls-user" FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: site_condition_hazards fk-site_condition_hazards-user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_condition_hazards
    ADD CONSTRAINT "fk-site_condition_hazards-user" FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: task_controls fk-task_controls-user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_controls
    ADD CONSTRAINT "fk-task_controls-user" FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: task_hazards fk-task_hazards-user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_hazards
    ADD CONSTRAINT "fk-task_hazards-user" FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users fk-users-tenants; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT "fk-users-tenants" FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: ingest_work_package_to_compatible_unit_link fk_compatible_unit_id_tenant_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingest_work_package_to_compatible_unit_link
    ADD CONSTRAINT fk_compatible_unit_id_tenant_id FOREIGN KEY (compatible_unit_id, tenant_id) REFERENCES public.compatible_units(compatible_unit_id, tenant_id);


--
-- Name: form_definitions form_definitions_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.form_definitions
    ADD CONSTRAINT form_definitions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: incident_task_link incident_task_link_incident_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_task_link
    ADD CONSTRAINT incident_task_link_incident_id_fkey FOREIGN KEY (incident_id) REFERENCES public.incidents(id);


--
-- Name: incident_task_link incident_task_link_library_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_task_link
    ADD CONSTRAINT incident_task_link_library_task_id_fkey FOREIGN KEY (library_task_id) REFERENCES public.library_tasks(id);


--
-- Name: incidents incidents_contractor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_contractor_id_fkey FOREIGN KEY (contractor_id) REFERENCES public.contractor(id);


--
-- Name: incidents incidents_supervisor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_supervisor_id_fkey FOREIGN KEY (supervisor_id) REFERENCES public.supervisor(id);


--
-- Name: incidents incidents_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: ingestion_settings ingestion_settings_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingestion_settings
    ADD CONSTRAINT ingestion_settings_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: jsbs jsbs_completed_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jsbs
    ADD CONSTRAINT jsbs_completed_by_id_fkey FOREIGN KEY (completed_by_id) REFERENCES public.users(id);


--
-- Name: jsbs jsbs_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jsbs
    ADD CONSTRAINT jsbs_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id);


--
-- Name: jsbs jsbs_project_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jsbs
    ADD CONSTRAINT jsbs_project_location_id_fkey FOREIGN KEY (project_location_id) REFERENCES public.project_locations(id);


--
-- Name: jsbs jsbs_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jsbs
    ADD CONSTRAINT jsbs_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: library_activity_type_tenant_link library_activity_type_tenant_link_library_activity_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_activity_type_tenant_link
    ADD CONSTRAINT library_activity_type_tenant_link_library_activity_type_id_fkey FOREIGN KEY (library_activity_type_id) REFERENCES public.library_activity_types(id);


--
-- Name: library_activity_type_tenant_link library_activity_type_tenant_link_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_activity_type_tenant_link
    ADD CONSTRAINT library_activity_type_tenant_link_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: library_division_tenant_link library_division_tenant_link_library_division_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_division_tenant_link
    ADD CONSTRAINT library_division_tenant_link_library_division_id_fkey FOREIGN KEY (library_division_id) REFERENCES public.library_divisions(id);


--
-- Name: library_division_tenant_link library_division_tenant_link_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_division_tenant_link
    ADD CONSTRAINT library_division_tenant_link_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: library_region_tenant_link library_region_tenant_link_library_region_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_region_tenant_link
    ADD CONSTRAINT library_region_tenant_link_library_region_id_fkey FOREIGN KEY (library_region_id) REFERENCES public.library_regions(id);


--
-- Name: library_region_tenant_link library_region_tenant_link_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_region_tenant_link
    ADD CONSTRAINT library_region_tenant_link_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: library_site_condition_recommendations library_site_condition_recommend_library_site_condition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_site_condition_recommendations
    ADD CONSTRAINT library_site_condition_recommend_library_site_condition_id_fkey FOREIGN KEY (library_site_condition_id) REFERENCES public.library_site_conditions(id);


--
-- Name: library_site_condition_recommendations library_site_condition_recommendations_library_control_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_site_condition_recommendations
    ADD CONSTRAINT library_site_condition_recommendations_library_control_id_fkey FOREIGN KEY (library_control_id) REFERENCES public.library_controls(id);


--
-- Name: library_site_condition_recommendations library_site_condition_recommendations_library_hazard_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_site_condition_recommendations
    ADD CONSTRAINT library_site_condition_recommendations_library_hazard_id_fkey FOREIGN KEY (library_hazard_id) REFERENCES public.library_hazards(id);


--
-- Name: library_task_activity_groups library_task_activity_groups_activity_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_task_activity_groups
    ADD CONSTRAINT library_task_activity_groups_activity_group_id_fkey FOREIGN KEY (activity_group_id) REFERENCES public.library_activity_groups(id);


--
-- Name: library_task_activity_groups library_task_activity_groups_library_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_task_activity_groups
    ADD CONSTRAINT library_task_activity_groups_library_task_id_fkey FOREIGN KEY (library_task_id) REFERENCES public.library_tasks(id);


--
-- Name: library_task_recommendations library_task_recommendations_library_control_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_task_recommendations
    ADD CONSTRAINT library_task_recommendations_library_control_id_fkey FOREIGN KEY (library_control_id) REFERENCES public.library_controls(id);


--
-- Name: library_task_recommendations library_task_recommendations_library_hazard_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_task_recommendations
    ADD CONSTRAINT library_task_recommendations_library_hazard_id_fkey FOREIGN KEY (library_hazard_id) REFERENCES public.library_hazards(id);


--
-- Name: library_task_recommendations library_task_recommendations_library_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_task_recommendations
    ADD CONSTRAINT library_task_recommendations_library_task_id_fkey FOREIGN KEY (library_task_id) REFERENCES public.library_tasks(id);


--
-- Name: library_tasks library_tasks_work_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.library_tasks
    ADD CONSTRAINT library_tasks_work_type_id_fkey FOREIGN KEY (work_type_id) REFERENCES public.work_types(id);


--
-- Name: location_hazard_control_settings location_hazard_control_settings_library_control_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.location_hazard_control_settings
    ADD CONSTRAINT location_hazard_control_settings_library_control_id_fkey FOREIGN KEY (library_control_id) REFERENCES public.library_controls(id);


--
-- Name: location_hazard_control_settings location_hazard_control_settings_library_hazard_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.location_hazard_control_settings
    ADD CONSTRAINT location_hazard_control_settings_library_hazard_id_fkey FOREIGN KEY (library_hazard_id) REFERENCES public.library_hazards(id);


--
-- Name: location_hazard_control_settings location_hazard_control_settings_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.location_hazard_control_settings
    ADD CONSTRAINT location_hazard_control_settings_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.project_locations(id);


--
-- Name: location_hazard_control_settings location_hazard_control_settings_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.location_hazard_control_settings
    ADD CONSTRAINT location_hazard_control_settings_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: location_hazard_control_settings location_hazard_control_settings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.location_hazard_control_settings
    ADD CONSTRAINT location_hazard_control_settings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: locations_clustering locations_clustering_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations_clustering
    ADD CONSTRAINT locations_clustering_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: observations observations_contractor_involved_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observations
    ADD CONSTRAINT observations_contractor_involved_id_fkey FOREIGN KEY (contractor_involved_id) REFERENCES public.contractor(id);


--
-- Name: observations observations_supervisor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observations
    ADD CONSTRAINT observations_supervisor_id_fkey FOREIGN KEY (supervisor_id) REFERENCES public.supervisor(id);


--
-- Name: observations observations_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observations
    ADD CONSTRAINT observations_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: parsed_files parsed_files_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parsed_files
    ADD CONSTRAINT parsed_files_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: projects project_asset_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT project_asset_type_id_fkey FOREIGN KEY (library_asset_type_id) REFERENCES public.library_asset_types(id);


--
-- Name: project_locations project_locations_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_locations
    ADD CONSTRAINT project_locations_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: project_locations project_locations_supervisor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_locations
    ADD CONSTRAINT project_locations_supervisor_id_fkey FOREIGN KEY (supervisor_id) REFERENCES public.users(id);


--
-- Name: project_locations project_locations_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_locations
    ADD CONSTRAINT project_locations_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: projects projects_contractor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_contractor_id_fkey FOREIGN KEY (contractor_id) REFERENCES public.contractor(id);


--
-- Name: projects projects_library_division_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_library_division_id_fkey FOREIGN KEY (library_division_id) REFERENCES public.library_divisions(id);


--
-- Name: projects projects_library_project_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_library_project_type_id_fkey FOREIGN KEY (library_project_type_id) REFERENCES public.library_project_types(id);


--
-- Name: projects projects_library_region_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_library_region_id_fkey FOREIGN KEY (library_region_id) REFERENCES public.library_regions(id);


--
-- Name: projects projects_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.users(id);


--
-- Name: projects projects_supervisor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_supervisor_id_fkey FOREIGN KEY (supervisor_id) REFERENCES public.users(id);


--
-- Name: rm_average_contractor_safety_score rm_average_contractor_safety_score_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_average_contractor_safety_score
    ADD CONSTRAINT rm_average_contractor_safety_score_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: rm_average_crew_risk rm_average_crew_risk_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_average_crew_risk
    ADD CONSTRAINT rm_average_crew_risk_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: rm_average_supervisor_engagement_factor rm_average_supervisor_engagement_factor_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_average_supervisor_engagement_factor
    ADD CONSTRAINT rm_average_supervisor_engagement_factor_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: rm_average_supervisor_relative_precursor_risk rm_average_supervisor_relative_precursor_risk_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_average_supervisor_relative_precursor_risk
    ADD CONSTRAINT rm_average_supervisor_relative_precursor_risk_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: rm_calc_parameters rm_calc_parameters_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_calc_parameters
    ADD CONSTRAINT rm_calc_parameters_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: rm_crew_risk rm_crew_risk_crew_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_crew_risk
    ADD CONSTRAINT rm_crew_risk_crew_id_fkey FOREIGN KEY (crew_id) REFERENCES public.crew(id);


--
-- Name: rm_division_relative_precursor_risk rm_division_relative_precursor_risk_division_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_division_relative_precursor_risk
    ADD CONSTRAINT rm_division_relative_precursor_risk_division_id_fkey FOREIGN KEY (division_id) REFERENCES public.library_divisions(id);


--
-- Name: rm_division_relative_precursor_risk rm_division_relative_precursor_risk_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_division_relative_precursor_risk
    ADD CONSTRAINT rm_division_relative_precursor_risk_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: rm_library_site_condition_relative_precursor_risk rm_library_site_condition_relati_library_site_condition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_library_site_condition_relative_precursor_risk
    ADD CONSTRAINT rm_library_site_condition_relati_library_site_condition_id_fkey FOREIGN KEY (library_site_condition_id) REFERENCES public.library_site_conditions(id);


--
-- Name: rm_library_site_condition_relative_precursor_risk rm_library_site_condition_relative_precursor_ris_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_library_site_condition_relative_precursor_risk
    ADD CONSTRAINT rm_library_site_condition_relative_precursor_ris_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: rm_librarytask_relative_precursor_risk rm_librarytask_relative_precursor_risk_library_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_librarytask_relative_precursor_risk
    ADD CONSTRAINT rm_librarytask_relative_precursor_risk_library_task_id_fkey FOREIGN KEY (library_task_id) REFERENCES public.library_tasks(id);


--
-- Name: rm_manually_added_site_conditions rm_manually_added_site_conditions_project_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_manually_added_site_conditions
    ADD CONSTRAINT rm_manually_added_site_conditions_project_location_id_fkey FOREIGN KEY (project_location_id) REFERENCES public.project_locations(id);


--
-- Name: rm_project_location_safety_climate_multiplier rm_project_location_safety_climate_mul_project_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_project_location_safety_climate_multiplier
    ADD CONSTRAINT rm_project_location_safety_climate_mul_project_location_id_fkey FOREIGN KEY (project_location_id) REFERENCES public.project_locations(id);


--
-- Name: rm_project_location_total_task_risk_score rm_project_location_total_task_risk_sc_project_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_project_location_total_task_risk_score
    ADD CONSTRAINT rm_project_location_total_task_risk_sc_project_location_id_fkey FOREIGN KEY (project_location_id) REFERENCES public.project_locations(id);


--
-- Name: rm_project_site_conditions_multiplier rm_project_site_conditions_multiplier_project_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_project_site_conditions_multiplier
    ADD CONSTRAINT rm_project_site_conditions_multiplier_project_location_id_fkey FOREIGN KEY (project_location_id) REFERENCES public.project_locations(id);


--
-- Name: rm_project_total_task_risk_score rm_project_total_task_risk_score_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_project_total_task_risk_score
    ADD CONSTRAINT rm_project_total_task_risk_score_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: rm_stddev_contractor_safety_score rm_stddev_contractor_safety_score_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stddev_contractor_safety_score
    ADD CONSTRAINT rm_stddev_contractor_safety_score_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: rm_stddev_crew_risk rm_stddev_crew_risk_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stddev_crew_risk
    ADD CONSTRAINT rm_stddev_crew_risk_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: rm_stddev_supervisor_engagement_factor rm_stddev_supervisor_engagement_factor_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stddev_supervisor_engagement_factor
    ADD CONSTRAINT rm_stddev_supervisor_engagement_factor_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: rm_stddev_supervisor_relative_precursor_risk rm_stddev_supervisor_relative_precursor_risk_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stddev_supervisor_relative_precursor_risk
    ADD CONSTRAINT rm_stddev_supervisor_relative_precursor_risk_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: rm_stochastic_activity_sc_relative_precursor_risk_score rm_stochastic_activity_sc_relative_precursor_r_activity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stochastic_activity_sc_relative_precursor_risk_score
    ADD CONSTRAINT rm_stochastic_activity_sc_relative_precursor_r_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES public.activities(id);


--
-- Name: rm_stochastic_activity_total_task_risk_score rm_stochastic_activity_total_task_risk_score_activity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stochastic_activity_total_task_risk_score
    ADD CONSTRAINT rm_stochastic_activity_total_task_risk_score_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES public.activities(id);


--
-- Name: rm_stochastic_location_total_task_risk_score rm_stochastic_location_total_task_risk_project_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stochastic_location_total_task_risk_score
    ADD CONSTRAINT rm_stochastic_location_total_task_risk_project_location_id_fkey FOREIGN KEY (project_location_id) REFERENCES public.project_locations(id);


--
-- Name: rm_stochastic_task_specific_risk_score rm_stochastic_task_specific_risk_score_project_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stochastic_task_specific_risk_score
    ADD CONSTRAINT rm_stochastic_task_specific_risk_score_project_task_id_fkey FOREIGN KEY (project_task_id) REFERENCES public.tasks(id);


--
-- Name: rm_stochastic_total_location_risk_score rm_stochastic_total_location_risk_scor_project_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stochastic_total_location_risk_score
    ADD CONSTRAINT rm_stochastic_total_location_risk_scor_project_location_id_fkey FOREIGN KEY (project_location_id) REFERENCES public.project_locations(id);


--
-- Name: rm_stochastic_total_work_package_risk_score rm_stochastic_total_work_package_risk_score_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_stochastic_total_work_package_risk_score
    ADD CONSTRAINT rm_stochastic_total_work_package_risk_score_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: rm_task_specific_risk_score rm_task_specific_risk_score_project_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_task_specific_risk_score
    ADD CONSTRAINT rm_task_specific_risk_score_project_task_id_fkey FOREIGN KEY (project_task_id) REFERENCES public.tasks(id);


--
-- Name: rm_task_specific_safety_climate_multiplier rm_task_specific_safety_climate_multiplier_library_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_task_specific_safety_climate_multiplier
    ADD CONSTRAINT rm_task_specific_safety_climate_multiplier_library_task_id_fkey FOREIGN KEY (library_task_id) REFERENCES public.library_tasks(id);


--
-- Name: rm_task_specific_site_conditions_multiplier rm_task_specific_site_conditions_multiplie_project_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_task_specific_site_conditions_multiplier
    ADD CONSTRAINT rm_task_specific_site_conditions_multiplie_project_task_id_fkey FOREIGN KEY (project_task_id) REFERENCES public.tasks(id);


--
-- Name: rm_total_activity_risk_score rm_total_activity_risk_score_activity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_total_activity_risk_score
    ADD CONSTRAINT rm_total_activity_risk_score_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES public.activities(id);


--
-- Name: rm_total_project_location_risk_score rm_total_project_location_risk_score_project_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_total_project_location_risk_score
    ADD CONSTRAINT rm_total_project_location_risk_score_project_location_id_fkey FOREIGN KEY (project_location_id) REFERENCES public.project_locations(id);


--
-- Name: rm_total_project_risk_score rm_total_project_risk_score_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rm_total_project_risk_score
    ADD CONSTRAINT rm_total_project_risk_score_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: site_condition_controls site_condition_controls_library_control_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_condition_controls
    ADD CONSTRAINT site_condition_controls_library_control_id_fkey FOREIGN KEY (library_control_id) REFERENCES public.library_controls(id);


--
-- Name: site_condition_controls site_condition_controls_site_condition_hazard_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_condition_controls
    ADD CONSTRAINT site_condition_controls_site_condition_hazard_id_fkey FOREIGN KEY (site_condition_hazard_id) REFERENCES public.site_condition_hazards(id);


--
-- Name: site_condition_hazards site_condition_hazards_library_hazard_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_condition_hazards
    ADD CONSTRAINT site_condition_hazards_library_hazard_id_fkey FOREIGN KEY (library_hazard_id) REFERENCES public.library_hazards(id);


--
-- Name: site_condition_hazards site_condition_hazards_site_condition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_condition_hazards
    ADD CONSTRAINT site_condition_hazards_site_condition_id_fkey FOREIGN KEY (site_condition_id) REFERENCES public.site_conditions(id);


--
-- Name: site_conditions site_conditions_library_site_condition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_conditions
    ADD CONSTRAINT site_conditions_library_site_condition_id_fkey FOREIGN KEY (library_site_condition_id) REFERENCES public.library_site_conditions(id);


--
-- Name: site_conditions site_conditions_project_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_conditions
    ADD CONSTRAINT site_conditions_project_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.project_locations(id);


--
-- Name: site_conditions site_conditions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_conditions
    ADD CONSTRAINT site_conditions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: supervisor supervisor_tenenat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supervisor
    ADD CONSTRAINT supervisor_tenenat_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: supervisor supervisors_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supervisor
    ADD CONSTRAINT supervisors_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: task_controls task_controls_library_control_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_controls
    ADD CONSTRAINT task_controls_library_control_id_fkey FOREIGN KEY (library_control_id) REFERENCES public.library_controls(id);


--
-- Name: task_controls task_controls_task_hazard_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_controls
    ADD CONSTRAINT task_controls_task_hazard_id_fkey FOREIGN KEY (task_hazard_id) REFERENCES public.task_hazards(id);


--
-- Name: task_hazards task_hazards_library_hazard_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_hazards
    ADD CONSTRAINT task_hazards_library_hazard_id_fkey FOREIGN KEY (library_hazard_id) REFERENCES public.library_hazards(id);


--
-- Name: task_hazards task_hazards_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_hazards
    ADD CONSTRAINT task_hazards_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id);


--
-- Name: tasks tasks_activity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES public.activities(id);


--
-- Name: tasks tasks_library_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_library_task_id_fkey FOREIGN KEY (library_task_id) REFERENCES public.library_tasks(id);


--
-- Name: tasks tasks_project_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_project_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.project_locations(id);


--
-- Name: work_type_tenant_link work_type_tenant_link_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.work_type_tenant_link
    ADD CONSTRAINT work_type_tenant_link_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: work_type_tenant_link work_type_tenant_link_work_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.work_type_tenant_link
    ADD CONSTRAINT work_type_tenant_link_work_type_id_fkey FOREIGN KEY (work_type_id) REFERENCES public.work_types(id);


--
-- PostgreSQL database dump complete
--

