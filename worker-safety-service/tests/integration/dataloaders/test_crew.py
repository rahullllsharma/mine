import uuid

import pytest

from tests.integration.dataloaders.conftest import (
    LoaderFactory,
    TenantCrewInit,
    assert_dataloader_filter_tenants,
    assert_dataloader_return_right_order,
    assert_mocked_dataloader_return_right_order,
)
from worker_safety_service.graphql.data_loaders.crew import TenantCrewLoader
from worker_safety_service.models import AsyncSession


class TestCrewMe:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_loader_filters_tenants(
        self,
        crew_init: TenantCrewInit,
        crew_loader_factory: LoaderFactory[TenantCrewLoader],
    ) -> None:
        """Make sure dataloaders filter tenants"""

        x = crew_init
        await assert_dataloader_filter_tenants(
            crew_loader_factory,
            "load_crew",
            "me",
            [
                # Tenant 1 should only see tenant 1 crew
                (
                    x.tenant_1.id,
                    [x.crew_13.id, x.crew_21.id],
                    [x.crew_13, None],
                ),
                # Tenant 2 should only see tenant 2 crew
                (
                    x.tenant_2.id,
                    [x.crew_13.id, x.crew_21.id],
                    [None, x.crew_21],
                ),
                # Invalid tenant
                (
                    x.tenant_3.id,
                    [x.crew_13.id, x.crew_21.id],
                    [None, None],
                ),
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_loader_returns_result_in_specified_order(
        self,
        db_session: AsyncSession,
        crew_init: TenantCrewInit,
        crew_loader_factory: LoaderFactory[TenantCrewLoader],
    ) -> None:
        """Make sure order returned by dataloaders match request"""

        x = crew_init
        await assert_mocked_dataloader_return_right_order(
            db_session,
            crew_loader_factory,
            "load_crew",
            "me",
            x.tenant_1.id,
            filter_ids=[x.crew_11.id, x.crew_13.id],
            expected_result=[x.crew_11, x.crew_13],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_non_existent_crew_returns_empty(
        self,
        crew_init: TenantCrewInit,
        crew_loader_factory: LoaderFactory[TenantCrewLoader],
    ) -> None:
        """Return empty list and don't raise an error when crew don't exists"""

        x = crew_init
        await assert_dataloader_return_right_order(
            crew_loader_factory,
            "load_crew",
            "me",
            x.tenant_1.id,
            filter_ids=[x.crew_13.id, uuid.uuid4()],
            expected_result=[x.crew_13, None],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_empty_input_returns_empty(
        self,
        crew_init: TenantCrewInit,
        crew_loader_factory: LoaderFactory[TenantCrewLoader],
    ) -> None:
        """If an empty list is sent don't return anything"""
        x = crew_init
        items = await crew_loader_factory(x.tenant_1.id).load_crew([])
        assert items == []
