import strawberry
from fastapi.encoders import jsonable_encoder

from worker_safety_service.context import Info
from worker_safety_service.graphql.common import (
    ManagerType,
    MeType,
    SupervisorType,
    SystemType,
)
from worker_safety_service.graphql.insights.types import (
    PortfolioLearningsType,
    PortfolioPlanningType,
    ProjectLearningsType,
    ProjectPlanningType,
    get_portfolio_learnings,
    get_portfolio_planning,
    get_project_learnings,
    get_project_planning,
)
from worker_safety_service.graphql.permissions import (
    CanConfigureTheApplication,
    CanReadActivity,
    CanReadControls,
    CanReadHazards,
    CanReadProject,
    CanReadReports,
    CanReadSiteConditions,
    CanReadTasks,
    CanViewCompanies,
    CanViewCrew,
    CanViewCrewLeaders,
    CanViewManagers,
)
from worker_safety_service.graphql.types import (
    ActivityType,
    ContractorType,
    CrewLeaderType,
    DailyReportFormsListType,
    DailyReportType,
    EnergyBasedObservationFormsListType,
    EnergyBasedObservationType,
    FirstAIDAEDLocationType,
    FormDefinitionType,
    FormInterface,
    FormInterfaceWithContents,
    FormListFilterOptions,
    IncidentType,
    IngestColumn,
    IngestOption,
    IngestOptionItems,
    IngestOptions,
    IngestType,
    InsightType,
    JobSafetyBriefingFormsListType,
    JobSafetyBriefingType,
    JSBSupervisorType,
    LibraryActivityGroupType,
    LibraryActivityType,
    LibraryAssetType,
    LibraryControlType,
    LibraryDivisionType,
    LibraryHazardType,
    LibraryProjectType,
    LibraryRegionType,
    LibrarySiteConditionType,
    LibraryTaskType,
    LinkedLibraryControlType,
    LinkedLibraryHazardType,
    LinkedLibrarySiteConditionType,
    LinkedLibraryTaskType,
    LocationHazardControlSettingsType,
    MedicalFacilityType,
    NatGridJobSafetyBriefingFormsListType,
    NatGridJobSafetyBriefingType,
    ProjectLocationResponseType,
    ProjectLocationType,
    ProjectType,
    RecentUsedCrewLeaderReturnType,
    RecommendationType,
    RestApiWrapperType,
    SiteConditionType,
    TaskType,
    UIConfigType,
    WorkTypeType,
)
from worker_safety_service.workos.types import WorkOSDirectoryUsersResponseType

from .resolvers import (
    get_activities_for_project_location,
    get_adhoc_site_conditions,
    get_contractors,
    get_crew_leaders,
    get_daily_report,
    get_daily_report_forms_list,
    get_daily_reports_for_project_location,
    get_dated_project_locations,
    get_energy_based_observation,
    get_energy_based_observation_forms_list,
    get_first_aid_aed_locations_from_location_type,
    get_form_definitions,
    get_form_list,
    get_form_list_count,
    get_form_list_filter_options,
    get_form_list_with_contents,
    get_historical_incidents_for_library_task,
    get_historical_incidents_for_library_tasks,
    get_insights,
    get_job_safety_briefing,
    get_job_safety_briefing_forms_list,
    get_jsb_supervisors,
    get_last_adhoc_jsb,
    get_last_job_safety_briefing,
    get_last_natgrid_job_safety_briefing_for_user,
    get_library_activity_groups_library,
    get_library_activity_types,
    get_library_asset_types,
    get_library_controls,
    get_library_divisions,
    get_library_hazards,
    get_library_project_types,
    get_library_regions,
    get_library_site_conditions,
    get_library_tasks,
    get_location_hazard_control_settings,
    get_managers,
    get_me,
    get_natgrid_job_safety_briefing,
    get_natgrid_job_safety_briefing_forms_list,
    get_nearest_medical_facilities,
    get_project_by_id,
    get_project_locations,
    get_projects,
    get_recent_used_crew_leaders,
    get_recommendations,
    get_site_conditions,
    get_supervisors,
    get_system,
    get_tasks_for_project_location,
    get_tenant_and_work_type_linked_library_site_conditions,
    get_tenant_and_work_type_linked_library_tasks,
    get_tenant_linked_library_controls,
    get_tenant_linked_library_hazards,
    get_tenant_work_types,
    get_ui_config_on_form_type,
    get_workos_directory_users,
    rest_api_wrapper,
)


@strawberry.type
class Query:
    system: SystemType = strawberry.field(resolver=get_system)

    me: MeType = strawberry.field(resolver=get_me)

    managers: list[ManagerType] = strawberry.field(
        resolver=get_managers,
        permission_classes=[CanViewManagers],
    )
    supervisors: list[SupervisorType] = strawberry.field(
        resolver=get_supervisors,
        permission_classes=[CanViewCrew],
    )
    contractors: list[ContractorType] = strawberry.field(
        resolver=get_contractors,
        permission_classes=[CanViewCompanies],
    )

    project: ProjectType = strawberry.field(
        resolver=get_project_by_id, permission_classes=[CanReadProject]
    )
    projects: list[ProjectType] = strawberry.field(
        resolver=get_projects, permission_classes=[CanReadProject]
    )
    project_locations: list[ProjectLocationType] = strawberry.field(
        resolver=get_project_locations, permission_classes=[CanReadProject]
    )
    filter_location_date_range: list[ProjectLocationResponseType] = strawberry.field(
        resolver=get_dated_project_locations, permission_classes=[CanReadProject]
    )

    project_planning: ProjectPlanningType = strawberry.field(
        resolver=get_project_planning, permission_classes=[CanReadReports]
    )
    portfolio_planning: PortfolioPlanningType = strawberry.field(
        resolver=get_portfolio_planning, permission_classes=[CanReadReports]
    )
    project_learnings: ProjectLearningsType = strawberry.field(
        resolver=get_project_learnings, permission_classes=[CanReadReports]
    )
    portfolio_learnings: PortfolioLearningsType = strawberry.field(
        resolver=get_portfolio_learnings, permission_classes=[CanReadReports]
    )

    site_conditions: list[SiteConditionType] = strawberry.field(
        resolver=get_site_conditions,
        permission_classes=[CanReadSiteConditions],
    )
    location_site_conditions: list[SiteConditionType] = strawberry.field(
        resolver=get_adhoc_site_conditions,
        permission_classes=[CanReadSiteConditions],
    )

    tasks: list[TaskType] = strawberry.field(
        resolver=get_tasks_for_project_location, permission_classes=[CanReadTasks]
    )

    activities: list[ActivityType] = strawberry.field(
        resolver=get_activities_for_project_location,
        permission_classes=[CanReadActivity],
    )

    tasks_library: list[LibraryTaskType] = strawberry.field(
        resolver=get_library_tasks, permission_classes=[CanReadTasks]
    )

    tenant_and_work_type_linked_library_tasks: list[
        LinkedLibraryTaskType
    ] = strawberry.field(
        resolver=get_tenant_and_work_type_linked_library_tasks,
        permission_classes=[CanReadTasks],
    )
    site_conditions_library: list[LibrarySiteConditionType] = strawberry.field(
        resolver=get_library_site_conditions,
        permission_classes=[CanReadSiteConditions],
    )
    tenant_and_work_type_linked_library_site_conditions: list[
        LinkedLibrarySiteConditionType
    ] = strawberry.field(
        resolver=get_tenant_and_work_type_linked_library_site_conditions,
        permission_classes=[CanReadSiteConditions],
    )
    hazards_library: list[LibraryHazardType] = strawberry.field(
        resolver=get_library_hazards, permission_classes=[CanReadHazards]
    )
    tenant_linked_hazards_library: list[LinkedLibraryHazardType] = strawberry.field(
        resolver=get_tenant_linked_library_hazards, permission_classes=[CanReadHazards]
    )
    controls_library: list[LibraryControlType] = strawberry.field(
        resolver=get_library_controls, permission_classes=[CanReadControls]
    )
    tenant_linked_controls_library: list[LinkedLibraryControlType] = strawberry.field(
        resolver=get_tenant_linked_library_controls,
        permission_classes=[CanReadControls],
    )
    divisions_library: list[LibraryDivisionType] = strawberry.field(
        resolver=get_library_divisions, permission_classes=[CanReadProject]
    )
    regions_library: list[LibraryRegionType] = strawberry.field(
        resolver=get_library_regions, permission_classes=[CanReadProject]
    )
    # FIXME: To be deprecated
    project_types_library: list[LibraryProjectType] = strawberry.field(
        resolver=get_library_project_types, permission_classes=[CanReadProject]
    )
    asset_types_library: list[LibraryAssetType] = strawberry.field(
        resolver=get_library_asset_types, permission_classes=[CanReadProject]
    )
    historical_incidents: list[IncidentType] = strawberry.field(
        resolver=get_historical_incidents_for_library_task,
        permission_classes=[CanReadProject],
    )
    historical_incidents_for_tasks: list[IncidentType] = strawberry.field(
        resolver=get_historical_incidents_for_library_tasks,
        permission_classes=[CanReadProject],
    )
    activity_types_library: list[LibraryActivityType] = strawberry.field(
        resolver=get_library_activity_types, permission_classes=[CanReadActivity]
    )
    activity_groups_library: list[LibraryActivityGroupType] = strawberry.field(
        resolver=get_library_activity_groups_library,
        permission_classes=[CanReadActivity],
    )

    daily_report: DailyReportType | None = strawberry.field(
        resolver=get_daily_report, permission_classes=[CanReadReports]
    )

    daily_report_response: DailyReportFormsListType = strawberry.field(
        resolver=get_daily_report_forms_list, permission_classes=[CanReadReports]
    )
    daily_reports: list[DailyReportType] = strawberry.field(
        resolver=get_daily_reports_for_project_location,
        permission_classes=[CanReadReports],
    )
    recommendations: RecommendationType = strawberry.field(
        resolver=get_recommendations, permission_classes=[CanReadReports]
    )

    location_hazard_control_settings: list[
        LocationHazardControlSettingsType
    ] = strawberry.field(
        resolver=get_location_hazard_control_settings,
        permission_classes=[CanReadReports],
    )
    form_definitions: list[FormDefinitionType] = strawberry.field(
        resolver=get_form_definitions,
        permission_classes=[
            CanReadReports
        ],  # TODO Apply new Forms permissions when available here
    )

    job_safety_briefing: JobSafetyBriefingType = strawberry.field(
        resolver=get_job_safety_briefing, permission_classes=[CanReadReports]
    )

    natgrid_job_safety_briefing: NatGridJobSafetyBriefingType = strawberry.field(
        resolver=get_natgrid_job_safety_briefing, permission_classes=[CanReadReports]
    )

    last_natgrid_job_safety_briefing: NatGridJobSafetyBriefingType = strawberry.field(
        resolver=get_last_natgrid_job_safety_briefing_for_user,
        permission_classes=[CanReadReports],
    )

    natgrid_job_safety_briefing_response: NatGridJobSafetyBriefingFormsListType = (
        strawberry.field(
            resolver=get_natgrid_job_safety_briefing_forms_list,
            permission_classes=[CanReadReports],
        )
    )

    job_safety_briefing_response: JobSafetyBriefingFormsListType = strawberry.field(
        resolver=get_job_safety_briefing_forms_list, permission_classes=[CanReadReports]
    )

    last_added_job_safety_briefing: JobSafetyBriefingType | None = strawberry.field(
        resolver=get_last_job_safety_briefing, permission_classes=[CanReadReports]
    )
    last_added_adhoc_job_safety_briefing: JobSafetyBriefingType | None = (
        strawberry.field(
            resolver=get_last_adhoc_jsb, permission_classes=[CanReadReports]
        )
    )

    nearest_medical_facilities: list[MedicalFacilityType] = strawberry.field(
        resolver=get_nearest_medical_facilities, permission_classes=[CanReadReports]
    )

    first_aid_aed_location: list[FirstAIDAEDLocationType] = strawberry.field(
        resolver=get_first_aid_aed_locations_from_location_type,
        permission_classes=[CanReadReports],
    )
    ui_config: UIConfigType = strawberry.field(
        resolver=get_ui_config_on_form_type,
        permission_classes=[CanReadReports],
    )

    forms_list: list[FormInterface] = strawberry.field(
        resolver=get_form_list, permission_classes=[CanReadReports]
    )

    rest_api_wrapper: RestApiWrapperType = strawberry.field(
        resolver=rest_api_wrapper,
        permission_classes=[CanReadReports],
    )

    forms_list_with_contents: list[FormInterfaceWithContents] = strawberry.field(
        resolver=get_form_list_with_contents, permission_classes=[CanReadReports]
    )

    forms_list_count: int = strawberry.field(
        resolver=get_form_list_count, permission_classes=[CanReadReports]
    )
    forms_list_filter_options: FormListFilterOptions = strawberry.field(
        resolver=get_form_list_filter_options, permission_classes=[CanReadReports]
    )

    energy_based_observation: EnergyBasedObservationType = strawberry.field(
        resolver=get_energy_based_observation, permission_classes=[CanReadReports]
    )

    energy_based_observation_response: EnergyBasedObservationFormsListType = (
        strawberry.field(
            resolver=get_energy_based_observation_forms_list,
            permission_classes=[CanReadReports],
        )
    )
    insights: list[InsightType] = strawberry.field(
        resolver=get_insights, permission_classes=[CanConfigureTheApplication]
    )
    crew_leaders: list[CrewLeaderType] = strawberry.field(
        resolver=get_crew_leaders, permission_classes=[CanViewCrewLeaders]
    )
    tenant_work_types: list[WorkTypeType] = strawberry.field(
        resolver=get_tenant_work_types, permission_classes=[CanReadProject]
    )
    recently_used_crew_leaders: list[RecentUsedCrewLeaderReturnType] = strawberry.field(
        resolver=get_recent_used_crew_leaders, permission_classes=[CanViewCrewLeaders]
    )
    jsb_supervisors: list[JSBSupervisorType] = strawberry.field(
        resolver=get_jsb_supervisors, permission_classes=[CanReadReports]
    )
    workos_directory_users: WorkOSDirectoryUsersResponseType = strawberry.field(
        resolver=get_workos_directory_users, permission_classes=[CanViewCrewLeaders]
    )

    @strawberry.field(permission_classes=[CanConfigureTheApplication])
    async def ingest_options(self, info: Info) -> IngestOptions:
        return IngestOptions(
            options=sorted(
                (
                    IngestOption(
                        id=i.key,
                        name=i.name,
                        description=i.description,
                        columns=[
                            IngestColumn(
                                attribute=c.attribute,
                                name=c.name,
                                required_on_ingest=c.required_on_ingest,
                                ignore_on_ingest=c.ignore_on_ingest,
                            )
                            for c in i.columns
                        ],
                    )
                    for i in info.context.ingest.get_options()
                ),
                key=lambda i: i.name,
            ),
        )

    @strawberry.field(permission_classes=[CanConfigureTheApplication])
    async def ingest_option_items(
        self, info: Info, key: IngestType
    ) -> IngestOptionItems:
        items = await info.context.ingest.get_items(key)
        return IngestOptionItems(items=jsonable_encoder(items))
