import datetime
import functools
import uuid
from decimal import Decimal
from typing import Optional

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.exceptions import EntityNotFoundException
from worker_safety_service.dal.site_conditions import SiteConditionManager
from worker_safety_service.graphql.data_loaders.utils import create_order_by_hash
from worker_safety_service.models import (
    BaseHazardCreate,
    LibraryControl,
    LibraryHazard,
    LibrarySiteCondition,
    Location,
    SiteCondition,
    SiteConditionControl,
    SiteConditionCreate,
    SiteConditionHazard,
    User,
)
from worker_safety_service.risk_model.riskmodelreactor import RiskModelReactorInterface
from worker_safety_service.risk_model.triggers import (
    ProjectLocationSiteConditionsChanged,
)
from worker_safety_service.types import OrderBy


class TenantSiteConditionLoader:
    """
    Given project location site condition ids, load objects
    """

    def __init__(
        self,
        manager: SiteConditionManager,
        risk_model_reactor: RiskModelReactorInterface,
        tenant_id: uuid.UUID,
    ):
        self.tenant_id = tenant_id
        self.__risk_model_reactor = risk_model_reactor
        self.manually_added = DataLoader(
            load_fn=self.load_manually_added_site_conditions
        )
        self.manually_added_with_archived = DataLoader(
            load_fn=self.load_manually_added_site_conditions_with_archived
        )

        self.__manager = manager
        self.__hazards_map: dict[
            tuple[bool | None, int | None],
            DataLoader,
        ] = {}
        self.__controls_map: dict[
            tuple[bool | None, int | None],
            DataLoader,
        ] = {}

    async def create_site_condition(
        self,
        site_condition: SiteConditionCreate,
        hazards: list[BaseHazardCreate],
        user: User | None,
    ) -> SiteCondition:
        site_condition = await self.__manager.create_site_condition(
            site_condition=site_condition,
            hazards=hazards,
            user=user,
        )

        await self.__risk_model_reactor.add(
            ProjectLocationSiteConditionsChanged(
                project_location_id=site_condition.location_id
            )
        )

        return site_condition

    async def load_manually_added_site_conditions(
        self, ids: list[uuid.UUID]
    ) -> list[tuple[LibrarySiteCondition, SiteCondition] | None]:
        items = {
            i[1].id: i
            for i in await self.__manager.get_manually_added_site_conditions(
                ids=ids, tenant_id=self.tenant_id
            )
        }
        return [items.get(i) for i in ids]

    async def load_manually_added_site_conditions_with_archived(
        self, ids: list[uuid.UUID]
    ) -> list[tuple[LibrarySiteCondition, SiteCondition] | None]:
        items = {
            i[1].id: i
            for i in await self.__manager.get_manually_added_site_conditions(
                ids=ids, tenant_id=self.tenant_id, with_archived=True
            )
        }
        return [items.get(i) for i in ids]

    def hazards(
        self,
        is_applicable: bool | None = None,
        order_by: list[OrderBy] | None = None,
        filter_tenant_settings: bool | None = False,
    ) -> DataLoader:
        key = (
            is_applicable,
            create_order_by_hash(order_by),
        )
        dataloader = self.__hazards_map.get(key)
        if not dataloader:
            dataloader = self.__hazards_map[key] = DataLoader(
                load_fn=functools.partial(
                    self.load_hazards,
                    is_applicable=is_applicable,
                    order_by=order_by,
                    filter_tenant_settings=filter_tenant_settings,
                )
            )
        return dataloader

    async def load_hazards(
        self,
        site_condition_ids: list[uuid.UUID],
        is_applicable: bool | None = None,
        order_by: list[OrderBy] | None = None,
        filter_tenant_settings: bool | None = False,
    ) -> list[list[tuple[LibraryHazard, SiteConditionHazard]]]:
        items = await self.__manager.get_hazards_by_site_condition(
            site_condition_ids=site_condition_ids,
            is_applicable=is_applicable,
            order_by=order_by,
            tenant_id=self.tenant_id,
            filter_tenant_settings=filter_tenant_settings,
        )
        return [items[i] for i in site_condition_ids]

    def controls(
        self,
        is_applicable: bool | None = None,
        order_by: list[OrderBy] | None = None,
        filter_tenant_settings: bool | None = False,
    ) -> DataLoader:
        key = (
            is_applicable,
            create_order_by_hash(order_by),
        )
        dataloader = self.__controls_map.get(key)
        if not dataloader:
            dataloader = self.__controls_map[key] = DataLoader(
                load_fn=functools.partial(
                    self.load_controls,
                    is_applicable=is_applicable,
                    order_by=order_by,
                    filter_tenant_settings=filter_tenant_settings,
                )
            )
        return dataloader

    async def load_controls(
        self,
        hazard_ids: list[uuid.UUID],
        is_applicable: bool | None = None,
        order_by: list[OrderBy] | None = None,
        filter_tenant_settings: bool | None = False,
    ) -> list[list[tuple[LibraryControl, SiteConditionControl]]]:
        items = await self.__manager.get_controls_by_hazard(
            hazard_ids=hazard_ids,
            is_applicable=is_applicable,
            order_by=order_by,
            tenant_id=self.tenant_id,
            filter_tenant_settings=filter_tenant_settings,
        )
        return [items[i] for i in hazard_ids]

    async def get_manually_added_site_conditions(
        self,
        ids: list[uuid.UUID] | None = None,
        project_location_ids: list[uuid.UUID] | None = None,
        order_by: list[OrderBy] | None = None,
    ) -> list[tuple[LibrarySiteCondition, SiteCondition]]:
        """
        Retrieve project location site conditions
        """
        return await self.__manager.get_manually_added_site_conditions(
            ids=ids,
            location_ids=project_location_ids,
            order_by=order_by,
            tenant_id=self.tenant_id,
        )

    async def get_site_conditions(
        self,
        ids: list[uuid.UUID] | None = None,
        location_ids: list[uuid.UUID] | None = None,
        date: datetime.date | None = None,
        filter_tenant_settings: Optional[bool] = False,
        order_by: list[OrderBy] | None = None,
    ) -> list[tuple[LibrarySiteCondition, SiteCondition]]:
        """
        Retrieve project location site conditions
        """
        return await self.__manager.get_site_conditions(
            ids=ids,
            location_ids=location_ids,
            order_by=order_by,
            date=date,
            tenant_id=self.tenant_id,
            filter_tenant_settings=filter_tenant_settings,
        )

    async def get_adhoc_site_conditions(
        self,
        latitude: Decimal,
        longitude: Decimal,
        date: datetime.date,
        order_by: list[OrderBy] | None = None,
        filter_tenant_settings: bool | None = False,
    ) -> list[tuple[LibrarySiteCondition, SiteCondition, Location]]:
        """
        Retrieve adhoc location site conditions
        """
        return await self.__manager.get_adhoc_site_conditions(
            latitude=latitude,
            longitude=longitude,
            date=date,
            order_by=order_by,
            tenant_id=self.tenant_id,
            filter_tenant_settings=filter_tenant_settings,
        )

    async def archive_site_condition(
        self,
        id: uuid.UUID,
        user: User | None,
    ) -> None:
        site_conditions = await self.__manager.get_manually_added_site_conditions(
            ids=[id], tenant_id=self.tenant_id, with_archived=False
        )
        if len(site_conditions) == 0:
            raise EntityNotFoundException(entity_id=id, entity_type=SiteCondition)
        _, site_condition = site_conditions[0]

        await self.__manager.archive_site_condition(
            site_condition=site_condition, user=user
        )
        await self.__risk_model_reactor.add(
            ProjectLocationSiteConditionsChanged(
                project_location_id=site_condition.location_id
            )
        )
