import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

import tests.factories as factories
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

from .helpers import (
    HazardsResult,
    SampleControl,
    assert_hazards_count,
    assert_hazards_data,
    batch_upsert_control_report,
    to_portfolio_input,
    to_project_input,
)

################################################################################
# Test Query and helper

project_task_query = """
query TestQuery($filter: ProjectLearningsInput!,
  $libraryHazardId: UUID!,
) {
  projectLearnings(projectLearningsInput: $filter) {
    applicableHazardsByTask(libraryHazardId: $libraryHazardId) {
      count libraryTask { id name }
    }
  }
}
"""

project_task_type_query = """
query TestQuery($filter: ProjectLearningsInput!,
  $libraryHazardId: UUID!,
) {
  projectLearnings(projectLearningsInput: $filter) {
    applicableHazardsByTaskType(libraryHazardId: $libraryHazardId) {
      count libraryTask { id category }
    }
  }
}
"""

portfolio_task_query = """
query TestQuery($filter: PortfolioLearningsInput!,
  $libraryHazardId: UUID!,
) {
  portfolioLearnings(portfolioLearningsInput: $filter) {
    applicableHazardsByTask(libraryHazardId: $libraryHazardId) {
      count libraryTask { id name }
    }
  }
}
"""

portfolio_task_type_query = """
query TestQuery($filter: PortfolioLearningsInput!,
  $libraryHazardId: UUID!,
) {
  portfolioLearnings(portfolioLearningsInput: $filter) {
    applicableHazardsByTaskType(libraryHazardId: $libraryHazardId) {
      count libraryTask { id category }
    }
  }
}
"""


async def execute_applicable_hazards(
    execute_gql: ExecuteGQL,
    query: str,
    library_hazard_id: uuid.UUID,
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
        sub_query_name = "applicableHazardsByTask"
    elif query in [project_task_type_query, portfolio_task_type_query]:
        sub_query_name = "applicableHazardsByTaskType"
    assert sub_query_name

    data = await execute_gql(
        query=query,
        variables={"filter": filt, "libraryHazardId": library_hazard_id},
    )
    return data[query_name][sub_query_name]


async def assert_applicable_hazards(
    execute_gql: ExecuteGQL,
    query: str,
    filters: Any,
    expected_data: dict[uuid.UUID, HazardsResult] | None = None,
    expected_count: list[int] | None = None,
) -> None:
    hazards_data = await execute_applicable_hazards(execute_gql, query, **filters)

    if isinstance(expected_count, list):
        assert_hazards_count(expected_count, hazards_data)

    if expected_data:
        assert_hazards_data(expected_data, hazards_data)


################################################################################
# Tests


@pytest.mark.asyncio
@pytest.mark.integration
async def test_applicable_hazards_by_task(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Creates applicable hazards on daily-reports across 3 tasks.
    Queries for applicable-hazards-by-task for each library_hazard.
    Tests for both project and portfolio learnings.
    """
    project = await factories.WorkPackageFactory.persist(db_session)
    lib_task1, lib_task2, lib_task3 = await factories.LibraryTaskFactory.persist_many(
        db_session, size=3
    )
    items = await factories.TaskFactory.batch_with_project_and_location(
        db_session,
        [
            {"project": project, "task_kwargs": {"library_task_id": lib_task1.id}},
            {"project": project, "task_kwargs": {"library_task_id": lib_task2.id}},
            {"project": project, "task_kwargs": {"library_task_id": lib_task3.id}},
        ],
    )
    task1, task2, task3 = [i[0] for i in items]

    day1, day2 = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    hazard1, hazard2 = await factories.LibraryHazardFactory.persist_many(
        db_session, size=2
    )

    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    hazard_is_applicable=False, library_hazard=hazard1, task=task1
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    task=task2,
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard2,
                    task=task3,
                ),
            ],
            day2: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    task=task1,
                ),
                SampleControl(
                    hazard_is_applicable=True, library_hazard=hazard1, task=task2
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard2,
                    task=task3,
                ),
            ],
        },
    )

    # portfolio task, hazard1
    await assert_applicable_hazards(
        execute_gql,
        query=portfolio_task_query,
        filters={**filters, "library_hazard_id": hazard1.id},
        expected_data={
            lib_task1.id: HazardsResult(count=1, library_task_name=lib_task1.name),
            lib_task2.id: HazardsResult(count=2, library_task_name=lib_task2.name),
        },
    )
    # portfolio task, hazard2
    await assert_applicable_hazards(
        execute_gql,
        query=portfolio_task_query,
        filters={**filters, "library_hazard_id": hazard2.id},
        expected_data={
            lib_task3.id: HazardsResult(count=1, library_task_name=lib_task3.name),
        },
    )
    # portfolio task type, hazard1
    await assert_applicable_hazards(
        execute_gql,
        query=portfolio_task_query,
        filters={**filters, "library_hazard_id": hazard1.id},
        expected_data={
            lib_task1.id: HazardsResult(
                count=1, library_task_category=lib_task1.category
            ),
            lib_task2.id: HazardsResult(
                count=2, library_task_category=lib_task2.category
            ),
        },
    )
    # portfolio task type, hazard2
    await assert_applicable_hazards(
        execute_gql,
        query=portfolio_task_query,
        filters={**filters, "library_hazard_id": hazard2.id},
        expected_data={
            lib_task3.id: HazardsResult(
                count=1, library_task_category=lib_task3.category
            ),
        },
    )

    # portfolio task, only day 2
    await assert_applicable_hazards(
        execute_gql,
        query=portfolio_task_query,
        filters={**filters, "library_hazard_id": hazard2.id, "start_date": day2},
        expected_data={
            lib_task3.id: HazardsResult(count=1, library_task_name=lib_task3.name),
        },
    )
    # portfolio task type, only day 2
    await assert_applicable_hazards(
        execute_gql,
        query=portfolio_task_query,
        filters={**filters, "library_hazard_id": hazard2.id, "start_date": day2},
        expected_data={
            lib_task3.id: HazardsResult(
                count=1, library_task_category=lib_task3.category
            ),
        },
    )

    # project task, hazard1
    await assert_applicable_hazards(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_id": project.id,
        },
        expected_data={
            lib_task1.id: HazardsResult(count=1, library_task_name=lib_task1.name),
            lib_task2.id: HazardsResult(count=2, library_task_name=lib_task2.name),
        },
    )
    # project task, hazard2
    await assert_applicable_hazards(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_hazard_id": hazard2.id,
            "project_id": project.id,
        },
        expected_data={
            lib_task3.id: HazardsResult(count=1, library_task_name=lib_task3.name),
        },
    )
    # project task type, hazard1
    await assert_applicable_hazards(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_id": project.id,
        },
        expected_data={
            lib_task1.id: HazardsResult(
                count=1, library_task_category=lib_task1.category
            ),
            lib_task2.id: HazardsResult(
                count=2, library_task_category=lib_task2.category
            ),
        },
    )
    # project task type, hazard2
    await assert_applicable_hazards(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_hazard_id": hazard2.id,
            "project_id": project.id,
        },
        expected_data={
            lib_task3.id: HazardsResult(
                count=1, library_task_category=lib_task3.category
            ),
        },
    )

    # project task, only day 2
    await assert_applicable_hazards(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_hazard_id": hazard2.id,
            "start_date": day2,
            "project_id": project.id,
        },
        expected_data={
            lib_task3.id: HazardsResult(count=1, library_task_name=lib_task3.name),
        },
    )
    # project task type, only day 2
    await assert_applicable_hazards(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_hazard_id": hazard2.id,
            "start_date": day2,
            "project_id": project.id,
        },
        expected_data={
            lib_task3.id: HazardsResult(
                count=1, library_task_category=lib_task3.category
            ),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_applicable_hazards_by_task_location_filter(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    project = await factories.WorkPackageFactory.persist(db_session)
    location1, location2 = await factories.LocationFactory.persist_many(
        db_session, project_id=project.id, size=2
    )
    lib_task1, lib_task2, lib_task3 = await factories.LibraryTaskFactory.persist_many(
        db_session, size=3
    )
    items = await factories.TaskFactory.batch_with_project_and_location(
        db_session,
        [
            {
                "project": project,
                "location": location1,
                "task_kwargs": {"library_task_id": lib_task1.id},
            },
            {
                "project": project,
                "location": location2,
                "task_kwargs": {"library_task_id": lib_task2.id},
            },
            {
                "project": project,
                "location": location2,
                "task_kwargs": {"library_task_id": lib_task3.id},
            },
        ],
    )
    task1, task2, task3 = [i[0] for i in items]

    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    [hazard1, hazard2] = await factories.LibraryHazardFactory.persist_many(
        db_session, size=2
    )

    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    hazard_is_applicable=False, library_hazard=hazard1, task=task1
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    task=task2,
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard2,
                    task=task3,
                ),
            ],
            day2: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    task=task1,
                ),
                SampleControl(
                    hazard_is_applicable=True, library_hazard=hazard1, task=task2
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard2,
                    task=task3,
                ),
            ],
        },
    )

    # project task, both locations, hazard 1
    await assert_applicable_hazards(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_id": project.id,
            "location_ids": [location1.id, location2.id],
        },
        expected_data={
            lib_task1.id: HazardsResult(count=1, library_task_name=lib_task1.name),
            lib_task2.id: HazardsResult(count=2, library_task_name=lib_task2.name),
        },
    )
    # project task, both locations, hazard 2
    await assert_applicable_hazards(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_hazard_id": hazard2.id,
            "project_id": project.id,
            "location_ids": [location1.id, location2.id],
        },
        expected_data={
            lib_task3.id: HazardsResult(count=1, library_task_name=lib_task3.name),
        },
    )
    # project task type, both locations, hazard 1
    await assert_applicable_hazards(
        execute_gql,
        query=project_task_type_query,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_id": project.id,
            "location_ids": [location1.id, location2.id],
        },
        expected_data={
            lib_task1.id: HazardsResult(
                count=1, library_task_category=lib_task1.category
            ),
            lib_task2.id: HazardsResult(
                count=2, library_task_category=lib_task2.category
            ),
        },
    )
    # project task type, both locations, hazard 2
    await assert_applicable_hazards(
        execute_gql,
        query=project_task_type_query,
        filters={
            **filters,
            "library_hazard_id": hazard2.id,
            "project_id": project.id,
            "location_ids": [location1.id, location2.id],
        },
        expected_data={
            lib_task3.id: HazardsResult(
                count=1, library_task_category=lib_task3.category
            ),
        },
    )

    # project task, location1, hazard1
    await assert_applicable_hazards(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_id": project.id,
            "location_ids": [location1.id],
        },
        expected_data={
            lib_task1.id: HazardsResult(count=1, library_task_name=lib_task1.name),
        },
    )
    # project task, location1, hazard2
    await assert_applicable_hazards(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_hazard_id": hazard2.id,
            "project_id": project.id,
            "location_ids": [location1.id],
        },
        expected_data={},
        expected_count=[],
    )

    # project task type, location1, hazard1
    await assert_applicable_hazards(
        execute_gql,
        query=project_task_type_query,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_id": project.id,
            "location_ids": [location1.id],
        },
        expected_data={
            lib_task1.id: HazardsResult(
                count=1, library_task_category=lib_task1.category
            ),
        },
    )
    # project task type, location1, hazard2
    await assert_applicable_hazards(
        execute_gql,
        query=project_task_type_query,
        filters={
            **filters,
            "library_hazard_id": hazard2.id,
            "project_id": project.id,
            "location_ids": [location1.id],
        },
        expected_data={},
        expected_count=[],
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_applicable_hazards_by_task_project_filter(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    project1, project2 = await factories.WorkPackageFactory.persist_many(
        db_session, size=2
    )
    lib_task1, lib_task2, lib_task3 = await factories.LibraryTaskFactory.persist_many(
        db_session, size=3
    )
    items = await factories.TaskFactory.batch_with_project_and_location(
        db_session,
        [
            {"project": project1, "task_kwargs": {"library_task_id": lib_task1.id}},
            {"project": project2, "task_kwargs": {"library_task_id": lib_task2.id}},
            {"project": project2, "task_kwargs": {"library_task_id": lib_task3.id}},
        ],
    )
    task1, task2, task3 = [i[0] for i in items]

    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    [hazard1, hazard2] = await factories.LibraryHazardFactory.persist_many(
        db_session, size=2
    )

    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    hazard_is_applicable=False, library_hazard=hazard1, task=task1
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    task=task2,
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard2,
                    task=task3,
                ),
            ],
            day2: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    task=task1,
                ),
                SampleControl(
                    hazard_is_applicable=True, library_hazard=hazard1, task=task2
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard2,
                    task=task3,
                ),
            ],
        },
    )

    # portfolio task, both projects, hazard1
    await assert_applicable_hazards(
        execute_gql,
        query=portfolio_task_query,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_ids": [project1.id, project2.id],
        },
        expected_data={
            lib_task1.id: HazardsResult(count=1, library_task_name=lib_task1.name),
            lib_task2.id: HazardsResult(count=2, library_task_name=lib_task2.name),
        },
    )
    # portfolio task type, both projects, hazard1
    await assert_applicable_hazards(
        execute_gql,
        query=portfolio_task_type_query,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_ids": [project1.id, project2.id],
        },
        expected_data={
            lib_task1.id: HazardsResult(
                count=1, library_task_category=lib_task1.category
            ),
            lib_task2.id: HazardsResult(
                count=2, library_task_category=lib_task2.category
            ),
        },
    )

    # portfolio task, project1, hazard1
    await assert_applicable_hazards(
        execute_gql,
        query=portfolio_task_query,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_ids": [project1.id],
        },
        expected_data={
            lib_task1.id: HazardsResult(count=1, library_task_name=lib_task1.name),
        },
    )
    # portfolio task type, project1, hazard1
    await assert_applicable_hazards(
        execute_gql,
        query=portfolio_task_type_query,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_ids": [project1.id],
        },
        expected_data={
            lib_task1.id: HazardsResult(
                count=1, library_task_category=lib_task1.category
            ),
        },
    )

    # portfolio task, project2, hazard1
    await assert_applicable_hazards(
        execute_gql,
        query=portfolio_task_query,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_ids": [project2.id],
        },
        expected_data={
            lib_task2.id: HazardsResult(count=2, library_task_name=lib_task2.name),
        },
    )
    # portfolio task type, project2, hazard1
    await assert_applicable_hazards(
        execute_gql,
        query=portfolio_task_type_query,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_ids": [project2.id],
        },
        expected_data={
            lib_task2.id: HazardsResult(
                count=2, library_task_category=lib_task2.category
            ),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_applicable_hazards_by_task_limit_ten(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    This endpoint should return the ten largest applicable count.
    """
    day1 = datetime.now(timezone.utc)
    library_tasks = await factories.LibraryTaskFactory.persist_many(db_session, size=11)
    project = await factories.WorkPackageFactory.persist(db_session)
    items = await factories.TaskFactory.batch_with_project_and_location(
        db_session,
        [
            {"project": project, "task_kwargs": {"library_task_id": lib_task.id}}
            for lib_task in library_tasks
        ],
    )
    tasks = [i[0] for i in items]
    library_hazard = await factories.LibraryHazardFactory.persist(db_session)
    filters = dict(start_date=day1, end_date=day1)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    hazard_is_applicable=True, library_hazard=library_hazard, task=task
                )
                for task in tasks
            ]
        },
    )

    for query in (portfolio_task_query, portfolio_task_type_query):
        await assert_applicable_hazards(
            execute_gql,
            query=query,
            filters={**filters, "library_hazard_id": library_hazard.id},
            expected_count=[1] * 10,
        )
    for query in (project_task_query, project_task_type_query):
        await assert_applicable_hazards(
            execute_gql,
            query=query,
            filters={
                **filters,
                "library_hazard_id": library_hazard.id,
                "project_id": project.id,
            },
            expected_count=[1] * 10,
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_applicable_hazards_by_task_drop_zeroes(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    This endpoint should drop zeroes.
    """
    day1 = datetime.now(timezone.utc)

    library_tasks = await factories.LibraryTaskFactory.persist_many(db_session, size=2)
    project = await factories.WorkPackageFactory.persist(db_session)
    items = await factories.TaskFactory.batch_with_project_and_location(
        db_session,
        [
            {"project": project, "task_kwargs": {"library_task_id": lib_task.id}}
            for lib_task in library_tasks
        ],
    )
    task1, task2 = [i[0] for i in items]

    library_hazard = await factories.LibraryHazardFactory.persist(db_session)

    filters = dict(start_date=day1, end_date=day1)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    hazard_is_applicable=True, library_hazard=library_hazard, task=task1
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=library_hazard,
                    task=task2,
                ),
            ]
        },
    )

    # portfolio task
    await assert_applicable_hazards(
        execute_gql,
        query=portfolio_task_query,
        filters={**filters, "library_hazard_id": library_hazard.id},
        expected_count=[1],
    )
    # portfolio task type
    await assert_applicable_hazards(
        execute_gql,
        query=portfolio_task_type_query,
        filters={**filters, "library_hazard_id": library_hazard.id},
        expected_count=[1],
    )
    # project task
    await assert_applicable_hazards(
        execute_gql,
        query=project_task_query,
        filters={
            **filters,
            "library_hazard_id": library_hazard.id,
            "project_id": project.id,
        },
        expected_count=[1],
    )
    # project task type
    await assert_applicable_hazards(
        execute_gql,
        query=project_task_type_query,
        filters={
            **filters,
            "library_hazard_id": library_hazard.id,
            "project_id": project.id,
        },
        expected_count=[1],
    )
