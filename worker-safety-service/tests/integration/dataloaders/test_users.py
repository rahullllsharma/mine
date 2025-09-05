import uuid

import pytest

from tests.integration.dataloaders.conftest import (
    LoaderFactory,
    TenantUsersInit,
    assert_dataloader_filter_tenants,
    assert_dataloader_return_right_order,
    assert_mocked_dataloader_return_right_order,
)
from worker_safety_service.graphql.data_loaders.users import TenantUsersLoader
from worker_safety_service.models import AsyncSession


class TestUsersMe:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tenants(
        self,
        users_init: TenantUsersInit,
        user_loader_factory: LoaderFactory[TenantUsersLoader],
    ) -> None:
        """Make sure dataloaders filter tenants"""

        x = users_init
        await assert_dataloader_filter_tenants(
            user_loader_factory,
            "load_users",
            "me",
            [
                # Tenant 1 should only see tenant 1 users
                (
                    x.tenant_1.id,
                    [x.user_13.id, x.manager_21.id],
                    [x.user_13, None],
                ),
                # Tenant 2 should only see tenant 2 users
                (
                    x.tenant_2.id,
                    [x.user_13.id, x.manager_21.id],
                    [None, x.manager_21],
                ),
                # Invalid tenant
                (
                    x.tenant_3.id,
                    [x.user_13.id, x.manager_21.id],
                    [None, None],
                ),
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_order(
        self,
        db_session: AsyncSession,
        users_init: TenantUsersInit,
        user_loader_factory: LoaderFactory[TenantUsersLoader],
    ) -> None:
        """Make sure order returned by dataloaders match request"""

        x = users_init
        await assert_mocked_dataloader_return_right_order(
            db_session,
            user_loader_factory,
            "load_users",
            "me",
            x.tenant_1.id,
            filter_ids=[x.manager_11.id, x.user_13.id],
            expected_result=[x.manager_11, x.user_13],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_missing(
        self,
        users_init: TenantUsersInit,
        user_loader_factory: LoaderFactory[TenantUsersLoader],
    ) -> None:
        """Return empty list and don't raise an error when user don't exists"""

        x = users_init
        await assert_dataloader_return_right_order(
            user_loader_factory,
            "load_users",
            "me",
            x.tenant_1.id,
            filter_ids=[x.user_13.id, uuid.uuid4()],
            expected_result=[x.user_13, None],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_empty(
        self,
        users_init: TenantUsersInit,
        user_loader_factory: LoaderFactory[TenantUsersLoader],
    ) -> None:
        """If an empty list is sent don't return anything"""
        x = users_init
        items = await user_loader_factory(x.tenant_1.id).load_users([])
        assert items == []


class TestUsersByRole:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tenants(
        self,
        users_init: TenantUsersInit,
        user_loader_factory: LoaderFactory[TenantUsersLoader],
    ) -> None:
        """Make sure dataloaders filter tenants"""

        x = users_init

        # Tenant 1 should only see tenant 1 users
        users = await user_loader_factory(x.tenant_1.id).by_role("manager")
        assert {i.id for i in users} == {x.manager_11.id}
        users = await user_loader_factory(x.tenant_1.id).by_role("supervisor")
        assert {i.id for i in users} == {x.supervisor_12.id}

        # Tenant 2 should only see tenant 2 users
        users = await user_loader_factory(x.tenant_2.id).by_role("manager")
        assert {i.id for i in users} == {x.manager_21.id}
        users = await user_loader_factory(x.tenant_2.id).by_role("supervisor")
        assert {i.id for i in users} == set()

        # Invalid tenant
        users = await user_loader_factory(x.tenant_3.id).by_role("manager")
        assert {i.id for i in users} == set()
