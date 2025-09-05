import datetime
import functools
import uuid

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models import RiskLevel
from worker_safety_service.risk_model.is_at_risk import (
    is_contractor_at_risk,
    is_crew_at_risk,
    is_supervisor_at_risk,
)
from worker_safety_service.risk_model.rankings import (
    project_location_risk_level_bulk,
    task_specific_risk_score_ranking_bulk,
    total_project_risk_level_bulk,
    total_task_risk_score_ranking_bulk,
)


class TenantRiskModelLoader:
    def __init__(self, manager: RiskModelMetricsManager, tenant_id: uuid.UUID):
        self.tenant_id = tenant_id
        self.contractor_safety_score_data = DataLoader(
            load_fn=self.load_is_contractor_at_risk
        )
        self.supervisor_safety_score_data = DataLoader(
            load_fn=self.load_is_supervisor_at_risk
        )
        self.crew_score_data = DataLoader(load_fn=self.load_is_crew_at_risk)

        self.__manager = manager
        self.__total_task_map: dict[datetime.date | None, DataLoader] = {}
        self.__task_specific_map: dict[datetime.date | None, DataLoader] = {}
        self.__project_location_map: dict[datetime.date | None, DataLoader] = {}
        self.__total_project_map: dict[datetime.date | None, DataLoader] = {}

    async def load_is_contractor_at_risk(
        self, contractor_ids: list[uuid.UUID]
    ) -> list[bool]:
        return await is_contractor_at_risk(self.__manager, contractor_ids)

    async def load_is_supervisor_at_risk(
        self, supervisor_ids: list[uuid.UUID]
    ) -> list[bool]:
        return await is_supervisor_at_risk(self.__manager, supervisor_ids)

    async def load_is_crew_at_risk(self, crew_ids: list[uuid.UUID]) -> list[bool]:
        return await is_crew_at_risk(self.__manager, crew_ids)

    def total_task_risk_score_ranking(
        self, date: datetime.date | None
    ) -> DataLoader[uuid.UUID, RiskLevel]:
        # TODO tenant?
        key = date
        loader = self.__total_task_map.get(key)
        if loader is None:
            supplier = functools.partial(
                total_task_risk_score_ranking_bulk,
                self.__manager,
                tenant_id=self.tenant_id,
                date=date,
            )
            loader = DataLoader(load_fn=supplier)
            self.__total_task_map[key] = loader
        return loader

    def task_specific_risk_score_ranking(
        self, date: datetime.date | None
    ) -> DataLoader:
        # TODO tenant?
        key = date
        loader = self.__task_specific_map.get(key)
        if loader is None:
            supplier = functools.partial(
                task_specific_risk_score_ranking_bulk,
                self.__manager,
                tenant_id=self.tenant_id,
                date=date,
            )
            loader = DataLoader(load_fn=supplier)
            self.__task_specific_map[key] = loader
        return loader

    def project_location_risk_level(self, date: datetime.date | None) -> DataLoader:
        # TODO tenant?
        key = date
        loader = self.__project_location_map.get(key)
        if loader is None:
            supplier = functools.partial(
                project_location_risk_level_bulk,
                self.__manager,
                tenant_id=self.tenant_id,
                date=date,
            )
            loader = DataLoader(load_fn=supplier)
            self.__project_location_map[key] = loader

        return loader

    def total_project_risk_level(self, date: datetime.date | None) -> DataLoader:
        # TODO tenant?
        key = date
        loader = self.__total_project_map.get(key)
        if loader is None:
            supplier = functools.partial(
                total_project_risk_level_bulk,
                self.__manager,
                tenant_id=self.tenant_id,
                date=date,
            )
            loader = DataLoader(load_fn=supplier)
            self.__total_project_map[key] = loader

        return loader
