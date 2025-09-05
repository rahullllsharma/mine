from functools import cache
from typing import Dict

from fastapi import Depends
from sqlalchemy.orm import sessionmaker
from starlette.background import BackgroundTasks
from strawberry.fastapi import BaseContext
from strawberry.types import Info as BaseInfo
from structlog.contextvars import bind_contextvars

from worker_safety_service import get_logger
from worker_safety_service.background_tasks import (
    BackgroundNotificationsUpdate,
    BackgroundRiskModelReactor,
    BackgroundSiteConditionEvaluator,
)
from worker_safety_service.dal.activities import ActivityManager
from worker_safety_service.dal.activity_work_type_settings import (
    ActivityWorkTypeSettingsManager,
)
from worker_safety_service.dal.audit_events import AuditEventManager
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.crew import CrewManager
from worker_safety_service.dal.crew_leader_manager import CrewLeaderManager
from worker_safety_service.dal.daily_reports import DailyReportManager
from worker_safety_service.dal.department_manager import DepartmentManager
from worker_safety_service.dal.device_details import DeviceDetailsManager
from worker_safety_service.dal.energy_based_observations import (
    EnergyBasedObservationManager,
)
from worker_safety_service.dal.file_storage import FileStorageManager
from worker_safety_service.dal.first_aid_aed_locations import (
    FirstAIDAEDLocationsManager,
)
from worker_safety_service.dal.forms import FormsManager
from worker_safety_service.dal.incidents import IncidentsManager
from worker_safety_service.dal.ingest import IngestManager
from worker_safety_service.dal.insight_manager import InsightManager
from worker_safety_service.dal.insights import InsightsManager
from worker_safety_service.dal.jsb import JobSafetyBriefingManager
from worker_safety_service.dal.jsb_supervisors import JSBSupervisorsManager
from worker_safety_service.dal.library import LibraryManager
from worker_safety_service.dal.library_controls import LibraryControlManager
from worker_safety_service.dal.library_hazards import LibraryHazardManager
from worker_safety_service.dal.library_site_conditions import (
    LibrarySiteConditionManager,
)
from worker_safety_service.dal.library_tasks import LibraryTasksManager
from worker_safety_service.dal.location_clustering import LocationClustering
from worker_safety_service.dal.locations import LocationsManager
from worker_safety_service.dal.medical_facilities import MedicalFacilitiesManager
from worker_safety_service.dal.natgrid_jsb import NatGridJobSafetyBriefingManager
from worker_safety_service.dal.notifications import NotificationsManager
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
from worker_safety_service.dal.user_preference import UserPreferenceManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.dal.work_types import WorkTypeManager
from worker_safety_service.gcloud import FileStorage, get_file_storage
from worker_safety_service.gcloud.fcm import FirebaseMessagingService
from worker_safety_service.graphql.data_loaders.activities import TenantActivityLoader
from worker_safety_service.graphql.data_loaders.audits import TenantAuditLoader
from worker_safety_service.graphql.data_loaders.configurations import (
    TenantConfigurationsLoader,
)
from worker_safety_service.graphql.data_loaders.contractors import (
    TenantContractorsLoader,
)
from worker_safety_service.graphql.data_loaders.crew import TenantCrewLoader
from worker_safety_service.graphql.data_loaders.crew_leader import CrewLeaderLoader
from worker_safety_service.graphql.data_loaders.daily_reports import (
    TenantDailyReportsLoader,
)
from worker_safety_service.graphql.data_loaders.departments import DepartmentLoader
from worker_safety_service.graphql.data_loaders.energy_based_observation import (
    TenantEnergyBasedObservationLoader,
)
from worker_safety_service.graphql.data_loaders.files import TenantFileLoader
from worker_safety_service.graphql.data_loaders.first_aid_aed_locations import (
    FirstAIDAEDLocationsLoader,
)
from worker_safety_service.graphql.data_loaders.forms import TenantFormLoader
from worker_safety_service.graphql.data_loaders.incidents import IncidentsLoader
from worker_safety_service.graphql.data_loaders.ingest import TenantIngestLoader
from worker_safety_service.graphql.data_loaders.insight import InsightLoader
from worker_safety_service.graphql.data_loaders.insights import TenantInsightsLoader
from worker_safety_service.graphql.data_loaders.job_safety_briefings import (
    TenantJobSafetyBriefingLoader,
)
from worker_safety_service.graphql.data_loaders.jsb_supervisors import (
    JSBSupervisorLoader,
)
from worker_safety_service.graphql.data_loaders.library import LibraryLoader
from worker_safety_service.graphql.data_loaders.library_controls import (
    LibraryControlsLoader,
)
from worker_safety_service.graphql.data_loaders.library_hazards import (
    LibraryHazardsLoader,
)
from worker_safety_service.graphql.data_loaders.library_site_conditions import (
    LibrarySiteConditionsLoader,
)
from worker_safety_service.graphql.data_loaders.library_tasks import LibraryTasksLoader
from worker_safety_service.graphql.data_loaders.medical_facilities import (
    MedicalFacilitiesLoader,
)
from worker_safety_service.graphql.data_loaders.natgrid_job_safety_briefings import (
    TenantNatGridJobSafetyBriefingLoader,
)
from worker_safety_service.graphql.data_loaders.opco import OpcoLoader
from worker_safety_service.graphql.data_loaders.project_locations import (
    TenantProjectLocationLoader,
)
from worker_safety_service.graphql.data_loaders.risk_model import TenantRiskModelLoader
from worker_safety_service.graphql.data_loaders.site_conditions import (
    TenantSiteConditionLoader,
)
from worker_safety_service.graphql.data_loaders.standard_operating_procedures import (
    StandardOperatingProceduresLoader,
)
from worker_safety_service.graphql.data_loaders.supervisors import (
    TenantSupervisorLoader,
)
from worker_safety_service.graphql.data_loaders.tasks import TenantTaskLoader
from worker_safety_service.graphql.data_loaders.tenant_settings.tenant_library_control_settings import (
    TenantLibraryControlSettingsLoader,
)
from worker_safety_service.graphql.data_loaders.tenant_settings.tenant_library_hazard_settings import (
    TenantLibraryHazardSettingsLoader,
)
from worker_safety_service.graphql.data_loaders.tenant_settings.tenant_library_site_condition_settings import (
    TenantLibrarySiteConditionSettingsLoader,
)
from worker_safety_service.graphql.data_loaders.tenant_settings.tenant_library_task_settings import (
    TenantLibraryTaskSettingsLoader,
)
from worker_safety_service.graphql.data_loaders.tenants import TenantLoader
from worker_safety_service.graphql.data_loaders.ui_config import UIConfigLoader
from worker_safety_service.graphql.data_loaders.user_preferences import (
    UserPreferenceLoader,
)
from worker_safety_service.graphql.data_loaders.users import TenantUsersLoader
from worker_safety_service.graphql.data_loaders.work_packages import (
    TenantWorkPackageLoader,
)
from worker_safety_service.graphql.data_loaders.work_type_settings import (
    ActivityWorkTypesSettingsLoader,
)
from worker_safety_service.graphql.data_loaders.work_types import WorkTypesLoader
from worker_safety_service.keycloak import get_auth_token, get_user
from worker_safety_service.models import AsyncSession, User, with_session
from worker_safety_service.models.utils import get_sessionmaker
from worker_safety_service.risk_model import riskmodel_container
from worker_safety_service.risk_model.riskmodel_container import RiskModelContainer
from worker_safety_service.risk_model.riskmodelreactor import RiskModelReactor
from worker_safety_service.site_conditions import SiteConditionsEvaluator

logger = get_logger(__name__)


@cache
def create_riskmodel_container() -> RiskModelContainer:
    return riskmodel_container.create_and_wire(get_sessionmaker())


# Initialising in the startup, to make sure notifications are not missed
def initialize_firebase_messaging() -> None:
    # TODO: This is a quick fix, Change the way of initialising it
    FirebaseMessagingService()


async def get_context(
    session: AsyncSession = Depends(with_session),
    user: User = Depends(get_user),
    file_storage: FileStorage = Depends(get_file_storage),
    riskmodel_container: RiskModelContainer = Depends(create_riskmodel_container),
    auth_token: str = Depends(get_auth_token),
) -> "Context":
    # User for log
    bind_contextvars(user_id=str(user.id), tenant_id=str(user.tenant_id))
    session_maker = riskmodel_container.session_factory()
    risk_model_reactor = await riskmodel_container.risk_model_reactor()
    return Context(
        session, session_maker, user, file_storage, risk_model_reactor, auth_token
    )


class Context(BaseContext):
    def __init__(
        self,
        session: AsyncSession,
        session_maker: sessionmaker,
        user: User,
        file_storage: FileStorage,
        risk_model_reactor: RiskModelReactor,
        token: str,
    ) -> None:
        super().__init__()
        # Managers (should not be added to context)
        audit_manager = AuditEventManager(session)
        configurations_manager = ConfigurationsManager(session)
        contractor_manager = ContractorsManager(session)
        crew_manager = CrewManager(session)
        library_manager = LibraryManager(session)
        library_tasks_manager = LibraryTasksManager(session)
        library_hazards_manager = LibraryHazardManager(session)
        library_controls_manager = LibraryControlManager(session)
        library_site_conditions_manager = LibrarySiteConditionManager(session)
        supervisors_manager = SupervisorsManager(session)
        tenant_manager = TenantManager(session)
        user_manager = UserManager(session)
        work_type_manager = WorkTypeManager(session)
        activity_work_type_settings_manager = ActivityWorkTypeSettingsManager(session)

        file_manager = FileStorageManager(session, file_storage)
        forms_manager = FormsManager(session)
        jsb_manager = JobSafetyBriefingManager(session)
        natgrid_jsb_manager = NatGridJobSafetyBriefingManager(session)
        ebo_manager = EnergyBasedObservationManager(session)
        task_manager = TaskManager(session, library_manager)
        activity_manager = ActivityManager(
            session, task_manager, configurations_manager
        )
        site_condition_manager = SiteConditionManager(
            session, library_manager, library_site_conditions_manager
        )
        medical_facilities_manager = MedicalFacilitiesManager(session)
        risk_model_metrics_manager = RiskModelMetricsManager(
            session_maker, configurations_manager
        )
        insights_manager = InsightsManager(
            session, task_manager, site_condition_manager, risk_model_metrics_manager
        )
        incidents_manager = IncidentsManager(
            session,
            contractor_manager,
            supervisors_manager,
            work_type_manager,
        )
        daily_report_manager = DailyReportManager(
            session, task_manager, site_condition_manager
        )
        department_manager = DepartmentManager(session)
        location_clustering = LocationClustering(session)
        locations_manager = LocationsManager(
            session,
            activity_manager,
            daily_report_manager,
            risk_model_metrics_manager,
            site_condition_manager,
            task_manager,
            location_clustering,
        )
        work_package_manager = WorkPackageManager(
            session,
            risk_model_metrics_manager,
            contractor_manager,
            library_manager,
            locations_manager,
            task_manager,
            site_condition_manager,
            user_manager,
            daily_report_manager,
            activity_manager,
            configurations_manager,
            location_clustering,
            work_type_manager,
        )
        ingest_manager = IngestManager(
            session,
            work_package_manager,
            work_type_manager,
            activity_manager,
            library_manager,
            library_tasks_manager,
            incidents_manager,
            risk_model_reactor,
        )
        device_details_manager = DeviceDetailsManager(session)
        notifications_manager = NotificationsManager(session, device_details_manager)
        insight_manager = InsightManager(session)
        opco_manager = OpcoManager(session)
        crew_leader_manager = CrewLeaderManager(session)
        jsb_supervisors_manager = JSBSupervisorsManager(session)
        first_aid_aed_location_manager = FirstAIDAEDLocationsManager(session)
        ui_config_manager = UIConfigManager(session)
        user_preference_manager = UserPreferenceManager(session)
        standard_operating_procedure_manager = StandardOperatingProcedureManager(
            session
        )
        tenant_library_task_settings_manager = TenantLibraryTaskSettingsManager(session)
        tenant_library_hazard_settings_manager = TenantLibraryHazardSettingsManager(
            session
        )
        tenant_library_control_settings_manager = TenantLibraryControlSettingsManager(
            session
        )
        tenant_library_site_condition_settings_manager = (
            TenantLibrarySiteConditionSettingsManager(session)
        )

        self.user = user
        self.tenant_id = self.user.tenant_id
        self.token = token
        self.params: Dict = {}  # NOTE: Can be used to pass parameters

        # Background reactor
        background_reactor = BackgroundRiskModelReactor(
            self.get_background_tasks, risk_model_reactor
        )
        self.projects = TenantWorkPackageLoader(
            work_package_manager,
            background_reactor,
            locations_manager,
            self.tenant_id,
        )
        self.insights = TenantInsightsLoader(insights_manager, self.tenant_id)
        self.tenants = TenantLoader(tenant_manager)
        self.activities = TenantActivityLoader(
            activity_manager,
            task_manager,
            library_manager,
            background_reactor,
            locations_manager,
            configurations_manager,
            self.tenant_id,
        )
        self.project_locations = TenantProjectLocationLoader(
            locations_manager,
            work_package_manager,
            activity_manager,
            task_manager,
            site_condition_manager,
            daily_report_manager,
            library_manager,
            background_reactor,
            self.activities,
            self.projects,
            jsb_manager,
            self.tenant_id,
        )
        self.tasks = TenantTaskLoader(task_manager, background_reactor, self.tenant_id)
        self.site_conditions = TenantSiteConditionLoader(
            site_condition_manager,
            risk_model_reactor,
            self.tenant_id,
        )
        site_condition_evaluator = SiteConditionsEvaluator(
            work_package_manager,
            site_condition_manager,
            task_manager,
            library_site_conditions_manager,
        )
        self.background_site_condition_evaluator = BackgroundSiteConditionEvaluator(
            self.get_background_tasks, site_condition_evaluator
        )
        self.background_notifications_update = BackgroundNotificationsUpdate(
            self.get_background_tasks, notifications_manager
        )
        self.incidents = IncidentsLoader(
            incidents_manager, background_reactor, self.tenant_id
        )
        self.library = LibraryLoader(
            library_manager, library_tasks_manager, work_type_manager, self.tenant_id
        )
        self.library_tasks = LibraryTasksLoader(
            library_tasks_manager, risk_model_reactor, self.tenant_id
        )
        self.library_controls = LibraryControlsLoader(
            library_controls_manager, self.tenant_id
        )
        self.library_hazards = LibraryHazardsLoader(
            library_hazards_manager, self.tenant_id
        )
        self.library_site_conditions = LibrarySiteConditionsLoader(
            library_site_conditions_manager, self.tenant_id
        )
        self.daily_reports = TenantDailyReportsLoader(
            daily_report_manager, self.tenant_id
        )
        self.departments = DepartmentLoader(department_manager)
        self.risk_model = TenantRiskModelLoader(
            risk_model_metrics_manager, self.tenant_id
        )
        self.users = TenantUsersLoader(user_manager, self.tenant_id)
        self.supervisors = TenantSupervisorLoader(supervisors_manager, self.tenant_id)
        self.forms = TenantFormLoader(forms_manager, self.tenant_id)
        self.job_safety_briefings = TenantJobSafetyBriefingLoader(
            manager=jsb_manager,
            tenant_id=self.tenant_id,
        )
        self.natgrid_job_safety_briefings = TenantNatGridJobSafetyBriefingLoader(
            manager=natgrid_jsb_manager,
            tenant_id=self.tenant_id,
        )
        self.medical_facilities = MedicalFacilitiesLoader(medical_facilities_manager)
        self.opcos = OpcoLoader(opco_manager, self.tenant_id)
        self.files = TenantFileLoader(file_manager, self.tenant_id)
        self.contractors = TenantContractorsLoader(contractor_manager, self.tenant_id)
        self.audit = TenantAuditLoader(audit_manager, self.tenant_id)
        self.ingest = TenantIngestLoader(ingest_manager, self.tenant_id)

        self.risk_model_reactor = risk_model_reactor

        self.configurations_manager = configurations_manager
        self.configurations = TenantConfigurationsLoader(
            configurations_manager, self.tenant_id
        )
        self.crew = TenantCrewLoader(crew_manager, self.tenant_id)
        self.first_aid_aed_locations = FirstAIDAEDLocationsLoader(
            first_aid_aed_location_manager
        )
        self.ui_config_loader = UIConfigLoader(ui_config_manager, self.tenant_id)
        self.energy_based_observations = TenantEnergyBasedObservationLoader(
            ebo_manager, self.tenant_id
        )
        self.insight = InsightLoader(insight_manager, self.tenant_id)
        self.crew_leader = CrewLeaderLoader(crew_leader_manager, self.tenant_id)
        self.jsb_supervisors = JSBSupervisorLoader(jsb_supervisors_manager)
        self.user_preference = UserPreferenceLoader(user_preference_manager)
        self.standard_operating_procedures = StandardOperatingProceduresLoader(
            standard_operating_procedure_manager, self.tenant_id
        )
        self.work_types = WorkTypesLoader(work_type_manager, self.tenant_id)
        self.activity_work_type_settings = ActivityWorkTypesSettingsLoader(
            activity_work_type_settings_manager
        )
        self.tenant_library_task_settings = TenantLibraryTaskSettingsLoader(
            tenant_library_task_settings_manager, self.tenant_id
        )
        self.tenant_library_hazard_settings = TenantLibraryHazardSettingsLoader(
            tenant_library_hazard_settings_manager, self.tenant_id
        )
        self.tenant_library_control_settings = TenantLibraryControlSettingsLoader(
            tenant_library_control_settings_manager, self.tenant_id
        )
        self.tenant_library_site_condition_settings = (
            TenantLibrarySiteConditionSettingsLoader(
                tenant_library_site_condition_settings_manager, self.tenant_id
            )
        )

    def get_background_tasks(self) -> BackgroundTasks:
        # The background tasks are mutated during runtime, so we need a supplier to get the most accurate reference.
        if self.background_tasks is None:
            self.background_tasks = BackgroundTasks()

        return self.background_tasks


class Info(BaseInfo):
    context: Context
