import functools
import inspect
import uuid
from typing import Awaitable, Callable, Optional
from unittest.mock import call, patch

import fastapi
import pytest
from _pytest.mark import ParameterSet

from tests.factories import (
    AdminUserFactory,
    ConfigurationFactory,
    ContractorFactory,
    LibraryAssetTypeFactory,
    LibraryDivisionFactory,
    LibraryProjectTypeFactory,
    LibraryRegionFactory,
    ManagerUserFactory,
    SupervisorUserFactory,
    TenantFactory,
    WorkPackageFactory,
    WorkTypeFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.helpers import (
    create_project,
    create_project_gql,
    edit_project_gql,
    gql_project,
    update_configuration,
    valid_project_location_request,
    valid_project_request,
)
from worker_safety_service.dal.configurations import (
    WORK_PACKAGE_CONFIG,
    ConfigurationsManager,
)
from worker_safety_service.models import AsyncSession
from worker_safety_service.risk_model.riskmodel_container import RiskModelContainer
from worker_safety_service.risk_model.riskmodelreactor import MetricCalculation
from worker_safety_service.risk_model.triggers.project_changed import ProjectChanged

archive_all_projects_query = """
    mutation ArchiveAllProjects {
        count: archiveAllProjects
    }
"""


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_project(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> tuple[dict, dict]:
    project_data, data = await create_project(execute_gql, db_session)
    assert data["name"] == project_data["name"]
    assert data["manager"]["id"] == project_data["managerId"]
    assert data["supervisor"]["id"] == project_data["supervisorId"]
    assert {i["id"] for i in data["additionalSupervisors"]} == set(
        project_data["additionalSupervisors"]
    )
    assert data["contractor"]["id"] == project_data["contractorId"]
    return project_data, data


@pytest.fixture()
async def existing_project(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> tuple[dict, dict]:
    return await create_project(execute_gql, db_session, populate_ids=True)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_project_with_all_attributes_required(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
) -> None:
    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    project = WorkPackageFactory.build(
        manager_id=(await ManagerUserFactory.persist(db_session)).id,
        primary_assigned_user_id=(await SupervisorUserFactory.persist(db_session)).id,
        additional_assigned_users_ids=[
            (await SupervisorUserFactory.persist(db_session)).id
        ],
        contractor_id=(await ContractorFactory.persist(db_session)).id,
        region_id=(await LibraryRegionFactory.persist(db_session)).id,
        division_id=(await LibraryDivisionFactory.persist(db_session)).id,
        work_type_id=(await LibraryProjectTypeFactory.persist(db_session)).id,
        work_type_ids=[(await WorkTypeFactory.persist(db_session)).id],
        asset_type_id=(await LibraryAssetTypeFactory.persist(db_session)).id,
    ).dict(exclude={"id"})

    await update_configuration(
        configurations_manager,
        tenant_id,
        WORK_PACKAGE_CONFIG,
        required_fields=None,  # Means all
    )

    project_data = gql_project(project)
    project_data["locations"] = [await valid_project_location_request(db_session)]
    data = await create_project_gql(execute_gql, project_data)
    assert data["name"] == project_data["name"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_project_with_all_attributes_not_required(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
) -> None:
    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    project = WorkPackageFactory.build(
        primary_assigned_user_id=(
            await SupervisorUserFactory.persist(db_session, tenant_id=tenant_id)
        ).id,
        contractor_id=None,
        region_id=None,
        division_id=None,
        work_type_id=None,
        work_type_ids=[(await WorkTypeFactory.persist(db_session)).id],
        asset_type_id=None,
    ).dict(exclude={"id"})

    await update_configuration(
        configurations_manager,
        tenant_id,
        WORK_PACKAGE_CONFIG,
        required_fields=[],
    )

    project_data = gql_project(project)
    project_data["locations"] = [await valid_project_location_request(db_session)]
    data = await create_project_gql(execute_gql, project_data)
    assert data["name"] == project_data["name"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_project_no_update(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    existing_project: tuple[dict, dict],
) -> tuple[dict, dict]:
    project_data, data = existing_project
    new_data = await edit_project_gql(execute_gql, project_data)
    assert data == new_data
    return project_data, new_data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_project(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    existing_project: tuple[dict, dict],
) -> tuple[dict, dict]:
    project_data, _ = existing_project

    manager_id = (await ManagerUserFactory.persist(db_session)).id
    supervisor_id = (await SupervisorUserFactory.persist(db_session)).id
    supervisor_2_id = (await SupervisorUserFactory.persist(db_session)).id
    contractor_id = (await ContractorFactory.persist(db_session)).id
    project_data.update(
        managerId=manager_id,
        supervisorId=supervisor_id,
        additionalSupervisors=[supervisor_2_id],
        contractorId=contractor_id,
    )
    new_data = await edit_project_gql(execute_gql, project_data)
    assert new_data["manager"]["id"] == str(manager_id)
    assert new_data["supervisor"]["id"] == str(supervisor_id)
    assert {i["id"] for i in new_data["additionalSupervisors"]} == {
        str(supervisor_2_id)
    }
    assert new_data["contractor"]["id"] == str(contractor_id)
    return project_data, new_data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_all_projects_fail_for_wrong_tenant(
    execute_gql: ExecuteGQL,
) -> None:
    with pytest.raises(Exception) as e:
        await execute_gql(
            operation_name="ArchiveAllProjects",
            query=archive_all_projects_query,
        )
    e.match("User is not authorized to delete all projects!")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_all_projects_for_hydro1_tenant(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    new_tenant, new_admin = await TenantFactory.new_with_admin(
        db_session, tenant_name="hydro1"
    )

    await ConfigurationFactory.persist(
        db_session,
        tenant_id=new_tenant.id,
        name="FEATURES.IS_ARCHIVE_ALL_WORK_PACKAGES_ENABLED",
        value="true",
    )

    workpackages = await WorkPackageFactory.persist_many(
        session=db_session, tenant_id=new_tenant.id, size=6
    )

    response = await execute_gql(
        operation_name="ArchiveAllProjects",
        query=archive_all_projects_query,
        raw=True,
        user=new_admin,
    )
    data = response.json().get("data")

    assert data
    assert data["count"] == len(workpackages)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_invalid_manager(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    existing_project: tuple[dict, dict],
) -> None:
    admin_id = (await AdminUserFactory.persist(db_session)).id
    supervisor_id = (await SupervisorUserFactory.persist(db_session)).id
    for user_id in [admin_id, supervisor_id, uuid.uuid4()]:
        # Test create
        project_data = await valid_project_request(db_session)
        project_data["managerId"] = user_id
        data = await create_project_gql(execute_gql, project_data, with_errors=True)
        assert data.get("errors")

        # Test edit
        _, data = existing_project
        project_data["id"] = data["id"]
        data = await edit_project_gql(execute_gql, project_data, with_errors=True)
        assert data.get("errors")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_invalid_supervisor(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    existing_project: tuple[dict, dict],
) -> None:
    admin_id = (await AdminUserFactory.persist(db_session)).id
    manager_id = (await ManagerUserFactory.persist(db_session)).id
    for user_id in [admin_id, manager_id, uuid.uuid4()]:
        # Test create
        project_data = await valid_project_request(db_session)
        project_data["supervisorId"] = user_id
        data = await create_project_gql(execute_gql, project_data, with_errors=True)
        assert data.get("errors")

        # Test edit
        _, data = existing_project
        project_data["id"] = data["id"]
        data = await edit_project_gql(execute_gql, project_data, with_errors=True)
        assert data.get("errors")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_invalid_additional_supervisors(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    existing_project: tuple[dict, dict],
) -> None:
    admin_id = (await AdminUserFactory.persist(db_session)).id
    manager_id = (await ManagerUserFactory.persist(db_session)).id
    for user_id in [admin_id, manager_id, uuid.uuid4()]:
        # Test create
        project_data = await valid_project_request(db_session)
        project_data["additionalSupervisors"] = [user_id]
        data = await create_project_gql(execute_gql, project_data, with_errors=True)
        assert data.get("errors")

        # Test edit
        _, data = existing_project
        project_data["id"] = data["id"]
        data = await edit_project_gql(execute_gql, project_data, with_errors=True)
        assert data.get("errors")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_duplicated_supervisors(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    existing_project: tuple[dict, dict],
) -> None:
    supervisor_id = (await SupervisorUserFactory.persist(db_session)).id
    supervisor_2_id = (await SupervisorUserFactory.persist(db_session)).id

    # Test create
    project_data = await valid_project_request(db_session)
    project_data["supervisorId"] = supervisor_id
    project_data["additionalSupervisors"] = [supervisor_id]
    data = await create_project_gql(execute_gql, project_data, with_errors=True)
    assert data.get("errors")

    project_data_2 = await valid_project_request(db_session)
    project_data_2["supervisorId"] = supervisor_id
    project_data_2["additionalSupervisors"] = [supervisor_2_id, supervisor_2_id]
    data = await create_project_gql(execute_gql, project_data_2, with_errors=True)
    assert data.get("errors")

    # Test edit
    _, data = existing_project
    project_data["id"] = data["id"]
    project_data_2["id"] = data["id"]
    data = await edit_project_gql(execute_gql, project_data, with_errors=True)
    assert data.get("errors")

    project_data = await valid_project_request(db_session)
    project_data["supervisorId"] = supervisor_id
    project_data["additionalSupervisors"] = [supervisor_2_id, supervisor_2_id]
    data = await edit_project_gql(execute_gql, project_data_2, with_errors=True)
    assert data.get("errors")


async def _setup_test_triggers(
    wrapped_function: Callable,
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    expect_triggers: bool = False,
) -> tuple[
    Callable[[], Awaitable[Optional[uuid.UUID]]],
    Callable[[uuid.UUID], list[MetricCalculation]],
]:
    kwargs = {}
    sig = inspect.signature(wrapped_function)
    if "existing_project" in sig.parameters:
        kwargs["existing_project"] = await create_project(
            execute_gql, db_session, populate_ids=True
        )

    async def call_fn() -> Optional[uuid.UUID]:
        ret = await wrapped_function(execute_gql, db_session, **kwargs)
        if ret is not None:
            # Then must be a tuple??
            project_data, data = ret
            project_id = uuid.UUID(data["id"])
            return project_id
        else:
            return None

    trigger_supplier: Callable[[uuid.UUID], list[MetricCalculation]] = (
        (lambda proj_id: [ProjectChanged(proj_id)])
        if expect_triggers
        else lambda proj_id: []
    )

    return call_fn, trigger_supplier


def param(
    supplier_function: Callable, fn: Callable, expect_triggers: bool = True
) -> ParameterSet:
    return pytest.param(
        functools.partial(supplier_function, fn, expect_triggers=expect_triggers),
        id=f"_{fn.__name__}_triggers",
    )


REACTOR_TRIGGERS_TEST_DATA = [
    param(_setup_test_triggers, test_create_project, expect_triggers=True),
    param(_setup_test_triggers, test_edit_project, expect_triggers=True),
    param(_setup_test_triggers, test_edit_project_no_update, expect_triggers=True),
    param(_setup_test_triggers, test_invalid_manager, expect_triggers=False),
    param(
        _setup_test_triggers,
        test_invalid_additional_supervisors,
        expect_triggers=False,
    ),
    param(_setup_test_triggers, test_duplicated_supervisors, expect_triggers=False),
]


@pytest.mark.parametrize(
    "test_data_supplier",
    REACTOR_TRIGGERS_TEST_DATA,
)
@pytest.mark.asyncio
@pytest.mark.integration
async def test_reactor_triggers_add_task(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    test_data_supplier: Callable[
        [ExecuteGQL, AsyncSession],
        Awaitable[
            tuple[
                Callable[[], Awaitable[uuid.UUID]],
                Callable[[uuid.UUID], list[MetricCalculation]],
            ]
        ],
    ],
) -> None:
    operation, expected_triggers_supplier = await test_data_supplier(
        execute_gql, db_session
    )

    with patch.object(fastapi.BackgroundTasks, "add_task") as mocked_method:
        project_id = await operation()
        expected_triggers = expected_triggers_supplier(project_id)
        # Checks if the tasks were fired.
        assert mocked_method.call_count == len(expected_triggers)


@pytest.mark.parametrize(
    "test_data_supplier",
    REACTOR_TRIGGERS_TEST_DATA,
)
@pytest.mark.asyncio
@pytest.mark.integration
async def test_reactor_triggers_reactor_mock(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    riskmodel_container_tests: RiskModelContainer,
    test_data_supplier: Callable[
        [ExecuteGQL, AsyncSession],
        Awaitable[
            tuple[
                Callable[[], Awaitable[uuid.UUID]],
                Callable[[uuid.UUID], list[MetricCalculation]],
            ]
        ],
    ],
) -> None:
    operation, expected_triggers_supplier = await test_data_supplier(
        execute_gql, db_session
    )

    reactor = await riskmodel_container_tests.risk_model_reactor()
    with patch.object(reactor, "add") as mocked_method:
        project_id = await operation()
        expected_triggers = expected_triggers_supplier(project_id)
        # We might need to sleep a bit because the background tasks are async
        mocked_method.assert_has_calls(
            list(map(lambda t: call(t), expected_triggers)), any_order=True
        )
