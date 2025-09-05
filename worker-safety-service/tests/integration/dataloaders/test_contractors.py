import uuid

import pytest

from tests.integration.dataloaders.conftest import (
    LoaderFactory,
    TenantContractorsInit,
    assert_dataloader_filter_tenants,
    assert_dataloader_return_right_order,
    assert_mocked_dataloader_return_right_order,
)
from worker_safety_service.graphql.data_loaders.contractors import (
    TenantContractorsLoader,
)
from worker_safety_service.models import AsyncSession


class TestContractorsMe:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tenants(
        self,
        contractors_init: TenantContractorsInit,
        contractor_loader_factory: LoaderFactory[TenantContractorsLoader],
    ) -> None:
        """Make sure dataloaders filter tenants"""

        x = contractors_init
        await assert_dataloader_filter_tenants(
            contractor_loader_factory,
            "load_contractors",
            "me",
            [
                # Tenant 1 should only see tenant 1 contractors
                (
                    x.tenant_1.id,
                    [x.contractor_13.id, x.contractor_21.id],
                    [x.contractor_13, None],
                ),
                # Tenant 2 should only see tenant 2 contractors
                (
                    x.tenant_2.id,
                    [x.contractor_13.id, x.contractor_21.id],
                    [None, x.contractor_21],
                ),
                # Invalid tenant
                (
                    x.tenant_3.id,
                    [x.contractor_13.id, x.contractor_21.id],
                    [None, None],
                ),
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_order(
        self,
        db_session: AsyncSession,
        contractors_init: TenantContractorsInit,
        contractor_loader_factory: LoaderFactory[TenantContractorsLoader],
    ) -> None:
        """Make sure order returned by dataloaders match request"""

        x = contractors_init
        await assert_mocked_dataloader_return_right_order(
            db_session,
            contractor_loader_factory,
            "load_contractors",
            "me",
            x.tenant_1.id,
            filter_ids=[x.contractor_11.id, x.contractor_13.id],
            expected_result=[x.contractor_11, x.contractor_13],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_missing(
        self,
        contractors_init: TenantContractorsInit,
        contractor_loader_factory: LoaderFactory[TenantContractorsLoader],
    ) -> None:
        """Return empty list and don't raise an error when contractor don't exists"""

        x = contractors_init
        await assert_dataloader_return_right_order(
            contractor_loader_factory,
            "load_contractors",
            "me",
            x.tenant_1.id,
            filter_ids=[x.contractor_13.id, uuid.uuid4()],
            expected_result=[x.contractor_13, None],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_empty(
        self,
        contractors_init: TenantContractorsInit,
        contractor_loader_factory: LoaderFactory[TenantContractorsLoader],
    ) -> None:
        """If an empty list is sent don't return anything"""
        x = contractors_init
        items = await contractor_loader_factory(x.tenant_1.id).load_contractors([])
        assert items == []


class TestContractorsGet:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tenants(
        self,
        contractors_init: TenantContractorsInit,
        contractor_loader_factory: LoaderFactory[TenantContractorsLoader],
    ) -> None:
        """Make sure dataloaders filter tenants"""

        x = contractors_init

        # Tenant 1 should only see tenant 1 contractors
        contractors = await contractor_loader_factory(x.tenant_1.id).get_contractors()
        assert {i.id for i in contractors} == {
            x.contractor_11.id,
            x.contractor_12.id,
            x.contractor_13.id,
        }

        # Tenant 2 should only see tenant 2 contractors
        contractors = await contractor_loader_factory(x.tenant_2.id).get_contractors()
        assert {i.id for i in contractors} == {x.contractor_21.id}

        # Invalid tenant
        contractors = await contractor_loader_factory(x.tenant_3.id).get_contractors()
        assert {i.id for i in contractors} == set()
