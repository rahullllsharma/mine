import uuid

import pytest

from tests.integration.dataloaders.conftest import (
    LoaderFactory,
    TasksInit,
    assert_dataloader_filter_tenants,
    assert_dataloader_return_right_order,
    assert_mocked_dataloader_return_right_order,
)
from worker_safety_service.graphql.data_loaders.activities import TenantActivityLoader
from worker_safety_service.models import AsyncSession


class TestActivityTasks:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tenants(
        self,
        tasks_init: TasksInit,
        activity_loader_factory: LoaderFactory[TenantActivityLoader],
    ) -> None:
        """Make sure dataloaders filter tenants"""

        t = tasks_init
        a = t.activities
        await assert_dataloader_filter_tenants(
            activity_loader_factory,
            "load_tasks",
            "tasks",
            [
                # Tenant 1 should only see tenant 1 activities
                (
                    a.tenant_1.id,
                    [a.activity_13.id, a.activity_21.id],
                    [[t.task_13], []],
                ),
                # Tenant 2 should only see tenant 2 activities
                (
                    a.tenant_2.id,
                    [a.activity_13.id, a.activity_21.id],
                    [[], [t.task_21]],
                ),
                # Invalid tenant
                (
                    a.tenant_3.id,
                    [a.activity_13.id, a.activity_21.id],
                    [[], []],
                ),
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_order(
        self,
        db_session: AsyncSession,
        tasks_init: TasksInit,
        activity_loader_factory: LoaderFactory[TenantActivityLoader],
    ) -> None:
        """Make sure order returned by dataloaders match request"""

        t = tasks_init
        a = t.activities
        await assert_mocked_dataloader_return_right_order(
            db_session,
            activity_loader_factory,
            "load_tasks",
            "tasks",
            a.tenant_1.id,
            filter_ids=[a.activity_11.id, a.activity_13.id],
            expected_result=[
                [t.task_11, t.task_112],
                [t.task_13],
            ],
            db_mock_data=[
                [t.task_11_item, t.task_112_item],
                [t.task_13_item],
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_missing(
        self,
        tasks_init: TasksInit,
        activity_loader_factory: LoaderFactory[TenantActivityLoader],
    ) -> None:
        """Return empty list and don't raise an error when activity don't exists"""

        t = tasks_init
        a = t.activities
        await assert_dataloader_return_right_order(
            activity_loader_factory,
            "load_tasks",
            "tasks",
            a.tenant_1.id,
            filter_ids=[a.activity_13.id, uuid.uuid4()],
            expected_result=[[t.task_13], []],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_empty(
        self,
        tasks_init: TasksInit,
        activity_loader_factory: LoaderFactory[TenantActivityLoader],
    ) -> None:
        """If an empty list is sent don't return anything"""
        a = tasks_init.activities
        items = await activity_loader_factory(a.tenant_1.id).load_tasks([])
        assert items == []
