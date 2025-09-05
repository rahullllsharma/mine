import dataclasses
import functools
import uuid
from typing import Any, Callable, TypeAlias, TypeVar
from unittest.mock import patch

import pytest
from sqlmodel import col, select
from strawberry.dataloader import DataLoader

from tests.factories import (
    ActivityFactory,
    AuditEventFactory,
    ContractorFactory,
    CrewFactory,
    LocationFactory,
    ManagerUserFactory,
    SiteConditionControlFactory,
    SiteConditionFactory,
    SiteConditionHazardFactory,
    SupervisorUserFactory,
    TaskControlFactory,
    TaskFactory,
    TaskHazardFactory,
    TenantFactory,
    UserFactory,
    WorkPackageFactory,
)
from worker_safety_service.dal.activities import ActivityManager
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.crew import CrewManager
from worker_safety_service.dal.daily_reports import DailyReportManager
from worker_safety_service.dal.jsb import JobSafetyBriefingManager
from worker_safety_service.dal.library import LibraryManager
from worker_safety_service.dal.locations import LocationsManager
from worker_safety_service.dal.site_conditions import SiteConditionManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.tenant import TenantManager
from worker_safety_service.dal.user import UserManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.graphql.data_loaders.activities import TenantActivityLoader
from worker_safety_service.graphql.data_loaders.configurations import (
    TenantConfigurationsLoader,
)
from worker_safety_service.graphql.data_loaders.contractors import (
    TenantContractorsLoader,
)
from worker_safety_service.graphql.data_loaders.crew import TenantCrewLoader
from worker_safety_service.graphql.data_loaders.daily_reports import (
    TenantDailyReportsLoader,
)
from worker_safety_service.graphql.data_loaders.project_locations import (
    TenantProjectLocationLoader,
)
from worker_safety_service.graphql.data_loaders.site_conditions import (
    TenantSiteConditionLoader,
)
from worker_safety_service.graphql.data_loaders.tasks import TenantTaskLoader
from worker_safety_service.graphql.data_loaders.tenants import TenantLoader
from worker_safety_service.graphql.data_loaders.users import TenantUsersLoader
from worker_safety_service.graphql.data_loaders.work_packages import (
    TenantWorkPackageLoader,
)
from worker_safety_service.models import (
    Activity,
    AsyncSession,
    Contractor,
    Crew,
    LibraryControl,
    LibraryHazard,
    LibrarySiteCondition,
    LibraryTask,
    Location,
    SiteCondition,
    SiteConditionControl,
    SiteConditionHazard,
    Task,
    TaskControl,
    TaskHazard,
    Tenant,
    User,
)
from worker_safety_service.models.audit_events import AuditEvent
from worker_safety_service.risk_model.riskmodel_container import RiskModelContainer

T = TypeVar("T")
LoaderFactory: TypeAlias = Callable[[uuid.UUID], T]


class MockedSQLResult:
    def __init__(self, result: Any) -> None:
        self.__mocked_result = result

    def all(self) -> Any:
        return self.__mocked_result


async def assert_dataloader_filter_tenants(
    dataloader_factory: LoaderFactory[T],
    direct_method: str,
    loader_method: str,
    tests: list[tuple[uuid.UUID, list, list]],
    filters: dict[str, Any] | None = None,
) -> None:
    """Make sure dataloaders filter tenants"""
    # TODO: add verbose comments to these helper methods
    for tenant_id, filter_ids, expected_result in tests:
        await assert_dataloader_return_right_order(
            dataloader_factory,
            direct_method,
            loader_method,
            tenant_id,
            filter_ids,
            expected_result,
            filters=filters,
        )


async def assert_mocked_dataloader_return_right_order(
    session: AsyncSession,
    dataloader_factory: LoaderFactory[T],
    direct_method: str,
    loader_method: str,
    tenant_id: uuid.UUID,
    filter_ids: list[uuid.UUID],
    expected_result: list,
    filters: dict[str, Any] | None = None,
    db_mock_data: list | None = None,
) -> None:
    """Make sure order returned by dataloaders match request"""

    # Reserve db results so we can check if dataloader still keeps the order
    reversed_for_db = []
    for items in reversed(db_mock_data or expected_result):
        if isinstance(items, list):
            reversed_for_db.extend(items)
        else:
            reversed_for_db.append(items)

    with patch.object(session, "exec", return_value=MockedSQLResult(reversed_for_db)):
        await assert_dataloader_return_right_order(
            dataloader_factory,
            direct_method,
            loader_method,
            tenant_id,
            filter_ids,
            expected_result,
            filters=filters,
        )


async def assert_dataloader_return_right_order(
    dataloader_factory: LoaderFactory[T],
    direct_method: str,
    loader_method: str,
    tenant_id: uuid.UUID,
    filter_ids: list[uuid.UUID],
    expected_result: list,
    filters: dict[str, Any] | None = None,
) -> None:
    # Direct call
    method = getattr(dataloader_factory(tenant_id), direct_method)
    items = await method(filter_ids, **filters or {})

    if items is not None:
        for subitems in items:
            if subitems is not None:
                for item in subitems:
                    if isinstance(item, dict):
                        if "form_id" in item:
                            item["form_id"] = None
                    elif hasattr(item, "form_id"):
                        item.form_id = None

    assert items == expected_result

    # Dataloader for many
    dl_method = getattr(dataloader_factory(tenant_id), loader_method)
    if not isinstance(dl_method, DataLoader):
        dl_method = dl_method(**filters or {})
    else:
        assert not filters

    items = await dl_method.load_many(filter_ids)
    assert items == expected_result

    # Dataloader for one
    # This tests too if for some reason the query returns more than expected
    for location_id, expected_location_result in zip(filter_ids, expected_result):
        dl_method = getattr(dataloader_factory(tenant_id), loader_method)
        if not isinstance(dl_method, DataLoader):
            dl_method = dl_method(**filters or {})
        else:
            assert not filters

        items = await dl_method.load(location_id)
        assert items == expected_location_result


@dataclasses.dataclass
class ActivitiesInit:
    session: AsyncSession
    tenant_1: Tenant
    location_11: Location
    activity_11: Activity
    location_12: Location
    activity_12: Activity
    location_13: Location
    activity_13: Activity
    tenant_2: Tenant
    location_21: Location
    activity_21: Activity
    tenant_3: Tenant


@pytest.fixture
async def activities_init(db_session_no_expire: AsyncSession) -> ActivitiesInit:
    session = db_session_no_expire
    tenant_1, tenant_2, tenant_3 = await TenantFactory.persist_many(session, size=3)
    (
        (activity_11, _, location_11),
        (activity_12, _, location_12),
        (activity_13, _, location_13),
        (activity_21, _, location_21),
    ) = await ActivityFactory.batch_with_project_and_location(
        session,
        [
            {"project_kwargs": {"tenant_id": tenant_1.id}},
            {"project_kwargs": {"tenant_id": tenant_1.id}},
            {"project_kwargs": {"tenant_id": tenant_1.id}},
            {"project_kwargs": {"tenant_id": tenant_2.id}},
        ],
    )
    return ActivitiesInit(
        session=session,
        tenant_1=tenant_1,
        location_11=location_11,
        activity_11=activity_11,
        location_12=location_12,
        activity_12=activity_12,
        location_13=location_13,
        activity_13=activity_13,
        tenant_2=tenant_2,
        location_21=location_21,
        activity_21=activity_21,
        tenant_3=tenant_3,
    )


@dataclasses.dataclass
class TasksInit:
    session: AsyncSession
    activities: ActivitiesInit
    tenant_1: Tenant
    location_11: Location
    task_11: Task
    task_11_item: tuple[LibraryTask, Task]
    task_112: Task
    task_112_item: tuple[LibraryTask, Task]
    task_12: Task
    task_12_item: tuple[LibraryTask, Task]
    location_13: Location
    task_13: Task
    task_13_item: tuple[LibraryTask, Task]
    tenant_2: Tenant
    location_21: Location
    task_21: Task
    task_21_item: tuple[LibraryTask, Task]
    tenant_3: Tenant


@pytest.fixture
async def tasks_init(activities_init: ActivitiesInit) -> TasksInit:
    a = activities_init

    task_11, task_112, task_12, task_13, task_21 = await TaskFactory.persist_many(
        a.session,
        per_item_kwargs=[
            {"location_id": a.location_11.id, "activity_id": a.activity_11.id},
            {"location_id": a.location_11.id, "activity_id": a.activity_11.id},
            {"location_id": a.location_12.id, "activity_id": a.activity_12.id},
            {"location_id": a.location_13.id, "activity_id": a.activity_13.id},
            {"location_id": a.location_21.id, "activity_id": a.activity_21.id},
        ],
    )

    library_ids = {
        task_11.library_task_id,
        task_112.library_task_id,
        task_12.library_task_id,
        task_13.library_task_id,
        task_21.library_task_id,
    }
    library = dict(
        (
            await activities_init.session.exec(
                select(LibraryTask.id, LibraryTask).where(
                    col(LibraryTask.id).in_(library_ids)
                )
            )
        ).all()
    )

    return TasksInit(
        session=activities_init.session,
        activities=a,
        tenant_1=a.tenant_1,
        location_11=a.location_11,
        task_11=task_11,
        task_11_item=(
            library[task_11.library_task_id],
            task_11,
        ),
        task_112=task_112,
        task_112_item=(
            library[task_112.library_task_id],
            task_112,
        ),
        task_12=task_12,
        task_12_item=(
            library[task_12.library_task_id],
            task_12,
        ),
        location_13=a.location_13,
        task_13=task_13,
        task_13_item=(
            library[task_13.library_task_id],
            task_13,
        ),
        tenant_2=a.tenant_2,
        location_21=a.location_21,
        task_21=task_21,
        task_21_item=(
            library[task_21.library_task_id],
            task_21,
        ),
        tenant_3=a.tenant_3,
    )


@dataclasses.dataclass
class TasksHazardsInit:
    hazard_111: TaskHazard
    hazard_111_item: tuple[LibraryHazard, TaskHazard]
    hazard_112: TaskHazard
    hazard_112_item: tuple[LibraryHazard, TaskHazard]
    hazard_121: TaskHazard
    hazard_121_item: tuple[LibraryHazard, TaskHazard]
    hazard_131: TaskHazard
    hazard_131_item: tuple[LibraryHazard, TaskHazard]

    hazard_211: TaskHazard
    hazard_211_item: tuple[LibraryHazard, TaskHazard]


@pytest.fixture
async def tasks_hazards_init(
    tasks_init: TasksInit,
) -> tuple[TasksInit, TasksHazardsInit]:
    t = tasks_init

    (
        hazard_111,
        hazard_112,
        hazard_121,
        hazard_131,
        hazard_211,
    ) = await TaskHazardFactory.persist_many(
        t.session,
        per_item_kwargs=[
            {"task_id": t.task_11.id},
            {"task_id": t.task_11.id},
            {"task_id": t.task_12.id},
            {"task_id": t.task_13.id},
            {"task_id": t.task_21.id},
        ],
    )

    library_ids = {
        hazard_111.library_hazard_id,
        hazard_112.library_hazard_id,
        hazard_121.library_hazard_id,
        hazard_131.library_hazard_id,
        hazard_211.library_hazard_id,
    }
    library = dict(
        (
            await t.session.exec(
                select(LibraryHazard.id, LibraryHazard).where(
                    col(LibraryHazard.id).in_(library_ids)
                )
            )
        ).all()
    )

    return (
        t,
        TasksHazardsInit(
            hazard_111=hazard_111,
            hazard_111_item=(
                library[hazard_111.library_hazard_id],
                hazard_111,
            ),
            hazard_112=hazard_112,
            hazard_112_item=(
                library[hazard_112.library_hazard_id],
                hazard_112,
            ),
            hazard_121=hazard_121,
            hazard_121_item=(
                library[hazard_121.library_hazard_id],
                hazard_121,
            ),
            hazard_131=hazard_131,
            hazard_131_item=(
                library[hazard_131.library_hazard_id],
                hazard_131,
            ),
            hazard_211=hazard_211,
            hazard_211_item=(
                library[hazard_211.library_hazard_id],
                hazard_211,
            ),
        ),
    )


@dataclasses.dataclass
class TasksHazardsControlsInit:
    control_1111: TaskControl
    control_1111_item: tuple[LibraryControl, TaskControl]
    control_1112: TaskControl
    control_1112_item: tuple[LibraryControl, TaskControl]
    control_1211: TaskControl
    control_1211_item: tuple[LibraryControl, TaskControl]
    control_1311: TaskControl
    control_1311_item: tuple[LibraryControl, TaskControl]

    control_2111: TaskControl
    control_2111_item: tuple[LibraryControl, TaskControl]


@pytest.fixture
async def tasks_controls_init(
    tasks_hazards_init: tuple[TasksInit, TasksHazardsInit]
) -> tuple[TasksInit, TasksHazardsInit, TasksHazardsControlsInit]:
    t, h = tasks_hazards_init

    (
        control_1111,
        control_1112,
        control_1211,
        control_1311,
        control_2111,
    ) = await TaskControlFactory.persist_many(
        t.session,
        per_item_kwargs=[
            {"task_hazard_id": h.hazard_111.id},
            {"task_hazard_id": h.hazard_111.id},
            {"task_hazard_id": h.hazard_121.id},
            {"task_hazard_id": h.hazard_131.id},
            {"task_hazard_id": h.hazard_211.id},
        ],
    )

    library_ids = {
        control_1111.library_control_id,
        control_1112.library_control_id,
        control_1211.library_control_id,
        control_1311.library_control_id,
        control_2111.library_control_id,
    }
    library = dict(
        (
            await t.session.exec(
                select(LibraryControl.id, LibraryControl).where(
                    col(LibraryControl.id).in_(library_ids)
                )
            )
        ).all()
    )

    return (
        t,
        h,
        TasksHazardsControlsInit(
            control_1111=control_1111,
            control_1111_item=(
                library[control_1111.library_control_id],
                control_1111,
            ),
            control_1112=control_1112,
            control_1112_item=(
                library[control_1112.library_control_id],
                control_1112,
            ),
            control_1211=control_1211,
            control_1211_item=(
                library[control_1211.library_control_id],
                control_1211,
            ),
            control_1311=control_1311,
            control_1311_item=(
                library[control_1311.library_control_id],
                control_1311,
            ),
            control_2111=control_2111,
            control_2111_item=(
                library[control_2111.library_control_id],
                control_2111,
            ),
        ),
    )


@dataclasses.dataclass
class SiteConditionsInit:
    session: AsyncSession
    tenant_1: Tenant
    location_11: Location
    site_condition_11: SiteCondition
    site_condition_11_item: tuple[LibrarySiteCondition, SiteCondition]
    site_condition_12: SiteCondition
    site_condition_12_item: tuple[LibrarySiteCondition, SiteCondition]
    location_13: Location
    site_condition_13: SiteCondition
    site_condition_13_item: tuple[LibrarySiteCondition, SiteCondition]
    tenant_2: Tenant
    location_21: Location
    site_condition_21: SiteCondition
    site_condition_21_item: tuple[LibrarySiteCondition, SiteCondition]
    tenant_3: Tenant


@pytest.fixture
async def site_conditions_init(
    db_session_no_expire: AsyncSession,
) -> SiteConditionsInit:
    session = db_session_no_expire
    tenant_1, tenant_2, tenant_3 = await TenantFactory.persist_many(session, size=3)
    project_11 = await WorkPackageFactory.persist(
        db_session_no_expire, tenant_id=tenant_1.id
    )
    location_11 = await LocationFactory.persist(
        db_session_no_expire, project_id=project_11.id
    )
    (
        (
            site_condition_11,
            _,
            _,
        ),
        (site_condition_12, _, _),
        (site_condition_13, _, location_13),
        (
            site_condition_21,
            _,
            location_21,
        ),
    ) = await SiteConditionFactory.batch_with_project_and_location(
        session,
        [
            {"project": project_11, "location": location_11},
            {"project": project_11, "location": location_11},
            {"project_kwargs": {"tenant_id": tenant_1.id}},
            {"project_kwargs": {"tenant_id": tenant_2.id}},
        ],
    )

    library_ids = {
        site_condition_11.library_site_condition_id,
        site_condition_12.library_site_condition_id,
        site_condition_13.library_site_condition_id,
        site_condition_21.library_site_condition_id,
    }
    library = dict(
        (
            await session.exec(
                select(LibrarySiteCondition.id, LibrarySiteCondition).where(
                    col(LibrarySiteCondition.id).in_(library_ids)
                )
            )
        ).all()
    )

    return SiteConditionsInit(
        session=session,
        tenant_1=tenant_1,
        location_11=location_11,
        site_condition_11=site_condition_11,
        site_condition_11_item=(
            library[site_condition_11.library_site_condition_id],
            site_condition_11,
        ),
        site_condition_12=site_condition_12,
        site_condition_12_item=(
            library[site_condition_12.library_site_condition_id],
            site_condition_12,
        ),
        location_13=location_13,
        site_condition_13=site_condition_13,
        site_condition_13_item=(
            library[site_condition_13.library_site_condition_id],
            site_condition_13,
        ),
        tenant_2=tenant_2,
        location_21=location_21,
        site_condition_21=site_condition_21,
        site_condition_21_item=(
            library[site_condition_21.library_site_condition_id],
            site_condition_21,
        ),
        tenant_3=tenant_3,
    )


@dataclasses.dataclass
class SiteConditionsHazardsInit:
    hazard_111: SiteConditionHazard
    hazard_111_item: tuple[LibraryHazard, SiteConditionHazard]
    hazard_112: SiteConditionHazard
    hazard_112_item: tuple[LibraryHazard, SiteConditionHazard]
    hazard_121: SiteConditionHazard
    hazard_121_item: tuple[LibraryHazard, SiteConditionHazard]
    hazard_131: SiteConditionHazard
    hazard_131_item: tuple[LibraryHazard, SiteConditionHazard]

    hazard_211: SiteConditionHazard
    hazard_211_item: tuple[LibraryHazard, SiteConditionHazard]


@pytest.fixture
async def site_conditions_hazards_init(
    site_conditions_init: SiteConditionsInit,
) -> tuple[SiteConditionsInit, SiteConditionsHazardsInit]:
    t = site_conditions_init

    (
        hazard_111,
        hazard_112,
        hazard_121,
        hazard_131,
        hazard_211,
    ) = await SiteConditionHazardFactory.persist_many(
        t.session,
        per_item_kwargs=[
            {"site_condition_id": t.site_condition_11.id},
            {"site_condition_id": t.site_condition_11.id},
            {"site_condition_id": t.site_condition_12.id},
            {"site_condition_id": t.site_condition_13.id},
            {"site_condition_id": t.site_condition_21.id},
        ],
    )

    library_ids = {
        hazard_111.library_hazard_id,
        hazard_112.library_hazard_id,
        hazard_121.library_hazard_id,
        hazard_131.library_hazard_id,
        hazard_211.library_hazard_id,
    }
    library = dict(
        (
            await t.session.exec(
                select(LibraryHazard.id, LibraryHazard).where(
                    col(LibraryHazard.id).in_(library_ids)
                )
            )
        ).all()
    )

    return (
        t,
        SiteConditionsHazardsInit(
            hazard_111=hazard_111,
            hazard_111_item=(
                library[hazard_111.library_hazard_id],
                hazard_111,
            ),
            hazard_112=hazard_112,
            hazard_112_item=(
                library[hazard_112.library_hazard_id],
                hazard_112,
            ),
            hazard_121=hazard_121,
            hazard_121_item=(
                library[hazard_121.library_hazard_id],
                hazard_121,
            ),
            hazard_131=hazard_131,
            hazard_131_item=(
                library[hazard_131.library_hazard_id],
                hazard_131,
            ),
            hazard_211=hazard_211,
            hazard_211_item=(
                library[hazard_211.library_hazard_id],
                hazard_211,
            ),
        ),
    )


@dataclasses.dataclass
class SiteConditionsHazardsControlsInit:
    control_1111: SiteConditionControl
    control_1111_item: tuple[LibraryControl, SiteConditionControl]
    control_1112: SiteConditionControl
    control_1112_item: tuple[LibraryControl, SiteConditionControl]
    control_1211: SiteConditionControl
    control_1211_item: tuple[LibraryControl, SiteConditionControl]
    control_1311: SiteConditionControl
    control_1311_item: tuple[LibraryControl, SiteConditionControl]

    control_2111: SiteConditionControl
    control_2111_item: tuple[LibraryControl, SiteConditionControl]


@pytest.fixture
async def site_conditions_controls_init(
    site_conditions_hazards_init: tuple[SiteConditionsInit, SiteConditionsHazardsInit]
) -> tuple[
    SiteConditionsInit, SiteConditionsHazardsInit, SiteConditionsHazardsControlsInit
]:
    t, h = site_conditions_hazards_init

    (
        control_1111,
        control_1112,
        control_1211,
        control_1311,
        control_2111,
    ) = await SiteConditionControlFactory.persist_many(
        t.session,
        per_item_kwargs=[
            {"site_condition_hazard_id": h.hazard_111.id},
            {"site_condition_hazard_id": h.hazard_111.id},
            {"site_condition_hazard_id": h.hazard_121.id},
            {"site_condition_hazard_id": h.hazard_131.id},
            {"site_condition_hazard_id": h.hazard_211.id},
        ],
    )
    library_ids = {
        control_1111.library_control_id,
        control_1112.library_control_id,
        control_1211.library_control_id,
        control_1311.library_control_id,
        control_2111.library_control_id,
    }
    library = dict(
        (
            await t.session.exec(
                select(LibraryControl.id, LibraryControl).where(
                    col(LibraryControl.id).in_(library_ids)
                )
            )
        ).all()
    )

    return (
        t,
        h,
        SiteConditionsHazardsControlsInit(
            control_1111=control_1111,
            control_1111_item=(
                library[control_1111.library_control_id],
                control_1111,
            ),
            control_1112=control_1112,
            control_1112_item=(
                library[control_1112.library_control_id],
                control_1112,
            ),
            control_1211=control_1211,
            control_1211_item=(
                library[control_1211.library_control_id],
                control_1211,
            ),
            control_1311=control_1311,
            control_1311_item=(
                library[control_1311.library_control_id],
                control_1311,
            ),
            control_2111=control_2111,
            control_2111_item=(
                library[control_2111.library_control_id],
                control_2111,
            ),
        ),
    )


@dataclasses.dataclass
class TenantUsersInit:
    tenant_1: Tenant
    manager_11: User
    supervisor_12: User
    user_13: User
    tenant_2: Tenant
    manager_21: User
    tenant_3: Tenant


@pytest.fixture
async def users_init(db_session_no_expire: AsyncSession) -> TenantUsersInit:
    session = db_session_no_expire
    tenant_1, tenant_2, tenant_3 = await TenantFactory.persist_many(session, size=3)
    manager_11 = await ManagerUserFactory.persist(session, tenant_id=tenant_1.id)
    supervisor_12 = await SupervisorUserFactory.persist(session, tenant_id=tenant_1.id)
    user_13 = await UserFactory.persist(session, tenant_id=tenant_1.id)
    manager_21 = await ManagerUserFactory.persist(session, tenant_id=tenant_2.id)
    return TenantUsersInit(
        tenant_1=tenant_1,
        manager_11=manager_11,
        supervisor_12=supervisor_12,
        user_13=user_13,
        tenant_2=tenant_2,
        manager_21=manager_21,
        tenant_3=tenant_3,
    )


@dataclasses.dataclass
class TenantContractorsInit:
    tenant_1: Tenant
    contractor_11: Contractor
    contractor_12: Contractor
    contractor_13: Contractor
    tenant_2: Tenant
    contractor_21: Contractor
    tenant_3: Tenant


@pytest.fixture
async def contractors_init(db_session_no_expire: AsyncSession) -> TenantContractorsInit:
    session = db_session_no_expire
    tenant_1, tenant_2, tenant_3 = await TenantFactory.persist_many(session, size=3)
    (
        contractor_11,
        contractor_12,
        contractor_13,
        contractor_21,
    ) = await ContractorFactory.persist_many(
        session,
        per_item_kwargs=[
            {"tenant_id": tenant_1.id},
            {"tenant_id": tenant_1.id},
            {"tenant_id": tenant_1.id},
            {"tenant_id": tenant_2.id},
        ],
    )
    return TenantContractorsInit(
        tenant_1=tenant_1,
        contractor_11=contractor_11,
        contractor_12=contractor_12,
        contractor_13=contractor_13,
        tenant_2=tenant_2,
        contractor_21=contractor_21,
        tenant_3=tenant_3,
    )


@dataclasses.dataclass
class TenantCrewInit:
    tenant_1: Tenant
    crew_11: Crew
    crew_12: Crew
    crew_13: Crew
    tenant_2: Tenant
    crew_21: Crew
    tenant_3: Tenant


@pytest.fixture
async def crew_init(db_session_no_expire: AsyncSession) -> TenantCrewInit:
    session = db_session_no_expire
    tenant_1, tenant_2, tenant_3 = await TenantFactory.persist_many(session, size=3)
    (
        crew_11,
        crew_12,
        crew_13,
        crew_21,
    ) = await CrewFactory.persist_many(
        session,
        per_item_kwargs=[
            {"tenant_id": tenant_1.id},
            {"tenant_id": tenant_1.id},
            {"tenant_id": tenant_1.id},
            {"tenant_id": tenant_2.id},
        ],
    )
    return TenantCrewInit(
        tenant_1=tenant_1,
        crew_11=crew_11,
        crew_12=crew_12,
        crew_13=crew_13,
        tenant_2=tenant_2,
        crew_21=crew_21,
        tenant_3=tenant_3,
    )


@dataclasses.dataclass
class TenantAuditInit:
    tenant_1: Tenant
    audit_event_11: AuditEvent
    audit_event_12: AuditEvent
    audit_event_13: AuditEvent
    tenant_2: Tenant
    audit_event_21: AuditEvent
    tenant_3: Tenant


@pytest.fixture
async def audits_init(db_session_no_expire: AsyncSession) -> TenantAuditInit:
    session = db_session_no_expire
    tenant_1, tenant_2, tenant_3 = await TenantFactory.persist_many(session, size=3)
    user_1 = await UserFactory.persist(session, tenant_id=tenant_1.id)
    audits_1 = await AuditEventFactory.persist_many(session, size=3, user_id=user_1.id)
    user_2 = await UserFactory.persist(session, tenant_id=tenant_2.id)
    audit_21 = await AuditEventFactory.persist(session, user_id=user_2.id)
    return TenantAuditInit(
        tenant_1=tenant_1,
        audit_event_11=audits_1[0],
        audit_event_12=audits_1[1],
        audit_event_13=audits_1[2],
        tenant_2=tenant_2,
        audit_event_21=audit_21,
        tenant_3=tenant_3,
    )


@pytest.mark.asyncio
@pytest.fixture
async def project_loader_factory(
    work_package_manager: WorkPackageManager,
    riskmodel_container_tests: RiskModelContainer,
    locations_manager: LocationsManager,
) -> LoaderFactory[TenantWorkPackageLoader]:
    reactor = await riskmodel_container_tests.risk_model_reactor()
    return functools.partial(
        TenantWorkPackageLoader, work_package_manager, reactor, locations_manager
    )


@pytest.fixture
def daily_reports_loader_factory(
    daily_report_manager: DailyReportManager,
) -> Callable[[uuid.UUID], TenantDailyReportsLoader]:
    return functools.partial(
        TenantDailyReportsLoader,
        daily_report_manager,
    )


@pytest.fixture
def contractor_loader_factory(
    contractor_manager: ContractorsManager,
) -> Callable[[uuid.UUID], TenantContractorsLoader]:
    return functools.partial(TenantContractorsLoader, contractor_manager)


@pytest.fixture
def crew_loader_factory(
    crew_manager: CrewManager,
) -> Callable[[uuid.UUID], TenantCrewLoader]:
    return functools.partial(TenantCrewLoader, crew_manager)


@pytest.fixture
async def site_condition_loader_factory(
    site_condition_manager: SiteConditionManager,
    riskmodel_container_tests: RiskModelContainer,
) -> Callable[[uuid.UUID], TenantSiteConditionLoader]:
    reactor = await riskmodel_container_tests.risk_model_reactor()
    return functools.partial(TenantSiteConditionLoader, site_condition_manager, reactor)


@pytest.mark.asyncio
@pytest.fixture
async def activity_loader_factory(
    activity_manager: ActivityManager,
    task_manager: TaskManager,
    library_manager: LibraryManager,
    configurations_manager: ConfigurationsManager,
    riskmodel_container_tests: RiskModelContainer,
    locations_manager: LocationsManager,
) -> Callable[[uuid.UUID], TenantActivityLoader]:
    reactor = await riskmodel_container_tests.risk_model_reactor()
    return functools.partial(
        TenantActivityLoader,
        activity_manager,
        task_manager,
        library_manager,
        reactor,
        locations_manager,
        configurations_manager,
    )


@pytest.mark.asyncio
@pytest.fixture
async def project_location_loader_factory(
    work_package_manager: WorkPackageManager,
    activity_manager: ActivityManager,
    task_manager: TaskManager,
    site_condition_manager: SiteConditionManager,
    daily_report_manager: DailyReportManager,
    library_manager: LibraryManager,
    locations_manager: LocationsManager,
    riskmodel_container_tests: RiskModelContainer,
    activity_loader_factory: TenantActivityLoader,
    project_loader_factory: TenantWorkPackageLoader,
    job_safety_briefings_manager: JobSafetyBriefingManager,
) -> LoaderFactory[TenantProjectLocationLoader]:
    reactor = await riskmodel_container_tests.risk_model_reactor()
    return functools.partial(
        TenantProjectLocationLoader,
        locations_manager,
        work_package_manager,
        activity_manager,
        task_manager,
        site_condition_manager,
        daily_report_manager,
        library_manager,
        reactor,
        activity_loader_factory,
        project_loader_factory,
        job_safety_briefings_manager,
    )


@pytest.mark.asyncio
@pytest.fixture
async def task_loader_factory(
    task_manager: TaskManager,
    riskmodel_container_tests: RiskModelContainer,
) -> Callable[[uuid.UUID], TenantTaskLoader]:
    reactor = await riskmodel_container_tests.risk_model_reactor()
    return functools.partial(TenantTaskLoader, task_manager, reactor)


@pytest.fixture
def tenant_loader(tenant_manager: TenantManager) -> TenantLoader:
    return TenantLoader(tenant_manager)


@pytest.fixture
def user_loader_factory(
    user_manager: UserManager,
) -> Callable[[uuid.UUID], TenantUsersLoader]:
    return functools.partial(TenantUsersLoader, user_manager)


@pytest.fixture
def configurations_loader_factory(
    configurations_manager: ConfigurationsManager,
) -> Callable[[uuid.UUID], TenantConfigurationsLoader]:
    return functools.partial(TenantConfigurationsLoader, configurations_manager)
