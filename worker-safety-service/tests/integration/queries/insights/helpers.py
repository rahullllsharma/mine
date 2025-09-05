import uuid
from datetime import date, datetime, timezone
from operator import attrgetter
from typing import Any, Callable, Optional, TypedDict, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, or_
from sqlmodel import select

import tests.factories as factories
import worker_safety_service.models as models
import worker_safety_service.utils as utils
from tests.factories import (
    TaskSpecificRiskScoreModelFactory,
    TotalProjectLocationRiskScoreModelFactory,
    TotalProjectRiskScoreModelFactory,
)
from worker_safety_service.models import (
    AsyncSession,
    ProjectStatus,
    RiskLevel,
    TaskSpecificRiskScoreModel,
    TotalProjectLocationRiskScoreModel,
    TotalProjectRiskScoreModel,
)

CountsByRiskLevel = dict[str, int]


def risk_level_counts(counts: CountsByRiskLevel) -> CountsByRiskLevel:
    """
    Ensure every risk score is set.
    """
    by_risk: CountsByRiskLevel = {
        RiskLevel.LOW.name: 0,
        RiskLevel.MEDIUM.name: 0,
        RiskLevel.HIGH.name: 0,
    }

    return {**by_risk, **counts}


async def batch_create_risk_score(
    session: AsyncSession,
    items: list[dict],
) -> list[
    Union[
        TotalProjectRiskScoreModel,
        TotalProjectLocationRiskScoreModel,
        TaskSpecificRiskScoreModel,
    ]
]:
    """
    Creates a risk score for the passed project_id. If no project_id is passed,
    one is created using the passed project_dict and the ProjectFactory.
    """

    project_risk = {}
    location_risk = {}
    task_risk = {}

    for idx, item in enumerate(items):
        day = item["day"]
        score = item["score"]
        project_id = item.get("project_id")
        location_id = item.get("location_id")
        task_id = item.get("task_id")

        if project_id:
            project_risk[idx] = {
                "project_id": project_id,
                "value": score,
                "date": day,
                "calculated_at": datetime.now(timezone.utc).replace(microsecond=idx),
            }
        elif location_id:
            location_risk[idx] = {
                "project_location_id": location_id,
                "value": score,
                "date": day,
                "calculated_at": datetime.now(timezone.utc).replace(microsecond=idx),
            }
        elif task_id:
            task_risk[idx] = {
                "project_task_id": task_id,
                "value": score,
                "date": day,
                "calculated_at": datetime.now(timezone.utc).replace(microsecond=idx),
            }

    response: list[
        Union[
            TotalProjectRiskScoreModel,
            TotalProjectLocationRiskScoreModel,
            TaskSpecificRiskScoreModel,
            None,
        ]
    ] = [None for _ in range(len(items))]
    if project_risk:
        project_scores = await TotalProjectRiskScoreModelFactory.persist_many(
            session,
            per_item_kwargs=project_risk.values(),
        )
        for idx, score in zip(project_risk.keys(), project_scores):
            response[idx] = score
    if location_risk:
        location_scores = await TotalProjectLocationRiskScoreModelFactory.persist_many(
            session,
            per_item_kwargs=location_risk.values(),
        )
        for idx, score in zip(location_risk.keys(), location_scores):
            response[idx] = score
    if task_risk:
        task_scores = await TaskSpecificRiskScoreModelFactory.persist_many(
            session,
            per_item_kwargs=task_risk.values(),
        )
        for idx, score in zip(task_risk.keys(), task_scores):
            response[idx] = score

    result: list[
        Union[
            TotalProjectRiskScoreModel,
            TotalProjectLocationRiskScoreModel,
            TaskSpecificRiskScoreModel,
        ]
    ] = []
    for score in response:
        assert score
        result.append(score)
    return result


def to_project_input(
    project_id: uuid.UUID,
    start_date: datetime,
    end_date: datetime,
    location_ids: Optional[list[uuid.UUID]] = None,
) -> dict[str, Any]:
    vs = {
        "projectId": project_id,
        "startDate": start_date.date(),
        "endDate": end_date.date(),
    }
    if location_ids:
        vs["locationIds"] = location_ids

    return vs


def to_portfolio_input(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    project_ids: Optional[list[uuid.UUID]] = None,
    statuses: Optional[list[ProjectStatus]] = None,
    region_ids: Optional[list[uuid.UUID]] = None,
    division_ids: Optional[list[uuid.UUID]] = None,
    contractor_ids: Optional[list[uuid.UUID]] = None,
) -> dict[str, Any]:
    vs: dict[str, Any] = dict()
    if start_date:
        vs["startDate"] = start_date.date()
    if end_date:
        vs["endDate"] = end_date.date()
    if project_ids:
        vs["projectIds"] = project_ids
    if statuses:
        vs["projectStatuses"] = statuses
    if region_ids:
        vs["regionIds"] = region_ids
    if division_ids:
        vs["divisionIds"] = division_ids
    if contractor_ids:
        vs["contractorIds"] = contractor_ids

    return vs


################################################################################
# Controls Not Impled/Applicable Hazards Daily Report helpers
################################################################################


async def fetch_daily_report(
    session: AsyncSession, location: models.Location, day: datetime
) -> models.DailyReport | None:
    # assert on our test data
    stmt = select(models.DailyReport).where(
        models.DailyReport.project_location_id == location.id,
        models.DailyReport.date_for == datetime.date(day),
    )
    result = await session.exec(stmt)
    if result:
        return result.first()
    return None


class SampleControl(TypedDict, total=False):
    implemented: bool
    not_implemented_reason: str | None
    further_explanation: str | None
    hazard_is_applicable: bool

    library_hazard: models.LibraryHazard
    library_control: models.LibraryControl

    project: models.WorkPackage
    location: models.Location
    task: models.Task
    site_condition: models.SiteCondition
    hazard: models.TaskHazard | models.SiteConditionHazard
    control: models.TaskControl | models.SiteConditionControl


def create_control_analysis(
    sample_control: SampleControl,
    control: models.SiteConditionControl | models.TaskControl,
) -> models.DailyReportControlAnalysis:
    return models.DailyReportControlAnalysis(
        id=control.id,
        implemented=sample_control.get("implemented", False),
        not_implemented_reason=sample_control.get("not_implemented_reason", None),
        further_explanation=sample_control.get("further_explanation", None),
    )


def create_hazard_analysis(
    sample_control: SampleControl,
    hazard: models.SiteConditionHazard | models.TaskHazard,
    control: models.SiteConditionControl | models.TaskControl,
) -> models.DailyReportHazardAnalysis:
    return models.DailyReportHazardAnalysis(
        id=hazard.id,
        isApplicable=sample_control.get("hazard_is_applicable", True),
        controls=[create_control_analysis(sample_control, control)],
    )


def create_task_analysis(
    sample_control: SampleControl,
    task: models.Task,
    hazard: models.SiteConditionHazard | models.TaskHazard,
    control: models.SiteConditionControl | models.TaskControl,
) -> models.DailyReportTaskAnalysis:
    return models.DailyReportTaskAnalysis(
        id=task.id,
        notes=None,
        not_applicable_reason=None,
        performed=True,
        hazards=[create_hazard_analysis(sample_control, hazard, control)],
    )


def create_site_condition_analysis(
    sample_control: SampleControl,
    site_condition: models.SiteCondition,
    hazard: models.SiteConditionHazard | models.TaskHazard,
    control: models.SiteConditionControl | models.TaskControl,
) -> models.DailyReportSiteConditionAnalysis:
    return models.DailyReportSiteConditionAnalysis(
        id=site_condition.id,
        isApplicable=sample_control.get("site_condition_is_applicable", True),
        hazards=[create_hazard_analysis(sample_control, hazard, control)],
    )


def update_jha_controls(
    sample_control: SampleControl,
    hazard_analysis: models.DailyReportHazardAnalysis,
    control: models.SiteConditionControl | models.TaskControl,
) -> None:
    """
    Updates the passed analysis in-place, upserting the hazard/control analysis
    with the passed hazard/control.
    """
    control_ids = set(map(lambda x: x.id, hazard_analysis.controls))

    has_control = control.id in control_ids

    if has_control:
        for control_analysis in hazard_analysis.controls:
            if control_analysis.id == control.id:
                new_control = create_control_analysis(sample_control, control)
                for key in (
                    "implemented",
                    "not_implemented_reason",
                    "further_explanation",
                ):
                    setattr(control_analysis, key, getattr(new_control, key))
    else:
        hazard_analysis.controls.append(
            create_control_analysis(sample_control, control)
        )


def update_jha_hazards(
    sample_control: SampleControl,
    tsc_analysis: models.DailyReportTaskAnalysis
    | models.DailyReportSiteConditionAnalysis,
    hazard: models.SiteConditionHazard | models.TaskHazard,
    control: models.SiteConditionControl | models.TaskControl,
) -> None:
    """
    Updates the passed analysis in-place, upserting the hazards analyses
    with the passed hazard/control.
    """
    hazard_ids = set(map(lambda x: x.id, tsc_analysis.hazards))

    has_hazard = hazard.id in hazard_ids

    if has_hazard:
        for hazard_analysis in tsc_analysis.hazards:
            if hazard_analysis.id == hazard.id:
                update_jha_controls(sample_control, hazard_analysis, control)
    else:
        tsc_analysis.hazards.append(
            create_hazard_analysis(sample_control, hazard, control)
        )


def update_jha_sections(
    sample_control: SampleControl,
    sections: models.DailyReportSections,
    hazard: models.SiteConditionHazard | models.TaskHazard,
    control: models.SiteConditionControl | models.TaskControl,
    task: models.Task | None = None,
    site_condition: models.SiteCondition | None = None,
) -> None:
    """
    Updates the passed daily_report job_hazard_analysis task/site_condition
    sections, upserting with the passed task, hazard, and control.
    """
    assert task or site_condition

    create_task_or_sc = "task" if task else "site_condition"

    if not sections.job_hazard_analysis:
        sections.job_hazard_analysis = models.DailyReportJobHazardAnalysisSection(
            tasks=[],
            site_conditions=[],
        )
    if not sections.job_hazard_analysis.tasks:
        sections.job_hazard_analysis.tasks = []
    if not sections.job_hazard_analysis.site_conditions:
        sections.job_hazard_analysis.site_conditions = []
    tasks = sections.job_hazard_analysis.tasks

    task_ids = set(map(lambda x: x.id, tasks))
    has_task = task and task.id in task_ids

    if has_task:
        assert task
        for task_analysis in tasks:
            if task_analysis.id == task.id:
                update_jha_hazards(sample_control, task_analysis, hazard, control)
    elif create_task_or_sc == "task":
        assert task
        tasks.append(create_task_analysis(sample_control, task, hazard, control))

    site_conditions = sections.job_hazard_analysis.site_conditions
    site_condition_ids = set(map(lambda x: x.id, site_conditions))
    has_site_condition = site_condition and site_condition.id in site_condition_ids

    if has_site_condition:
        assert site_condition
        for site_condition_analysis in site_conditions:
            if site_condition_analysis.id == site_condition.id:
                update_jha_hazards(
                    sample_control, site_condition_analysis, hazard, control
                )
    elif create_task_or_sc == "site_condition":
        assert site_condition
        site_conditions.append(
            create_site_condition_analysis(
                sample_control, site_condition, hazard, control
            )
        )


async def batch_upsert_control_report(
    session: AsyncSession,
    items: dict[datetime, list[SampleControl]],
    custom_report_upsert: Optional[Callable] = None,
) -> None:
    """
    Given a day and SampleControl, creates or upserts a daily_report with the
    indicated sampleControl data.

    By default, creates a new library_control, project, location, task, hazard,
    and control, then creates/finds a daily_report for the location/day and adds
    a job_analysis report to it, upserting on the task, hazard and control
    analyses.

    If a sampel_control.site_condition is included, the control_analysis will
    be added to a site_condition_analysis instead.

    project, location, task, hazard, and library_control can be passed to force
    the created control and analysis into the desired relations. `location` is
    especially useful as it will result in the daily_report being re-used, if
    you need to test data from the same report.
    """

    # Build main data (project, location, etc)
    batch_tasks: dict[int, factories.ItemsOptions] = {}
    batch_site_conditions: dict[int, factories.ItemsOptions] = {}
    idx = 0
    for day, sample_controls in items.items():
        for sample_control in sample_controls:
            task = sample_control.get("task")
            hazard = sample_control.get("hazard")
            site_condition = sample_control.get("site_condition")
            library_hazard = sample_control.get("library_hazard")
            library_control = sample_control.get("library_control")
            control = sample_control.get("control")

            hazard_kwargs: dict[str, Any] = {}
            if library_hazard:
                hazard_kwargs["library_hazard_id"] = library_hazard.id

            control_kwargs = {}
            if library_control:
                control_kwargs["library_control_id"] = library_control.id
            elif control:
                control_kwargs["library_control_id"] = control.library_control_id

            if (
                task
                or isinstance(hazard, models.TaskHazard)
                or isinstance(control, models.TaskControl)
                or (
                    not site_condition
                    and not isinstance(hazard, models.SiteConditionHazard)
                    and not isinstance(control, models.SiteConditionControl)
                )
            ):
                batch_tasks[idx] = {
                    "task_control": control,  # type: ignore
                    "task_control_kwargs": control_kwargs,
                    "task_hazard": hazard,  # type: ignore
                    "task_hazard_kwargs": hazard_kwargs,
                    "task": task,
                    "location": sample_control.get("location"),
                    "project": sample_control.get("project"),
                }
            else:
                batch_site_conditions[idx] = {
                    "site_condition_control": control,
                    "site_condition_control_kwargs": control_kwargs,
                    "site_condition_hazard": hazard,
                    "site_condition_hazard_kwargs": hazard_kwargs,
                    "site_condition": site_condition,
                    "location": sample_control.get("location"),
                    "project": sample_control.get("project"),
                }
            idx += 1

    new_items: dict[
        int,
        tuple[
            str,
            tuple[
                models.TaskControl | models.SiteConditionControl,
                models.WorkPackage,
                models.Location,
                models.Task | models.SiteCondition,
                models.TaskHazard | models.SiteConditionHazard,
            ],
        ],
    ] = {}
    if batch_tasks:
        new_tasks = await factories.TaskControlFactory.batch_with_relations(
            session, batch_tasks.values()
        )
        new_items.update(
            (idx, ("task", item)) for idx, item in zip(batch_tasks.keys(), new_tasks)
        )
    if batch_site_conditions:
        new_site_conditions = (
            await factories.SiteConditionControlFactory.batch_with_relations(
                session, batch_site_conditions.values()
            )
        )
        new_items.update(
            (idx, ("site_condition", item))
            for idx, item in zip(batch_site_conditions.keys(), new_site_conditions)
        )

    # Build daily reports
    # This seeding algorithm used to create daily report for each pair of (Day, Location) from the sample control data.
    idx = 0
    missing_daily_reports: dict[
        tuple[date, uuid.UUID],
        tuple[date, models.WorkPackage, models.Location],
    ] = {}
    for day, sample_controls in items.items():
        for sample_control in sample_controls:
            project, location = new_items[idx][1][1:3]
            idx += 1
            day_date = datetime.date(day)
            missing_daily_reports[(day_date, location.id)] = (
                day_date,
                project,
                location,
            )

    daily_reports: dict[tuple[date, uuid.UUID], models.DailyReport] = {}
    stmt = select(models.DailyReport).where(
        or_(
            *(
                and_(  # type: ignore
                    models.DailyReport.project_location_id == l,
                    models.DailyReport.date_for == d,
                )
                for d, l in missing_daily_reports
            )
        )
    )
    for daily_report in (await session.exec(stmt)).all():
        key = (daily_report.date_for, daily_report.project_location_id)
        missing_daily_reports.pop(key, None)
        daily_reports[key] = daily_report
    if missing_daily_reports:
        if custom_report_upsert:
            for d, p, l in missing_daily_reports.values():
                daily_report = await custom_report_upsert(
                    date=d, project_location_id=l.id, daily_report_id=None
                )
                daily_reports[
                    (daily_report.date_for, daily_report.project_location_id)
                ] = daily_report
        else:
            daily_reports.update(
                ((d.date_for, d.project_location_id), d)
                for d, *_ in await factories.DailyReportFactory.batch_with_project_and_location(
                    session,
                    [
                        {
                            "project": p,
                            "location": l,
                            "daily_report_kwargs": {"date_for": d},
                        }
                        for d, p, l in missing_daily_reports.values()
                    ],
                )
            )

    idx = 0
    for day, sample_controls in items.items():
        for sample_control in sample_controls:
            item_type, item_data = new_items[idx]
            idx += 1
            if item_type == "task":
                control, project, location, item_obj, hazard = item_data
                assert isinstance(item_obj, models.Task)
                task = item_obj
            else:
                control, project, location, item_obj, hazard = item_data
                assert isinstance(item_obj, models.SiteCondition)
                site_condition = item_obj

            daily_report = daily_reports[(datetime.date(day), location.id)]

            sections = models.DailyReport.sections_to_pydantic(daily_report)
            if not sections:
                sections = models.DailyReportSections()

            # update sections in-place
            update_jha_sections(
                sample_control,
                sections,
                hazard,
                control,
                task=task,
                site_condition=site_condition,
            )

            daily_report.sections = jsonable_encoder(sections)
            await session.commit()

            # make sure this did something
            sections = models.DailyReport.sections_to_pydantic(daily_report)
            tasks = attrgetter("job_hazard_analysis.tasks")(sections)
            site_conditions = attrgetter("job_hazard_analysis.site_conditions")(
                sections
            )
            if task:
                assert tasks
                assert tasks[0]
                assert tasks[0].hazards[0]
                assert tasks[0].hazards[0].id
                assert tasks[0].hazards[0].controls[0]
                assert tasks[0].hazards[0].controls[0].id
            else:
                assert site_conditions
                assert site_conditions[0]
                assert site_conditions[0].hazards[0]
                assert site_conditions[0].hazards[0].id
                assert site_conditions[0].hazards[0].controls[0]
                assert site_conditions[0].hazards[0].controls[0].id


def assert_daily_report_section_counts(
    daily_report: models.DailyReport,
    task_count: int | None = None,
    site_condition_count: int | None = None,
    task: models.Task | None = None,
    site_condition: models.SiteCondition | None = None,
    hazard: models.SiteConditionHazard | models.TaskHazard | None = None,
    hazard_count: int | None = None,
    control_count: int | None = None,
) -> None:
    """
    A helper for making sure the dailyReports test data is building as expected.
    Note that task/site_condition must be provided for hazards/control assertions
    to be executed.
    """

    # at least one of these is required
    assert task_count or site_condition_count

    sections = models.DailyReport.sections_to_pydantic(daily_report)
    task_analyses = attrgetter("job_hazard_analysis.tasks")(sections)

    if task_count:
        assert len(task_analyses) == task_count
    if task:
        assert task.id in [ta.id for ta in task_analyses]

        if hazard_count:
            for ta in task_analyses:
                if ta.id == task.id:
                    assert len(ta.hazards) == hazard_count

                    if hazard:
                        assert hazard.id in [haz_a.id for haz_a in ta.hazards]

                        if control_count:
                            for haz_a in ta.hazards:
                                if haz_a.id == hazard.id:
                                    assert len(haz_a.controls) == control_count
    elif not site_condition:
        # if task is not provided, crash here b/c the assertion is mis-configed
        assert not hazard, "Misconfigured daily_report section counts assertion"
        assert not hazard_count, "Misconfigured daily_report section counts assertion"
        assert not control_count, "Misconfigured daily_report section counts assertion"

    site_condition_analyses = attrgetter("job_hazard_analysis.site_conditions")(
        sections
    )
    if site_condition_count:
        assert len(site_condition_analyses) == site_condition_count
    if site_condition:
        assert site_condition.id in [ta.id for ta in site_condition_analyses]

        if hazard_count:
            for ta in site_condition_analyses:
                if ta.id == site_condition.id:
                    assert len(ta.hazards) == hazard_count

                    if hazard:
                        assert hazard.id in [haz_a.id for haz_a in ta.hazards]

                        if control_count:
                            for haz_a in ta.hazards:
                                if haz_a.id == hazard.id:
                                    assert len(haz_a.controls) == control_count
    elif not task:
        # if task is not provided, crash here b/c the assertion is mis-configed
        assert not hazard, "Misconfigured daily_report section counts assertion"
        assert not hazard_count, "Misconfigured daily_report section counts assertion"
        assert not control_count, "Misconfigured daily_report section counts assertion"


class HazardsResult(TypedDict, total=False):
    count: int
    library_name: str
    project_name: str
    location_name: str
    library_task_name: str
    library_task_category: Optional[str]
    library_site_condition_name: str


def assert_hazards_count(expected_count: list[int], hazards_data: Any) -> None:
    """
    Provides a simpler assertion on just the returned counts.
    Useful for checking return count and order.
    """
    mapfunc = lambda x: x["count"]  # noqa: E731
    returned_counts = list(map(mapfunc, hazards_data))
    assert expected_count == returned_counts, f"{expected_count} -> {returned_counts}"


def assert_hazards_data(
    expected_data: dict[uuid.UUID, HazardsResult],
    hazards_data: Any,
) -> None:
    """
    Asserts that the results match the expected dates and risk_level counts
    in test_data.
    """
    assert len(
        expected_data
    ), "No expected data passed - use `assert_hazards_count` to test for empty results"

    first = list(expected_data.values())[0]
    keyfunc = None
    if first.get("library_name"):
        keyfunc = lambda x: x["libraryHazard"]["id"]  # noqa: E731
    elif first.get("project_name"):
        keyfunc = lambda x: x["project"]["id"]  # noqa: E731
    elif first.get("location_name"):
        keyfunc = lambda x: x["location"]["id"]  # noqa: E731
    elif first.get("library_task_name"):
        keyfunc = lambda x: x["libraryTask"]["id"]  # noqa: E731
    elif first.get("library_task_category"):
        keyfunc = lambda x: x["libraryTask"]["id"]  # noqa: E731
    elif first.get("library_site_condition_name"):
        keyfunc = lambda x: x["librarySiteCondition"]["id"]  # noqa: E731

    assert keyfunc, "Invalid expected_data config"

    fetched_by_id = utils.groupby(hazards_data, key=keyfunc)

    assert len(fetched_by_id) == len(expected_data)

    assert set(fetched_by_id.keys()) == set(
        map(str, expected_data.keys())
    ), f"{fetched_by_id.keys()} -> {expected_data.keys()}"

    # assert only one libary_hazard per library_id
    for ctrls in fetched_by_id.values():
        assert len(ctrls) == 1

    for expected_id, expected_result in expected_data.items():
        assert str(expected_id) in fetched_by_id

        fetched_hazard_data = fetched_by_id[str(expected_id)][0]
        assert expected_result["count"] == fetched_hazard_data["count"]

        if hasattr(expected_result, "library_name"):
            assert (
                expected_result["library_name"]
                == fetched_hazard_data["libraryHazard"]["name"]
            )
        if hasattr(expected_result, "project_name"):
            assert (
                expected_result["project_name"]
                == fetched_hazard_data["project"]["name"]
            )
        if hasattr(expected_result, "location_name"):
            assert (
                expected_result["location_name"]
                == fetched_hazard_data["location"]["name"]
            )
        if hasattr(expected_result, "library_task_name"):
            assert (
                expected_result["library_task_name"]
                == fetched_hazard_data["libraryTask"]["name"]
            )
        if hasattr(expected_result, "library_task_category"):
            assert (
                expected_result["library_task_category"]
                == fetched_hazard_data["libraryTask"]["category"]
            )
        if hasattr(expected_result, "library_site_condition_name"):
            assert (
                expected_result["library_site_condition_name"]
                == fetched_hazard_data["librarySiteCondition"]["name"]
            )

        assert str(expected_id) == keyfunc(fetched_hazard_data)  # type: ignore


class ControlsResult(TypedDict, total=False):
    percent: float
    library_name: str
    project_name: str
    location_name: str
    library_hazard_name: str
    library_task_name: str
    library_task_category: Optional[str]


def assert_controls_percentages(
    expected_percentages: list[float], controls_data: Any
) -> None:
    """
    Provides a simpler assertion on just the returned percentages.
    Useful for checking return count and order.
    """
    mapfunc = lambda x: x["percent"]  # noqa: E731
    returned_percentages = list(map(mapfunc, controls_data))
    assert expected_percentages == returned_percentages


def assert_controls_data(
    expected_data: dict[uuid.UUID, ControlsResult],
    controls_data: Any,
) -> None:
    """
    Asserts that the results match the expected dates and risk_level counts
    in test_data.
    """
    assert len(
        expected_data
    ), "No expected data passed - use `assert_controls_percentage` to test for empty results"

    first = list(expected_data.values())[0]
    keyfunc = None
    if first.get("library_name"):
        keyfunc = lambda x: x["libraryControl"]["id"]  # noqa: E731
    elif first.get("project_name"):
        keyfunc = lambda x: x["project"]["id"]  # noqa: E731
    elif first.get("location_name"):
        keyfunc = lambda x: x["location"]["id"]  # noqa: E731
    elif first.get("library_hazard_name"):
        keyfunc = lambda x: x["libraryHazard"]["id"]  # noqa: E731
    elif first.get("library_task_name"):
        keyfunc = lambda x: x["libraryTask"]["id"]  # noqa: E731
    elif first.get("library_task_category"):
        keyfunc = lambda x: x["libraryTask"]["id"]  # noqa: E731

    assert keyfunc, "Invalid expected_data config"

    fetched_by_id = utils.groupby(controls_data, key=keyfunc)

    assert len(fetched_by_id) == len(expected_data)

    assert set(fetched_by_id.keys()) == set(map(str, expected_data.keys()))

    # assert only one libary_control per library_id
    for ctrls in fetched_by_id.values():
        assert len(ctrls) == 1

    for expected_id, expected_result in expected_data.items():
        assert str(expected_id) in fetched_by_id

        fetched_control_data = fetched_by_id[str(expected_id)][0]
        assert expected_result["percent"] == fetched_control_data["percent"]

        if hasattr(expected_result, "library_name"):
            assert (
                expected_result["library_name"]
                == fetched_control_data["libraryControl"]["name"]
            )
        if hasattr(expected_result, "project_name"):
            assert (
                expected_result["project_name"]
                == fetched_control_data["project"]["name"]
            )
        if hasattr(expected_result, "location_name"):
            assert (
                expected_result["location_name"]
                == fetched_control_data["location"]["name"]
            )
        if hasattr(expected_result, "library_hazard_name"):
            assert (
                expected_result["library_hazard_name"]
                == fetched_control_data["libraryHazard"]["name"]
            )
        if hasattr(expected_result, "library_task_name"):
            assert (
                expected_result["library_task_name"]
                == fetched_control_data["libraryTask"]["name"]
            )
        if hasattr(expected_result, "library_task_category"):
            assert (
                expected_result["library_task_category"]
                == fetched_control_data["libraryTask"]["category"]
            )

        assert str(expected_id) == keyfunc(fetched_control_data)  # type: ignore


def assert_reasons_data(
    expected_data: dict[str, int],
    reasons_data: Any,
) -> None:
    """
    Asserts that the reasons api data match the expected reason counts.
    """
    assert len(
        expected_data
    ), "No expected data passed - use `assert_reasons_count` to test for empty results"

    by_reason = lambda x: x["reason"]  # noqa: E731
    counts_by_reason = utils.groupby(reasons_data, key=by_reason)

    assert len(counts_by_reason) == len(expected_data)
    assert set(counts_by_reason.keys()) == set(map(str, expected_data.keys()))

    # assert only one count per reason
    for counts in counts_by_reason.values():
        assert len(counts) == 1

    for expected_reason, expected_count in expected_data.items():
        assert str(expected_reason) in counts_by_reason
        count = counts_by_reason[expected_reason][0]["count"]
        assert expected_count == count
