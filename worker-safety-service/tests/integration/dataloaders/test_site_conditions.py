import uuid

import pytest

from tests.integration.dataloaders.conftest import (
    LoaderFactory,
    SiteConditionsHazardsControlsInit,
    SiteConditionsHazardsInit,
    SiteConditionsInit,
    assert_dataloader_filter_tenants,
    assert_dataloader_return_right_order,
    assert_mocked_dataloader_return_right_order,
)
from worker_safety_service.graphql.data_loaders.site_conditions import (
    TenantSiteConditionLoader,
)
from worker_safety_service.models import AsyncSession


class TestSiteConditionsGetManuallyAddedSiteConditions:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tenants(
        self,
        site_conditions_init: SiteConditionsInit,
        site_condition_loader_factory: LoaderFactory[TenantSiteConditionLoader],
    ) -> None:
        """Make sure dataloaders filter tenants"""

        x = site_conditions_init

        # Tenant 1 should only see tenant 1 site_conditions
        site_conditions = await site_condition_loader_factory(
            x.tenant_1.id
        ).get_manually_added_site_conditions()
        assert {i[1].id for i in site_conditions} == {
            x.site_condition_11.id,
            x.site_condition_12.id,
            x.site_condition_13.id,
        }

        # Tenant 2 should only see tenant 2 site_conditions
        site_conditions = await site_condition_loader_factory(
            x.tenant_2.id
        ).get_manually_added_site_conditions()
        assert {i[1].id for i in site_conditions} == {x.site_condition_21.id}

        # Invalid tenant
        site_conditions = await site_condition_loader_factory(
            x.tenant_3.id
        ).get_manually_added_site_conditions()
        assert {i[1].id for i in site_conditions} == set()


class TestSiteConditionsManuallyAdded:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tenants(
        self,
        site_conditions_init: SiteConditionsInit,
        site_condition_loader_factory: LoaderFactory[TenantSiteConditionLoader],
    ) -> None:
        """Make sure dataloaders filter tenants"""

        x = site_conditions_init
        all_ids = [
            x.site_condition_11.id,
            x.site_condition_12.id,
            x.site_condition_13.id,
            x.site_condition_21.id,
        ]

        # Tenant 1 should only see tenant 1 site_conditions
        dataloader = site_condition_loader_factory(x.tenant_1.id).manually_added
        site_conditions = await dataloader.load_many(all_ids)
        assert {i[1].id for i in site_conditions if i} == {
            x.site_condition_11.id,
            x.site_condition_12.id,
            x.site_condition_13.id,
        }

        # Tenant 2 should only see tenant 2 site_conditions
        dataloader = site_condition_loader_factory(x.tenant_2.id).manually_added
        site_conditions = await dataloader.load_many(all_ids)
        assert {i[1].id for i in site_conditions if i} == {x.site_condition_21.id}

        # Invalid tenant
        dataloader = site_condition_loader_factory(x.tenant_3.id).manually_added
        site_conditions = await dataloader.load_many(all_ids)
        assert {i[1].id for i in site_conditions if i} == set()


class TestSiteConditionsHazards:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tenants(
        self,
        site_conditions_hazards_init: tuple[
            SiteConditionsInit, SiteConditionsHazardsInit
        ],
        site_condition_loader_factory: LoaderFactory[TenantSiteConditionLoader],
    ) -> None:
        """Make sure dataloaders filter tenants"""

        t, h = site_conditions_hazards_init
        await assert_dataloader_filter_tenants(
            site_condition_loader_factory,
            "load_hazards",
            "hazards",
            [
                # Tenant 1 should only see tenant 1 site conditions
                (
                    t.tenant_1.id,
                    [t.site_condition_13.id, t.site_condition_21.id],
                    [[h.hazard_131_item], []],
                ),
                # Tenant 2 should only see tenant 2 site conditions
                (
                    t.tenant_2.id,
                    [t.site_condition_13.id, t.site_condition_21.id],
                    [[], [h.hazard_211_item]],
                ),
                # Invalid tenant
                (
                    t.tenant_3.id,
                    [t.site_condition_13.id, t.site_condition_21.id],
                    [[], []],
                ),
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_order(
        self,
        db_session: AsyncSession,
        site_conditions_hazards_init: tuple[
            SiteConditionsInit, SiteConditionsHazardsInit
        ],
        site_condition_loader_factory: LoaderFactory[TenantSiteConditionLoader],
    ) -> None:
        """Make sure order returned by dataloaders match request"""

        t, h = site_conditions_hazards_init
        await assert_mocked_dataloader_return_right_order(
            db_session,
            site_condition_loader_factory,
            "load_hazards",
            "hazards",
            t.tenant_1.id,
            filter_ids=[t.site_condition_11.id, t.site_condition_13.id],
            expected_result=[
                [h.hazard_111_item, h.hazard_112_item],
                [h.hazard_131_item],
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_missing(
        self,
        site_conditions_hazards_init: tuple[
            SiteConditionsInit, SiteConditionsHazardsInit
        ],
        site_condition_loader_factory: LoaderFactory[TenantSiteConditionLoader],
    ) -> None:
        """Return empty list and don't raise an error when site_condition don't exists"""

        t, h = site_conditions_hazards_init
        await assert_dataloader_return_right_order(
            site_condition_loader_factory,
            "load_hazards",
            "hazards",
            t.tenant_1.id,
            filter_ids=[t.site_condition_13.id, uuid.uuid4()],
            expected_result=[[h.hazard_131_item], []],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_empty(
        self,
        site_conditions_hazards_init: tuple[
            SiteConditionsInit, SiteConditionsHazardsInit
        ],
        site_condition_loader_factory: LoaderFactory[TenantSiteConditionLoader],
    ) -> None:
        """If an empty list is sent don't return anything"""
        t, _ = site_conditions_hazards_init
        items = await site_condition_loader_factory(t.tenant_1.id).load_hazards([])
        assert items == []


class TestSiteConditionsHazardsControls:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tenants(
        self,
        site_conditions_controls_init: tuple[
            SiteConditionsInit,
            SiteConditionsHazardsInit,
            SiteConditionsHazardsControlsInit,
        ],
        site_condition_loader_factory: LoaderFactory[TenantSiteConditionLoader],
    ) -> None:
        """Make sure dataloaders filter tenants"""

        t, h, c = site_conditions_controls_init
        await assert_dataloader_filter_tenants(
            site_condition_loader_factory,
            "load_controls",
            "controls",
            [
                # Tenant 1 should only see tenant 1 site conditions
                (
                    t.tenant_1.id,
                    [h.hazard_131.id, h.hazard_211.id],
                    [[c.control_1311_item], []],
                ),
                # Tenant 2 should only see tenant 2 site conditions
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
        site_conditions_controls_init: tuple[
            SiteConditionsInit,
            SiteConditionsHazardsInit,
            SiteConditionsHazardsControlsInit,
        ],
        site_condition_loader_factory: LoaderFactory[TenantSiteConditionLoader],
    ) -> None:
        """Make sure order returned by dataloaders match request"""

        t, h, c = site_conditions_controls_init
        await assert_mocked_dataloader_return_right_order(
            db_session,
            site_condition_loader_factory,
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
        site_conditions_controls_init: tuple[
            SiteConditionsInit,
            SiteConditionsHazardsInit,
            SiteConditionsHazardsControlsInit,
        ],
        site_condition_loader_factory: LoaderFactory[TenantSiteConditionLoader],
    ) -> None:
        """Return empty list and don't raise an error when hazard don't exists"""

        t, h, c = site_conditions_controls_init
        await assert_dataloader_return_right_order(
            site_condition_loader_factory,
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
        site_conditions_controls_init: tuple[
            SiteConditionsInit,
            SiteConditionsHazardsInit,
            SiteConditionsHazardsControlsInit,
        ],
        site_condition_loader_factory: LoaderFactory[TenantSiteConditionLoader],
    ) -> None:
        """If an empty list is sent don't return anything"""
        t, _, _ = site_conditions_controls_init
        items = await site_condition_loader_factory(t.tenant_1.id).load_controls([])
        assert items == []
