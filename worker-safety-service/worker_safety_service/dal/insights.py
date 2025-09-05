import asyncio
import datetime
import uuid
from collections import defaultdict
from operator import itemgetter
from typing import Callable, Collection, Literal, Tuple, TypedDict, Union

import pendulum
from sqlmodel import and_, col, select

import worker_safety_service.models as models
import worker_safety_service.utils as utils
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.site_conditions import SiteConditionManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.models import (
    AsyncSession,
    RiskLevel,
    WorkPackage,
    set_order_by,
)
from worker_safety_service.risk_model.rankings import (
    project_location_risk_level_bulk,
    task_specific_risk_score_ranking_bulk,
    total_project_risk_level_bulk,
)
from worker_safety_service.types import OrderBy, OrderByDirection


class AggRiskLevelCount(TypedDict, total=False):
    count: int
    date: datetime.date
    risk_level: models.RiskLevel


class RiskRankingByDate(TypedDict):
    entity_id: uuid.UUID
    date: datetime.date
    risk_level: models.RiskLevel


def by_date_and_level(lr: AggRiskLevelCount) -> str:
    return lr["date"].strftime("%Y-%m-%d") + str(lr["risk_level"])


class LibraryHazardGroup(TypedDict):
    hazard_ids: set[uuid.UUID]
    library_hazard: models.LibraryHazard


class LibraryControlGroup(TypedDict):
    control_ids: set[uuid.UUID]
    library_control: models.LibraryControl


class InsightsManager:
    def __init__(
        self,
        session: AsyncSession,
        task_manager: TaskManager,
        site_condition_manager: SiteConditionManager,
        risk_model_metrics_manager: RiskModelMetricsManager,
    ):
        self.session = session
        self.task_manager = task_manager
        self.site_condition_manager = site_condition_manager
        self.risk_model_metrics_manager = risk_model_metrics_manager

    async def filter_projects(
        self,
        tenant_id: uuid.UUID,
        project_ids: list[uuid.UUID] | None,
        project_statuses: list[models.ProjectStatus] | None,
        library_region_ids: list[uuid.UUID] | None,
        library_division_ids: list[uuid.UUID] | None,
        contractor_ids: list[uuid.UUID] | None,
    ) -> list[models.WorkPackage]:
        stmt = select(models.WorkPackage)

        filters = [
            col(models.WorkPackage.archived_at).is_(None),
            col(models.WorkPackage.tenant_id) == tenant_id,
        ]

        if project_ids:
            filters.append(col(models.WorkPackage.id).in_(project_ids))

        if project_statuses:
            filters.append(col(models.WorkPackage.status).in_(project_statuses))

        if library_region_ids:
            filters.append(col(models.WorkPackage.region_id).in_(library_region_ids))

        if library_division_ids:
            filters.append(
                col(models.WorkPackage.division_id).in_(library_division_ids)
            )

        if contractor_ids:
            filters.append(col(models.WorkPackage.contractor_id).in_(contractor_ids))

        stmt = stmt.where(and_(*filters))
        stmt = set_order_by(
            models.WorkPackage,
            stmt,
            order_by=[OrderBy(field="name", direction=OrderByDirection.ASC)],
        )

        return (await self.session.exec(stmt)).all()

    def aggregate_risk_counts(
        self,
        risk_models: Union[
            list[models.TotalProjectLocationRiskScoreModel],
            list[models.TotalProjectRiskScoreModel],
        ],
        value_to_risk_level: Callable[[float], models.RiskLevel],
    ) -> list[AggRiskLevelCount]:
        # create a list of AggRiskLevelCount to group on date and level
        agg_risks = [
            AggRiskLevelCount(
                date=x.date,
                risk_level=value_to_risk_level(x.value),
            )
            for x in risk_models
        ]

        # group by date and risk_level. be sure to sort before groupby!
        risk_counts = []
        for _, group in utils.groupby(agg_risks, key=by_date_and_level).items():
            lrs = list(group)  # convert subgroup iter to list
            lr = lrs[0]  # grab first in group
            lr["count"] = len(lrs)
            risk_counts.append(lr)

        return risk_counts

    async def project_risk_levels_by_date(
        self,
        start_date: datetime.date,
        end_date: datetime.date,
        project_ids: list[uuid.UUID],
        tenant_id: uuid.UUID,
    ) -> list[RiskRankingByDate]:
        """
        Returns a list of RiskRankingByDate objects, each containing
        the ID of the entity (in this case Project), date and RiskLevel.
        `start_date` and `end_date` are used to filter TotalProjectRiskScores,
        inclusively.
        """

        period = pendulum.Interval(start_date, end_date)
        risk_level_lists: list[list[RiskLevel]] = await asyncio.gather(
            *[
                total_project_risk_level_bulk(
                    metrics_manager=self.risk_model_metrics_manager,
                    project_ids=project_ids,
                    tenant_id=tenant_id,
                    date=date,
                )
                for date in period
            ]
        )

        # generating RiskRankings and adding them to a list already in a sorted position
        return sorted(
            (
                RiskRankingByDate(
                    entity_id=project_id,
                    date=date,
                    risk_level=risk_level,
                )
                for date, risk_list in zip(period, risk_level_lists)
                for project_id, risk_level in zip(project_ids, risk_list)
            ),
            key=itemgetter("date", "entity_id"),
        )

    async def location_risk_levels_by_date(
        self,
        location_ids: list[uuid.UUID],
        start_date: datetime.date,
        end_date: datetime.date,
        tenant_id: uuid.UUID,
    ) -> list[RiskRankingByDate]:
        """
        Returns a list of RiskRankingByDate objects, each containing
        the ID of the entity (in this case Location), date and RiskLevel.
        `start_date` and `end_date` are used to filter LocationRiskScores,
        inclusively.
        """

        period = pendulum.Interval(start_date, end_date)
        risk_level_lists: list[list[RiskLevel]] = await asyncio.gather(
            *[
                project_location_risk_level_bulk(
                    metrics_manager=self.risk_model_metrics_manager,
                    project_location_ids=location_ids,
                    tenant_id=tenant_id,
                    date=date,
                )
                for date in period
            ]
        )

        rankings = []
        for date, risk_list in zip(period, risk_level_lists):
            for location_id, risk_level in zip(location_ids, risk_list):
                risk_ranking: RiskRankingByDate = {
                    "entity_id": location_id,
                    "date": date,
                    "risk_level": risk_level,
                }
                rankings.append(risk_ranking)

        # order by date and location id
        rankings.sort(key=itemgetter("date", "entity_id"))

        return rankings

    async def task_risk_levels_by_date(
        self,
        task_ids: list[uuid.UUID],
        start_date: datetime.date,
        end_date: datetime.date,
        tenant_id: uuid.UUID,
    ) -> list[RiskRankingByDate]:
        """
        Returns a list of RiskRankingByDate objects, each containing
        the ID of the entity (in this case Location), date and RiskLevel.
        `start_date` and `end_date` are used to filter LocationRiskScores,
        inclusively.
        """

        period = pendulum.Interval(start_date, end_date)
        risk_level_lists: list[list[RiskLevel]] = await asyncio.gather(
            *[
                task_specific_risk_score_ranking_bulk(
                    metrics_manager=self.risk_model_metrics_manager,
                    project_task_ids=task_ids,
                    tenant_id=tenant_id,
                    date=date,
                )
                for date in period
            ]
        )

        rankings = []
        for date, risk_list in zip(period, risk_level_lists):
            for location_id, risk_level in zip(task_ids, risk_list):
                risk_ranking: RiskRankingByDate = {
                    "entity_id": location_id,
                    "date": date,
                    "risk_level": risk_level,
                }
                rankings.append(risk_ranking)

        # order by date and location id
        rankings.sort(key=itemgetter("date", "entity_id"))

        return rankings

    async def grouped_hazard_data(
        self,
        hazard_ids: list[uuid.UUID],
        tenant_id: uuid.UUID | None = None,
    ) -> list[LibraryHazardGroup]:
        tasks_res = await self.task_manager.get_hazards(
            ids=hazard_ids,
            tenant_id=tenant_id,
            with_archived=True,
        )
        conds_res = await self.site_condition_manager.get_hazards(
            ids=hazard_ids,
            tenant_id=tenant_id,
            with_archived=True,
        )

        hazards_by_library: dict[uuid.UUID, LibraryHazardGroup] = {}
        # acc some data by library_hazard_id
        for library_hazard, hazard in [*tasks_res, *conds_res]:
            if hazards_by_library.get(library_hazard.id):
                hazards_by_library[library_hazard.id]["hazard_ids"].add(hazard.id)
            else:
                hazards_by_library[library_hazard.id] = LibraryHazardGroup(
                    hazard_ids={hazard.id},
                    library_hazard=library_hazard,
                )

        return list(hazards_by_library.values())

    async def grouped_control_data(
        self,
        control_ids: list[uuid.UUID],
        tenant_id: uuid.UUID | None = None,
    ) -> list[LibraryControlGroup]:
        tasks_res = await self.task_manager.get_controls(
            ids=control_ids,
            tenant_id=tenant_id,
            with_archived=True,
        )
        conds_res = await self.site_condition_manager.get_controls(
            ids=control_ids,
            tenant_id=tenant_id,
            with_archived=True,
        )

        controls_by_lib_control_id: dict[uuid.UUID, LibraryControlGroup] = dict()
        # acc some data by library_control_id
        for library_control, control in [*tasks_res, *conds_res]:
            if controls_by_lib_control_id.get(library_control.id):
                controls_by_lib_control_id[library_control.id]["control_ids"].add(
                    control.id
                )
            else:
                controls_by_lib_control_id[library_control.id] = LibraryControlGroup(
                    control_ids={control.id},
                    library_control=library_control,
                )

        return list(controls_by_lib_control_id.values())

    async def get_project_data_for_library(
        self,
        *,
        library_hazard_id: uuid.UUID | None = None,
        library_control_id: uuid.UUID | None = None,
        project_ids: Collection[uuid.UUID] | None = None,
        tenant_id: uuid.UUID | None = None,
    ) -> Tuple[dict[uuid.UUID, set[uuid.UUID]], set[uuid.UUID]]:
        """
        For the given library_hazard_id or library_control_id, returns a dict from project.id -> set[hazard/control.id],
        and set[location.id] for those hazards/controls.

        Fetches from both task and site conditions.
        Filters results using the passed project_ids.
        """

        (
            task_column_id,
            task_filter,
            site_condition_column_id,
            site_condition_filter,
            relate_with_controls,
        ) = validate_for_library_data(
            library_hazard_id,
            library_control_id,
        )

        tasks_stmt = select(
            models.WorkPackage.id,
            models.Location.id,
            task_column_id,
        ).where(
            task_filter,
            models.Task.id == models.TaskHazard.task_id,
            models.Location.id == models.Task.location_id,
            models.WorkPackage.id == models.Location.project_id,
            col(models.WorkPackage.id).in_(project_ids),
        )
        if relate_with_controls:
            tasks_stmt = tasks_stmt.where(
                models.TaskHazard.id == models.TaskControl.task_hazard_id
            )
        if tenant_id:
            tasks_stmt = tasks_stmt.where(WorkPackage.tenant_id == tenant_id)

        sc_stmt = select(
            models.WorkPackage.id,
            models.Location.id,
            site_condition_column_id,
        ).where(
            site_condition_filter,
            models.SiteCondition.id == models.SiteConditionHazard.site_condition_id,
            models.Location.id == models.SiteCondition.location_id,
            models.WorkPackage.id == models.Location.project_id,
            col(models.WorkPackage.id).in_(project_ids),
        )
        if relate_with_controls:
            sc_stmt = sc_stmt.where(
                models.SiteConditionHazard.id
                == models.SiteConditionControl.site_condition_hazard_id
            )
        if tenant_id:
            sc_stmt = sc_stmt.where(WorkPackage.tenant_id == tenant_id)

        task_scalar, sc_scalar = await asyncio.gather(
            self.session.exec(tasks_stmt),
            self.session.exec(sc_stmt),
        )

        # group locations, group hazards/controls by project
        ids_by_project: defaultdict[uuid.UUID, set] = defaultdict(set)
        location_ids = set()
        for type_ids in (task_scalar.all(), sc_scalar.all()):
            for project_id, location_id, type_id in type_ids:
                ids_by_project[project_id].add(type_id)
                location_ids.add(location_id)
        return ids_by_project, location_ids

    async def get_location_data_for_library(
        self,
        *,
        library_hazard_id: uuid.UUID | None = None,
        library_control_id: uuid.UUID | None = None,
        location_ids: Collection[uuid.UUID] | None = None,
        tenant_id: uuid.UUID | None = None,
    ) -> dict[uuid.UUID, set[uuid.UUID]]:
        """
        For the given library_hazard_id or library_control_id, returns a dict from
        location_id -> set(hazard/control_id).
        Fetches from both task and site conditions.
        Filters results using the passed location_ids.
        """

        (
            task_column_id,
            task_filter,
            site_condition_column_id,
            site_condition_filter,
            relate_with_controls,
        ) = validate_for_library_data(
            library_hazard_id,
            library_control_id,
        )

        tasks_stmt = select(models.Location.id, task_column_id).where(
            task_filter,
            models.Task.id == models.TaskHazard.task_id,
            models.Location.id == models.Task.location_id,
            col(models.Location.id).in_(location_ids),
        )
        if relate_with_controls:
            tasks_stmt = tasks_stmt.where(
                models.TaskHazard.id == models.TaskControl.task_hazard_id
            )
        if tenant_id:
            tasks_stmt = tasks_stmt.where(
                models.WorkPackage.id == models.Location.project_id,
                WorkPackage.tenant_id == tenant_id,
            )

        sc_stmt = select(models.Location.id, site_condition_column_id).where(
            site_condition_filter,
            models.SiteCondition.id == models.SiteConditionHazard.site_condition_id,
            models.Location.id == models.SiteCondition.location_id,
            col(models.Location.id).in_(location_ids),
        )
        if relate_with_controls:
            sc_stmt = sc_stmt.where(
                models.SiteConditionHazard.id
                == models.SiteConditionControl.site_condition_hazard_id
            )
        if tenant_id:
            sc_stmt = sc_stmt.where(
                models.WorkPackage.id == models.Location.project_id,
                WorkPackage.tenant_id == tenant_id,
            )

        tasks_scalar, sc_scalar = await asyncio.gather(
            self.session.exec(tasks_stmt),
            self.session.exec(sc_stmt),
        )

        ids_by_location: defaultdict[uuid.UUID, set] = defaultdict(set)
        for type_ids in (tasks_scalar.all(), sc_scalar.all()):
            for location_id, type_id in type_ids:
                ids_by_location[location_id].add(type_id)
        return ids_by_location

    async def get_control_ids_by_library_hazard_id(
        self,
        library_control_id: uuid.UUID,
        location_ids: Collection[uuid.UUID] | None = None,
        tenant_id: uuid.UUID | None = None,
    ) -> Tuple[
        dict[uuid.UUID, set[uuid.UUID]],
        dict[uuid.UUID, models.LibraryHazard],
        set[uuid.UUID],
    ]:
        """
        For the given library_control_id, returns:
        - a dict from library_hazard.id -> set[control.id]
        - a dict from library_hazard.id -> library_hazard
        - a set[location.id] relevant for those controls

        Fetches from both task and site conditions.
        Filters results using the passed project_ids.
        """

        tasks_stmt = select(
            models.LibraryHazard,
            models.Location.id,
            models.TaskControl.id,
        ).where(
            models.TaskControl.library_control_id == library_control_id,
            models.TaskHazard.id == models.TaskControl.task_hazard_id,
            models.Task.id == models.TaskHazard.task_id,
            models.Location.id == models.Task.location_id,
            col(models.Location.id).in_(location_ids),
            models.LibraryHazard.id == models.TaskHazard.library_hazard_id,
        )
        if tenant_id:
            tasks_stmt = tasks_stmt.where(
                WorkPackage.tenant_id == tenant_id,
                models.WorkPackage.id == models.Location.project_id,
            )

        sc_stmt = select(
            models.LibraryHazard,
            models.Location.id,
            models.SiteConditionControl.id,
        ).where(
            models.SiteConditionControl.library_control_id == library_control_id,
            models.SiteConditionHazard.id
            == models.SiteConditionControl.site_condition_hazard_id,
            models.SiteCondition.id == models.SiteConditionHazard.site_condition_id,
            models.Location.id == models.SiteCondition.location_id,
            models.WorkPackage.id == models.Location.project_id,
            col(models.Location.id).in_(location_ids),
            models.LibraryHazard.id == models.SiteConditionHazard.library_hazard_id,
        )
        if tenant_id:
            sc_stmt = sc_stmt.where(
                WorkPackage.tenant_id == tenant_id,
                models.WorkPackage.id == models.Location.project_id,
            )

        tasks_scalar, sc_scalar = await asyncio.gather(
            self.session.exec(tasks_stmt),
            self.session.exec(sc_stmt),
        )

        # group locations, group controls by project
        control_ids_by_lib_hazard: defaultdict[uuid.UUID, set] = defaultdict(set)
        library_hazard_by_id = dict()
        location_ids = set()
        for library_hazard, location_id, control_id in (
            tasks_scalar.all() + sc_scalar.all()
        ):
            control_ids_by_lib_hazard[library_hazard.id].add(control_id)
            library_hazard_by_id[library_hazard.id] = library_hazard
            location_ids.add(location_id)

        return control_ids_by_lib_hazard, library_hazard_by_id, location_ids

    async def get_library_task_data_for_library(
        self,
        by_column: Literal["name", "category"],
        *,
        library_hazard_id: uuid.UUID | None = None,
        library_control_id: uuid.UUID | None = None,
        location_ids: Collection[uuid.UUID] | None = None,
        tenant_id: uuid.UUID | None = None,
    ) -> Tuple[
        dict[str, set[uuid.UUID]],
        dict[str, models.LibraryTask],
        set[uuid.UUID],
    ]:
        """
        For the given library_hazard_id or library_control_id, returns:
        - a dict from library_task.name/category -> set[hazard/control.id]
        - a dict from library_task.name/category -> library_task
        - a set[location.id] relevant for those hazards/controls

        Filters results using the passed project_ids.
        """

        if by_column not in ("name", "category"):
            raise ValueError("by_column must be name or category")

        by_name = by_column == "name"

        (
            task_column_id,
            task_filter,
            _,
            _,
            relate_with_controls,
        ) = validate_for_library_data(
            library_hazard_id,
            library_control_id,
        )

        tasks_stmt = select(
            models.LibraryTask,
            models.Location.id,
            task_column_id,
        ).where(
            task_filter,
            models.Task.id == models.TaskHazard.task_id,
            models.Location.id == models.Task.location_id,
            col(models.Location.id).in_(location_ids),
            models.LibraryTask.id == models.Task.library_task_id,
        )
        if relate_with_controls:
            tasks_stmt = tasks_stmt.where(
                models.TaskHazard.id == models.TaskControl.task_hazard_id
            )
        if tenant_id:
            tasks_stmt = tasks_stmt.where(
                WorkPackage.tenant_id == tenant_id,
                models.WorkPackage.id == models.Location.project_id,
            )
        task_id_tuples = (await self.session.exec(tasks_stmt)).all()

        # group locations, group hazards/controls by project
        ids_by_task: defaultdict[str, set[uuid.UUID]] = defaultdict(set)
        library_tasks = {}
        location_ids = set()
        for library_task, location_id, type_id in task_id_tuples:
            by_value = (
                library_task.name if by_name else library_task.category or "No category"
            )
            ids_by_task[by_value].add(type_id)
            library_tasks[by_value] = library_task
            location_ids.add(location_id)

        return ids_by_task, library_tasks, location_ids

    async def get_library_site_condition_data_for_library(
        self,
        *,
        library_hazard_id: uuid.UUID | None = None,
        location_ids: Collection[uuid.UUID] | None = None,
        tenant_id: uuid.UUID | None = None,
    ) -> Tuple[
        dict[str, set[uuid.UUID]],
        dict[str, models.LibrarySiteCondition],
        set[uuid.UUID],
    ]:
        """
        For the given library_hazard_id returns:
        - a dict from library_site_condition.name -> set[hazard.id]
        - a dict from library_site_condition.name -> library_site_condition
        - a set[location.id] relevant for those hazards

        Filters results using the passed project_ids.
        """

        (
            _,
            _,
            site_condition_column_id,
            site_condition_filter,
            _,
        ) = validate_for_library_data(
            library_hazard_id,
            None,
        )

        site_conditions_stmt = select(
            models.LibrarySiteCondition,
            models.Location.id,
            site_condition_column_id,
        ).where(
            site_condition_filter,
            models.SiteCondition.id == models.SiteConditionHazard.site_condition_id,
            models.Location.id == models.SiteCondition.location_id,
            col(models.Location.id).in_(location_ids),
            models.LibrarySiteCondition.id
            == models.SiteCondition.library_site_condition_id,
        )
        if tenant_id:
            site_conditions_stmt = site_conditions_stmt.where(
                WorkPackage.tenant_id == tenant_id,
                models.WorkPackage.id == models.Location.project_id,
            )
        site_condition_id_tuples = (await self.session.exec(site_conditions_stmt)).all()

        # group locations, group hazards/controls by project
        ids_by_site_condition: defaultdict[str, set[uuid.UUID]] = defaultdict(set)
        library_site_conditions = {}
        location_ids = set()
        for library_site_condition, location_id, type_id in site_condition_id_tuples:
            by_value = library_site_condition.name
            ids_by_site_condition[by_value].add(type_id)
            library_site_conditions[by_value] = library_site_condition
            location_ids.add(location_id)

        return ids_by_site_condition, library_site_conditions, location_ids


def validate_for_library_data(
    library_hazard_id: uuid.UUID | None,
    library_control_id: uuid.UUID | None,
) -> tuple[uuid.UUID, bool, uuid.UUID, bool, bool]:
    relate_with_controls = False
    if library_hazard_id is not None:
        assert not library_control_id
        task_column_id = models.TaskHazard.id
        task_filter = models.TaskHazard.library_hazard_id == library_hazard_id
        site_condition_column_id = models.SiteConditionHazard.id
        site_condition_filter = (
            models.SiteConditionHazard.library_hazard_id == library_hazard_id
        )
    elif library_control_id is not None:
        task_column_id = models.TaskControl.id
        task_filter = models.TaskControl.library_control_id == library_control_id
        site_condition_column_id = models.SiteConditionControl.id
        site_condition_filter = (
            models.SiteConditionControl.library_control_id == library_control_id
        )
        relate_with_controls = True
    else:
        raise NotImplementedError()

    return (
        task_column_id,
        task_filter,
        site_condition_column_id,
        site_condition_filter,
        relate_with_controls,
    )
