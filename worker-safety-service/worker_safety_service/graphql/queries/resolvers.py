import asyncio
import datetime
import json
import uuid
from decimal import Decimal
from typing import Awaitable, Optional

import httpx
from httpx import Timeout

from worker_safety_service.config import settings
from worker_safety_service.constants import GeneralConstants
from worker_safety_service.context import Info
from worker_safety_service.dal.audit_events import AuditEventMetadata
from worker_safety_service.graphql.common import (
    FormListOrderByInput,
    InternalLocationFilterBy,
    LibraryTaskOrderByInput,
    LocationFilterByInput,
    LocationOrderByInput,
    ManagerType,
    MeType,
    OrderByInput,
    ProjectLocationOrderByInput,
    ProjectOrderByInput,
    SupervisorType,
    SystemType,
    TaskOrderByInput,
    order_by_to_pydantic,
)
from worker_safety_service.graphql.common.types import (
    INTERNAL_LOCATION_FILTER_MAPPER,
    PROJECT_STATUS_MAPPER,
    RISK_LEVEL_MAPPER,
    OrderByDirectionType,
    OrderByFieldType,
)
from worker_safety_service.graphql.types import (
    ActivityType,
    ContractorType,
    CrewLeaderType,
    DailyReportFormsListType,
    DailyReportType,
    EnergyBasedObservationFormsListType,
    EnergyBasedObservationType,
    FilterLocationDateRangeType,
    FirstAIDAEDLocationType,
    FormDefinitionType,
    FormInterface,
    FormInterfaceWithContents,
    FormListFilterOptions,
    FormListFilterSearchInput,
    FormStatus,
    FormsType,
    IncidentType,
    InsightType,
    JobSafetyBriefingFormsListType,
    JobSafetyBriefingType,
    JSBFilterOnEnum,
    JSBSupervisorType,
    LibraryActivityGroupType,
    LibraryActivityType,
    LibraryAssetType,
    LibraryControlType,
    LibraryDivisionType,
    LibraryFilterType,
    LibraryHazardType,
    LibraryProjectType,
    LibraryRegionType,
    LibrarySiteConditionType,
    LibraryTaskType,
    LinkedLibraryControlType,
    LinkedLibraryHazardType,
    LinkedLibraryTaskType,
    LocationHazardControlSettingsType,
    LocationType,
    MapExtentInput,
    MedicalFacilityType,
    NatGridJobSafetyBriefingFormsListType,
    NatGridJobSafetyBriefingType,
    OptionItem,
    ProjectLocationResponseType,
    ProjectLocationType,
    ProjectType,
    RecentUsedCrewLeaderReturnType,
    RecommendationType,
    RestApiWrapperType,
    SiteConditionType,
    SiteLocationInput,
    TaskType,
    UIConfigType,
    WorkTypeType,
)
from worker_safety_service.models import (
    DailyReport,
    EnergyBasedObservation,
    JobSafetyBriefing,
    Location,
    NatGridJobSafetyBriefing,
    ProjectStatus,
    RiskLevel,
    WorkPackage,
)
from worker_safety_service.models.user import User
from worker_safety_service.workos.types import WorkOSDirectoryUsersResponseType
from worker_safety_service.workos.workos_data import DirectoryUsersQuery, WorkOSCrewData


async def get_project_by_id(
    info: Info, project_id: uuid.UUID, filter_tenant_settings: Optional[bool] = False
) -> ProjectType:
    info.context.params["filter_tenant_settings"] = filter_tenant_settings
    project: WorkPackage | None = await info.context.projects.me.load(project_id)
    if not project:
        raise ValueError(f"Project ID {project_id} not found")
    else:
        return ProjectType.from_orm(project)


async def get_projects(
    info: Info,
    id: Optional[uuid.UUID] = None,
    status: Optional[ProjectStatus] = None,
    search: Optional[str] = None,
    order_by: Optional[list[ProjectOrderByInput]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> list[ProjectType]:
    # Find date on riskLevel resolver
    # TODO should we have a riskLevelDate where and drop riskLevel.date?
    risk_level_date = None
    for field in info.selected_fields:
        if getattr(field, "name", "") == info.field_name:
            risk_level_date = ProjectType.find_risk_level_date(field.selections)
            break

    if id is None:
        with_risk, projects = await info.context.projects.get_projects_with_risk(
            search=search,
            risk_level_date=risk_level_date,
            status=status,
            order_by=order_by_to_pydantic(order_by),
            limit=limit,
            offset=offset,
        )
        if with_risk:
            projects_with_risk: list[tuple[WorkPackage, str]] = projects  # type: ignore
            return [
                ProjectType.from_orm(project, risk_level=getattr(RiskLevel, risk_value))
                for project, risk_value in projects_with_risk
            ]
        else:
            projects_no_risk: list[WorkPackage] = projects  # type: ignore
            return [ProjectType.from_orm(project) for project in projects_no_risk]
    else:
        project: WorkPackage | None = await info.context.projects.me.load(id)
        if not project:
            raise ValueError(f"Project ID {id} not found")
        return [ProjectType.from_orm(project)]


async def get_dated_project_locations(
    info: Info,
    id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    order_by: Optional[list[ProjectLocationOrderByInput]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    library_region_ids: Optional[list[uuid.UUID]] = None,
    library_division_ids: Optional[list[uuid.UUID]] = None,
    library_project_type_ids: Optional[list[uuid.UUID]] = None,
    work_type_ids: Optional[list[uuid.UUID]] = None,
    project_ids: Optional[list[uuid.UUID]] = None,
    project_status: Optional[list[ProjectStatus]] = None,
    contractor_ids: Optional[list[uuid.UUID]] = None,
    supervisor_ids: Optional[list[uuid.UUID]] = None,
    map_extent: Optional[MapExtentInput] = None,
    filter_by: Optional[list[LocationFilterByInput]] = None,
    filter_tenant_settings: Optional[bool] = False,
) -> list[ProjectLocationResponseType]:
    risk_level_date = None

    info.context.params["filter_tenant_settings"] = filter_tenant_settings
    for field in info.selected_fields:
        if getattr(field, "name", "") == info.field_name:
            risk_level_date = ProjectType.find_risk_level_date(field.selections)
            break

    ids: list[uuid.UUID] | None = None
    if id:
        ids = [id]

    internal_filter_by = InternalLocationFilterBy()
    if filter_by:
        internal_filter_data = {
            INTERNAL_LOCATION_FILTER_MAPPER[i.field.value]: i.values for i in filter_by
        }
        risk_filter = internal_filter_data.pop("risk_levels", None)
        if risk_filter:
            internal_filter_data["risk_levels"] = [
                RISK_LEVEL_MAPPER.get(i, i) for i in risk_filter
            ]
        project_status_filter = internal_filter_data.pop("project_status", None)
        if project_status_filter:
            internal_filter_data["project_status"] = [
                PROJECT_STATUS_MAPPER.get(i, i) for i in project_status_filter
            ]
        internal_filter_by = InternalLocationFilterBy(**internal_filter_data)

    x_max_map_extent = None
    x_min_map_extent = None
    y_max_map_extent = None
    y_min_map_extent = None
    if map_extent:
        x_max_map_extent = map_extent.x_max
        x_min_map_extent = map_extent.x_min
        y_max_map_extent = map_extent.y_max
        y_min_map_extent = map_extent.y_min

    (
        with_risk,
        count,
        locations,
    ) = await info.context.project_locations.get_locations_with_risk(
        ids=ids,
        library_region_ids=library_region_ids or internal_filter_by.library_region_ids,
        library_division_ids=(
            library_division_ids or internal_filter_by.library_division_ids
        ),
        library_project_type_ids=(
            library_project_type_ids or internal_filter_by.library_project_type_ids
        ),
        work_type_ids=(work_type_ids or internal_filter_by.work_type_ids),
        project_ids=project_ids or internal_filter_by.project_ids,
        project_status=project_status or internal_filter_by.project_status,
        contractor_ids=contractor_ids or internal_filter_by.contractor_ids,
        all_supervisor_ids=supervisor_ids or internal_filter_by.supervisor_ids,
        search=search,
        order_by=order_by_to_pydantic(order_by),
        limit=limit,
        offset=offset,
        risk_level_date=risk_level_date,
        risk_levels=internal_filter_by.risk_levels,
        x_max_map_extent=x_max_map_extent,
        x_min_map_extent=x_min_map_extent,
        y_max_map_extent=y_max_map_extent,
        y_min_map_extent=y_min_map_extent,
        load_project=True,
    )

    project_locations_list = []

    if with_risk:
        locations_with_risk: list[tuple[Location, str]] = locations  # type: ignore
        project_locations_list = [
            ProjectLocationResponseType(
                locations_count=count,
                filter_locations_date_range=[
                    FilterLocationDateRangeType.from_orm(
                        project,
                        risk_level=getattr(RiskLevel, risk_level),  # type: ignore
                    )
                    for project, risk_level in locations_with_risk
                ],
            )
        ]
    else:
        locations_no_risk: list[Location] = locations  # type: ignore
        project_locations_list = [
            ProjectLocationResponseType(
                locations_count=count,
                filter_locations_date_range=[
                    FilterLocationDateRangeType.from_orm(project)  # type: ignore
                    for project in locations_no_risk
                ],
            )
        ]

    return project_locations_list


async def get_project_locations(
    info: Info,
    id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    order_by: Optional[list[ProjectLocationOrderByInput]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    library_region_ids: Optional[list[uuid.UUID]] = None,
    library_division_ids: Optional[list[uuid.UUID]] = None,
    library_project_type_ids: Optional[list[uuid.UUID]] = None,
    work_type_ids: Optional[list[uuid.UUID]] = None,
    project_ids: Optional[list[uuid.UUID]] = None,
    project_status: Optional[list[ProjectStatus]] = None,
    contractor_ids: Optional[list[uuid.UUID]] = None,
    supervisor_ids: Optional[list[uuid.UUID]] = None,
    filter_by: Optional[
        list[LocationFilterByInput]
    ] = None,  # TODO remove after FE changes
    filter_tenant_settings: Optional[bool] = False,
) -> list[ProjectLocationType]:
    info.context.params["filter_tenant_settings"] = filter_tenant_settings
    # Find date on riskLevel resolver
    # TODO should we have a riskLevelDate where and drop riskLevel.date?
    risk_level_date = None
    for field in info.selected_fields:
        if getattr(field, "name", "") == info.field_name:
            risk_level_date = ProjectType.find_risk_level_date(field.selections)
            break

    ids: list[uuid.UUID] | None = None
    if id:
        ids = [id]

    internal_filter_by = InternalLocationFilterBy()
    if filter_by:
        internal_filter_data = {
            INTERNAL_LOCATION_FILTER_MAPPER[i.field.value]: i.values for i in filter_by
        }
        risk_filter = internal_filter_data.pop("risk_levels", None)
        if risk_filter:
            internal_filter_data["risk_levels"] = [
                RISK_LEVEL_MAPPER.get(i, i) for i in risk_filter
            ]
        project_status_filter = internal_filter_data.pop("project_status", None)
        if project_status_filter:
            internal_filter_data["project_status"] = [
                PROJECT_STATUS_MAPPER.get(i, i) for i in project_status_filter
            ]
        internal_filter_by = InternalLocationFilterBy(**internal_filter_data)

    (
        with_risk,
        count,
        locations,
    ) = await info.context.project_locations.get_locations_with_risk(
        ids=ids,
        library_region_ids=library_region_ids or internal_filter_by.library_region_ids,
        library_division_ids=(
            library_division_ids or internal_filter_by.library_division_ids
        ),
        library_project_type_ids=(
            library_project_type_ids or internal_filter_by.library_project_type_ids
        ),
        work_type_ids=(work_type_ids or internal_filter_by.work_type_ids),
        project_ids=project_ids or internal_filter_by.project_ids,
        project_status=project_status or internal_filter_by.project_status,
        contractor_ids=contractor_ids or internal_filter_by.contractor_ids,
        all_supervisor_ids=supervisor_ids or internal_filter_by.supervisor_ids,
        search=search,
        order_by=order_by_to_pydantic(order_by),
        limit=limit,
        offset=offset,
        risk_level_date=risk_level_date,
        risk_levels=internal_filter_by.risk_levels,
        load_project=True,
    )
    if with_risk:
        locations_with_risk: list[tuple[Location, str]] = locations  # type: ignore
        return [
            ProjectLocationType.from_orm(
                project, risk_level=getattr(RiskLevel, risk_level)
            )
            for project, risk_level in locations_with_risk
        ]
    else:
        locations_no_risk: list[Location] = locations  # type: ignore
        return [ProjectLocationType.from_orm(project) for project in locations_no_risk]


async def get_form_definitions(
    info: Info,
) -> list[FormDefinitionType]:
    form_definitions = await info.context.forms.get_form_definitions()
    return [
        FormDefinitionType.from_orm(form_definition)
        for form_definition in form_definitions
    ]


async def get_site_conditions(
    info: Info,
    id: Optional[uuid.UUID] = None,
    location_id: Optional[uuid.UUID] = None,
    date: Optional[datetime.date] = None,
    filter_tenant_settings: Optional[bool] = False,
    order_by: Optional[list[OrderByInput]] = None,
) -> list[SiteConditionType]:
    info.context.params["filter_tenant_settings"] = filter_tenant_settings
    site_conditions = []
    if id:
        site_conditions = await info.context.site_conditions.get_site_conditions(
            ids=[id],
            filter_tenant_settings=filter_tenant_settings,
            order_by=order_by_to_pydantic(order_by),
        )
    elif location_id:
        site_conditions = await info.context.site_conditions.get_site_conditions(
            location_ids=[location_id],
            date=date,
            filter_tenant_settings=filter_tenant_settings,
            order_by=order_by_to_pydantic(order_by),
        )

    return [
        SiteConditionType.from_orm(site_condition)
        for _, site_condition in site_conditions
    ]


async def get_adhoc_site_conditions(
    info: Info,
    site_input: SiteLocationInput,
    order_by: Optional[list[OrderByInput]] = None,
    filter_tenant_settings: bool | None = False,
) -> list[SiteConditionType]:
    info.context.params["filter_tenant_settings"] = filter_tenant_settings
    site_conditions = await info.context.site_conditions.get_adhoc_site_conditions(
        latitude=site_input.latitude,
        longitude=site_input.longitude,
        date=site_input.date,
        order_by=order_by_to_pydantic(order_by),
        filter_tenant_settings=filter_tenant_settings,
    )
    return [
        SiteConditionType.from_orm(site_condition)
        for _, site_condition, _ in site_conditions
    ]


async def get_tasks_for_project_location(
    info: Info,
    id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    location_id: Optional[uuid.UUID] = None,
    date: Optional[datetime.date] = None,
    filter_tenant_settings: Optional[bool] = False,
    order_by: Optional[list[TaskOrderByInput]] = None,
) -> list[TaskType]:
    info.context.params["filter_tenant_settings"] = filter_tenant_settings
    tasks = await info.context.tasks.get_tasks(
        ids=[id] if id else None,
        location_ids=[location_id] if location_id else None,
        date=date,
        search=search,
        filter_tenant_settings=filter_tenant_settings,
        order_by=order_by_to_pydantic(order_by),
    )
    return [TaskType.from_orm(task) for _, task in tasks]


async def get_activities_for_project_location(
    info: Info,
    id: Optional[uuid.UUID] = None,
    date: Optional[datetime.date] = None,
    location_id: Optional[uuid.UUID] = None,
    filter_tenant_settings: Optional[bool] = False,
    order_by: Optional[list[OrderByInput]] = None,
) -> list[ActivityType]:
    info.context.params["filter_tenant_settings"] = filter_tenant_settings
    activities = await info.context.activities.get_activities(
        ids=[id] if id else None,
        location_ids=[location_id] if location_id else None,
        date=date,
        order_by=order_by_to_pydantic(order_by),
    )

    return [ActivityType.from_orm(activity) for activity in activities]


async def get_library_tasks(
    info: Info,
    ids: Optional[list[uuid.UUID]] = None,
    order_by: Optional[list[LibraryTaskOrderByInput]] = None,
    allow_archived: bool = False,
) -> list[LibraryTaskType]:
    """
    Get the details of a library task
    """
    return [
        LibraryTaskType.from_orm(item)
        for item in await info.context.library_tasks.get_tasks(
            ids=ids if ids else None,
            order_by=order_by_to_pydantic(order_by),
            allow_archived=allow_archived,
        )
    ]


async def get_tenant_and_work_type_linked_library_tasks(
    info: Info,
    tenant_work_type_ids: list[uuid.UUID],
    ids: Optional[list[uuid.UUID]] = None,
    order_by: Optional[list[LibraryTaskOrderByInput]] = None,
) -> list[LinkedLibraryTaskType]:
    # NOTE: Add params to context so that it can be used by nested resolvers
    info.context.params["tenant_work_type_ids"] = tenant_work_type_ids
    return [
        LinkedLibraryTaskType.from_orm(item)
        for item in await info.context.library_tasks.get_tenant_and_work_type_linked_library_tasks(
            tenant_work_type_ids=tenant_work_type_ids,
            ids=ids if ids else None,
            order_by=order_by_to_pydantic(order_by),
        )
    ]


async def get_library_site_conditions(
    info: Info,
    id: Optional[uuid.UUID] = None,
    order_by: Optional[list[OrderByInput]] = None,
    allow_archived: bool = False,
) -> list[LibrarySiteConditionType]:
    """
    Get the details of a library site condition
    """
    return [
        LibrarySiteConditionType.from_orm(item)
        for item in await info.context.library_site_conditions.get_library_site_conditions(
            ids=[id] if id else None,
            order_by=order_by_to_pydantic(order_by),
            allow_archived=allow_archived,
        )
    ]


async def get_tenant_and_work_type_linked_library_site_conditions(
    info: Info,
    tenant_work_type_ids: list[uuid.UUID],
    id: Optional[uuid.UUID] = None,
    order_by: Optional[list[OrderByInput]] = None,
) -> list[LibrarySiteConditionType]:
    return [
        LibrarySiteConditionType.from_orm(item)
        for item in await info.context.library_site_conditions.get_tenant_and_work_type_linked_library_site_conditions(
            tenant_work_type_ids=tenant_work_type_ids,
            ids=[id] if id else None,
            order_by=order_by_to_pydantic(order_by),
        )
    ]


async def get_library_hazards(
    info: Info,
    type: LibraryFilterType,
    id: Optional[uuid.UUID] = None,
    library_task_id: Optional[uuid.UUID] = None,
    library_site_condition_id: Optional[uuid.UUID] = None,
    order_by: Optional[list[OrderByInput]] = None,
    allow_archived: bool = True,
) -> list[LibraryHazardType]:
    """
    Get the details of a library hazard
    """
    hazards = await info.context.library.get_hazards(
        type,
        id=id,
        library_task_id=library_task_id,
        library_site_condition_id=library_site_condition_id,
        order_by=order_by_to_pydantic(order_by),
    )

    parent_id: Optional[uuid.UUID] = None
    if type == LibraryFilterType.TASK:
        parent_id = library_task_id
    elif type == LibraryFilterType.SITE_CONDITION:
        parent_id = library_site_condition_id

    return [
        LibraryHazardType.from_orm(
            hazard,
            parent_type=type,
            parent_id=parent_id,
            library_task_id=library_task_id,
        )
        for hazard in hazards
    ]


async def get_tenant_linked_library_hazards(
    info: Info,
    type: Optional[LibraryFilterType] = None,
    id: Optional[uuid.UUID] = None,
    library_task_id: Optional[uuid.UUID] = None,
    library_site_condition_id: Optional[uuid.UUID] = None,
    order_by: Optional[list[OrderByInput]] = None,
    allow_archived: bool = True,
) -> list[LinkedLibraryHazardType]:
    return [
        LinkedLibraryHazardType.from_orm(hazard)
        for hazard in await info.context.library.get_hazards_v2(
            type,
            id=id,
            library_task_id=library_task_id,
            library_site_condition_id=library_site_condition_id,
            order_by=order_by_to_pydantic(order_by),
            allow_archived=allow_archived,
        )
    ]


async def get_library_controls(
    info: Info,
    type: LibraryFilterType,
    id: Optional[uuid.UUID] = None,
    library_hazard_id: Optional[uuid.UUID] = None,
    library_task_id: Optional[uuid.UUID] = None,
    library_site_condition_id: Optional[uuid.UUID] = None,
    order_by: Optional[list[OrderByInput]] = None,
    allow_archived: bool = True,
) -> list[LibraryControlType]:
    """
    Get the details of a library control
    """
    controls = await info.context.library.get_controls(
        type,
        id=id,
        library_hazard_id=library_hazard_id,
        library_task_id=library_task_id,
        library_site_condition_id=library_site_condition_id,
        order_by=order_by_to_pydantic(order_by),
        allow_archived=allow_archived,
    )
    return [
        LibraryControlType.from_orm(library_control) for library_control in controls
    ]


async def get_tenant_linked_library_controls(
    info: Info,
    type: LibraryFilterType | None = None,
    id: Optional[uuid.UUID] = None,
    library_hazard_id: Optional[uuid.UUID] = None,
    library_task_id: Optional[uuid.UUID] = None,
    library_site_condition_id: Optional[uuid.UUID] = None,
    order_by: Optional[list[OrderByInput]] = None,
    allow_archived: bool = True,
) -> list[LinkedLibraryControlType]:
    """
    Get tenant linked library controls
    """
    controls = await info.context.library.get_controls_v2(
        type,
        id=id,
        library_hazard_id=library_hazard_id,
        library_task_id=library_task_id,
        library_site_condition_id=library_site_condition_id,
        order_by=order_by_to_pydantic(order_by),
        allow_archived=allow_archived,
    )
    return [
        LinkedLibraryControlType.from_orm(library_control)
        for library_control in controls
    ]


async def get_location_hazard_control_settings(
    info: Info, location_id: uuid.UUID
) -> list[LocationHazardControlSettingsType]:
    hazard_control_settings = (
        await info.context.library.get_location_hazard_control_settings(location_id)
    )

    return [
        LocationHazardControlSettingsType.from_orm(hazard_control_setting)
        for hazard_control_setting in hazard_control_settings
    ]


async def get_library_divisions(
    info: Info, order_by: Optional[list[OrderByInput]] = None
) -> list[LibraryDivisionType]:
    return [
        LibraryDivisionType.from_orm(division)
        for division in await info.context.library.get_divisions(
            order_by=order_by_to_pydantic(order_by)
        )
    ]


async def get_library_regions(
    info: Info, order_by: Optional[list[OrderByInput]] = None
) -> list[LibraryRegionType]:
    order_by = order_by or [
        OrderByInput(field=OrderByFieldType.NAME, direction=OrderByDirectionType.ASC)
    ]
    return [
        LibraryRegionType.from_orm(region)
        for region in await info.context.library.get_regions(
            order_by=order_by_to_pydantic(order_by)
        )
    ]


async def get_library_project_types(
    info: Info, order_by: Optional[list[OrderByInput]] = None
) -> list[LibraryProjectType]:
    return [
        LibraryProjectType.from_orm(project_type)
        for project_type in await info.context.library.get_project_types(
            order_by=order_by_to_pydantic(order_by)
        )
    ]


async def get_system() -> SystemType:
    return SystemType(
        version=settings.APP_VERSION,
    )


async def get_me(info: Info) -> MeType:
    return MeType.from_orm(info.context.user)


async def get_managers(
    info: Info, order_by: Optional[list[OrderByInput]] = None
) -> list[ManagerType]:
    return [
        ManagerType.from_orm(user)
        for user in await info.context.users.by_role(
            "manager", order_by=order_by_to_pydantic(order_by)
        )
    ]


async def get_supervisors(
    info: Info, order_by: Optional[list[OrderByInput]] = None
) -> list[SupervisorType]:
    return [
        SupervisorType.from_orm(user)
        for user in await info.context.users.by_role(
            "supervisor", order_by=order_by_to_pydantic(order_by)
        )
    ]


async def get_contractors(
    info: Info, order_by: Optional[list[OrderByInput]] = None
) -> list[ContractorType]:
    return [
        ContractorType.from_orm(contractor)
        for contractor in await info.context.contractors.get_contractors(
            order_by=order_by_to_pydantic(order_by)
        )
    ]


async def get_library_asset_types(
    info: Info, order_by: Optional[list[OrderByInput]] = None
) -> list[LibraryAssetType]:
    return [
        LibraryAssetType.from_orm(asset_type)
        for asset_type in await info.context.library.get_asset_types(
            order_by=order_by_to_pydantic(order_by)
        )
    ]


async def get_ui_config_on_form_type(info: Info, form_type: FormsType) -> UIConfigType:
    ui_config = await info.context.ui_config_loader.load_get_ui_config_on_form_type(
        form_type
    )
    return UIConfigType.from_orm(ui_config)


async def get_first_aid_aed_locations_from_location_type(
    info: Info,
    location_type: Optional[LocationType] = None,
    order_by: Optional[list[LocationOrderByInput]] = None,
) -> Optional[list[FirstAIDAEDLocationType]]:
    first_aid_aed_locations = (
        await info.context.first_aid_aed_locations.load_first_aid_aed_locations(
            location_type, order_by=order_by_to_pydantic(order_by)
        )
    )
    return [
        FirstAIDAEDLocationType.from_orm(first_aid_location)
        for first_aid_location in first_aid_aed_locations
    ]


async def get_library_activity_types(
    info: Info, order_by: Optional[list[OrderByInput]] = None
) -> list[LibraryActivityType]:
    return [
        LibraryActivityType.from_orm(activity_type)
        for activity_type in await info.context.library.get_activity_types(
            order_by=order_by_to_pydantic(order_by)
        )
    ]


async def get_library_activity_groups_library(
    info: Info, order_by: Optional[list[OrderByInput]] = None
) -> list[LibraryActivityGroupType]:
    return [
        LibraryActivityGroupType.from_orm(activity_group)
        for activity_group in await info.context.library.get_activity_groups(
            order_by=order_by_to_pydantic(order_by)
        )
    ]


async def get_daily_report(
    info: Info, id: uuid.UUID, status: Optional[FormStatus] = None
) -> Optional[DailyReportType]:
    daily_report = await info.context.daily_reports.get_daily_report(id, status=status)
    if not daily_report:
        return None
    else:
        return DailyReportType.from_orm(daily_report)


async def get_daily_report_forms_list(
    info: Info, id: uuid.UUID, status: Optional[FormStatus] = None
) -> Optional[DailyReportFormsListType]:
    daily_report = await info.context.daily_reports.get_daily_report(id, status=status)
    if not daily_report:
        return None
    else:
        return DailyReportFormsListType.from_orm(daily_report)


async def get_daily_reports_for_project_location(
    info: Info, project_location_id: uuid.UUID, date: datetime.date
) -> list[DailyReportType]:
    daily_reports = await info.context.project_locations.daily_reports(date=date).load(
        project_location_id
    )
    return [DailyReportType.from_orm(daily_report) for daily_report in daily_reports]


async def get_recommendations() -> RecommendationType:
    return RecommendationType()


async def get_historical_incidents_for_library_task(
    info: Info, library_task_id: uuid.UUID, allow_archived: bool = True
) -> list[IncidentType]:
    loaded_incidents = await info.context.incidents.load_incidents_for_library_task(
        library_task_ids=[library_task_id], allow_archived=allow_archived
    )
    return [IncidentType.from_orm(incident) for incident in loaded_incidents[0]]


async def get_historical_incidents_for_library_tasks(
    info: Info,
    library_task_ids: list[uuid.UUID],
    allow_archived: bool = False,
    limit: Optional[int] = GeneralConstants.HISTORIC_INCIDENTS_LIMIT,
) -> list[IncidentType]:
    loaded_incidents = (
        await info.context.incidents.load_incidents_for_multiple_library_tasks(
            library_task_ids=library_task_ids,
            allow_archived=allow_archived,
            limit=limit,
        )
    )
    return [IncidentType.from_orm(incident) for incident in loaded_incidents]


async def get_job_safety_briefing(
    info: Info,
    id: uuid.UUID,
) -> JobSafetyBriefingType:
    result = await info.context.job_safety_briefings.get_job_safety_briefing(
        id=id,
    )

    return JobSafetyBriefingType.from_orm(result)


async def get_natgrid_job_safety_briefing(
    info: Info,
    id: uuid.UUID,
) -> NatGridJobSafetyBriefingType:
    result = (
        await info.context.natgrid_job_safety_briefings.get_natgrid_job_safety_briefing(
            id=id,
        )
    )

    return NatGridJobSafetyBriefingType.from_orm(result)


async def get_last_natgrid_job_safety_briefing_for_user(
    info: Info,
    allow_archived: Optional[bool] = True,
) -> NatGridJobSafetyBriefingType:
    jsb_data = await info.context.natgrid_job_safety_briefings.get_last_natgrid_job_safety_briefing_by_user_id(
        user_id=info.context.user.id,
        tenant_id=info.context.tenant_id,
        allow_archived=allow_archived,
    )
    return NatGridJobSafetyBriefingType.from_orm(jsb_data)


async def get_natgrid_job_safety_briefing_forms_list(
    info: Info,
    id: uuid.UUID,
) -> NatGridJobSafetyBriefingFormsListType:
    result = (
        await info.context.natgrid_job_safety_briefings.get_natgrid_job_safety_briefing(
            id=id,
        )
    )

    return NatGridJobSafetyBriefingFormsListType.from_orm(result)


async def get_job_safety_briefing_forms_list(
    info: Info,
    id: uuid.UUID,
) -> JobSafetyBriefingFormsListType:
    result = await info.context.job_safety_briefings.get_job_safety_briefing(
        id=id,
    )
    return JobSafetyBriefingFormsListType.from_orm(result)


async def get_last_job_safety_briefing(
    info: Info,
    filter_on: JSBFilterOnEnum = JSBFilterOnEnum.USER_DETAILS,
    project_location_id: Optional[uuid.UUID] = None,
) -> JobSafetyBriefingType | None:
    if filter_on == JSBFilterOnEnum.PROJECT_LOCATION and project_location_id is None:
        raise ValueError("Please enter project location id")

    result = await info.context.job_safety_briefings.get_last_jsb(
        actor=info.context.user,
        project_location_id=project_location_id,
    )

    if result is None:
        return None

    return JobSafetyBriefingType.from_orm(result)


async def get_last_adhoc_jsb(info: Info) -> JobSafetyBriefingType | None:
    result = await info.context.job_safety_briefings.get_last_adhoc_jsb(
        actor=info.context.user,
    )

    if result is None:
        return None

    return JobSafetyBriefingType.from_orm(result)


async def get_energy_based_observation(
    info: Info,
    id: uuid.UUID,
) -> EnergyBasedObservationType:
    result = await info.context.energy_based_observations.get_energy_based_observations(
        ebo_id=id, allow_archived=False
    )

    return EnergyBasedObservationType.from_orm(result)


async def get_energy_based_observation_forms_list(
    info: Info,
    id: uuid.UUID,
) -> EnergyBasedObservationFormsListType:
    result = await info.context.energy_based_observations.get_energy_based_observations(
        ebo_id=id, allow_archived=False
    )

    return EnergyBasedObservationFormsListType.from_orm(result)


async def get_nearest_medical_facilities(
    info: Info,
    latitude: Decimal,
    longitude: Decimal,
) -> list[MedicalFacilityType]:
    results = await info.context.medical_facilities.load_nearest_medical_facilities(
        latitude, longitude
    )

    return [MedicalFacilityType.from_pydantic(facility) for facility in results]


async def get_form_list(
    info: Info,
    # TODO: This should be a enum for form types
    form_name: Optional[list[str]] = None,
    form_id: Optional[list[str]] = None,
    form_status: Optional[list[FormStatus]] = None,
    project_ids: Optional[list[uuid.UUID]] = None,
    created_by_ids: Optional[list[uuid.UUID]] = None,
    updated_by_ids: list[uuid.UUID] | None = None,
    location_ids: Optional[list[uuid.UUID]] = None,
    start_created_at: Optional[datetime.date] = None,
    end_created_at: Optional[datetime.date] = None,
    start_updated_at: Optional[datetime.date] = None,
    end_updated_at: Optional[datetime.date] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[list[FormListOrderByInput]] = None,
    search: Optional[str] = None,
    ad_hoc: bool = False,
    start_completed_at: Optional[datetime.date] = None,
    end_completed_at: Optional[datetime.date] = None,
    start_report_date: Optional[datetime.date] = None,
    end_report_date: Optional[datetime.date] = None,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    operating_region_names: Optional[list[str]] = None,
    manager_ids: Optional[list[str]] = None,
) -> list[FormInterface]:
    results = await info.context.forms.get_forms(
        form_name=form_name,
        form_id=form_id,
        form_status=form_status,
        start_created_at=start_created_at,
        end_created_at=end_created_at,
        start_updated_at=start_updated_at,
        end_updated_at=end_updated_at,
        created_by_ids=created_by_ids,
        updated_by_ids=updated_by_ids,
        project_ids=project_ids,
        location_ids=location_ids,
        limit=limit,
        offset=offset,
        order_by=order_by_to_pydantic(order_by),
        search=search,
        ad_hoc=ad_hoc,
        start_completed_at=start_completed_at,
        end_completed_at=end_completed_at,
        start_report_date=start_report_date,
        end_report_date=end_report_date,
        start_date=start_date,
        end_date=end_date,
        operating_region_names=operating_region_names,
        manager_ids=manager_ids,
    )

    form_list: list[FormInterface] = []
    for form, operating_hq in results:
        if isinstance(form, JobSafetyBriefing):
            form_list.append(JobSafetyBriefingType.from_orm(form, operating_hq))
        elif isinstance(form, EnergyBasedObservation):
            form_list.append(EnergyBasedObservationType.from_orm(form, operating_hq))
        elif isinstance(form, DailyReport):
            form_list.append(DailyReportType.from_orm(form, operating_hq))
        elif isinstance(form, NatGridJobSafetyBriefing):
            form_list.append(NatGridJobSafetyBriefingType.from_orm(form, operating_hq))
        else:
            raise ValueError(f"Unknown form type {type(form)}")
    return form_list


async def get_form_list_count(
    info: Info,
    # TODO: This should be a enum for form types
    form_name: Optional[list[str]] = None,
    form_id: Optional[list[str]] = None,
    form_status: Optional[list[FormStatus]] = None,
    project_ids: Optional[list[uuid.UUID]] = None,
    created_by_ids: Optional[list[uuid.UUID]] = None,
    updated_by_ids: list[uuid.UUID] | None = None,
    location_ids: Optional[list[uuid.UUID]] = None,
    start_created_at: Optional[datetime.date] = None,
    end_created_at: Optional[datetime.date] = None,
    start_updated_at: Optional[datetime.date] = None,
    end_updated_at: Optional[datetime.date] = None,
    search: Optional[str] = None,
    ad_hoc: bool = False,
    start_completed_at: Optional[datetime.date] = None,
    end_completed_at: Optional[datetime.date] = None,
    start_report_date: Optional[datetime.date] = None,
    end_report_date: Optional[datetime.date] = None,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    operating_region_names: Optional[list[str]] = None,
    manager_ids: Optional[list[str]] = None,
) -> int:
    result_count = await info.context.forms.get_forms_count(
        form_name=form_name,
        form_id=form_id,
        form_status=form_status,
        start_created_at=start_created_at,
        end_created_at=end_created_at,
        start_updated_at=start_updated_at,
        end_updated_at=end_updated_at,
        created_by_ids=created_by_ids,
        updated_by_ids=updated_by_ids,
        project_ids=project_ids,
        location_ids=location_ids,
        search=search,
        ad_hoc=ad_hoc,
        start_completed_at=start_completed_at,
        end_completed_at=end_completed_at,
        start_report_date=start_report_date,
        end_report_date=end_report_date,
        start_date=start_date,
        end_date=end_date,
        operating_region_names=operating_region_names,
        manager_ids=manager_ids,
    )

    return result_count


async def get_form_list_filter_options(
    info: Info,
    limit: Optional[int] = 8000,
    offset: Optional[int] = None,
    filter_search: Optional[FormListFilterSearchInput] = None,
) -> FormListFilterOptions:
    formIds = set[str]()
    formNames = set[str]()
    operatingHqs = set[str]()
    createdByUsers = set[OptionItem]()
    updatedByUsers = set[OptionItem]()
    workPackages = set[OptionItem]()
    locations = set[OptionItem]()
    supervisors = set[OptionItem]()
    created_by_load_calls = list[Awaitable[User | None]]()
    updated_by_load_calls = list[Awaitable[AuditEventMetadata | None]]()
    location_calls = list[Awaitable[Location | None]]()
    supervisor_calls = []

    filter_search_dict = filter_search.to_dict() if filter_search else {}

    for form, operating_hq in await info.context.forms.get_forms(
        limit=limit,
        offset=offset,
        filter_search=filter_search_dict,
    ):
        if (
            isinstance(form, JobSafetyBriefing)
            or isinstance(form, EnergyBasedObservation)
            or isinstance(form, DailyReport)
            or isinstance(form, NatGridJobSafetyBriefing)
        ):
            formNames.add(form.__class__.__name__)
            if form.form_id:
                formIds.add(form.form_id)
            if operating_hq:
                operatingHqs.add(operating_hq)
            created_by_load_calls.append(info.context.users.me.load(form.created_by_id))
            updated_by_load_calls.append(info.context.audit.last_updates.load(form.id))
            if isinstance(form, JobSafetyBriefing):
                # Supervisor is only implemented for JSB
                supervisor_calls.append(
                    info.context.jsb_supervisors.jsb_supervisors.load_many([form.id])
                )
        else:
            raise ValueError(f"Unknown form type {type(form)}")

        if (
            isinstance(form, JobSafetyBriefing)
            or isinstance(form, DailyReport)
            or isinstance(form, NatGridJobSafetyBriefing)
        ):
            location_calls.append(
                info.context.project_locations.with_archived.load(
                    form.project_location_id
                )
            )

    (
        created_by_result,
        update_by_result,
        location_result,
        supervisor_result,
    ) = await asyncio.gather(
        asyncio.gather(*created_by_load_calls),
        asyncio.gather(*updated_by_load_calls),
        asyncio.gather(*location_calls),
        asyncio.gather(*supervisor_calls),
    )

    for created_by_user in created_by_result:
        if created_by_user:
            createdByUsers.add(
                OptionItem(id=str(created_by_user.id), name=created_by_user.get_name())
            )

    for audit_event_metadata in update_by_result:
        if audit_event_metadata and audit_event_metadata.user:
            updatedByUsers.add(
                OptionItem(
                    id=str(audit_event_metadata.user.id),
                    name=audit_event_metadata.user.get_name(),
                )
            )

    for project_location in location_result:
        if project_location:
            locations.add(
                OptionItem(id=str(project_location.id), name=project_location.name)
            )
            if project_location.project:
                workPackages.add(
                    OptionItem(
                        id=str(project_location.project.id),
                        name=project_location.project.name,
                    )
                )

    for results in supervisor_result:
        for supervisor in filter(None, results):
            supervisors.update(
                OptionItem(id=str(item.manager_id), name=item.manager_name)
                for item in supervisor
                if item and item.manager_id and item.manager_name
            )

    return FormListFilterOptions(
        formIds=sorted(formIds, reverse=True),
        formNames=sorted(formNames),
        operatingHqs=sorted(operatingHqs),
        createdByUsers=sorted(createdByUsers),
        updatedByUsers=sorted(updatedByUsers),
        workPackages=sorted(workPackages),
        locations=sorted(locations),
        supervisors=sorted(supervisors),
    )


async def get_insights(
    info: Info,
    limit: Optional[int] = None,
    after: Optional[uuid.UUID] = None,
) -> list[InsightType]:
    db_insights = await info.context.insight.load_insights(limit=limit, after=after)
    return [InsightType.from_orm(db_insight) for db_insight in db_insights]


async def get_crew_leaders(
    info: Info,
    limit: Optional[int] = None,
    offset: int | None = None,
) -> list[CrewLeaderType]:
    db_crew_leaders = await info.context.crew_leader.load_crew_leaders(
        limit=limit, offset=offset
    )
    return [
        CrewLeaderType.from_orm(db_crew_leader) for db_crew_leader in db_crew_leaders
    ]


async def extract_unique_crew_leaders(
    jsb_data: list,
) -> set[RecentUsedCrewLeaderReturnType]:
    unique_crew_leaders: set[RecentUsedCrewLeaderReturnType] = set()
    if not jsb_data:
        return unique_crew_leaders

    for i, item in jsb_data:
        if item is None:
            continue
        crew_sign = item.get("crew_sign")
        if not crew_sign or not isinstance(crew_sign, list):
            continue

        for crew_leader in crew_sign:
            if not isinstance(crew_leader, dict):
                continue

            crew_details = crew_leader.get("crew_details")
            if not crew_details or not isinstance(crew_details, dict):
                continue

            crew_id = crew_details.get("id")
            crew_name = crew_details.get("name")
            if crew_id and crew_name:
                unique_crew_leaders.add(
                    RecentUsedCrewLeaderReturnType(id=crew_id, name=crew_name)
                )
    return unique_crew_leaders


async def get_recent_used_crew_leaders(
    info: Info,
    limit: Optional[int] = None,
    allow_archived: Optional[bool] = True,
) -> set[RecentUsedCrewLeaderReturnType]:
    jsb_data = await info.context.natgrid_job_safety_briefings.get_natgrid_job_safety_briefings_by_user_id(
        info.context.user.id, limit=limit, allow_archived=allow_archived
    )
    data: set[RecentUsedCrewLeaderReturnType] = await extract_unique_crew_leaders(
        jsb_data
    )
    existing_names = await info.context.crew_leader.match_if_crew_leader_exists(
        crew_leaders=[cl.name for cl in data]
    )
    filtered_crew_leaders = {cl for cl in data if cl.name in existing_names}
    return filtered_crew_leaders


async def get_jsb_supervisors(
    info: Info,
    limit: Optional[int] = None,
    offset: int | None = None,
) -> list[JSBSupervisorType]:
    jsb_supervisors = await info.context.jsb_supervisors.get_jsb_supervisors(
        limit=limit, offset=offset
    )
    return [
        JSBSupervisorType.from_orm(jsb_supervisor) for jsb_supervisor in jsb_supervisors
    ]


async def get_workos_directory_users(
    info: Info,
    directory_ids: list[str],
    group: Optional[str] = None,
    limit: Optional[str] = None,
    before: Optional[str] = None,
    after: Optional[str] = None,
    order: Optional[str] = None,
    update_cache: Optional[bool] = None,
) -> WorkOSDirectoryUsersResponseType:
    response = await WorkOSCrewData().fetch_workos_crew_info(
        list(directory_ids),
        DirectoryUsersQuery(
            group=group,
            limit=limit,
            before=before,
            after=after,
            order=order,
        ),
        tenant_id=info.context.tenant_id,
        update_cache=update_cache,
    )
    return response


async def get_form_list_with_contents(
    info: Info,
    # TODO: This should be a enum for form types
    form_name: Optional[list[str]] = None,
    form_id: Optional[list[str]] = None,
    form_status: Optional[list[FormStatus]] = None,
    project_ids: Optional[list[uuid.UUID]] = None,
    created_by_ids: Optional[list[uuid.UUID]] = None,
    updated_by_ids: list[uuid.UUID] | None = None,
    location_ids: Optional[list[uuid.UUID]] = None,
    start_created_at: Optional[datetime.date] = None,
    end_created_at: Optional[datetime.date] = None,
    start_updated_at: Optional[datetime.date] = None,
    end_updated_at: Optional[datetime.date] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[list[FormListOrderByInput]] = None,
    search: Optional[str] = None,
    ad_hoc: bool = False,
    start_completed_at: Optional[datetime.date] = None,
    end_completed_at: Optional[datetime.date] = None,
    start_report_date: Optional[datetime.date] = None,
    end_report_date: Optional[datetime.date] = None,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    operating_region_names: Optional[list[str]] = None,
    manager_ids: Optional[list[str]] = None,
) -> list[FormInterfaceWithContents]:
    results = await info.context.forms.get_forms(
        form_name=form_name,
        form_id=form_id,
        form_status=form_status,
        start_created_at=start_created_at,
        end_created_at=end_created_at,
        start_updated_at=start_updated_at,
        end_updated_at=end_updated_at,
        created_by_ids=created_by_ids,
        updated_by_ids=updated_by_ids,
        project_ids=project_ids,
        location_ids=location_ids,
        limit=limit,
        offset=offset,
        order_by=order_by_to_pydantic(order_by),
        search=search,
        ad_hoc=ad_hoc,
        with_contents=True,
        start_completed_at=start_completed_at,
        end_completed_at=end_completed_at,
        start_report_date=start_report_date,
        end_report_date=end_report_date,
        start_date=start_date,
        end_date=end_date,
        operating_region_names=operating_region_names,
        manager_ids=manager_ids,
    )

    form_list: list[FormInterfaceWithContents] = []
    for form, operating_hq in results:
        if isinstance(form, JobSafetyBriefing):
            form_list.append(
                JobSafetyBriefingFormsListType.from_orm(form, operating_hq)
            )
        elif isinstance(form, EnergyBasedObservation):
            form_list.append(
                EnergyBasedObservationFormsListType.from_orm(form, operating_hq)
            )
        elif isinstance(form, DailyReport):
            form_list.append(DailyReportFormsListType.from_orm(form, operating_hq))
        elif isinstance(form, NatGridJobSafetyBriefing):
            form_list.append(
                NatGridJobSafetyBriefingFormsListType.from_orm(form, operating_hq)
            )
        else:
            raise ValueError(f"Unknown form type {type(form)}")

    return form_list


async def get_tenant_work_types(info: Info) -> list[WorkTypeType]:
    return [
        WorkTypeType.from_orm(work_type)
        for work_type in await info.context.work_types.load_tenant_work_types()
    ]


async def rest_api_wrapper(
    info: Info, endpoint: str, method: str, payload: Optional[str] = None
) -> RestApiWrapperType:
    method = method.upper()
    valid_methods = {"GET", "POST", "PUT", "PATCH", "DELETE"}

    if method not in valid_methods:
        raise ValueError(f"Invalid method: {method}. Must be one of {valid_methods}")

    headers = {
        "Authorization": f"Bearer {info.context.token}",
        "Content-Type": "application/json",
    }

    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON payload")

    client_timeout = Timeout(5.0, read=settings.REST_API_WRAPPER_READ_TIMEOUT)

    async with httpx.AsyncClient(timeout=client_timeout) as client:
        try:
            response = await client.request(
                method=method,
                url=endpoint,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

            try:
                return RestApiWrapperType(
                    endpoint=endpoint,
                    method=method,
                    payload=payload,
                    response=response.json(),
                )
            except ValueError:
                raise ValueError({"text": response.text})

        except httpx.HTTPStatusError as http_err:
            raise ValueError(
                {
                    "error": f"HTTP error: {http_err.response.status_code} - {http_err.response.text}"
                }
            )
        except httpx.RequestError as req_err:
            raise ValueError(f"Request error: {str(req_err)}")
        except Exception as e:
            raise ValueError(f"Unexpected error: {str(e)}")
