import datetime
import uuid
from typing import Callable, Collection, Literal, Tuple, Union

from worker_safety_service.dal.insights import (
    AggRiskLevelCount,
    InsightsManager,
    LibraryControlGroup,
    LibraryHazardGroup,
    RiskRankingByDate,
)
from worker_safety_service.models import (
    LibraryHazard,
    LibrarySiteCondition,
    LibraryTask,
    ProjectStatus,
    RiskLevel,
    TotalProjectLocationRiskScoreModel,
    TotalProjectRiskScoreModel,
    WorkPackage,
)


class TenantInsightsLoader:
    """
    Data wrappers for tenant manager functions.
    """

    def __init__(self, manager: InsightsManager, tenant_id: uuid.UUID):
        self.tenant_id = tenant_id
        self.__manager = manager

    async def filter_projects(
        self,
        project_ids: list[uuid.UUID] | None,
        project_statuses: list[ProjectStatus] | None,
        library_region_ids: list[uuid.UUID] | None,
        library_division_ids: list[uuid.UUID] | None,
        contractor_ids: list[uuid.UUID] | None,
    ) -> list[WorkPackage]:
        return await self.__manager.filter_projects(
            tenant_id=self.tenant_id,
            project_ids=project_ids,
            project_statuses=project_statuses,
            library_region_ids=library_region_ids,
            library_division_ids=library_division_ids,
            contractor_ids=contractor_ids,
        )

    async def project_risk_levels_by_date(
        self,
        start_date: datetime.date,
        end_date: datetime.date,
        project_ids: list[uuid.UUID],
    ) -> list[RiskRankingByDate]:
        return await self.__manager.project_risk_levels_by_date(
            start_date,
            end_date,
            project_ids,
            tenant_id=self.tenant_id,
        )

    async def location_risk_levels_by_date(
        self,
        location_ids: list[uuid.UUID],
        start_date: datetime.date,
        end_date: datetime.date,
    ) -> list[RiskRankingByDate]:
        return await self.__manager.location_risk_levels_by_date(
            location_ids,
            start_date,
            end_date,
            tenant_id=self.tenant_id,
        )

    async def task_risk_levels_by_date(
        self,
        task_ids: list[uuid.UUID],
        start_date: datetime.date,
        end_date: datetime.date,
    ) -> list[RiskRankingByDate]:
        return await self.__manager.task_risk_levels_by_date(
            task_ids, start_date, end_date, tenant_id=self.tenant_id
        )

    def aggregate_risk_counts(
        self,
        risk_models: Union[
            list[TotalProjectLocationRiskScoreModel], list[TotalProjectRiskScoreModel]
        ],
        value_to_risk_level: Callable[[float], RiskLevel],
    ) -> list[AggRiskLevelCount]:
        return self.__manager.aggregate_risk_counts(risk_models, value_to_risk_level)

    async def grouped_hazard_data(
        self,
        hazard_ids: list[uuid.UUID],
    ) -> list[LibraryHazardGroup]:
        return await self.__manager.grouped_hazard_data(
            hazard_ids, tenant_id=self.tenant_id
        )

    async def grouped_control_data(
        self,
        control_ids: list[uuid.UUID],
    ) -> list[LibraryControlGroup]:
        return await self.__manager.grouped_control_data(
            control_ids, tenant_id=self.tenant_id
        )

    async def get_project_data_for_library(
        self,
        *,
        library_hazard_id: uuid.UUID | None = None,
        library_control_id: uuid.UUID | None = None,
        project_ids: Collection[uuid.UUID] | None = None,
    ) -> Tuple[dict[uuid.UUID, set[uuid.UUID]], set[uuid.UUID]]:
        return await self.__manager.get_project_data_for_library(
            library_hazard_id=library_hazard_id,
            library_control_id=library_control_id,
            project_ids=project_ids,
            tenant_id=self.tenant_id,
        )

    async def get_location_data_for_library(
        self,
        *,
        library_hazard_id: uuid.UUID | None = None,
        library_control_id: uuid.UUID | None = None,
        location_ids: Collection[uuid.UUID] | None = None,
    ) -> dict[uuid.UUID, set[uuid.UUID]]:
        return await self.__manager.get_location_data_for_library(
            library_hazard_id=library_hazard_id,
            library_control_id=library_control_id,
            location_ids=location_ids,
            tenant_id=self.tenant_id,
        )

    async def get_control_ids_by_library_hazard_id(
        self,
        library_control_id: uuid.UUID,
        location_ids: Collection[uuid.UUID] | None = None,
    ) -> Tuple[
        dict[uuid.UUID, set[uuid.UUID]], dict[uuid.UUID, LibraryHazard], set[uuid.UUID]
    ]:
        return await self.__manager.get_control_ids_by_library_hazard_id(
            library_control_id, location_ids=location_ids, tenant_id=self.tenant_id
        )

    async def get_library_task_data_for_library(
        self,
        by_column: Literal["name", "category"],
        *,
        library_hazard_id: uuid.UUID | None = None,
        library_control_id: uuid.UUID | None = None,
        location_ids: Collection[uuid.UUID] | None = None,
    ) -> Tuple[dict[str, set[uuid.UUID]], dict[str, LibraryTask], set[uuid.UUID]]:
        return await self.__manager.get_library_task_data_for_library(
            by_column,
            library_hazard_id=library_hazard_id,
            library_control_id=library_control_id,
            location_ids=location_ids,
            tenant_id=self.tenant_id,
        )

    async def get_library_site_condition_data_for_library(
        self,
        *,
        library_hazard_id: uuid.UUID | None = None,
        location_ids: Collection[uuid.UUID] | None = None,
    ) -> Tuple[
        dict[str, set[uuid.UUID]], dict[str, LibrarySiteCondition], set[uuid.UUID]
    ]:
        return await self.__manager.get_library_site_condition_data_for_library(
            library_hazard_id=library_hazard_id,
            location_ids=location_ids,
            tenant_id=self.tenant_id,
        )
