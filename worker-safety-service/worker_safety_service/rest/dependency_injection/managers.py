from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import sessionmaker

from worker_safety_service.dal.activities import ActivityManager
from worker_safety_service.dal.activity_work_type_settings import (
    ActivityWorkTypeSettingsManager,
)
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.crew_leader_manager import CrewLeaderManager
from worker_safety_service.dal.daily_reports import DailyReportManager
from worker_safety_service.dal.data_source import DataSourceManager
from worker_safety_service.dal.department_manager import DepartmentManager
from worker_safety_service.dal.energy_based_observations import (
    EnergyBasedObservationManager,
)
from worker_safety_service.dal.feature_flag import FeatureFlagManager
from worker_safety_service.dal.first_aid_aed_locations import (
    FirstAIDAEDLocationsManager,
)
from worker_safety_service.dal.forms import FormsManager
from worker_safety_service.dal.incident_severity_list_manager import (
    IncidentSeverityManager,
)
from worker_safety_service.dal.incidents import IncidentsManager
from worker_safety_service.dal.insight_manager import InsightManager
from worker_safety_service.dal.jsb import JobSafetyBriefingManager
from worker_safety_service.dal.jsb_supervisors import JSBSupervisorsManager
from worker_safety_service.dal.library import LibraryManager
from worker_safety_service.dal.library_activity_groups import (
    LibraryActivityGroupManager,
)
from worker_safety_service.dal.library_controls import LibraryControlManager
from worker_safety_service.dal.library_hazards import LibraryHazardManager
from worker_safety_service.dal.library_site_conditions import (
    LibrarySiteConditionManager,
)
from worker_safety_service.dal.library_site_conditions_recommendations import (
    LibrarySiteConditionRecommendationManager,
)
from worker_safety_service.dal.library_tasks import LibraryTasksManager
from worker_safety_service.dal.library_tasks_recomendations import (
    LibraryTaskHazardRecommendationsManager,
)
from worker_safety_service.dal.location_clustering import LocationClustering
from worker_safety_service.dal.locations import LocationsManager
from worker_safety_service.dal.opco_manager import OpcoManager
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.site_conditions import SiteConditionManager
from worker_safety_service.dal.standard_operating_procedures import (
    StandardOperatingProcedureManager,
)
from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.tenant import TenantManager
from worker_safety_service.dal.tenant_settings.tenant_library_control_settings import (
    TenantLibraryControlSettingsManager,
)
from worker_safety_service.dal.tenant_settings.tenant_library_hazard_settings import (
    TenantLibraryHazardSettingsManager,
)
from worker_safety_service.dal.tenant_settings.tenant_library_site_condition_settings import (
    TenantLibrarySiteConditionSettingsManager,
)
from worker_safety_service.dal.tenant_settings.tenant_library_task_settings import (
    TenantLibraryTaskSettingsManager,
)
from worker_safety_service.dal.ui_config import UIConfigManager
from worker_safety_service.dal.user import UserManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.dal.work_types import WorkTypeManager
from worker_safety_service.dal.workos import WorkOSManager
from worker_safety_service.models.utils import AsyncSession, get_sessionmaker
from worker_safety_service.rest.dependency_injection.session import (
    with_autocommit_session,
)

SessionDep = Annotated[AsyncSession, Depends(with_autocommit_session)]


def get_tenant_manager(session: SessionDep) -> TenantManager:
    return TenantManager(session=session)


def get_configurations_manager(session: SessionDep) -> ConfigurationsManager:
    return ConfigurationsManager(session=session)


def get_contractor_manager(session: SessionDep) -> ContractorsManager:
    return ContractorsManager(session=session)


def get_supervisors_manager(session: SessionDep) -> SupervisorsManager:
    return SupervisorsManager(session=session)


def get_standard_operating_procedure_manager(
    session: SessionDep,
) -> StandardOperatingProcedureManager:
    return StandardOperatingProcedureManager(session=session)


def get_work_types_manager(session: SessionDep) -> WorkTypeManager:
    return WorkTypeManager(session=session)


def get_department_manager(session: SessionDep) -> DepartmentManager:
    return DepartmentManager(session=session)


def get_incidents_manager(
    session: SessionDep,
    contractor_manager: ContractorsManager = Depends(get_contractor_manager),
    supervisors_manager: SupervisorsManager = Depends(get_supervisors_manager),
    work_type_manager: WorkTypeManager = Depends(get_work_types_manager),
) -> IncidentsManager:
    return IncidentsManager(
        session=session,
        contractor_manager=contractor_manager,
        supervisors_manager=supervisors_manager,
        work_type_manager=work_type_manager,
    )


def get_data_source_manager(session: SessionDep) -> DataSourceManager:
    return DataSourceManager(session=session)


def get_library_manager(session: SessionDep) -> LibraryManager:
    return LibraryManager(session=session)


def get_opco_manager(session: SessionDep) -> OpcoManager:
    return OpcoManager(session=session)


def get_ebo_manager(session: SessionDep) -> EnergyBasedObservationManager:
    return EnergyBasedObservationManager(session=session)


def get_library_tasks_manager(
    session: SessionDep,
) -> LibraryTasksManager:
    return LibraryTasksManager(session=session)


def get_library_tasks_hazard_recommendations_manager(
    session: SessionDep,
) -> LibraryTaskHazardRecommendationsManager:
    return LibraryTaskHazardRecommendationsManager(session=session)


def get_library_hazard_manager(session: SessionDep) -> LibraryHazardManager:
    return LibraryHazardManager(session=session)


def get_library_control_manager(
    session: SessionDep,
) -> LibraryControlManager:
    return LibraryControlManager(session=session)


def get_library_site_condition_manager(
    session: SessionDep,
) -> LibrarySiteConditionManager:
    return LibrarySiteConditionManager(session=session)


def get_library_site_condition_recommendation_manager(
    session: SessionDep,
) -> LibrarySiteConditionRecommendationManager:
    return LibrarySiteConditionRecommendationManager(session=session)


def get_location_clustering(session: SessionDep) -> LocationClustering:
    return LocationClustering(session=session)


def get_forms_manager(session: SessionDep) -> FormsManager:
    return FormsManager(session=session)


def get_job_safety_briefings_manager(
    session: SessionDep,
) -> JobSafetyBriefingManager:
    return JobSafetyBriefingManager(session=session)


def get_risk_model_metrics_manager(
    session_factory: sessionmaker = Depends(get_sessionmaker),
    configurations_manager: ConfigurationsManager = Depends(get_configurations_manager),
) -> RiskModelMetricsManager:
    return RiskModelMetricsManager(
        session_factory=session_factory, configurations_manager=configurations_manager
    )


def get_site_condition_manager(
    session: SessionDep,
    library_manager: LibraryManager = Depends(get_library_manager),
    library_site_condition_manager: LibrarySiteConditionManager = Depends(
        get_library_site_condition_manager
    ),
) -> SiteConditionManager:
    return SiteConditionManager(
        session=session,
        library_manager=library_manager,
        library_site_condition_manager=library_site_condition_manager,
    )


def get_task_manager(
    session: SessionDep,
    library_manager: LibraryManager = Depends(get_library_manager),
) -> TaskManager:
    return TaskManager(session=session, library_manager=library_manager)


def get_user_manager(session: SessionDep) -> UserManager:
    return UserManager(session=session)


def get_incident_severity_list_manager(session: SessionDep) -> IncidentSeverityManager:
    return IncidentSeverityManager(session=session)


def get_activity_manager(
    session: SessionDep,
    task_manager: TaskManager = Depends(get_task_manager),
    configurations_manager: ConfigurationsManager = Depends(get_configurations_manager),
) -> ActivityManager:
    return ActivityManager(
        session=session,
        task_manager=task_manager,
        configurations_manager=configurations_manager,
    )


def get_daily_report_manager(
    session: SessionDep,
    task_manager: TaskManager = Depends(get_task_manager),
    site_condition_manager: SiteConditionManager = Depends(get_site_condition_manager),
) -> DailyReportManager:
    return DailyReportManager(
        session=session,
        task_manager=task_manager,
        site_condition_manager=site_condition_manager,
    )


def get_locations_manager(
    session: SessionDep,
    activity_manager: ActivityManager = Depends(get_activity_manager),
    daily_report_manager: DailyReportManager = Depends(get_daily_report_manager),
    risk_model_metrics_manager: RiskModelMetricsManager = Depends(
        get_risk_model_metrics_manager
    ),
    site_condition_manager: SiteConditionManager = Depends(get_site_condition_manager),
    task_manager: TaskManager = Depends(get_task_manager),
    location_clustering: LocationClustering = Depends(get_location_clustering),
) -> LocationsManager:
    return LocationsManager(
        session=session,
        activity_manager=activity_manager,
        daily_report_manager=daily_report_manager,
        risk_model_metrics_manager=risk_model_metrics_manager,
        site_condition_manager=site_condition_manager,
        task_manager=task_manager,
        location_clustering=location_clustering,
    )


def get_work_package_manager(
    session: SessionDep,
    risk_model_metrics_manager: RiskModelMetricsManager = Depends(
        get_risk_model_metrics_manager
    ),
    contractor_manager: ContractorsManager = Depends(get_contractor_manager),
    library_manager: LibraryManager = Depends(get_library_manager),
    locations_manager: LocationsManager = Depends(get_locations_manager),
    task_manager: TaskManager = Depends(get_task_manager),
    site_condition_manager: SiteConditionManager = Depends(get_site_condition_manager),
    user_manager: UserManager = Depends(get_user_manager),
    daily_report_manager: DailyReportManager = Depends(get_daily_report_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager),
    configurations_manager: ConfigurationsManager = Depends(get_configurations_manager),
    location_clustering: LocationClustering = Depends(get_location_clustering),
    work_type_manager: WorkTypeManager = Depends(get_work_types_manager),
) -> WorkPackageManager:
    return WorkPackageManager(
        session=session,
        risk_model_metrics_manager=risk_model_metrics_manager,
        contractor_manager=contractor_manager,
        library_manager=library_manager,
        locations_manager=locations_manager,
        task_manager=task_manager,
        site_condition_manager=site_condition_manager,
        user_manager=user_manager,
        daily_report_manager=daily_report_manager,
        activity_manager=activity_manager,
        configurations_manager=configurations_manager,
        location_clustering=location_clustering,
        work_type_manager=work_type_manager,
    )


def get_library_activity_group_manager(
    session: SessionDep,
) -> LibraryActivityGroupManager:
    return LibraryActivityGroupManager(session=session)


def get_insight_manager(session: SessionDep) -> InsightManager:
    return InsightManager(session=session)


def get_feature_flag_manager(session: SessionDep) -> FeatureFlagManager:
    return FeatureFlagManager(session=session)


def get_crew_leader_manager(session: SessionDep) -> CrewLeaderManager:
    return CrewLeaderManager(session=session)


def get_first_aid_aed_locations_manager(
    session: SessionDep,
) -> FirstAIDAEDLocationsManager:
    return FirstAIDAEDLocationsManager(session=session)


def get_ui_config_manager(
    session: SessionDep,
) -> UIConfigManager:
    return UIConfigManager(session=session)


def get_tenant_library_task_settings_manager(
    session: SessionDep,
) -> TenantLibraryTaskSettingsManager:
    return TenantLibraryTaskSettingsManager(session=session)


def get_tenant_library_hazard_settings_manager(
    session: SessionDep,
) -> TenantLibraryHazardSettingsManager:
    return TenantLibraryHazardSettingsManager(session=session)


def get_tenant_library_control_settings_manager(
    session: SessionDep,
) -> TenantLibraryControlSettingsManager:
    return TenantLibraryControlSettingsManager(session=session)


def get_tenant_library_site_condition_settings_manager(
    session: SessionDep,
) -> TenantLibrarySiteConditionSettingsManager:
    return TenantLibrarySiteConditionSettingsManager(session=session)


def get_workos_manager(
    session: SessionDep,
) -> WorkOSManager:
    return WorkOSManager(session=session)


def get_jsb_supervisor_manager(
    session: SessionDep,
) -> JSBSupervisorsManager:
    return JSBSupervisorsManager(session=session)


async def get_activity_work_type_settings_manager(
    session: SessionDep,
    work_type_manager: WorkTypeManager = Depends(get_work_types_manager),
) -> ActivityWorkTypeSettingsManager:
    """
    Get an instance of ActivityWorkTypeSettingsManager.
    """
    manager = ActivityWorkTypeSettingsManager(session)
    manager.set_work_type_manager(work_type_manager)
    return manager
