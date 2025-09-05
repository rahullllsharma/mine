from fastapi import Depends
from starlette.background import BackgroundTasks

from worker_safety_service.context import (
    BackgroundRiskModelReactor,
    create_riskmodel_container,
)
from worker_safety_service.dal.activities import ActivityManager
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.daily_reports import DailyReportManager
from worker_safety_service.dal.incidents import IncidentsManager
from worker_safety_service.dal.jsb import JobSafetyBriefingManager
from worker_safety_service.dal.library import LibraryManager
from worker_safety_service.dal.library_tasks import LibraryTasksManager
from worker_safety_service.dal.locations import LocationsManager
from worker_safety_service.dal.site_conditions import SiteConditionManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.graphql.data_loaders.activities import TenantActivityLoader
from worker_safety_service.graphql.data_loaders.incidents import IncidentsLoader
from worker_safety_service.graphql.data_loaders.library_tasks import LibraryTasksLoader
from worker_safety_service.graphql.data_loaders.project_locations import (
    TenantProjectLocationLoader,
)
from worker_safety_service.graphql.data_loaders.site_conditions import (
    TenantSiteConditionLoader,
)
from worker_safety_service.graphql.data_loaders.tasks import TenantTaskLoader
from worker_safety_service.graphql.data_loaders.work_packages import (
    TenantWorkPackageLoader,
)
from worker_safety_service.keycloak import get_tenant
from worker_safety_service.models import Tenant
from worker_safety_service.rest.dependency_injection.managers import (
    get_activity_manager,
    get_configurations_manager,
    get_daily_report_manager,
    get_incidents_manager,
    get_job_safety_briefings_manager,
    get_library_manager,
    get_library_tasks_manager,
    get_locations_manager,
    get_site_condition_manager,
    get_task_manager,
    get_work_package_manager,
)
from worker_safety_service.risk_model.riskmodel_container import RiskModelContainer
from worker_safety_service.risk_model.riskmodelreactor import RiskModelReactorInterface


async def get_risk_model_reactor(
    background_tasks: BackgroundTasks,
    riskmodel_container: RiskModelContainer = Depends(create_riskmodel_container),
) -> RiskModelReactorInterface:
    risk_model_reactor = await riskmodel_container.risk_model_reactor()
    return BackgroundRiskModelReactor(lambda: background_tasks, risk_model_reactor)


def get_task_loader(
    task_manager: TaskManager = Depends(get_task_manager),
    risk_model_reactor: RiskModelReactorInterface = Depends(get_risk_model_reactor),
    tenant: Tenant = Depends(get_tenant),
) -> TenantTaskLoader:
    return TenantTaskLoader(task_manager, risk_model_reactor, tenant.id)


def get_incidents_loader(
    incidents_manager: IncidentsManager = Depends(get_incidents_manager),
    tenant: Tenant = Depends(get_tenant),
    risk_model_reactor: RiskModelReactorInterface = Depends(get_risk_model_reactor),
) -> IncidentsLoader:
    return IncidentsLoader(incidents_manager, risk_model_reactor, tenant.id)


def get_activity_loader(
    activity_manager: ActivityManager = Depends(get_activity_manager),
    task_manager: TaskManager = Depends(get_task_manager),
    library_manager: LibraryManager = Depends(get_library_manager),
    risk_model_reactor: RiskModelReactorInterface = Depends(get_risk_model_reactor),
    tenant: Tenant = Depends(get_tenant),
    locations_manager: LocationsManager = Depends(get_locations_manager),
    configurations_manager: ConfigurationsManager = Depends(get_configurations_manager),
) -> TenantActivityLoader:
    return TenantActivityLoader(
        activity_manager,
        task_manager,
        library_manager,
        risk_model_reactor,
        locations_manager,
        configurations_manager,
        tenant.id,
    )


def get_work_package_loader(
    work_package_manager: WorkPackageManager = Depends(get_work_package_manager),
    risk_model_reactor: RiskModelReactorInterface = Depends(get_risk_model_reactor),
    tenant: Tenant = Depends(get_tenant),
    locations_manager: LocationsManager = Depends(get_locations_manager),
) -> TenantWorkPackageLoader:
    return TenantWorkPackageLoader(
        work_package_manager=work_package_manager,
        risk_model_reactor=risk_model_reactor,
        locations_manager=locations_manager,
        tenant_id=tenant.id,
    )


def get_project_locations_loader(
    work_package_manager: WorkPackageManager = Depends(get_work_package_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager),
    task_manager: TaskManager = Depends(get_task_manager),
    site_condition_manager: SiteConditionManager = Depends(get_site_condition_manager),
    daily_reports_manager: DailyReportManager = Depends(get_daily_report_manager),
    library_manager: LibraryManager = Depends(get_library_manager),
    locations_manager: LocationsManager = Depends(get_locations_manager),
    risk_model_reactor: RiskModelReactorInterface = Depends(get_risk_model_reactor),
    activity_loader: TenantActivityLoader = Depends(get_activity_loader),
    work_package_loader: TenantWorkPackageLoader = Depends(get_work_package_loader),
    job_safety_briefings_manager: JobSafetyBriefingManager = Depends(
        get_job_safety_briefings_manager
    ),
    tenant: Tenant = Depends(get_tenant),
) -> TenantProjectLocationLoader:
    return TenantProjectLocationLoader(
        work_package_manager=work_package_manager,
        activity_manager=activity_manager,
        task_manager=task_manager,
        site_condition_manager=site_condition_manager,
        daily_reports_manager=daily_reports_manager,
        library_manager=library_manager,
        locations_manager=locations_manager,
        risk_model_reactor=risk_model_reactor,
        activity_loader=activity_loader,
        work_package_loader=work_package_loader,
        job_safety_briefing_manager=job_safety_briefings_manager,
        tenant_id=tenant.id,
    )


def get_site_condition_loader(
    site_condition_manager: SiteConditionManager = Depends(get_site_condition_manager),
    risk_model_reactor: RiskModelReactorInterface = Depends(get_risk_model_reactor),
    tenant: Tenant = Depends(get_tenant),
) -> TenantSiteConditionLoader:
    return TenantSiteConditionLoader(
        manager=site_condition_manager,
        risk_model_reactor=risk_model_reactor,
        tenant_id=tenant.id,
    )


def get_library_tasks_loader(
    tenant: Tenant = Depends(get_tenant),
    library_task_manager: LibraryTasksManager = Depends(get_library_tasks_manager),
    risk_model_reactor: RiskModelReactorInterface = Depends(get_risk_model_reactor),
) -> LibraryTasksLoader:
    return LibraryTasksLoader(
        manager=library_task_manager,
        risk_model_reactor=risk_model_reactor,
        tenant_id=tenant.id,
    )
