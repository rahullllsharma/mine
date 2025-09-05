import datetime
import uuid
from collections import Counter, defaultdict
from operator import attrgetter
from typing import Callable, List, Optional, Tuple, Union

import strawberry

import worker_safety_service.models as models
import worker_safety_service.models.daily_reports as daily_reports
import worker_safety_service.utils as utils
from worker_safety_service.context import Info
from worker_safety_service.graphql.common import TaskOrderByInput, order_by_to_pydantic
from worker_safety_service.graphql.types import (
    LibraryControlType,
    LibraryHazardType,
    LibrarySiteConditionType,
    LibraryTaskType,
    ProjectLocationType,
    ProjectStatus,
    ProjectType,
    RiskLevel,
    TaskType,
)
from worker_safety_service.models import (
    LibraryTask,
    Location,
    Task,
    TaskSpecificRiskScoreModel,
    TotalProjectLocationRiskScoreModel,
    TotalProjectRiskScoreModel,
    WorkPackage,
)
from worker_safety_service.types import OrderBy, OrderByDirection


@strawberry.type(name="RiskLevelByDate")
class RiskLevelByDate:
    date: datetime.date
    risk_level: RiskLevel


def risk_level_by_date(
    risk_models: Optional[
        Union[
            List[TotalProjectLocationRiskScoreModel],
            List[TotalProjectRiskScoreModel],
            List[TaskSpecificRiskScoreModel],
        ]
    ],
    value_to_risk_level: Callable[[float], RiskLevel],
) -> List[RiskLevelByDate]:
    return [
        RiskLevelByDate(
            risk_level=value_to_risk_level(risk_model.value),
            date=risk_model.date,
        )
        for risk_model in risk_models or []
    ]


def get_start_end_date(
    root: Union[
        "ProjectPlanningType",
        "ProjectLearningsType",
        "PortfolioPlanningType",
        "PortfolioLearningsType",
    ],
) -> Tuple[datetime.date, datetime.date]:
    """
    Pulls the start/end date off of the input type for each root query.
    """
    start_date = None
    end_date = None
    if isinstance(root, ProjectPlanningType):
        start_date = root.project_planning_input.start_date
        end_date = root.project_planning_input.end_date
    elif isinstance(root, ProjectLearningsType):
        start_date = root.project_learnings_input.start_date
        end_date = root.project_learnings_input.end_date
    elif isinstance(root, PortfolioPlanningType):
        start_date = root.portfolio_planning_input.start_date
        end_date = root.portfolio_planning_input.end_date
    elif isinstance(root, PortfolioLearningsType):
        start_date = root.portfolio_learnings_input.start_date
        end_date = root.portfolio_learnings_input.end_date

    assert start_date, "Asserting that start_date was found on root"
    assert end_date, "Asserting that end_date was found on root"
    return start_date, end_date


async def get_locations_from_context(
    root: Union[
        "ProjectLearningsType",
        "PortfolioLearningsType",
    ],
    info: Info,
) -> List[Location]:
    """
    Pulls or fetches location_ids for various root insight types.
    """
    if isinstance(root, ProjectLearningsType):
        return root.locations
    elif isinstance(root, PortfolioLearningsType):
        # get location_ids for root.projects
        location_groups = await info.context.projects.locations().load_many(
            [p.id for p in root.projects]
        )
        return [loc for location_group in location_groups for loc in location_group]
    return []


async def get_location_ids(
    root: Union[
        "ProjectLearningsType",
        "PortfolioLearningsType",
    ],
    info: Info,
) -> List[uuid.UUID]:
    locations = await get_locations_from_context(root, info)
    return [loc.id for loc in locations]


################################################################################
# LocationRiskOverTime
################################################################################


@strawberry.type(name="LocationRiskLevelCount")
class LocationRiskLevelCount:
    date: datetime.date
    risk_level: RiskLevel
    count: int


async def get_location_risk_level_over_time(
    root: Union["ProjectPlanningType", "ProjectLearningsType"],
    info: Info,
) -> List[LocationRiskLevelCount]:
    """
    Fetches risks by date for the root.project_planning_input start/end dates,
    then aggregates the risk counts by date and level.
    """

    locations = root.locations
    location_ids = [x.id for x in locations]

    start_date, end_date = get_start_end_date(root)
    loc_risk_models = await info.context.insights.location_risk_levels_by_date(
        location_ids=location_ids,
        start_date=start_date,
        end_date=end_date,
    )

    _counter = Counter(
        map(lambda lrm: (lrm["date"], lrm["risk_level"]), loc_risk_models)
    )
    # TODO: Check if this needs to be exaustive or not.
    ret = []
    for key, count in _counter.items():
        if key[1] in (models.RiskLevel.UNKNOWN, models.RiskLevel.RECALCULATING):
            continue  # the original method didn't include these types of value, so we're keeping this
        ret.append(LocationRiskLevelCount(date=key[0], risk_level=key[1], count=count))

    return ret


################################################################################
# LocationRiskByDate
################################################################################


@strawberry.type(name="LocationRiskLevelByDate")
class LocationRiskLevelByDate:
    risk_level_by_date: List[RiskLevelByDate]
    location: ProjectLocationType | None
    location_name: str
    project_name: str


async def get_location_risk_level_by_date(
    root: "ProjectPlanningType",
    info: Info,
) -> List[LocationRiskLevelByDate]:
    # TODO: Check where sorting should happen. There is a test for that but we cannot find it in the code.
    # tests.integration.queries.insights.test_project_location_risk.test_planning_location_risk_sorting
    """
    Fetches and returns locations along with a list of RiskByDate, for the
    passed start/end dates.
    """

    locations = root.locations
    location_ids = [x.id for x in locations]

    risk_rankings = await info.context.insights.location_risk_levels_by_date(
        location_ids=location_ids,
        start_date=root.project_planning_input.start_date,
        end_date=root.project_planning_input.end_date,
    )
    risk_rankings_by_location: dict[uuid.UUID, list[RiskLevelByDate]] = defaultdict(
        list
    )
    for risk_ranking in risk_rankings:
        if risk_ranking["risk_level"] in (
            models.RiskLevel.UNKNOWN,
            models.RiskLevel.RECALCULATING,
        ):
            continue  # the original method didn't include these types of value, so we're keeping this

        _risk_lvl_by_date = RiskLevelByDate(
            date=risk_ranking["date"], risk_level=risk_ranking["risk_level"]
        )

        location_id = risk_ranking["entity_id"]
        risk_rankings_by_location[location_id].append(_risk_lvl_by_date)

    return [
        LocationRiskLevelByDate(
            location=ProjectLocationType.from_orm(location),
            location_name=location.name,
            project_name=location.project.name if location.project is not None else "",
            risk_level_by_date=risk_rankings_by_location[location.id],
        )
        for location in locations
    ]


################################################################################
# TaskRiskByDate
################################################################################


@strawberry.type(name="TaskRiskLevelByDate")
class TaskRiskLevelByDate:
    risk_level_by_date: List[RiskLevelByDate]
    task: TaskType | None
    task_name: str
    location_name: str
    project_name: str


async def get_task_risk_level_by_date(
    info: Info,
    task_tuples: List[Tuple[LibraryTask, Task]],
    start_date: datetime.date,
    end_date: datetime.date,
) -> List[TaskRiskLevelByDate]:
    """
    Fetches and returns tasks alongside a list of RiskByDate, for the
    passed start/end dates.
    """

    task_ids = [task.id for _, task in task_tuples]

    risk_rankings = await info.context.insights.task_risk_levels_by_date(
        task_ids=task_ids,
        start_date=start_date,
        end_date=end_date,
    )

    risk_rankings_by_task: dict[uuid.UUID, list[RiskLevelByDate]] = defaultdict(list)
    for risk_ranking in risk_rankings:
        if risk_ranking["risk_level"] in (
            models.RiskLevel.UNKNOWN,
            models.RiskLevel.RECALCULATING,
        ):
            continue  # the original method didn't include these types of value, so we're keeping this

        _risk_lvl_by_date = RiskLevelByDate(
            date=risk_ranking["date"], risk_level=risk_ranking["risk_level"]
        )

        task_id = risk_ranking["entity_id"]
        risk_rankings_by_task[task_id].append(_risk_lvl_by_date)

    return [
        TaskRiskLevelByDate(
            task=TaskType.from_orm(task),
            task_name=library_task.name,
            location_name=task.location.name,
            project_name=task.location.project.name
            if task.location.project is not None
            else "",
            risk_level_by_date=risk_rankings_by_task[task.id],
        )
        for library_task, task in task_tuples
    ]


async def get_task_risk_level_by_date_project_planning(
    root: "ProjectPlanningType",
    info: Info,
    order_by: Optional[List[TaskOrderByInput]] = None,
) -> List[TaskRiskLevelByDate]:
    """
    Fetches and returns tasks alongside a list of RiskByDate, for the
    passed start/end dates.
    """

    locations = root.locations
    location_ids = [loc.id for loc in locations]
    task_tuples = await info.context.tasks.get_tasks(
        location_ids=location_ids,
        start_date=root.project_planning_input.start_date,
        end_date=root.project_planning_input.end_date,
        order_by=order_by_to_pydantic(order_by),
    )

    return await get_task_risk_level_by_date(
        info,
        task_tuples=task_tuples,
        start_date=root.project_planning_input.start_date,
        end_date=root.project_planning_input.end_date,
    )


async def get_task_risk_level_by_date_portfolio_planning(
    root: "PortfolioPlanningType",
    info: Info,
    order_by: Optional[List[TaskOrderByInput]] = None,
) -> List[TaskRiskLevelByDate]:
    """
    Fetches and returns tasks alongside a list of RiskByDate, for the
    passed start/end dates of their parent Activities.
    """

    location_groups = await info.context.projects.locations().load_many(
        [p.id for p in root.projects]
    )
    location_ids = [
        loc.id for location_group in location_groups for loc in location_group
    ]
    task_tuples = await info.context.tasks.get_tasks(
        location_ids=location_ids,
        start_date=root.portfolio_planning_input.start_date,
        end_date=root.portfolio_planning_input.end_date,
        order_by=order_by_to_pydantic(order_by),
    )

    return await get_task_risk_level_by_date(
        info,
        task_tuples=task_tuples,
        start_date=root.portfolio_planning_input.start_date,
        end_date=root.portfolio_planning_input.end_date,
    )


################################################################################
# Applicable Hazards helper
################################################################################


def calc_applicable_count(
    analyses: List[models.DailyReportHazardAnalysis]
    | List[models.DailyReportHazardAnalysis | None],
) -> Tuple[int, int]:
    total = 0
    applicable = 0
    analyses = [ca for ca in analyses if ca]  # remove nones
    if analyses:
        total = len(analyses)
        applicable = len(list(filter(attrgetter("isApplicable"), analyses)))
    return total, applicable


################################################################################
# Not Implemented Controls helper
################################################################################


def calc_impled_percent(
    control_analyses: List[models.DailyReportControlAnalysis]
    | List[models.DailyReportControlAnalysis | None],
) -> Tuple[float, int, int]:
    control_analyses = [ca for ca in control_analyses if ca]  # remove nones
    percent = 0.0
    total = 0
    implemented = 0
    if control_analyses:
        total = len(control_analyses)
        implemented = len(list(filter(attrgetter("implemented"), control_analyses)))
        if total:
            percent = round((total - implemented) / (total or 1), 2)
    return percent, total, implemented


################################################################################
# Not Implemented Controls By Task and Task Type
################################################################################


@strawberry.type(name="NotImplementedControlPercentByTaskType")
class NotImplementedControlPercentByTaskType:
    percent: float
    total: int
    implemented: int
    library_task: LibraryTaskType


async def get_not_implemented_controls_by_task_type(
    root: Union["PortfolioLearningsType", "ProjectLearningsType"],
    info: Info,
    library_control_id: uuid.UUID,
) -> List[NotImplementedControlPercentByTaskType]:
    location_ids = await get_location_ids(root, info)

    # TODO by task_id, name, or category?
    (
        control_ids_by_task_category,
        library_task_by_category,
        relevant_location_ids,
    ) = await info.context.insights.get_library_task_data_for_library(
        by_column="category",
        library_control_id=library_control_id,
        location_ids=location_ids,
    )

    # fetch daily reports with location ids (for the date range)
    start_date, end_date = get_start_end_date(root)
    reports = await info.context.daily_reports.get_daily_reports(
        project_location_ids=relevant_location_ids,
        start_date=start_date,
        end_date=end_date,
    )

    control_analyses_by_id = daily_reports.applicable_controls_analyses_by_id(reports)

    not_impled_by_task = []
    # build impl %s for task-controls groups
    for task_category, control_ids in control_ids_by_task_category.items():
        lib_task = library_task_by_category[task_category]
        control_analyses = [
            ca for id in control_ids for ca in control_analyses_by_id.get(id, [])
        ]
        percent, total, implemented = calc_impled_percent(control_analyses)

        # drop zero-percenters
        if percent > 0:
            not_impled_by_task.append(
                NotImplementedControlPercentByTaskType(
                    percent=percent,
                    total=total,
                    implemented=implemented,
                    library_task=LibraryTaskType.from_orm(
                        library_task=lib_task,
                    ),
                )
            )

    # sort by percentage
    not_impled_by_task.sort(key=attrgetter("percent"), reverse=True)
    # limit to 10
    return not_impled_by_task[:10]


@strawberry.type(name="NotImplementedControlPercentByTask")
class NotImplementedControlPercentByTask:
    percent: float
    total: int
    implemented: int
    library_task: LibraryTaskType


async def get_not_implemented_controls_by_task(
    root: Union["PortfolioLearningsType", "ProjectLearningsType"],
    info: Info,
    library_control_id: uuid.UUID,
) -> List[NotImplementedControlPercentByTask]:
    location_ids = await get_location_ids(root, info)

    (
        control_ids_by_task_name,
        library_task_by_name,
        relevant_location_ids,
    ) = await info.context.insights.get_library_task_data_for_library(
        by_column="name",
        library_control_id=library_control_id,
        location_ids=location_ids,
    )

    # fetch daily reports with location ids (for the date range)
    start_date, end_date = get_start_end_date(root)
    reports = await info.context.daily_reports.get_daily_reports(
        project_location_ids=relevant_location_ids,
        start_date=start_date,
        end_date=end_date,
    )

    control_analyses_by_id = daily_reports.applicable_controls_analyses_by_id(reports)

    not_impled_by_task = []
    # build impl %s for task-controls groups
    for task_name, control_ids in control_ids_by_task_name.items():
        # TODO check lib task constraints
        task = library_task_by_name[task_name]
        control_analyses = [
            ca for id in control_ids for ca in control_analyses_by_id.get(id, [])
        ]
        percent, total, implemented = calc_impled_percent(control_analyses)

        # drop zero-percenters
        if percent > 0:
            not_impled_by_task.append(
                NotImplementedControlPercentByTask(
                    percent=percent,
                    total=total,
                    implemented=implemented,
                    library_task=LibraryTaskType.from_orm(
                        library_task=task,
                    ),
                )
            )

    # sort by percentage
    not_impled_by_task.sort(key=attrgetter("percent"), reverse=True)
    # limit to 10
    return not_impled_by_task[:10]


################################################################################
# Not Implemented Controls By Hazard
################################################################################


@strawberry.type(name="NotImplementedControlPercentByHazard")
class NotImplementedControlPercentByHazard:
    percent: float
    total: int
    implemented: int
    library_hazard: LibraryHazardType


async def get_not_implemented_controls_by_hazard(
    root: Union["PortfolioLearningsType", "ProjectLearningsType"],
    info: Info,
    library_control_id: uuid.UUID,
) -> List[NotImplementedControlPercentByHazard]:
    location_ids = await get_location_ids(root, info)

    (
        control_ids_by_hazard_id,
        library_hazard_by_id,
        relevant_location_ids,
    ) = await info.context.insights.get_control_ids_by_library_hazard_id(
        library_control_id, location_ids=location_ids
    )

    # fetch daily reports with location ids (for the date range)
    start_date, end_date = get_start_end_date(root)
    reports = await info.context.daily_reports.get_daily_reports(
        project_location_ids=relevant_location_ids,
        start_date=start_date,
        end_date=end_date,
    )

    control_analyses_by_id = daily_reports.applicable_controls_analyses_by_id(reports)

    not_impled_by_hazard = []
    # build impl %s for hazard-controls groups
    for hazard_id, control_ids in control_ids_by_hazard_id.items():
        hazard = library_hazard_by_id[hazard_id]
        control_analyses = [
            ca for id in control_ids for ca in control_analyses_by_id.get(id, [])
        ]
        percent, total, implemented = calc_impled_percent(control_analyses)

        # drop zero-percenters
        if percent > 0:
            not_impled_by_hazard.append(
                NotImplementedControlPercentByHazard(
                    percent=percent,
                    total=total,
                    implemented=implemented,
                    library_hazard=LibraryHazardType.from_orm(hazard),
                )
            )

    # sort by percentage
    not_impled_by_hazard.sort(key=attrgetter("percent"), reverse=True)
    # limit to 10
    return not_impled_by_hazard[:10]


################################################################################
# Not Implemented Controls By Location
################################################################################


@strawberry.type(name="NotImplementedControlPercentByLocation")
class NotImplementedControlPercentByLocation:
    percent: float
    total: int
    implemented: int
    location: ProjectLocationType


async def get_not_implemented_controls_by_location(
    root: "ProjectLearningsType",
    info: Info,
    library_control_id: uuid.UUID,
) -> List[NotImplementedControlPercentByLocation]:
    """
    Fetches locations and control_ids for the passed library_control_id,
    then fetches dailyReports for those locations,
    then aggregates control-impl-percentages for the relevant control_ids,
    grouped by location.
    """
    locations_by_id = {location.id: location for location in root.locations}

    control_ids_by_location_id = (
        await info.context.insights.get_location_data_for_library(
            library_control_id=library_control_id, location_ids=locations_by_id.keys()
        )
    )

    # fetch daily reports with location ids (for the date range)
    start_date, end_date = get_start_end_date(root)
    reports = await info.context.daily_reports.get_daily_reports(
        project_location_ids=control_ids_by_location_id.keys(),
        start_date=start_date,
        end_date=end_date,
    )

    control_analyses_by_id = daily_reports.applicable_controls_analyses_by_id(reports)

    not_impled_by_location = []
    # build impl %s for location-controls groups
    for location_id, control_ids in control_ids_by_location_id.items():
        location = locations_by_id[location_id]
        control_analyses = [
            ca for id in control_ids for ca in control_analyses_by_id.get(id, [])
        ]
        percent, total, implemented = calc_impled_percent(control_analyses)

        # drop zero-percenters
        if percent > 0:
            not_impled_by_location.append(
                NotImplementedControlPercentByLocation(
                    percent=percent,
                    total=total,
                    implemented=implemented,
                    location=ProjectLocationType.from_orm(location=location),
                )
            )

    # sort by percentage
    not_impled_by_location.sort(key=attrgetter("percent"), reverse=True)
    # limit to 10
    return not_impled_by_location[:10]


################################################################################
# Not Implemented Controls By Project
################################################################################


@strawberry.type(name="NotImplementedControlPercentByProject")
class NotImplementedControlPercentByProject:
    percent: float
    total: int
    implemented: int
    project: ProjectType


async def get_not_implemented_controls_by_project(
    root: "PortfolioLearningsType",
    info: Info,
    library_control_id: uuid.UUID,
) -> List[NotImplementedControlPercentByProject]:
    """
    Fetches projects/locations and control_ids for the library_control_id,
    then fetches dailyReports for those locations,
    then aggregates control-impl-percentages for the relevant control_ids,
    grouped by project.
    """
    project_by_id = {p.id: p for p in root.projects}

    (
        control_ids_by_project_id,
        location_ids,
    ) = await info.context.insights.get_project_data_for_library(
        library_control_id=library_control_id, project_ids=project_by_id.keys()
    )

    # fetch daily reports with location ids (for the date range)
    start_date, end_date = get_start_end_date(root)
    reports = await info.context.daily_reports.get_daily_reports(
        project_location_ids=location_ids,
        start_date=start_date,
        end_date=end_date,
    )
    control_analyses_by_id = daily_reports.applicable_controls_analyses_by_id(reports)

    not_impled_by_project = []
    # build impl %s for project-controls groups
    for project_id, control_ids in control_ids_by_project_id.items():
        project = project_by_id[project_id]
        control_analyses = [
            ca for id in control_ids for ca in control_analyses_by_id.get(id, [])
        ]
        percent, total, implemented = calc_impled_percent(control_analyses)

        # drop zero-percenters
        if percent > 0:
            not_impled_by_project.append(
                NotImplementedControlPercentByProject(
                    percent=percent,
                    total=total,
                    implemented=implemented,
                    project=ProjectType.from_orm(project=project),
                )
            )

    # sort by percentage
    not_impled_by_project.sort(key=attrgetter("percent"), reverse=True)
    # limit to 10
    return not_impled_by_project[:10]


################################################################################
# Not Implemented Controls
################################################################################


@strawberry.type(name="NotImplementedControlPercent")
class NotImplementedControlPercent:
    percent: float
    total: int
    implemented: int
    library_control: LibraryControlType


async def get_not_implemented_controls(
    root: Union["PortfolioLearningsType", "ProjectLearningsType"],
    info: Info,
) -> List[NotImplementedControlPercent]:
    location_ids = await get_location_ids(root, info)

    # fetch daily reports for those location ids
    start_date, end_date = get_start_end_date(root)
    reports = await info.context.daily_reports.get_daily_reports(
        project_location_ids=location_ids,
        start_date=start_date,
        end_date=end_date,
    )

    # gather all control_ids from the reports' job_analysis
    control_analyses_by_id = daily_reports.applicable_controls_analyses_by_id(reports)
    control_analyses_ids = list(control_analyses_by_id.keys())

    # group control_ids by library_controls
    control_data = await info.context.insights.grouped_control_data(
        control_analyses_ids
    )

    # convert each to a percent not-implemented
    not_implemented_controls = []
    for data in control_data:
        control_analyses = [
            ca
            for control_id in data.get("control_ids", [])
            for ca in control_analyses_by_id[control_id]
        ]
        percent, total, implemented = calc_impled_percent(control_analyses)
        library_control = data["library_control"]
        # drop zero-percenters
        if percent > 0:
            not_implemented_controls.append(
                NotImplementedControlPercent(
                    percent=percent,
                    total=total,
                    implemented=implemented,
                    library_control=LibraryControlType.from_orm(library_control),
                )
            )

    # sort by percentage
    not_implemented_controls.sort(key=attrgetter("percent"), reverse=True)
    # limit to 10
    return not_implemented_controls[:10]


################################################################################
# Reasons Not Implemented Controls
################################################################################


@strawberry.type(name="ReasonControlNotImplemented")
class ReasonControlNotImplemented:
    count: int
    reason: str


async def get_reasons_controls_not_implemented(
    root: Union["PortfolioLearningsType", "ProjectLearningsType"],
    info: Info,
) -> List[ReasonControlNotImplemented]:
    location_ids = await get_location_ids(root, info)

    # fetch daily reports for those location ids
    start_date, end_date = get_start_end_date(root)
    reports = await info.context.daily_reports.get_daily_reports(
        project_location_ids=location_ids,
        start_date=start_date,
        end_date=end_date,
    )

    # gather all control_ids from the reports' job_analysis
    control_analyses_by_id = daily_reports.applicable_controls_analyses_by_id(reports)
    not_impled_control_analyses = [
        ca
        for ca_group in control_analyses_by_id.values()
        for ca in ca_group
        if not ca.implemented
    ]

    grouped_by_reason = utils.groupby(
        not_impled_control_analyses, key=attrgetter("not_implemented_reason")
    )

    # convert each to a percent not-implemented
    reason_counts = []
    for reason, group in grouped_by_reason.items():
        if reason:  # drop empty "" reasons
            reason_counts.append(
                ReasonControlNotImplemented(
                    reason=reason,
                    count=len(group),
                )
            )

    return reason_counts


################################################################################
# Applicable Hazards
################################################################################


@strawberry.type(name="ApplicableHazardCount")
class ApplicableHazardCount:
    library_hazard: LibraryHazardType
    count: int
    total: int


async def get_applicable_hazards(
    root: Union["PortfolioLearningsType", "ProjectLearningsType"],
    info: Info,
) -> List[ApplicableHazardCount]:
    location_ids = await get_location_ids(root, info)

    # fetch daily reports for those location ids
    start_date, end_date = get_start_end_date(root)
    reports = await info.context.daily_reports.get_daily_reports(
        project_location_ids=location_ids,
        start_date=start_date,
        end_date=end_date,
    )

    # gather all hazard_ids from the reports' job_analysis
    hazard_analyses_by_id = daily_reports.applicable_hazard_analyses_by_id(reports)
    hazard_analyses_ids = list(hazard_analyses_by_id.keys())

    # group hazard_ids by library_hazards
    hazard_data = await info.context.insights.grouped_hazard_data(hazard_analyses_ids)

    # convert each to a applicable count
    applicable_hazards = []
    for data in hazard_data:
        hazard_analyses = [
            ha
            for hazard_id in data.get("hazard_ids", [])
            for ha in hazard_analyses_by_id[hazard_id]
        ]
        total, applicable = calc_applicable_count(hazard_analyses)
        # drop zero-percenters
        if applicable > 0:
            applicable_hazards.append(
                ApplicableHazardCount(
                    total=total,
                    count=applicable,
                    library_hazard=LibraryHazardType.from_orm(data["library_hazard"]),
                )
            )

    # sort by count
    applicable_hazards.sort(key=attrgetter("count"), reverse=True)
    # limit to 10
    return applicable_hazards[:10]


################################################################################
# Applicable Hazards By Project
################################################################################


@strawberry.type(name="ApplicableHazardCountByProject")
class ApplicableHazardCountByProject:
    count: int
    total: int
    project: ProjectType


async def get_applicable_hazards_by_project(
    root: "PortfolioLearningsType",
    info: Info,
    library_hazard_id: uuid.UUID,
) -> List[ApplicableHazardCountByProject]:
    """
    Fetches projects/locations and hazard_ids for the library_hazard_id,
    then fetches dailyReports for those locations,
    then aggregates applicable hazards for the relevant hazard_ids,
    grouped by project.
    """
    project_by_id = {p.id: p for p in root.projects}

    (
        ids_by_project_id,
        location_ids,
    ) = await info.context.insights.get_project_data_for_library(
        library_hazard_id=library_hazard_id, project_ids=project_by_id.keys()
    )

    # fetch daily reports with location ids (for the date range)
    start_date, end_date = get_start_end_date(root)
    reports = await info.context.daily_reports.get_daily_reports(
        project_location_ids=location_ids,
        start_date=start_date,
        end_date=end_date,
    )
    analyses_by_id = daily_reports.applicable_hazard_analyses_by_id(reports)

    by_project = []
    # build count for project-hazards groups
    for project_id, hazard_ids in ids_by_project_id.items():
        project = project_by_id[project_id]
        analyses = [
            ha for hazard_id in hazard_ids for ha in analyses_by_id.get(hazard_id, [])
        ]
        total, applicable = calc_applicable_count(analyses)
        if applicable > 0:
            by_project.append(
                ApplicableHazardCountByProject(
                    total=total,
                    count=applicable,
                    project=ProjectType.from_orm(project=project),
                )
            )

    # sort by count
    by_project.sort(key=attrgetter("count"), reverse=True)
    # limit to 10
    return by_project[:10]


################################################################################
# Applicable Hazards By Location
################################################################################


@strawberry.type(name="ApplicableHazardCountByLocation")
class ApplicableHazardCountByLocation:
    count: int
    total: int
    location: ProjectLocationType


async def get_applicable_hazards_by_location(
    root: "ProjectLearningsType",
    info: Info,
    library_hazard_id: uuid.UUID,
) -> List[ApplicableHazardCountByLocation]:
    """
    Fetches locations and hazard_ids for the passed library_hazard_id,
    then fetches dailyReports for those locations,
    then aggregates hazard-applicable-count for the relevant hazard_ids,
    grouped by location.
    """
    locations_by_id = {location.id: location for location in root.locations}

    ids_by_location_id = await info.context.insights.get_location_data_for_library(
        library_hazard_id=library_hazard_id, location_ids=locations_by_id.keys()
    )

    # fetch daily reports with location ids (for the date range)
    start_date, end_date = get_start_end_date(root)
    reports = await info.context.daily_reports.get_daily_reports(
        project_location_ids=ids_by_location_id.keys(),
        start_date=start_date,
        end_date=end_date,
    )

    analyses_by_id = daily_reports.applicable_hazard_analyses_by_id(reports)

    not_impled_by_location = []
    # build impl %s for location-hazards groups
    for location_id, hazard_ids in ids_by_location_id.items():
        location = locations_by_id[location_id]
        analyses = [
            ha for hazard_id in hazard_ids for ha in analyses_by_id.get(hazard_id, [])
        ]
        total, applicable = calc_applicable_count(analyses)
        if applicable > 0:
            not_impled_by_location.append(
                ApplicableHazardCountByLocation(
                    total=total,
                    count=applicable,
                    location=ProjectLocationType.from_orm(location=location),
                )
            )

    # sort by count
    not_impled_by_location.sort(key=attrgetter("count"), reverse=True)
    # limit to 10
    return not_impled_by_location[:10]


################################################################################
# Applicable hazards By Site Condition
################################################################################


@strawberry.type(name="ApplicableHazardCountBySiteCondition")
class ApplicableHazardCountBySiteCondition:
    count: int
    total: int
    library_site_condition: LibrarySiteConditionType


async def get_applicable_hazards_by_site_condition(
    root: Union["PortfolioLearningsType", "ProjectLearningsType"],
    info: Info,
    library_hazard_id: uuid.UUID,
) -> List[ApplicableHazardCountBySiteCondition]:
    location_ids = await get_location_ids(root, info)

    (
        ids_by_site_condition_category,
        library_site_condition_by_category,
        relevant_location_ids,
    ) = await info.context.insights.get_library_site_condition_data_for_library(
        library_hazard_id=library_hazard_id,
        location_ids=location_ids,
    )

    # fetch daily reports with location ids (for the date range)
    start_date, end_date = get_start_end_date(root)
    reports = await info.context.daily_reports.get_daily_reports(
        project_location_ids=relevant_location_ids,
        start_date=start_date,
        end_date=end_date,
    )

    analyses_by_id = daily_reports.applicable_hazard_analyses_by_id(reports)

    by_site_condition = []
    # build impl %s for site_condition-hazards groups
    for site_condition_category, hazard_ids in ids_by_site_condition_category.items():
        lib_site_condition = library_site_condition_by_category[site_condition_category]
        analyses = [
            ha for hazard_id in hazard_ids for ha in analyses_by_id.get(hazard_id, [])
        ]
        total, applicable = calc_applicable_count(analyses)
        if applicable > 0:
            by_site_condition.append(
                ApplicableHazardCountBySiteCondition(
                    total=total,
                    count=applicable,
                    library_site_condition=LibrarySiteConditionType.from_orm(
                        lib_site_condition
                    ),
                )
            )

    # sort by count
    by_site_condition.sort(key=attrgetter("count"), reverse=True)
    # limit to 10
    return by_site_condition[:10]


################################################################################
# Applicable hazards By Task and Task Type
################################################################################


@strawberry.type(name="ApplicableHazardCountByTaskType")
class ApplicableHazardCountByTaskType:
    count: int
    total: int
    library_task: LibraryTaskType


async def get_applicable_hazards_by_task_type(
    root: Union["PortfolioLearningsType", "ProjectLearningsType"],
    info: Info,
    library_hazard_id: uuid.UUID,
) -> List[ApplicableHazardCountByTaskType]:
    location_ids = await get_location_ids(root, info)

    # TODO by task_id, name, or category?
    (
        ids_by_task_category,
        library_task_by_category,
        relevant_location_ids,
    ) = await info.context.insights.get_library_task_data_for_library(
        by_column="category",
        library_hazard_id=library_hazard_id,
        location_ids=location_ids,
    )

    # fetch daily reports with location ids (for the date range)
    start_date, end_date = get_start_end_date(root)
    reports = await info.context.daily_reports.get_daily_reports(
        project_location_ids=relevant_location_ids,
        start_date=start_date,
        end_date=end_date,
    )

    analyses_by_id = daily_reports.applicable_hazard_analyses_by_id(reports)

    by_task = []
    # build impl %s for task-hazards groups
    for task_category, hazard_ids in ids_by_task_category.items():
        lib_task = library_task_by_category[task_category]
        analyses = [
            ha for hazard_id in hazard_ids for ha in analyses_by_id.get(hazard_id, [])
        ]
        total, applicable = calc_applicable_count(analyses)
        if applicable > 0:
            by_task.append(
                ApplicableHazardCountByTaskType(
                    total=total,
                    count=applicable,
                    library_task=LibraryTaskType.from_orm(lib_task),
                )
            )

    # sort by count
    by_task.sort(key=attrgetter("count"), reverse=True)
    # limit to 10
    return by_task[:10]


@strawberry.type(name="ApplicableHazardCountByTask")
class ApplicableHazardCountByTask:
    count: int
    total: int
    library_task: LibraryTaskType


async def get_applicable_hazards_by_task(
    root: Union["PortfolioLearningsType", "ProjectLearningsType"],
    info: Info,
    library_hazard_id: uuid.UUID,
) -> List[ApplicableHazardCountByTask]:
    location_ids = await get_location_ids(root, info)

    (
        ids_by_task_name,
        library_task_by_name,
        relevant_location_ids,
    ) = await info.context.insights.get_library_task_data_for_library(
        by_column="name",
        library_hazard_id=library_hazard_id,
        location_ids=location_ids,
    )

    # fetch daily reports with location ids (for the date range)
    start_date, end_date = get_start_end_date(root)
    reports = await info.context.daily_reports.get_daily_reports(
        project_location_ids=relevant_location_ids,
        start_date=start_date,
        end_date=end_date,
    )

    analyses_by_id = daily_reports.applicable_hazard_analyses_by_id(reports)

    by_task = []
    # build impl %s for task-hazards groups
    for task_name, hazard_ids in ids_by_task_name.items():
        # TODO check lib task constraints
        task = library_task_by_name[task_name]
        analyses = [
            ha for hazard_id in hazard_ids for ha in analyses_by_id.get(hazard_id, [])
        ]
        total, applicable = calc_applicable_count(analyses)
        if applicable > 0:
            by_task.append(
                ApplicableHazardCountByTask(
                    total=total,
                    count=applicable,
                    library_task=LibraryTaskType.from_orm(task),
                )
            )

    # sort by count
    by_task.sort(key=attrgetter("count"), reverse=True)
    # limit to 10
    return by_task[:10]


################################################################################
# ProjectPlanning / Learnings
################################################################################


async def get_locations(
    info: Info, project_input: Union["ProjectPlanningInput", "ProjectLearningsInput"]
) -> List[Location]:
    location_ids = project_input.location_ids

    locations: List[Location] = await info.context.projects.locations(
        order_by=[OrderBy(field="name", direction=OrderByDirection.ASC)]
    ).load(project_input.project_id)
    valid_location_ids = {x.id for x in locations}

    # if locations were passed, validate them
    if location_ids:
        difference = set(location_ids) - valid_location_ids
        # any remaining location_ids are not valid for this project_id.
        # they may be archived, or they belong to another project
        if difference:
            raise ValueError(
                "Invalid ProjectLearningsInput: invalid location_id for specified project_id.",
                difference,
            )

        # filter to only the passed locations
        locations = [loc for loc in locations if loc.id in location_ids]

    return locations


@strawberry.input
class ProjectPlanningInput:
    project_id: uuid.UUID
    start_date: datetime.date
    end_date: datetime.date
    location_ids: Optional[List[uuid.UUID]] = None


@strawberry.type(name="ProjectPlanning")
class ProjectPlanningType:
    project_planning_input: strawberry.Private[ProjectPlanningInput]
    locations: strawberry.Private[List[Location]]

    location_risk_level_over_time: List[LocationRiskLevelCount] = strawberry.field(
        resolver=get_location_risk_level_over_time
    )

    location_risk_level_by_date: List[LocationRiskLevelByDate] = strawberry.field(
        resolver=get_location_risk_level_by_date
    )

    task_risk_level_by_date: List[TaskRiskLevelByDate] = strawberry.field(
        resolver=get_task_risk_level_by_date_project_planning
    )


async def get_project_planning(
    info: Info, project_planning_input: ProjectPlanningInput
) -> ProjectPlanningType:
    locations = await get_locations(info, project_planning_input)
    return ProjectPlanningType(
        project_planning_input=project_planning_input, locations=locations
    )


@strawberry.input
class ProjectLearningsInput:
    project_id: uuid.UUID
    start_date: datetime.date
    end_date: datetime.date
    location_ids: Optional[List[uuid.UUID]] = None


@strawberry.type(name="ProjectLearnings")
class ProjectLearningsType:
    project_learnings_input: strawberry.Private[ProjectLearningsInput]
    locations: strawberry.Private[List[Location]]

    location_risk_level_over_time: List[LocationRiskLevelCount] = strawberry.field(
        resolver=get_location_risk_level_over_time
    )

    applicable_hazards: List[ApplicableHazardCount] = strawberry.field(
        resolver=get_applicable_hazards
    )
    applicable_hazards_by_location: List[
        ApplicableHazardCountByLocation
    ] = strawberry.field(resolver=get_applicable_hazards_by_location)
    applicable_hazards_by_site_condition: List[
        ApplicableHazardCountBySiteCondition
    ] = strawberry.field(resolver=get_applicable_hazards_by_site_condition)
    applicable_hazards_by_task: List[ApplicableHazardCountByTask] = strawberry.field(
        resolver=get_applicable_hazards_by_task
    )
    applicable_hazards_by_task_type: List[
        ApplicableHazardCountByTaskType
    ] = strawberry.field(resolver=get_applicable_hazards_by_task_type)

    not_implemented_controls: List[NotImplementedControlPercent] = strawberry.field(
        resolver=get_not_implemented_controls
    )

    not_implemented_controls_by_location: List[
        NotImplementedControlPercentByLocation
    ] = strawberry.field(resolver=get_not_implemented_controls_by_location)

    not_implemented_controls_by_hazard: List[
        NotImplementedControlPercentByHazard
    ] = strawberry.field(resolver=get_not_implemented_controls_by_hazard)

    not_implemented_controls_by_task: List[
        NotImplementedControlPercentByTask
    ] = strawberry.field(resolver=get_not_implemented_controls_by_task)

    not_implemented_controls_by_task_type: List[
        NotImplementedControlPercentByTaskType
    ] = strawberry.field(resolver=get_not_implemented_controls_by_task_type)

    reasons_controls_not_implemented: List[
        ReasonControlNotImplemented
    ] = strawberry.field(resolver=get_reasons_controls_not_implemented)


async def get_project_learnings(
    info: Info, project_learnings_input: ProjectLearningsInput
) -> ProjectLearningsType:
    locations = await get_locations(info, project_learnings_input)
    return ProjectLearningsType(
        project_learnings_input=project_learnings_input, locations=locations
    )


################################################################################
# ProjectRiskOverTime
################################################################################


@strawberry.type(name="ProjectRiskLevelCount")
class ProjectRiskLevelCount:
    date: datetime.date
    risk_level: RiskLevel
    count: int


async def get_project_risk_level_over_time(
    root: Union["PortfolioPlanningType", "PortfolioLearningsType"],
    info: Info,
) -> List[ProjectRiskLevelCount]:
    """
    Expects projects to be set on root.
    Passes project_ids to the total risk level aggregator.
    """

    start_date, end_date = get_start_end_date(root)
    project_risk_models = await info.context.insights.project_risk_levels_by_date(
        start_date=start_date,
        end_date=end_date,
        project_ids=[p.id for p in root.projects],
    )

    _counter = Counter(
        map(lambda lrm: (lrm["date"], lrm["risk_level"]), project_risk_models)
    )
    # TODO: Check if this needs to be exaustive or not.
    ret = []
    for key, count in _counter.items():
        if key[1] in (models.RiskLevel.UNKNOWN, models.RiskLevel.RECALCULATING):
            continue  # the original method didn't include these types of value, so we're keeping this
        ret.append(ProjectRiskLevelCount(date=key[0], risk_level=key[1], count=count))

    return ret


################################################################################
# ProjectRiskByDate
################################################################################


@strawberry.type(name="ProjectRiskLevelByDate")
class ProjectRiskLevelByDate:
    risk_level_by_date: List[RiskLevelByDate]
    project: ProjectType | None
    project_name: str


async def get_project_risk_level_by_date(
    root: "PortfolioPlanningType",
    info: Info,
) -> List[ProjectRiskLevelByDate]:
    """
    Fetches and returns projects along with a list of RiskByDate, for the
    passed start/end dates.
    """
    risk_rankings = await info.context.insights.project_risk_levels_by_date(
        project_ids=[p.id for p in root.projects],
        start_date=root.portfolio_planning_input.start_date,
        end_date=root.portfolio_planning_input.end_date,
    )

    risk_rankings_by_project: dict[uuid.UUID, list[RiskLevelByDate]] = defaultdict(list)
    for risk_ranking in risk_rankings:
        if risk_ranking["risk_level"] in (
            models.RiskLevel.UNKNOWN,
            models.RiskLevel.RECALCULATING,
        ):
            continue  # the original method didn't include these types of value, so we're keeping this

        _risk_lvl_by_date = RiskLevelByDate(
            date=risk_ranking["date"], risk_level=risk_ranking["risk_level"]
        )

        project_id = risk_ranking["entity_id"]
        risk_rankings_by_project[project_id].append(_risk_lvl_by_date)

    return [
        ProjectRiskLevelByDate(
            project=ProjectType.from_orm(project),
            project_name=project.name,
            risk_level_by_date=risk_rankings_by_project[project.id],
        )
        for project in root.projects
    ]


################################################################################
# PortfolioPlanning
################################################################################


@strawberry.input
class PortfolioPlanningInput:
    start_date: datetime.date
    end_date: datetime.date
    project_ids: Optional[List[uuid.UUID]] = None
    project_statuses: Optional[List[ProjectStatus]] = None
    region_ids: Optional[List[uuid.UUID]] = None
    division_ids: Optional[List[uuid.UUID]] = None
    contractor_ids: Optional[List[uuid.UUID]] = None


@strawberry.type(name="PortfolioPlanning")
class PortfolioPlanningType:
    portfolio_planning_input: strawberry.Private[PortfolioPlanningInput]
    projects: strawberry.Private[List[WorkPackage]]

    project_risk_level_over_time: List[ProjectRiskLevelCount] = strawberry.field(
        resolver=get_project_risk_level_over_time
    )

    project_risk_level_by_date: List[ProjectRiskLevelByDate] = strawberry.field(
        resolver=get_project_risk_level_by_date
    )

    task_risk_level_by_date: List[TaskRiskLevelByDate] = strawberry.field(
        resolver=get_task_risk_level_by_date_portfolio_planning
    )


async def get_portfolio_planning(
    info: Info, portfolio_planning_input: PortfolioPlanningInput
) -> PortfolioPlanningType:
    projects = await info.context.insights.filter_projects(
        project_ids=portfolio_planning_input.project_ids,
        project_statuses=portfolio_planning_input.project_statuses,
        library_region_ids=portfolio_planning_input.region_ids,
        library_division_ids=portfolio_planning_input.division_ids,
        contractor_ids=portfolio_planning_input.contractor_ids,
    )

    return PortfolioPlanningType(
        portfolio_planning_input=portfolio_planning_input, projects=projects
    )


################################################################################
# PortfolioLearnings
################################################################################


@strawberry.input
class PortfolioLearningsInput:
    start_date: datetime.date
    end_date: datetime.date
    project_ids: Optional[List[uuid.UUID]] = None
    project_statuses: Optional[List[ProjectStatus]] = None
    region_ids: Optional[List[uuid.UUID]] = None
    division_ids: Optional[List[uuid.UUID]] = None
    contractor_ids: Optional[List[uuid.UUID]] = None


@strawberry.type(name="PortfolioLearnings")
class PortfolioLearningsType:
    portfolio_learnings_input: strawberry.Private[PortfolioLearningsInput]
    projects: strawberry.Private[List[WorkPackage]]

    project_risk_level_over_time: List[ProjectRiskLevelCount] = strawberry.field(
        resolver=get_project_risk_level_over_time
    )

    applicable_hazards: List[ApplicableHazardCount] = strawberry.field(
        resolver=get_applicable_hazards
    )

    applicable_hazards_by_project: List[
        ApplicableHazardCountByProject
    ] = strawberry.field(resolver=get_applicable_hazards_by_project)
    applicable_hazards_by_site_condition: List[
        ApplicableHazardCountBySiteCondition
    ] = strawberry.field(resolver=get_applicable_hazards_by_site_condition)
    applicable_hazards_by_task: List[ApplicableHazardCountByTask] = strawberry.field(
        resolver=get_applicable_hazards_by_task
    )
    applicable_hazards_by_task_type: List[
        ApplicableHazardCountByTaskType
    ] = strawberry.field(resolver=get_applicable_hazards_by_task_type)

    not_implemented_controls: List[NotImplementedControlPercent] = strawberry.field(
        resolver=get_not_implemented_controls
    )

    not_implemented_controls_by_project: List[
        NotImplementedControlPercentByProject
    ] = strawberry.field(resolver=get_not_implemented_controls_by_project)

    not_implemented_controls_by_hazard: List[
        NotImplementedControlPercentByHazard
    ] = strawberry.field(resolver=get_not_implemented_controls_by_hazard)
    not_implemented_controls_by_task: List[
        NotImplementedControlPercentByTask
    ] = strawberry.field(resolver=get_not_implemented_controls_by_task)
    not_implemented_controls_by_task_type: List[
        NotImplementedControlPercentByTaskType
    ] = strawberry.field(resolver=get_not_implemented_controls_by_task_type)
    reasons_controls_not_implemented: List[
        ReasonControlNotImplemented
    ] = strawberry.field(resolver=get_reasons_controls_not_implemented)


async def get_portfolio_learnings(
    info: Info, portfolio_learnings_input: PortfolioLearningsInput
) -> PortfolioLearningsType:
    projects = await info.context.insights.filter_projects(
        project_ids=portfolio_learnings_input.project_ids,
        project_statuses=portfolio_learnings_input.project_statuses,
        library_region_ids=portfolio_learnings_input.region_ids,
        library_division_ids=portfolio_learnings_input.division_ids,
        contractor_ids=portfolio_learnings_input.contractor_ids,
    )

    return PortfolioLearningsType(
        portfolio_learnings_input=portfolio_learnings_input, projects=projects
    )
