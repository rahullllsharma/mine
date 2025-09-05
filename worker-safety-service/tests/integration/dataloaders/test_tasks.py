import uuid

import pytest
from sqlmodel import select

from tests.factories import (
    ActivityFactory,
    LibraryTaskFactory,
    LocationFactory,
    TenantFactory,
    WorkPackageFactory,
)
from tests.integration.dataloaders.conftest import (
    LoaderFactory,
    TasksHazardsControlsInit,
    TasksHazardsInit,
    TasksInit,
    assert_dataloader_filter_tenants,
    assert_dataloader_return_right_order,
    assert_mocked_dataloader_return_right_order,
)
from worker_safety_service.graphql.data_loaders.tasks import TenantTaskLoader
from worker_safety_service.models import AsyncSession, Task, TaskCreate


class TestTasksMe:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tenants(
        self,
        tasks_init: TasksInit,
        task_loader_factory: LoaderFactory[TenantTaskLoader],
    ) -> None:
        """Make sure dataloaders filter tenants"""

        x = tasks_init
        await assert_dataloader_filter_tenants(
            task_loader_factory,
            "load_tasks",
            "me",
            [
                # Tenant 1 should only see tenant 1 tasks
                (
                    x.tenant_1.id,
                    [x.task_13.id, x.task_21.id],
                    [x.task_13_item, None],
                ),
                # Tenant 2 should only see tenant 2 tasks
                (
                    x.tenant_2.id,
                    [x.task_13.id, x.task_21.id],
                    [None, x.task_21_item],
                ),
                # Invalid tenant
                (
                    x.tenant_3.id,
                    [x.task_13.id, x.task_21.id],
                    [None, None],
                ),
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_order(
        self,
        db_session: AsyncSession,
        tasks_init: TasksInit,
        task_loader_factory: LoaderFactory[TenantTaskLoader],
    ) -> None:
        """Make sure order returned by dataloaders match request"""

        x = tasks_init
        await assert_mocked_dataloader_return_right_order(
            db_session,
            task_loader_factory,
            "load_tasks",
            "me",
            x.tenant_1.id,
            filter_ids=[x.task_11.id, x.task_13.id],
            expected_result=[x.task_11_item, x.task_13_item],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_missing(
        self,
        tasks_init: TasksInit,
        task_loader_factory: LoaderFactory[TenantTaskLoader],
    ) -> None:
        """Return empty list and don't raise an error when task don't exists"""

        x = tasks_init
        await assert_dataloader_return_right_order(
            task_loader_factory,
            "load_tasks",
            "me",
            x.tenant_1.id,
            filter_ids=[x.task_13.id, uuid.uuid4()],
            expected_result=[x.task_13_item, None],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_empty(
        self,
        tasks_init: TasksInit,
        task_loader_factory: LoaderFactory[TenantTaskLoader],
    ) -> None:
        """If an empty list is sent don't return anything"""
        x = tasks_init
        items = await task_loader_factory(x.tenant_1.id).load_tasks([])
        assert items == []

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_tasks(
        self,
        db_session: AsyncSession,
        task_loader_factory: LoaderFactory[TenantTaskLoader],
    ) -> None:
        tenant = await TenantFactory.persist(db_session)
        work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
        location = await LocationFactory.persist(
            db_session, tenant_id=tenant.id, project_id=work_package.id
        )
        activity = await ActivityFactory.persist(
            db_session,
            tenant_id=tenant.id,
            location_id=location.id,
        )
        library_tasks = await LibraryTaskFactory.persist_many(db_session, size=2)
        lt_1, lt_2 = library_tasks

        task_create = [
            TaskCreate(library_task_id=lt_1.id, activity_id=activity.id, hazards=[])
        ]
        tasks = await task_loader_factory(tenant.id).create_tasks(
            task_create, None, db_commit=True
        )
        assert len(tasks) == 1
        tasks = await task_loader_factory(tenant.id).create_tasks(
            task_create, None, db_commit=True
        )
        assert len(tasks) == 1
        db_tasks = (
            await db_session.exec(select(Task).where(Task.activity_id == activity.id))
        ).all()
        assert db_tasks == tasks


class TestTasksGetTasks:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tenants(
        self,
        tasks_init: TasksInit,
        task_loader_factory: LoaderFactory[TenantTaskLoader],
    ) -> None:
        """Make sure dataloaders filter tenants"""

        x = tasks_init

        # Tenant 1 should only see tenant 1 tasks
        tasks = await task_loader_factory(x.tenant_1.id).get_tasks()
        assert {i[1].id for i in tasks} == {
            x.task_11.id,
            x.task_112.id,
            x.task_12.id,
            x.task_13.id,
        }

        # Tenant 2 should only see tenant 2 tasks
        tasks = await task_loader_factory(x.tenant_2.id).get_tasks()
        assert {i[1].id for i in tasks} == {x.task_21.id}

        # Invalid tenant
        tasks = await task_loader_factory(x.tenant_3.id).get_tasks()
        assert {i[1].id for i in tasks} == set()


class TestTasksHazards:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tenants(
        self,
        tasks_hazards_init: tuple[TasksInit, TasksHazardsInit],
        task_loader_factory: LoaderFactory[TenantTaskLoader],
    ) -> None:
        """Make sure dataloaders filter tenants"""

        t, h = tasks_hazards_init
        await assert_dataloader_filter_tenants(
            task_loader_factory,
            "load_hazards",
            "hazards",
            [
                # Tenant 1 should only see tenant 1 tasks
                (
                    t.tenant_1.id,
                    [t.task_13.id, t.task_21.id],
                    [[h.hazard_131_item], []],
                ),
                # Tenant 2 should only see tenant 2 tasks
                (
                    t.tenant_2.id,
                    [t.task_13.id, t.task_21.id],
                    [[], [h.hazard_211_item]],
                ),
                # Invalid tenant
                (
                    t.tenant_3.id,
                    [t.task_13.id, t.task_21.id],
                    [[], []],
                ),
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_order(
        self,
        db_session: AsyncSession,
        tasks_hazards_init: tuple[TasksInit, TasksHazardsInit],
        task_loader_factory: LoaderFactory[TenantTaskLoader],
    ) -> None:
        """Make sure order returned by dataloaders match request"""

        t, h = tasks_hazards_init
        await assert_mocked_dataloader_return_right_order(
            db_session,
            task_loader_factory,
            "load_hazards",
            "hazards",
            t.tenant_1.id,
            filter_ids=[t.task_11.id, t.task_13.id],
            expected_result=[
                [h.hazard_111_item, h.hazard_112_item],
                [h.hazard_131_item],
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_missing(
        self,
        tasks_hazards_init: tuple[TasksInit, TasksHazardsInit],
        task_loader_factory: LoaderFactory[TenantTaskLoader],
    ) -> None:
        """Return empty list and don't raise an error when task don't exists"""

        t, h = tasks_hazards_init
        await assert_dataloader_return_right_order(
            task_loader_factory,
            "load_hazards",
            "hazards",
            t.tenant_1.id,
            filter_ids=[t.task_13.id, uuid.uuid4()],
            expected_result=[[h.hazard_131_item], []],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_empty(
        self,
        tasks_hazards_init: tuple[TasksInit, TasksHazardsInit],
        task_loader_factory: LoaderFactory[TenantTaskLoader],
    ) -> None:
        """If an empty list is sent don't return anything"""
        t, _ = tasks_hazards_init
        items = await task_loader_factory(t.tenant_1.id).load_hazards([])
        assert items == []


class TestTasksHazardsControls:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tenants(
        self,
        tasks_controls_init: tuple[
            TasksInit, TasksHazardsInit, TasksHazardsControlsInit
        ],
        task_loader_factory: LoaderFactory[TenantTaskLoader],
    ) -> None:
        """Make sure dataloaders filter tenants"""

        t, h, c = tasks_controls_init
        await assert_dataloader_filter_tenants(
            task_loader_factory,
            "load_controls",
            "controls",
            [
                # Tenant 1 should only see tenant 1 tasks
                (
                    t.tenant_1.id,
                    [h.hazard_131.id, h.hazard_211.id],
                    [[c.control_1311_item], []],
                ),
                # Tenant 2 should only see tenant 2 tasks
                (
                    t.tenant_2.id,
                    [h.hazard_131.id, h.hazard_211.id],
                    [[], [c.control_2111_item]],
                ),
                # Invalid tenant
                (
                    t.tenant_3.id,
                    [h.hazard_131.id, h.hazard_211.id],
                    [[], []],
                ),
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_order(
        self,
        db_session: AsyncSession,
        tasks_controls_init: tuple[
            TasksInit, TasksHazardsInit, TasksHazardsControlsInit
        ],
        task_loader_factory: LoaderFactory[TenantTaskLoader],
    ) -> None:
        """Make sure order returned by dataloaders match request"""

        t, h, c = tasks_controls_init
        await assert_mocked_dataloader_return_right_order(
            db_session,
            task_loader_factory,
            "load_controls",
            "controls",
            t.tenant_1.id,
            filter_ids=[h.hazard_111.id, h.hazard_131.id],
            expected_result=[
                [c.control_1111_item, c.control_1112_item],
                [c.control_1311_item],
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_missing(
        self,
        tasks_controls_init: tuple[
            TasksInit, TasksHazardsInit, TasksHazardsControlsInit
        ],
        task_loader_factory: LoaderFactory[TenantTaskLoader],
    ) -> None:
        """Return empty list and don't raise an error when hazard don't exists"""

        t, h, c = tasks_controls_init
        await assert_dataloader_return_right_order(
            task_loader_factory,
            "load_controls",
            "controls",
            t.tenant_1.id,
            filter_ids=[h.hazard_131.id, uuid.uuid4()],
            expected_result=[[c.control_1311_item], []],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_empty(
        self,
        tasks_controls_init: tuple[
            TasksInit, TasksHazardsInit, TasksHazardsControlsInit
        ],
        task_loader_factory: LoaderFactory[TenantTaskLoader],
    ) -> None:
        """If an empty list is sent don't return anything"""
        t, _, _ = tasks_controls_init
        items = await task_loader_factory(t.tenant_1.id).load_controls([])
        assert items == []
