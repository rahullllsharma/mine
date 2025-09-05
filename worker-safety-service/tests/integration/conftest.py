import asyncio
import logging
import os
import re
import uuid
from collections import defaultdict
from datetime import date, timedelta
from typing import Any, AsyncGenerator, Awaitable, Callable, Generator, Optional
from unittest.mock import MagicMock, patch

import pytest
from _pytest.fixtures import SubRequest
from dependency_injector import providers
from fastapi import status
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import select

from tests.db_data import (
    DB_REUSE_NAME,
    DBData,
    RecreateDB,
    create_template_db,
    remove_template_db,
)
from tests.factories import (
    ContractorFactory,
    ManagerUserFactory,
    SupervisorUserFactory,
    TenantFactory,
)
from tests.integration.utils.connection_state_validator import (
    validate_connection_state_on_teardown,
)
from worker_safety_service.config import settings
from worker_safety_service.dal.activities import ActivityManager
from worker_safety_service.dal.audit_events import AuditEventManager
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.crew import CrewManager
from worker_safety_service.dal.daily_reports import DailyReportManager
from worker_safety_service.dal.forms import FormsManager
from worker_safety_service.dal.incidents import IncidentsManager
from worker_safety_service.dal.ingestion.compatible_units import CompatibleUnitManager
from worker_safety_service.dal.ingestion.elements import ElementManager
from worker_safety_service.dal.jsb import JobSafetyBriefingManager
from worker_safety_service.dal.library import LibraryManager
from worker_safety_service.dal.library_site_conditions import (
    LibrarySiteConditionManager,
)
from worker_safety_service.dal.library_tasks import LibraryTasksManager
from worker_safety_service.dal.library_tasks_recomendations import (
    LibraryTaskHazardRecommendationsManager,
)
from worker_safety_service.dal.location_clustering import LocationClustering
from worker_safety_service.dal.locations import LocationsManager
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.site_conditions import SiteConditionManager
from worker_safety_service.dal.standard_operating_procedures import (
    StandardOperatingProcedureManager,
)
from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.tenant import TenantManager
from worker_safety_service.dal.user import UserManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.dal.work_types import WorkTypeManager
from worker_safety_service.gcloud import file_storage
from worker_safety_service.keycloak.utils import (
    OwnerType,
    RealmDetails,
    get_realm_details,
)
from worker_safety_service.models import (
    AsyncSession,
    LibraryAssetType,
    LibraryDivision,
    LibraryProjectType,
    LibraryRegion,
    Tenant,
    User,
    WorkPackage,
    WorkPackageCreate,
    WorkType,
)
from worker_safety_service.models.utils import create_engine, create_sessionmaker
from worker_safety_service.notifications.main import app as notif_app
from worker_safety_service.rest.main import app
from worker_safety_service.risk_model import riskmodel_container
from worker_safety_service.risk_model.riskmodel_container import RiskModelContainer
from worker_safety_service.risk_model.riskmodelreactor import RiskModelReactor
from worker_safety_service.site_conditions import SiteConditionsEvaluator
from worker_safety_service.urbint_logging import get_logger
from worker_safety_service.urbint_logging.fastapi_utils import (
    CTX_STATS_CALLS,
    CTX_STATS_TIME,
)

# If for some reason the get_session is not mocked, we make sure the test DB is used
assert settings.POSTGRES_DB.endswith("_test")

# parse the xdist worker number and set a per-worker REDIS_DB
worker_number = os.getenv("PYTEST_XDIST_WORKER", None)
if worker_number:
    digits = re.findall(r"\d+$", worker_number)
    if digits:
        redis_db = digits[0]
        settings.REDIS_DB = str(int(redis_db) + 1)

logger = get_logger(__name__)

MARKER = object()

# Register log stats, we need to have this here to work with factories
CTX_STATS_CALLS.set(defaultdict(int))
CTX_STATS_TIME.set(defaultdict(float))


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers", "mock_cli_session: mark test to mock db session on CLI"
    )
    config.addinivalue_line("markers", "fresh_db: Use a empty db")

    for logger_name in ["alembic.runtime.migration"]:
        logger = logging.getLogger(logger_name)
        logger.disabled = True

    asyncio.run(create_template_db())


def pytest_unconfigure(config: pytest.Config) -> None:
    asyncio.run(remove_template_db())


@pytest.fixture(scope="module")
def event_loop() -> Generator:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
@pytest.fixture
async def db_dsn(request: SubRequest) -> AsyncGenerator[str, None]:
    if any(i.name == "fresh_db" for i in request.node.iter_markers()):
        async with RecreateDB() as db:
            yield db.dsn
    else:
        yield settings.build_db_dsn(db=DB_REUSE_NAME)


@pytest.fixture
async def engine(db_dsn: str) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_engine(db_dsn, poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest.fixture
def async_sessionmaker(engine: AsyncEngine) -> sessionmaker:
    return create_sessionmaker(engine)


TestClientFn = Callable[..., AsyncClient]


@pytest.fixture()
async def test_user(db_session: AsyncSession) -> User:
    user_id = uuid.UUID("bab6fc84-63c3-4fe6-b7a6-137e26189ad9")
    user = (await db_session.exec(select(User).filter_by(id=user_id))).first()
    if not user:
        tenant = await TenantFactory.default_tenant(db_session)
        user = User(
            id=user_id,
            tenant_id=tenant.id,
            first_name="Test",
            last_name="User",
            email="test@example.com",
            keycloak_id=uuid.UUID("6ef5a13a-2387-4e83-820c-856d21d9f9b6"),
            role="administrator",
        )
        db_session.add(user)
        await db_session.commit()

    return user


@pytest.fixture
def test_client_with_params(
    api_db_session: AsyncSession,
    test_user: User,
    riskmodel_container_tests: RiskModelContainer,
) -> TestClientFn:
    """
    A parameterized test_client.

    Supports a passed user object, which is ensured in the db and set as the
    get_user dependency_override. Defaults to some user.
    """

    def _client(user: Optional[User] = None) -> AsyncClient:
        test_client_user = user if user is not None else test_user

        async def with_session_override() -> AsyncGenerator[AsyncSession, None]:
            yield api_db_session

        def get_user_override() -> User:
            return test_client_user

        def get_token_override() -> str:
            return "test_token"

        from worker_safety_service.context import create_riskmodel_container
        from worker_safety_service.graphql.main import app
        from worker_safety_service.keycloak import get_auth_token, get_user
        from worker_safety_service.models import with_session

        client = AsyncClient(app=app, base_url="http://test")
        app.dependency_overrides[with_session] = with_session_override
        app.dependency_overrides[get_user] = get_user_override
        app.dependency_overrides[
            create_riskmodel_container
        ] = lambda: riskmodel_container_tests
        app.dependency_overrides[get_auth_token] = get_token_override
        return client

    return _client


@pytest.fixture
def test_client(test_client_with_params: TestClientFn) -> AsyncClient:
    """
    Supports usage of test_client with default params, to avoid refactoring
    all usage to `test_client()`.
    """
    return test_client_with_params()


@pytest.fixture
async def db_session(
    async_sessionmaker: sessionmaker,
) -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = async_sessionmaker()
    async with session as with_session:
        yield with_session


@pytest.fixture
async def db_session_no_expire(
    engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


@pytest.fixture
async def api_engine(db_dsn: str) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_engine(db_dsn, poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest.fixture
def api_sessionmaker(api_engine: AsyncEngine) -> sessionmaker:
    return create_sessionmaker(api_engine)


@pytest.fixture
async def api_db_session(
    api_sessionmaker: sessionmaker,
) -> AsyncGenerator[AsyncSession, None]:
    # For code use only, so we can have a different session for tests and api
    session: AsyncSession = api_sessionmaker()
    async with session as session_with_close:
        yield session_with_close


@pytest.fixture
async def project(db_session: AsyncSession) -> WorkPackage:
    library_region = (await db_session.exec(select(LibraryRegion))).first()
    assert library_region
    library_division = (await db_session.exec(select(LibraryDivision))).first()
    assert library_division
    library_project_type = (await db_session.exec(select(LibraryProjectType))).first()
    assert library_project_type
    work_type = (await db_session.exec(select(WorkType))).first()
    assert work_type
    library_asset_type = (await db_session.exec(select(LibraryAssetType))).first()
    assert library_asset_type

    manager_id = (await ManagerUserFactory.persist(db_session)).id
    supervisor_id = (await SupervisorUserFactory.persist(db_session)).id
    contractor_id = (await ContractorFactory.persist(db_session)).id
    project = WorkPackage.from_orm(
        WorkPackageCreate(
            name="fixture project",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=21),
            number="0",
            region_id=library_region.id,
            division_id=library_division.id,
            work_type_id=library_project_type.id,
            work_type_ids=[work_type.id],
            asset_type_id=library_asset_type.id,
            engineer_name="engineer_name",
            zip_code="12345",
            contract_reference="contract_reference",
            contract_name="contract_name",
            manager_id=manager_id,
            primary_assigned_user_id=supervisor_id,
            additional_assigned_users_ids=[],
            contractor_id=contractor_id,
            tenant_id=(await TenantFactory.default_tenant(db_session)).id,
        )
    )

    db_session.add(project)
    await db_session.commit()
    return project


ExecuteGQL = Callable[..., Awaitable[Any]]


@pytest.fixture
def execute_gql(test_client_with_params: TestClientFn) -> ExecuteGQL:
    async def _exec(
        operation_name: str = "TestQuery",  # default operation name
        query: str = "",
        variables: dict[str, Any] = dict(),
        raw: bool = False,
        user: User | None = None,
    ) -> Any:
        assert query

        client = test_client_with_params(user=user)

        post_data = {
            "operationName": operation_name,
            "query": query,
            "variables": jsonable_encoder(variables),
        }
        response = await client.post("/graphql", json=post_data)
        assert response.status_code == status.HTTP_200_OK
        if raw:
            return response

        data = response.json()
        if "errors" in data:
            for e in data["errors"]:
                logger.error(e["message"])
                raise Exception(e["message"])
            raise Exception("Response contains an error!")

        if "data" in data:
            return data["data"]

        raise Exception("Response missing 'data'!")

    return _exec


ExecuteRest = Callable[..., Awaitable[Any]]


@pytest.fixture
def execute_rest(test_client_with_params: TestClientFn) -> ExecuteRest:
    async def _exec(
        path: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        user: User | None = None,
        expected_status_code: int = status.HTTP_200_OK,
    ) -> Any:
        client = test_client_with_params(user=user)

        if data:
            response = await client.post(path, json=data, params=params)
        else:
            response = await client.get(path, params=params)

        assert response.status_code == expected_status_code
        return response

    return _exec


@pytest.fixture
def test_blob() -> Generator[str, None, None]:
    name = f"integration-tests/{uuid.uuid4()}"
    blob = file_storage.blob(name)
    blob.upload_from_string("this is for integration tests!")
    yield name
    blob.delete()


@pytest.mark.asyncio
@pytest.fixture()
async def riskmodel_container_tests(
    api_sessionmaker: sessionmaker,
) -> AsyncGenerator[RiskModelContainer, None]:
    async with riskmodel_container.create_and_wire_with_context(
        api_sessionmaker
    ) as rm_container:
        # Will override the riskmodel_reactor to a mock since we don't have an integration strategy at this point.
        with patch.multiple(RiskModelReactor, __abstractmethods__=set()):
            rm_container.risk_model_reactor.override(
                providers.Singleton(RiskModelReactor)
            )
            yield rm_container


# Some dal fixtures -- Could be in a separate file
@pytest.fixture
def risk_model_metrics_manager(
    async_sessionmaker: sessionmaker,
    configurations_manager: ConfigurationsManager,
) -> RiskModelMetricsManager:
    return RiskModelMetricsManager(async_sessionmaker, configurations_manager)


@pytest.fixture
def forms_manager(
    db_session: AsyncSession,
) -> FormsManager:
    return FormsManager(db_session)


@pytest.fixture
def job_safety_briefings_manager(
    db_session: AsyncSession,
) -> JobSafetyBriefingManager:
    return JobSafetyBriefingManager(db_session)


@pytest.fixture
def work_package_manager(
    db_session: AsyncSession,
    risk_model_metrics_manager: RiskModelMetricsManager,
    contractor_manager: ContractorsManager,
    locations_manager: LocationsManager,
    library_manager: LibraryManager,
    task_manager: TaskManager,
    site_condition_manager: SiteConditionManager,
    user_manager: UserManager,
    daily_report_manager: DailyReportManager,
    activity_manager: ActivityManager,
    configurations_manager: ConfigurationsManager,
    location_clustering: LocationClustering,
    work_type_manager: WorkTypeManager,
) -> WorkPackageManager:
    return WorkPackageManager(
        db_session,
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


@pytest.fixture
def locations_manager(
    db_session: AsyncSession,
    activity_manager: ActivityManager,
    daily_report_manager: DailyReportManager,
    risk_model_metrics_manager: RiskModelMetricsManager,
    site_condition_manager: SiteConditionManager,
    task_manager: TaskManager,
    location_clustering: LocationClustering,
) -> LocationsManager:
    return LocationsManager(
        db_session,
        activity_manager,
        daily_report_manager,
        risk_model_metrics_manager,
        site_condition_manager,
        task_manager,
        location_clustering,
    )


@pytest.fixture
def location_clustering(db_session: AsyncSession) -> LocationClustering:
    return LocationClustering(db_session)


@pytest.fixture
def daily_report_manager(
    db_session: AsyncSession,
    task_manager: TaskManager,
    site_condition_manager: SiteConditionManager,
) -> DailyReportManager:
    return DailyReportManager(db_session, task_manager, site_condition_manager)


@pytest.fixture
def audit_event_manager(db_session: AsyncSession) -> AuditEventManager:
    return AuditEventManager(db_session)


@pytest.fixture
def site_condition_manager(
    db_session: AsyncSession,
    library_manager: LibraryManager,
    library_site_condition_manager: LibrarySiteConditionManager,
) -> SiteConditionManager:
    return SiteConditionManager(
        db_session, library_manager, library_site_condition_manager
    )


@pytest.fixture
def user_manager(db_session: AsyncSession) -> UserManager:
    return UserManager(db_session)


@pytest.fixture
def tenant_manager(db_session: AsyncSession) -> TenantManager:
    return TenantManager(db_session)


@pytest.fixture
def activity_manager(
    db_session: AsyncSession,
    task_manager: TaskManager,
    configurations_manager: ConfigurationsManager,
) -> ActivityManager:
    return ActivityManager(db_session, task_manager, configurations_manager)


@pytest.fixture
def task_manager(
    db_session: AsyncSession, library_manager: LibraryManager
) -> TaskManager:
    return TaskManager(db_session, library_manager)


@pytest.fixture
def library_manager(db_session: AsyncSession) -> LibraryManager:
    return LibraryManager(db_session)


@pytest.fixture
@validate_connection_state_on_teardown
def library_tasks_manager(db_session: AsyncSession) -> LibraryTasksManager:
    return LibraryTasksManager(db_session)


@pytest.fixture
@validate_connection_state_on_teardown
def library_task_hazard_recommendations_manager(
    db_session: AsyncSession,
) -> LibraryTaskHazardRecommendationsManager:
    return LibraryTaskHazardRecommendationsManager(db_session)


@pytest.fixture
def library_site_condition_manager(
    db_session: AsyncSession,
) -> LibrarySiteConditionManager:
    return LibrarySiteConditionManager(db_session)


@pytest.fixture
def contractor_manager(db_session: AsyncSession) -> ContractorsManager:
    return ContractorsManager(db_session)


@pytest.fixture
def work_type_manager(db_session: AsyncSession) -> WorkTypeManager:
    return WorkTypeManager(db_session)


@pytest.fixture
def supervisors_manager(db_session: AsyncSession) -> SupervisorsManager:
    return SupervisorsManager(db_session)


@pytest.fixture
def crew_manager(db_session: AsyncSession) -> CrewManager:
    return CrewManager(db_session)


@pytest.fixture
def configurations_manager(
    db_session: AsyncSession,
) -> ConfigurationsManager:
    return ConfigurationsManager(db_session)


@pytest.fixture
def element_manager(
    db_session: AsyncSession,
) -> ElementManager:
    return ElementManager(db_session)


@pytest.fixture
def incidents_manager(
    db_session: AsyncSession,
    contractor_manager: ContractorsManager,
    supervisors_manager: SupervisorsManager,
    work_type_manager: WorkTypeManager,
) -> IncidentsManager:
    return IncidentsManager(
        db_session, contractor_manager, supervisors_manager, work_type_manager
    )


@pytest.fixture
def standard_operating_procedure_manager(
    db_session: AsyncSession,
) -> StandardOperatingProcedureManager:
    return StandardOperatingProcedureManager(db_session)


@pytest.fixture
def compatible_unit_manager(
    db_session: AsyncSession,
) -> CompatibleUnitManager:
    return CompatibleUnitManager(db_session)


@pytest.fixture
def evaluator(
    work_package_manager: WorkPackageManager,
    site_condition_manager: SiteConditionManager,
    task_manager: TaskManager,
    library_site_condition_manager: LibrarySiteConditionManager,
) -> SiteConditionsEvaluator:
    return SiteConditionsEvaluator(
        work_package_manager=work_package_manager,
        site_conditions_manager=site_condition_manager,
        task_manager=task_manager,
        library_site_condition_manager=library_site_condition_manager,
    )


@pytest.fixture(autouse=True)
def mock_cli_session(async_sessionmaker: sessionmaker) -> Generator[None, None, None]:
    with patch(
        "worker_safety_service.cli.utils.get_session", return_value=async_sessionmaker()
    ):
        with patch(
            "worker_safety_service.models.utils.get_sessionmaker",
            return_value=async_sessionmaker,
        ):
            with patch(
                "worker_safety_service.cli.risk_model.explain.get_sessionmaker",
                return_value=async_sessionmaker,
            ):
                yield


@pytest.fixture
def db_data(db_session: AsyncSession) -> DBData:
    return DBData(db_session)


@pytest.mark.asyncio
@pytest.fixture
async def tenant(db_session: AsyncSession) -> Tenant:
    return await TenantFactory.default_tenant(db_session)


@pytest.mark.asyncio
@pytest.fixture
async def tenant_id(tenant: Tenant) -> uuid.UUID:
    return tenant.id


@pytest.fixture
def rest_client(api_db_session: AsyncSession, tenant: uuid.UUID) -> TestClientFn:
    def _client(
        custom_tenant: Tenant | None = None,
        default_role: str | None = "administrator",
        owner_type: OwnerType = OwnerType.INTEGRATION,
        parsed_token: dict[str, Any] | None = None,
    ) -> AsyncClient:
        async def with_realm_override() -> RealmDetails:
            return RealmDetails(
                name="worker-safety-api",
                audience="api",
                owner_type=owner_type,
            )

        async def with_session_override() -> AsyncGenerator[AsyncSession, None]:
            yield api_db_session

        from worker_safety_service.keycloak import get_parsed_token, get_tenant
        from worker_safety_service.launch_darkly import get_launch_darkly_client
        from worker_safety_service.models import with_session
        from worker_safety_service.reports_auth import utils

        client = AsyncClient(app=app, base_url="http://test")
        app.dependency_overrides[get_realm_details] = with_realm_override
        app.dependency_overrides[get_tenant] = lambda: (
            custom_tenant if custom_tenant is not None else tenant
        )
        app.dependency_overrides[utils.get_tenant_id] = lambda: (
            custom_tenant.id if custom_tenant is not None else tenant
        )
        app.dependency_overrides[with_session] = with_session_override
        app.dependency_overrides[get_launch_darkly_client] = lambda: None

        default_parsed_token = {
            "resource_access": {"worker-safety-api": {"roles": [default_role]}}
        }
        app.dependency_overrides[get_parsed_token] = lambda: (
            parsed_token if parsed_token else default_parsed_token
        )

        return client

    return _client


@pytest.fixture
def rest_api_test_client(rest_client: TestClientFn) -> AsyncClient:
    """
    Supports usage of test_client with default params, to avoid refactoring
    all usage to `test_client()`.
    """
    return rest_client()


@pytest.fixture
def notif_rest_client(
    api_db_session: AsyncSession, tenant: uuid.UUID, test_user: User
) -> TestClientFn:
    def _client(
        roles: list[str] | None = None,
        user: User | None = None,
        owner_type: OwnerType = OwnerType.USER,
        parsed_token: dict[str, Any] | None = None,
    ) -> AsyncClient:
        async def with_realm_override() -> RealmDetails:
            return RealmDetails(
                name="asgard",
                audience="asgard",
                owner_type=owner_type,
            )

        async def with_session_override() -> AsyncGenerator[AsyncSession, None]:
            yield api_db_session

        test_client_user = user if user is not None else test_user

        def get_user_override() -> User:
            return test_client_user

        from worker_safety_service.keycloak import get_parsed_token, get_user
        from worker_safety_service.launch_darkly import get_launch_darkly_client
        from worker_safety_service.models import with_session

        client = AsyncClient(app=notif_app, base_url="http://test")
        notif_app.dependency_overrides[get_realm_details] = with_realm_override
        notif_app.dependency_overrides[get_user] = get_user_override
        notif_app.dependency_overrides[with_session] = with_session_override
        notif_app.dependency_overrides[get_launch_darkly_client] = lambda: None

        default_parsed_token = {
            "resource_access": {
                "worker-safety-asgard": {"roles": roles if roles else ["viewer"]}
            },
        }
        notif_app.dependency_overrides[get_parsed_token] = lambda: (
            parsed_token if parsed_token else default_parsed_token
        )

        return client

    return _client


@pytest.fixture
def mocked_file_storage() -> MagicMock:
    from worker_safety_service.gcloud import FileStorage, get_file_storage
    from worker_safety_service.rest.main import app

    _file_storage = MagicMock(spec=FileStorage)
    _file_storage._url.side_effect = (
        lambda file_id, expiration: f"https://storage.googleapis.com/{file_id}?signed=true"
    )
    app.dependency_overrides[get_file_storage] = lambda: _file_storage
    return _file_storage


@pytest.fixture
def mocked_cache() -> MagicMock:
    from worker_safety_service.gcloud.cache import Cache, get_cache_impl
    from worker_safety_service.rest.main import app

    _cache = MagicMock(spec=Cache)
    app.dependency_overrides[get_cache_impl] = lambda: _cache
    return _cache
