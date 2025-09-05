import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

import tests.factories as factories
from tests.db_data import DBData
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

from .helpers import (
    ControlsResult,
    SampleControl,
    assert_controls_data,
    assert_controls_percentages,
    batch_upsert_control_report,
    to_portfolio_input,
    to_project_input,
)

################################################################################
# Test Query and helper

project_task_query = """
query TestQuery($filter: ProjectLearningsInput!,
  $libraryControlId: UUID!,
) {
  projectLearnings(projectLearningsInput: $filter) {
    notImplementedControlsByTask(libraryControlId: $libraryControlId) {
      percent libraryTask { id name }
    }
  }
}
"""

project_task_type_query = """
query TestQuery($filter: ProjectLearningsInput!,
  $libraryControlId: UUID!,
) {
  projectLearnings(projectLearningsInput: $filter) {
    notImplementedControlsByTaskType(libraryControlId: $libraryControlId) {
      percent libraryTask { id category }
    }
  }
}
"""

portfolio_task_query = """
query TestQuery($filter: PortfolioLearningsInput!,
  $libraryControlId: UUID!,
) {
  portfolioLearnings(portfolioLearningsInput: $filter) {
    notImplementedControlsByTask(libraryControlId: $libraryControlId) {
      percent libraryTask { id name }
    }
  }
}
"""

portfolio_task_type_query = """
query TestQuery($filter: PortfolioLearningsInput!,
  $libraryControlId: UUID!,
) {
  portfolioLearnings(portfolioLearningsInput: $filter) {
    notImplementedControlsByTaskType(libraryControlId: $libraryControlId) {
      percent libraryTask { id category }
    }
  }
}
"""


async def execute_not_implemented_controls(
    execute_gql: ExecuteGQL,
    query: str,
    library_control_id: uuid.UUID,
    **filters: Any,
) -> Any:
    filt = None
    query_name = None
    sub_query_name = None
    if query in [project_task_query, project_task_type_query]:
        filt = to_project_input(**filters)
        query_name = "projectLearnings"
    elif query in [portfolio_task_query, portfolio_task_type_query]:
        filt = to_portfolio_input(**filters)
        query_name = "portfolioLearnings"

    if query in [project_task_query, portfolio_task_query]:
        sub_query_name = "notImplementedControlsByTask"
    elif query in [project_task_type_query, portfolio_task_type_query]:
        sub_query_name = "notImplementedControlsByTaskType"
    assert sub_query_name

    data = await execute_gql(
        query=query,
        variables={"filter": filt, "libraryControlId": library_control_id},
    )
    return data[query_name][sub_query_name]


async def assert_not_implemented_controls(
    execute_gql: ExecuteGQL,
    query: str,
    filters: Any,
    expected_data: dict[uuid.UUID, ControlsResult] | None = None,
    expected_percentages: list[float] | None = None,
) -> None:
    controls_data = await execute_not_implemented_controls(
        execute_gql, query, **filters
    )

    if isinstance(expected_percentages, list):
        assert_controls_percentages(expected_percentages, controls_data)

    if expected_data:
        assert_controls_data(expected_data, controls_data)


################################################################################
# Tests


@pytest.mark.asyncio
@pytest.mark.integration
async def test_not_implemented_controls_by_task(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Creates impled/not-impled controls on daily-reports across 3 tasks.
    Queries for not-impled-controls-by-task for each library_control.
    Tests for both project and portfolio learnings.
    """
    project = await factories.WorkPackageFactory.persist(db_session)
    lib_tasks = await factories.LibraryTaskFactory.persist_many(db_session, size=3)
    [lib_task1, lib_task2, lib_task3] = lib_tasks
    task1, _, _ = await factories.TaskFactory.with_project_and_location(
        db_session, project=project, task_kwargs={"library_task_id": lib_task1.id}
    )
    task2, _, _ = await factories.TaskFactory.with_project_and_location(
        db_session, project=project, task_kwargs={"library_task_id": lib_task2.id}
    )
    task3, _, _ = await factories.TaskFactory.with_project_and_location(
        db_session, project=project, task_kwargs={"library_task_id": lib_task3.id}
    )

    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    [control1, control2] = await factories.LibraryControlFactory.persist_many(
        db_session, size=2
    )

    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(implemented=True, library_control=control1, task=task1),
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    task=task2,
                ),
                SampleControl(
                    implemented=True,
                    library_control=control2,
                    task=task3,
                ),
            ],
            day2: [
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    task=task1,
                ),
                SampleControl(implemented=False, library_control=control1, task=task2),
                SampleControl(
                    implemented=False,
                    library_control=control2,
                    task=task3,
                ),
            ],
        },
    )

    # portfolio task, control1
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_task_query,
        filters={**filters, "library_control_id": control1.id},
        expected_data={
            lib_task1.id: ControlsResult(percent=0.5, library_task_name=lib_task1.name),
            lib_task2.id: ControlsResult(percent=1.0, library_task_name=lib_task2.name),
        },
    )
    # portfolio task, control2
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_task_query,
        filters={**filters, "library_control_id": control2.id},
        expected_data={
            lib_task3.id: ControlsResult(percent=0.5, library_task_name=lib_task3.name),
        },
    )
    # portfolio task type, control1
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_task_query,
        filters={**filters, "library_control_id": control1.id},
        expected_data={
            lib_task1.id: ControlsResult(
                percent=0.5, library_task_category=lib_task1.category
            ),
            lib_task2.id: ControlsResult(
                percent=1.0, library_task_category=lib_task2.category
            ),
        },
    )
    # portfolio task type, control2
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_task_query,
        filters={**filters, "library_control_id": control2.id},
        expected_data={
            lib_task3.id: ControlsResult(
                percent=0.5, library_task_category=lib_task3.category
            ),
        },
    )

    # portfolio task, only day 2
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_task_query,
        filters={**filters, "library_control_id": control2.id, "start_date": day2},
        expected_data={
            lib_task3.id: ControlsResult(percent=1.0, library_task_name=lib_task3.name),
        },
    )
    # portfolio task type, only day 2
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_task_query,
        filters={**filters, "library_control_id": control2.id, "start_date": day2},
        expected_data={
            lib_task3.id: ControlsResult(
                percent=1.0, library_task_category=lib_task3.category
            ),
        },
    )

    # project task, control1
    await assert_not_implemented_controls(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_id": project.id,
        },
        expected_data={
            lib_task1.id: ControlsResult(percent=0.5, library_task_name=lib_task1.name),
            lib_task2.id: ControlsResult(percent=1.0, library_task_name=lib_task2.name),
        },
    )
    # project task, control2
    await assert_not_implemented_controls(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_control_id": control2.id,
            "project_id": project.id,
        },
        expected_data={
            lib_task3.id: ControlsResult(percent=0.5, library_task_name=lib_task3.name),
        },
    )
    # project task type, control1
    await assert_not_implemented_controls(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_id": project.id,
        },
        expected_data={
            lib_task1.id: ControlsResult(
                percent=0.5, library_task_category=lib_task1.category
            ),
            lib_task2.id: ControlsResult(
                percent=1.0, library_task_category=lib_task2.category
            ),
        },
    )
    # project task type, control2
    await assert_not_implemented_controls(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_control_id": control2.id,
            "project_id": project.id,
        },
        expected_data={
            lib_task3.id: ControlsResult(
                percent=0.5, library_task_category=lib_task3.category
            ),
        },
    )

    # project task, only day 2
    await assert_not_implemented_controls(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_control_id": control2.id,
            "start_date": day2,
            "project_id": project.id,
        },
        expected_data={
            lib_task3.id: ControlsResult(percent=1.0, library_task_name=lib_task3.name),
        },
    )
    # project task type, only day 2
    await assert_not_implemented_controls(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_control_id": control2.id,
            "start_date": day2,
            "project_id": project.id,
        },
        expected_data={
            lib_task3.id: ControlsResult(
                percent=1.0, library_task_category=lib_task3.category
            ),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_not_implemented_controls_by_task_location_filter(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    project = await factories.WorkPackageFactory.persist(db_session)
    locations = await factories.LocationFactory.persist_many(
        db_session, project_id=project.id, size=2
    )
    [location1, location2] = locations
    lib_tasks = await factories.LibraryTaskFactory.persist_many(db_session, size=3)
    [lib_task1, lib_task2, lib_task3] = lib_tasks
    task1, _, _ = await factories.TaskFactory.with_project_and_location(
        db_session,
        project=project,
        location=location1,
        task_kwargs={"library_task_id": lib_task1.id},
    )
    task2, _, _ = await factories.TaskFactory.with_project_and_location(
        db_session,
        project=project,
        location=location2,
        task_kwargs={"library_task_id": lib_task2.id},
    )
    task3, _, _ = await factories.TaskFactory.with_project_and_location(
        db_session,
        project=project,
        location=location2,
        task_kwargs={"library_task_id": lib_task3.id},
    )

    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    [control1, control2] = await factories.LibraryControlFactory.persist_many(
        db_session, size=2
    )

    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(implemented=True, library_control=control1, task=task1),
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    task=task2,
                ),
                SampleControl(
                    implemented=True,
                    library_control=control2,
                    task=task3,
                ),
            ],
            day2: [
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    task=task1,
                ),
                SampleControl(implemented=False, library_control=control1, task=task2),
                SampleControl(
                    implemented=False,
                    library_control=control2,
                    task=task3,
                ),
            ],
        },
    )

    # project task, both locations, control 1
    await assert_not_implemented_controls(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_id": project.id,
            "location_ids": [location1.id, location2.id],
        },
        expected_data={
            lib_task1.id: ControlsResult(percent=0.5, library_task_name=lib_task1.name),
            lib_task2.id: ControlsResult(percent=1.0, library_task_name=lib_task2.name),
        },
    )
    # project task, both locations, control 2
    await assert_not_implemented_controls(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_control_id": control2.id,
            "project_id": project.id,
            "location_ids": [location1.id, location2.id],
        },
        expected_data={
            lib_task3.id: ControlsResult(percent=0.5, library_task_name=lib_task3.name),
        },
    )
    # project task type, both locations, control 1
    await assert_not_implemented_controls(
        execute_gql,
        query=project_task_type_query,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_id": project.id,
            "location_ids": [location1.id, location2.id],
        },
        expected_data={
            lib_task1.id: ControlsResult(
                percent=0.5, library_task_category=lib_task1.category
            ),
            lib_task2.id: ControlsResult(
                percent=1.0, library_task_category=lib_task2.category
            ),
        },
    )
    # project task type, both locations, control 2
    await assert_not_implemented_controls(
        execute_gql,
        query=project_task_type_query,
        filters={
            **filters,
            "library_control_id": control2.id,
            "project_id": project.id,
            "location_ids": [location1.id, location2.id],
        },
        expected_data={
            lib_task3.id: ControlsResult(
                percent=0.5, library_task_category=lib_task3.category
            ),
        },
    )

    # project task, location1, control1
    await assert_not_implemented_controls(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_id": project.id,
            "location_ids": [location1.id],
        },
        expected_data={
            lib_task1.id: ControlsResult(percent=0.5, library_task_name=lib_task1.name),
        },
    )
    # project task, location1, control2
    await assert_not_implemented_controls(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_control_id": control2.id,
            "project_id": project.id,
            "location_ids": [location1.id],
        },
        expected_data={},
        expected_percentages=[],
    )

    # project task type, location1, control1
    await assert_not_implemented_controls(
        execute_gql,
        query=project_task_type_query,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_id": project.id,
            "location_ids": [location1.id],
        },
        expected_data={
            lib_task1.id: ControlsResult(
                percent=0.5, library_task_category=lib_task1.category
            ),
        },
    )
    # project task type, location1, control2
    await assert_not_implemented_controls(
        execute_gql,
        query=project_task_type_query,
        filters={
            **filters,
            "library_control_id": control2.id,
            "project_id": project.id,
            "location_ids": [location1.id],
        },
        expected_data={},
        expected_percentages=[],
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_not_implemented_controls_by_task_project_filter(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    [project1, project2] = await factories.WorkPackageFactory.persist_many(
        db_session, size=2
    )
    lib_tasks = await factories.LibraryTaskFactory.persist_many(db_session, size=3)
    [lib_task1, lib_task2, lib_task3] = lib_tasks
    task1, _, _ = await factories.TaskFactory.with_project_and_location(
        db_session,
        project=project1,
        task_kwargs={"library_task_id": lib_task1.id},
    )
    task2, _, _ = await factories.TaskFactory.with_project_and_location(
        db_session,
        project=project2,
        task_kwargs={"library_task_id": lib_task2.id},
    )
    task3, _, _ = await factories.TaskFactory.with_project_and_location(
        db_session,
        project=project2,
        task_kwargs={"library_task_id": lib_task3.id},
    )

    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    [control1, control2] = await factories.LibraryControlFactory.persist_many(
        db_session, size=2
    )

    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(implemented=True, library_control=control1, task=task1),
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    task=task2,
                ),
                SampleControl(
                    implemented=True,
                    library_control=control2,
                    task=task3,
                ),
            ],
            day2: [
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    task=task1,
                ),
                SampleControl(implemented=False, library_control=control1, task=task2),
                SampleControl(
                    implemented=False,
                    library_control=control2,
                    task=task3,
                ),
            ],
        },
    )

    # portfolio task, both projects, control1
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_task_query,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_ids": [project1.id, project2.id],
        },
        expected_data={
            lib_task1.id: ControlsResult(percent=0.5, library_task_name=lib_task1.name),
            lib_task2.id: ControlsResult(percent=1.0, library_task_name=lib_task2.name),
        },
    )
    # portfolio task type, both projects, control1
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_task_type_query,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_ids": [project1.id, project2.id],
        },
        expected_data={
            lib_task1.id: ControlsResult(
                percent=0.5, library_task_category=lib_task1.category
            ),
            lib_task2.id: ControlsResult(
                percent=1.0, library_task_category=lib_task2.category
            ),
        },
    )

    # portfolio task, project1, control1
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_task_query,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_ids": [project1.id],
        },
        expected_data={
            lib_task1.id: ControlsResult(percent=0.5, library_task_name=lib_task1.name),
        },
    )
    # portfolio task type, project1, control1
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_task_type_query,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_ids": [project1.id],
        },
        expected_data={
            lib_task1.id: ControlsResult(
                percent=0.5, library_task_category=lib_task1.category
            ),
        },
    )

    # portfolio task, project2, control1
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_task_query,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_ids": [project2.id],
        },
        expected_data={
            lib_task2.id: ControlsResult(percent=1.0, library_task_name=lib_task2.name),
        },
    )
    # portfolio task type, project2, control1
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_task_type_query,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_ids": [project2.id],
        },
        expected_data={
            lib_task2.id: ControlsResult(
                percent=1.0, library_task_category=lib_task2.category
            ),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_not_implemented_controls_task_limit_ten(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    This endpoint should return the ten largest not-impled percentages.
    """
    day1 = datetime.now(timezone.utc)
    library_tasks = await factories.LibraryTaskFactory.persist_many(db_session, size=11)
    location = await factories.LocationFactory.persist(db_session)
    assert location.project_id
    project = await db_data.project(location.project_id)
    task_tuples = await factories.TaskFactory.batch_with_project_and_location(
        db_session,
        [
            {
                "project": project,
                "location": location,
                "task_kwargs": {"library_task_id": lib_task.id},
            }
            for lib_task in library_tasks
        ],
    )
    tasks = list(map(lambda t: t[0], task_tuples))

    library_control = await factories.LibraryControlFactory.persist(db_session)

    filters = dict(start_date=day1, end_date=day1)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    implemented=False, library_control=library_control, task=task
                )
                for task in tasks
            ]
        },
    )

    # portfolio task
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_task_query,
        filters={**filters, "library_control_id": library_control.id},
        expected_percentages=[1.0 for _ in range(10)],
    )
    # portfolio task type
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_task_type_query,
        filters={**filters, "library_control_id": library_control.id},
        expected_percentages=[1.0 for _ in range(10)],
    )
    # project task
    await assert_not_implemented_controls(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_control_id": library_control.id,
            "project_id": location.project_id,
        },
        expected_percentages=[1.0 for _ in range(10)],
    )
    # project task type
    await assert_not_implemented_controls(
        execute_gql,
        query=project_task_type_query,
        filters={
            **filters,
            "library_control_id": library_control.id,
            "project_id": location.project_id,
        },
        expected_percentages=[1.0 for _ in range(10)],
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_not_implemented_controls_by_task_drop_zeroes(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    This endpoint should drop zeroes.
    """
    day1 = datetime.now(timezone.utc)

    library_tasks = await factories.LibraryTaskFactory.persist_many(db_session, size=2)
    project = await factories.WorkPackageFactory.persist(db_session)
    task_tuples = [
        await factories.TaskFactory.with_project_and_location(
            db_session, project=project, task_kwargs={"library_task_id": lib_task.id}
        )
        for lib_task in library_tasks
    ]
    [task1, task2] = list(map(lambda t: t[0], task_tuples))

    library_control = await factories.LibraryControlFactory.persist(db_session)

    filters = dict(start_date=day1, end_date=day1)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    implemented=False, library_control=library_control, task=task1
                ),
                SampleControl(
                    implemented=True, library_control=library_control, task=task2
                ),
            ]
        },
    )

    for query in (portfolio_task_query, portfolio_task_type_query):
        await assert_not_implemented_controls(
            execute_gql,
            query=query,
            filters={**filters, "library_control_id": library_control.id},
            expected_percentages=[1.0],
        )
    for query in (project_task_query, project_task_type_query):
        await assert_not_implemented_controls(
            execute_gql,
            query=query,
            filters={
                **filters,
                "library_control_id": library_control.id,
                "project_id": project.id,
            },
            expected_percentages=[1.0],
        )
