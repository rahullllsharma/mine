from contextlib import asynccontextmanager
from enum import Enum
from typing import AsyncGenerator

from dependency_injector import containers, providers
from redis.asyncio import Redis
from sqlalchemy.orm import sessionmaker

import worker_safety_service.risk_model.riskmodelreactor as riskmodel_module
from worker_safety_service import redis_client
from worker_safety_service.dal.activities import ActivityManager
from worker_safety_service.dal.base_relationship_manager import BaseRelationshipManager
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.daily_reports import DailyReportManager
from worker_safety_service.dal.incidents import IncidentsManager
from worker_safety_service.dal.library import LibraryManager
from worker_safety_service.dal.library_site_conditions import (
    LibrarySiteConditionManager,
)
from worker_safety_service.dal.library_tasks import LibraryTasksManager
from worker_safety_service.dal.locations import LocationsManager
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.site_conditions import SiteConditionManager
from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.tenant import TenantManager
from worker_safety_service.dal.user import UserManager
from worker_safety_service.dal.work_packages import (
    LocationClustering,
    WorkPackageManager,
)
from worker_safety_service.dal.work_types import WorkTypeManager
from worker_safety_service.risk_model.container.dal_manager_proxy import DALManagerProxy
from worker_safety_service.risk_model.riskmodelreactor_redis import (
    RiskModelReactorRedisImpl,
)
from worker_safety_service.site_conditions import SiteConditionsEvaluator


async def create_redis_client() -> AsyncGenerator[Redis, None]:
    redis: Redis = redis_client.create_redis_client()
    yield redis
    await redis.close()


class Mode(Enum):
    DAEMON = "daemon"
    LOCAL = "local"
    ISOLATED = "isolated"


class RiskModelContainer(containers.DeclarativeContainer):
    session_factory = providers.Dependency(instance_of=sessionmaker)
    mode = providers.Dependency(instance_of=str)

    # TODO: Probably move initializing function to a separate package.
    redis_database = providers.Resource(create_redis_client)

    configurations_manager = providers.Singleton(
        DALManagerProxy,
        session_factory=session_factory,
        wrapped=providers.Factory(ConfigurationsManager, session=None),
    )
    risk_model_metrics_manager = providers.Singleton(
        RiskModelMetricsManager,
        session_factory=session_factory,
        configurations_manager=configurations_manager,
    )

    library_manager = providers.Singleton(
        DALManagerProxy,
        session_factory=session_factory,
        wrapped=providers.Factory(LibraryManager, session=None),
    )

    library_site_condition_manager = providers.Singleton(
        DALManagerProxy,
        session_factory=session_factory,
        wrapped=providers.Factory(LibrarySiteConditionManager, session=None),
    )

    contractors_manager = providers.Singleton(
        DALManagerProxy,
        session_factory=session_factory,
        wrapped=providers.Factory(ContractorsManager, session=None),
    )

    supervisors_manager = providers.Singleton(
        DALManagerProxy,
        session_factory=session_factory,
        wrapped=providers.Factory(SupervisorsManager, session=None),
    )

    base_relationship_manager = providers.Factory(
        DALManagerProxy,
        session_factory=session_factory,
        wrapped=providers.Factory(BaseRelationshipManager, session=None),
    )

    work_type_manager = providers.Singleton(
        DALManagerProxy,
        session_factory=session_factory,
        wrapped=providers.Factory(WorkTypeManager, session=None),
    )

    library_tasks_manager = providers.Singleton(
        DALManagerProxy,
        session_factory=session_factory,
        wrapped=providers.Factory(LibraryTasksManager, session=None),
    )

    task_manager = providers.Singleton(
        DALManagerProxy,
        session_factory=session_factory,
        wrapped=providers.Factory(
            TaskManager, session=None, library_manager=library_manager
        ),
    )

    activity_manager = providers.Singleton(
        DALManagerProxy,
        session_factory=session_factory,
        wrapped=providers.Factory(
            ActivityManager,
            session=None,
            task_manager=task_manager,
            configurations_manager=configurations_manager,
        ),
    )

    site_conditions_manager = providers.Singleton(
        DALManagerProxy,
        session_factory=session_factory,
        wrapped=providers.Factory(
            SiteConditionManager,
            session=None,
            library_manager=library_manager,
            library_site_condition_manager=library_site_condition_manager,
        ),
    )

    user_manager = providers.Singleton(
        DALManagerProxy,
        session_factory=session_factory,
        wrapped=providers.Factory(UserManager, session=None),
    )

    daily_report_manager = providers.Singleton(
        DALManagerProxy,
        session_factory=session_factory,
        wrapped=providers.Factory(
            DailyReportManager,
            session=None,
            task_manager=task_manager,
            site_condition_manager=site_conditions_manager,
        ),
    )

    location_clustering = providers.Singleton(
        DALManagerProxy,
        session_factory=session_factory,
        wrapped=providers.Factory(LocationClustering, session=None),
    )

    locations_manager = providers.Singleton(
        DALManagerProxy,
        session_factory=session_factory,
        wrapped=providers.Factory(
            LocationsManager,
            session=None,
            activity_manager=activity_manager,
            daily_report_manager=daily_report_manager,
            risk_model_metrics_manager=risk_model_metrics_manager,
            site_condition_manager=site_conditions_manager,
            task_manager=task_manager,
            location_clustering=location_clustering,
        ),
    )

    work_package_manager = providers.Singleton(
        DALManagerProxy,
        session_factory=session_factory,
        wrapped=providers.Factory(
            WorkPackageManager,
            session=None,
            risk_model_metrics_manager=risk_model_metrics_manager,
            contractor_manager=contractors_manager,
            library_manager=library_manager,
            locations_manager=locations_manager,
            task_manager=task_manager,
            site_condition_manager=site_conditions_manager,
            user_manager=user_manager,
            daily_report_manager=daily_report_manager,
            activity_manager=activity_manager,
            configurations_manager=configurations_manager,
            location_clustering=location_clustering,
            work_type_manager=work_type_manager,
        ),
    )

    incidents_manager = providers.Singleton(
        DALManagerProxy,
        session_factory=session_factory,
        wrapped=providers.Factory(
            IncidentsManager,
            session=None,
            contractor_manager=contractors_manager,
            supervisors_manager=supervisors_manager,
            work_type_manager=work_type_manager,
        ),
    )

    tenant_manager = providers.Singleton(
        DALManagerProxy,
        session_factory=session_factory,
        wrapped=providers.Factory(TenantManager, session=None),
    )

    site_conditions_evaluator = providers.Singleton(
        SiteConditionsEvaluator,
        work_package_manager=work_package_manager,
        site_conditions_manager=site_conditions_manager,
        task_manager=task_manager,
        library_site_condition_manager=library_site_condition_manager,
    )

    risk_model_reactor = providers.Selector(
        mode,
        daemon=providers.Singleton(
            RiskModelReactorRedisImpl, redis_client=redis_database
        ),
        local=providers.Singleton(
            RiskModelReactorRedisImpl, redis_client=redis_database
        ),
        isolated=providers.Singleton(riskmodel_module.RiskModelReactorLocalImpl),
    )

    risk_model_reactor_worker = providers.Selector(
        mode,
        daemon=providers.Singleton(
            riskmodel_module.RiskModelReactorWorkerDaemon, reaktor=risk_model_reactor
        ),
        local=providers.Singleton(
            riskmodel_module.RiskModelReactorWorkerBlocking, reaktor=risk_model_reactor
        ),
        isolated=providers.Singleton(
            riskmodel_module.RiskModelReactorWorkerBlocking, reaktor=risk_model_reactor
        ),
    )


def create_and_wire(
    session_factory: sessionmaker,
    mode: Mode = Mode.LOCAL,
) -> RiskModelContainer:
    container = RiskModelContainer(
        session_factory=providers.Object(session_factory),
        mode=providers.Object(mode.value),
    )
    container.check_dependencies()
    container.wire(modules=[riskmodel_module])

    # Enable async mode despite the injected type.
    container.risk_model_reactor.enable_async_mode()
    container.risk_model_reactor_worker.enable_async_mode()

    return container


@asynccontextmanager
async def create_and_wire_with_context(
    session_factory: sessionmaker,
    mode: Mode = Mode.LOCAL,
) -> AsyncGenerator[RiskModelContainer, None]:
    container = create_and_wire(session_factory, mode)

    try:
        yield container
    finally:
        shutdown_hook = container.shutdown_resources()
        if shutdown_hook is not None:
            await shutdown_hook
