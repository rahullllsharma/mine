import asyncio
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional

import pytest
from faker import Faker

from tests.factories import (
    ActivityFactory,
    LocationFactory,
    TaskFactory,
    TenantFactory,
    TotalProjectRiskScoreModelFactory,
    WorkPackageFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.queries.helpers import (
    asc_order,
    create_project_locations_for_sort,
    create_projects_for_order_by,
    create_projects_risk_level_for_order_by,
    create_tasks_for_project_min_max_dates,
    desc_order,
    setup_tasks_for_project_min_max_dates_for_deleted_tasks,
)
from worker_safety_service.config import settings
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models import (
    AsyncSession,
    Location,
    ProjectStatus,
    WorkPackage,
)
from worker_safety_service.risk_model.metrics.project.total_project_risk_score import (
    TotalProjectRiskScore,
)

project_query = """
query TestQuery($projectId: UUID!, $orderBy: [OrderBy!], $locationId: UUID) {
  project(projectId: $projectId) {
    id
    name
    startDate
    endDate
    status
    number
    description
    minimumTaskDate
    maximumTaskDate
    manager {
      id
      name
      firstName
      lastName
    }
    supervisor {
      id
      name
      firstName
      lastName
    }
    additionalSupervisors {
      id
      name
      firstName
      lastName
    }
    contractor {
      id
      name
    }
    workTypes{
        name
        coreWorkTypeIds
        tenantId
    }
    locations (orderBy: $orderBy, id: $locationId) {
      id
      name
    }
  }
}
"""

projects_query = """
query TestQuery(
    $id: UUID,
    $orderBy: [ProjectOrderBy!],
    $locationsOrderBy: [OrderBy!],
    $riskLevelDate: Date,
    $withRiskLevel: Boolean! = false,
    $withProjectAlias: Boolean! = false,
    $aliasRiskLevelDate: Date,
    $status: ProjectStatus,
    $limit: Int,
    $offset: Int,
  ) {
  projects(id: $id, orderBy: $orderBy, status: $status, limit: $limit, offset: $offset) {
    id
    name
    locations (orderBy: $locationsOrderBy) {
      id
      name
    }
    riskLevel (date: $riskLevelDate) @include(if: $withRiskLevel)
  }
  projectsAlias: projects(orderBy: $orderBy) @include(if: $withProjectAlias) {
    id
    name
    riskLevel (date: $aliasRiskLevelDate)
  }
  projectsAlias2: projects(orderBy: $orderBy) @include(if: $withProjectAlias) {
    id
    name
    riskLevel
  }
}
"""


async def call_projects_query(execute_gql: ExecuteGQL, **kwargs: Any) -> list[dict]:
    filter_ids = kwargs.pop("filter_ids", None)
    data = await execute_gql(query=projects_query, variables=kwargs)
    projects: list[dict] = data["projects"]
    if filter_ids:
        return [i for i in projects if i["id"] in filter_ids]
    else:
        return projects


async def call_projects_query_with_alias(
    execute_gql: ExecuteGQL, **kwargs: Any
) -> tuple[list[dict], list[dict], list[dict]]:
    filter_ids = kwargs.pop("filter_ids", None)
    filter_alias_ids = kwargs.pop("filter_alias_ids", None)
    filter_alias_2_ids = kwargs.pop("filter_alias_2_ids", None)
    kwargs["withProjectAlias"] = True
    data = await execute_gql(query=projects_query, variables=kwargs)
    projects: list[dict] = data["projects"]
    if filter_ids:
        projects = [i for i in projects if i["id"] in filter_ids]
    projects_alias: list[dict] = data["projectsAlias"]
    if filter_alias_ids:
        projects_alias = [i for i in projects_alias if i["id"] in filter_alias_ids]
    project_alias_2: list[dict] = data["projectsAlias2"]
    if filter_alias_2_ids:
        project_alias_2 = [i for i in project_alias_2 if i["id"] in filter_alias_2_ids]
    return projects, projects_alias, project_alias_2


async def call_project_query(
    execute_gql: ExecuteGQL, project_id: str | uuid.UUID, **kwargs: Any
) -> dict:
    kwargs["projectId"] = project_id
    data = await execute_gql(query=project_query, variables=kwargs)
    project: dict = data["project"]
    return project


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_query(execute_gql: ExecuteGQL, project: WorkPackage) -> None:
    response_data = await call_project_query(execute_gql, project.id)
    assert response_data["name"] == project.name
    assert response_data["id"] == str(project.id)
    assert response_data["manager"]["id"] == str(project.manager_id)
    assert response_data["supervisor"]["id"] == str(project.primary_assigned_user_id)
    assert {i["id"] for i in response_data["additionalSupervisors"]} == set(
        map(str, project.additional_assigned_users_ids)
    )
    assert response_data["contractor"]["id"] == str(project.contractor_id)


project_risk_level_query_shape = """
query TestQuery($projectId: UUID!, $date: Date) {
  project(projectId: $projectId) {
    riskLevel(date :$date)
  }
}
"""

project_risk_level_query_shape_no_date = """
query TestQuery($projectId: UUID!) {
  project(projectId: $projectId) {
    riskLevel
  }
}
"""


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_project_query_risk_level(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    risk_model_metrics_manager: RiskModelMetricsManager,
) -> None:
    fake = Faker()
    Faker.seed(0)

    # Risk Model Calc Time-Range
    today = datetime.utcnow().date()
    two_weeks_from_today = today + timedelta(days=14)

    project: WorkPackage = await WorkPackageFactory.persist(
        db_session, start_date=fake.date_between(start_date="-7d", end_date="+1d")
    )
    location: Location = await LocationFactory.persist(
        db_session, project_id=project.id
    )
    await ActivityFactory.persist_many_with_task(
        db_session,
        location_id=location.id,
        start_date=project.start_date,
        end_date=project.end_date,
    )

    dates: list[date] = []
    while len(dates) < 4:
        # To test date = None scenario we want "today"
        # to not be included in risk scores we set
        d = fake.date_between(today + timedelta(days=1), two_weeks_from_today)
        if d not in dates:
            dates.append(d)

    await asyncio.gather(
        TotalProjectRiskScore.store(
            risk_model_metrics_manager, project.id, dates[0], 99
        ),
        TotalProjectRiskScore.store(
            risk_model_metrics_manager, project.id, dates[1], 100
        ),
        TotalProjectRiskScore.store(
            risk_model_metrics_manager, project.id, dates[2], 249
        ),
        TotalProjectRiskScore.store(
            risk_model_metrics_manager, project.id, dates[3], 250
        ),
    )

    # Execute
    async def execute_test(
        query_date: Optional[date], expected_risk_level: str
    ) -> None:
        post_data = {
            "operation_name": "TestQuery",
            "query": (
                project_risk_level_query_shape
                if query_date is not None
                else project_risk_level_query_shape_no_date
            ),
            "variables": {"projectId": str(project.id), "date": str(query_date)},
        }
        data = await execute_gql(**post_data)

        assert data["project"]
        risk_level = data["project"]["riskLevel"]
        assert risk_level and risk_level == expected_risk_level

    await execute_test(
        None, "RECALCULATING"
    )  # Evaluates for today which is within the risk model calc time-range
    await execute_test(dates[0], "LOW")
    await execute_test(dates[1], "MEDIUM")
    await execute_test(dates[2], "MEDIUM")
    await execute_test(dates[3], "HIGH")
    await execute_test(project.start_date - timedelta(days=1), "UNKNOWN")
    await execute_test(project.end_date + timedelta(days=1), "UNKNOWN")
    test_date = project.start_date
    while test_date <= project.end_date:
        if test_date not in dates:
            # Only show RECALCULATING risk level if test_date within
            # risk model calc time-range
            if test_date >= today and test_date < two_weeks_from_today:
                await execute_test(test_date, "RECALCULATING")
            else:
                await execute_test(test_date, "UNKNOWN")
        test_date += timedelta(days=1)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_query_risk_level_multiple_projects(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    risk_model_metrics_manager: RiskModelMetricsManager,
) -> None:
    fake = Faker()
    Faker.seed(0)

    today = datetime.utcnow().date()

    projects = await WorkPackageFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {
                "start_date": today - timedelta(days=10),
                "end_date": today - timedelta(days=1),
            },
            {"start_date": fake.past_date(), "end_date": fake.future_date()},
            {"start_date": fake.past_date(), "end_date": fake.future_date()},
            {"start_date": fake.past_date(), "end_date": fake.future_date()},
            {"start_date": fake.past_date(), "end_date": fake.future_date()},
            {"start_date": fake.past_date(), "end_date": today + timedelta(days=7)},
        ],
    )
    locations = await LocationFactory.persist_many(
        db_session, per_item_kwargs=[{"project_id": i.id} for i in projects]
    )
    await ActivityFactory.persist_many_with_task(
        db_session,
        per_item_kwargs=[
            {
                "location_id": locations[idx].id,
                "start_date": project.start_date,
                "end_date": project.end_date,
            }
            for idx, project in enumerate(projects)
        ],
    )

    await asyncio.gather(
        TotalProjectRiskScore.store(
            risk_model_metrics_manager, projects[1].id, today, 99
        ),  # LOW
        TotalProjectRiskScore.store(
            risk_model_metrics_manager, projects[2].id, today, 100
        ),  # MED
        TotalProjectRiskScore.store(
            risk_model_metrics_manager, projects[3].id, today, 249
        ),  # MED
        TotalProjectRiskScore.store(
            risk_model_metrics_manager, projects[4].id, today, 250
        ),  # HIGH
    )

    # Execute
    async def execute_test() -> Any:
        query = """
        query TestQuery {
          projects {
            id
            riskLevel
          }
        }
        """

        post_data = {"operation_name": "TestQuery", "query": query}
        data = await execute_gql(**post_data)

        assert data["projects"]
        return data["projects"]

    expected = ["UNKNOWN", "LOW", "MEDIUM", "MEDIUM", "HIGH", "RECALCULATING"]
    retrieved_projects = {p["id"]: p["riskLevel"] for p in await execute_test()}
    for n, project in enumerate(projects):
        risk_level = retrieved_projects[str(project.id)]
        expected_risk_level = expected[n]
        assert risk_level == expected_risk_level


@pytest.mark.asyncio
@pytest.mark.integration
async def test_projects_with_status(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check projects are returned with status filter"""

    items: dict[ProjectStatus, str] = {}
    for status in ProjectStatus:
        items[status] = str(
            (await WorkPackageFactory.persist(db_session, status=status)).id
        )

    all_ids = list(items.values())
    for status in ProjectStatus:
        projects = await call_projects_query(
            execute_gql, status=status.name, filter_ids=all_ids
        )
        assert {i["id"] for i in projects} == {items[status]}


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_projects_pagination(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check projects pagination is working"""
    projects_ids = [
        str(i.id)
        for i in await WorkPackageFactory.persist_many(
            db_session,
            per_item_kwargs=[
                {"name": "1"},
                {"name": "2"},
                {"name": "3"},
                {"name": "4"},
                {"name": "5"},
            ],
        )
    ]

    for offset, limit, expected_ids in [
        (0, 2, projects_ids[:2]),
        (2, 2, projects_ids[2:4]),
        (0, 100, projects_ids),
        # Invalid limit defaults to 1
        (0, -100, projects_ids[:1]),
        # Invalid offset defaults to 0
        (-100, 2, projects_ids[:2]),
        # After number of entries, nothing is returned
        (100, 2, []),
    ]:
        projects = await call_projects_query(
            execute_gql,
            limit=limit,
            offset=offset,
            orderBy=[{"field": "NAME", "direction": "ASC"}],
        )
        assert [i["id"] for i in projects] == expected_ids


@pytest.mark.asyncio
@pytest.mark.integration
async def test_projects_ignore_archived(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check archived projects are not returned at all"""

    projects = await WorkPackageFactory.persist_many(db_session, size=5)
    project_ids = [str(p.id) for p in projects]
    fetched_projects = await call_projects_query(execute_gql, filter_ids=project_ids)
    assert {i["id"] for i in fetched_projects} == set(project_ids)

    [p1, project2, p3, project4, p5] = projects
    project2.archived_at = datetime.now(timezone.utc)
    project4.archived_at = datetime.now(timezone.utc)
    await db_session.commit()

    fetched_projects = await call_projects_query(execute_gql, filter_ids=project_ids)
    assert {i["id"] for i in fetched_projects} == set(
        [str(p1.id), str(p3.id), str(p5.id)]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_projects_no_sort(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check projects no order"""

    expected_order = await create_projects_for_order_by(db_session)
    projects = await call_projects_query(
        execute_gql, orderBy=None, filter_ids=expected_order
    )
    assert {i["id"] for i in projects} == set(expected_order)

    projects = await call_projects_query(
        execute_gql, orderBy=[], filter_ids=expected_order
    )
    assert {i["id"] for i in projects} == set(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_projects_asc_sort_on_name(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check projects asc order on name"""

    expected_order = await create_projects_for_order_by(db_session)
    projects = await call_projects_query(
        execute_gql,
        orderBy=[{"field": "NAME", "direction": "ASC"}],
        filter_ids=expected_order,
    )
    assert [i["id"] for i in projects] == asc_order(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_projects_desc_sort_on_name(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check projects desc order on name"""

    expected_order = await create_projects_for_order_by(db_session)
    projects = await call_projects_query(
        execute_gql,
        orderBy=[{"field": "NAME", "direction": "DESC"}],
        filter_ids=expected_order,
    )
    assert [i["id"] for i in projects] == desc_order(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_projects_duplicated_sort_on_name(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check projects duplicated order on name"""

    expected_order = await create_projects_for_order_by(db_session)
    projects = await call_projects_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
        filter_ids=expected_order,
    )
    assert [i["id"] for i in projects] == expected_order

    projects = await call_projects_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "NAME", "direction": "ASC"},
        ],
        filter_ids=expected_order,
    )
    assert [i["id"] for i in projects] == desc_order(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_projects_asc_sort_on_risk_level(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Check projects asc order on risk level
    Call for today, yesterday and no date (today) risk level on same query
    """
    today = datetime.utcnow().date()
    today_order, yesterday_order = await create_projects_risk_level_for_order_by(
        db_session
    )
    (
        projects_today,
        projects_yesterday,
        projects_no_date,
    ) = await call_projects_query_with_alias(
        execute_gql,
        orderBy=[{"field": "RISK_LEVEL", "direction": "ASC"}],
        withRiskLevel=True,
        riskLevelDate=today,
        filter_ids=today_order,
        aliasRiskLevelDate=today - timedelta(days=1),
        filter_alias_ids=yesterday_order,
        filter_alias_2_ids=today_order,
    )
    assert len(projects_today) == len(today_order)
    assert "UNKNOWN" not in {i["riskLevel"] for i in projects_today}
    assert [i["id"] for i in projects_today] == asc_order(today_order)
    assert len(projects_yesterday) == len(yesterday_order)
    assert "UNKNOWN" not in {i["riskLevel"] for i in projects_yesterday}
    assert [i["id"] for i in projects_yesterday] == asc_order(yesterday_order)
    assert len(projects_no_date) == len(today_order)
    assert "UNKNOWN" not in {i["riskLevel"] for i in projects_no_date}
    assert [i["id"] for i in projects_no_date] == asc_order(today_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_projects_desc_sort_on_risk_level(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Check projects desc order on risk level
    Call for today, yesterday and no date (today) risk level on same query
    """
    today = datetime.utcnow().date()
    today_order, yesterday_order = await create_projects_risk_level_for_order_by(
        db_session
    )
    (
        projects_today,
        projects_yesterday,
        projects_no_date,
    ) = await call_projects_query_with_alias(
        execute_gql,
        orderBy=[{"field": "RISK_LEVEL", "direction": "DESC"}],
        withRiskLevel=True,
        riskLevelDate=today,
        filter_ids=today_order,
        aliasRiskLevelDate=today - timedelta(days=1),
        filter_alias_ids=yesterday_order,
        filter_alias_2_ids=today_order,
    )
    assert len(projects_today) == len(today_order)
    assert "UNKNOWN" not in {i["riskLevel"] for i in projects_today}
    assert [i["id"] for i in projects_today] == desc_order(today_order)
    assert len(projects_yesterday) == len(yesterday_order)
    assert "UNKNOWN" not in {i["riskLevel"] for i in projects_yesterday}
    assert [i["id"] for i in projects_yesterday] == desc_order(yesterday_order)
    assert len(projects_no_date) == len(today_order)
    assert "UNKNOWN" not in {i["riskLevel"] for i in projects_no_date}
    assert [i["id"] for i in projects_no_date] == desc_order(today_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_projects_risk_level_and_name(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    If project risk level is the same, name should be the next used order
    """

    today = date.today()
    start_date = today - timedelta(days=5)
    end_date = today + timedelta(days=5)
    kwargs = {"start_date": start_date, "end_date": end_date}
    tasks = await TaskFactory.batch_with_project_and_location(
        db_session,
        [
            {"task_kwargs": kwargs, "project_kwargs": {"name": "á 1", **kwargs}},
            {"task_kwargs": kwargs, "project_kwargs": {"name": "A 2", **kwargs}},
            {"task_kwargs": kwargs, "project_kwargs": {"name": "a 3", **kwargs}},
        ],
    )
    project_1, project_2, project_3 = [str(i[1].id) for i in tasks]

    expected_order = [project_1, project_2, project_3]
    # Reverse the risk level order
    await TotalProjectRiskScoreModelFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {
                "project_id": project_id,
                "value": value,
                "date": today,
                "calculated_at": datetime.now(tz=timezone.utc).replace(
                    hour=11, minute=value, second=0, microsecond=value
                ),
            }
            for value, project_id in enumerate(reversed(expected_order))
        ],
    )

    projects = await call_projects_query(
        execute_gql,
        orderBy=[
            {"field": "RISK_LEVEL", "direction": "ASC"},
            {"field": "NAME", "direction": "ASC"},
        ],
        filter_ids=expected_order,
        withRiskLevel=True,
    )
    assert len(projects) == len(expected_order)
    assert "UNKNOWN" not in {i["riskLevel"] for i in projects}
    assert len({i["riskLevel"] for i in projects}) == 1
    assert [i["id"] for i in projects] == expected_order


@pytest.mark.asyncio
@pytest.mark.integration
async def test_locations_no_order_on_projects(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check locations no order on projects query"""

    project_id, expected_order = await create_project_locations_for_sort(db_session)
    projects = await call_projects_query(
        execute_gql, id=project_id, locationsOrderBy=None
    )
    locations = projects[0]["locations"]
    locations_ids = [i["id"] for i in locations if i["id"] in expected_order]
    assert set(locations_ids) == set(expected_order)

    projects = await call_projects_query(
        execute_gql, id=project_id, locationsOrderBy=[]
    )
    locations = projects[0]["locations"]
    locations_ids = [i["id"] for i in locations if i["id"] in expected_order]
    assert set(locations_ids) == set(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_locations_asc_order_on_projects(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check locations asc order on projects query"""

    project_id, expected_order = await create_project_locations_for_sort(db_session)
    projects = await call_projects_query(
        execute_gql,
        id=project_id,
        locationsOrderBy=[{"field": "NAME", "direction": "ASC"}],
    )
    locations = projects[0]["locations"]
    locations_ids = [i["id"] for i in locations if i["id"] in expected_order]
    assert locations_ids == expected_order


@pytest.mark.asyncio
@pytest.mark.integration
async def test_locations_desc_order_on_projects(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check locations desc order on projects query"""

    project_id, expected_order = await create_project_locations_for_sort(db_session)
    projects = await call_projects_query(
        execute_gql,
        id=project_id,
        locationsOrderBy=[{"field": "NAME", "direction": "DESC"}],
    )
    locations = projects[0]["locations"]
    locations_ids = [i["id"] for i in locations if i["id"] in expected_order]
    assert locations_ids == desc_order(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_locations_no_order_on_project(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check locations no order on project query"""

    project_id, expected_order = await create_project_locations_for_sort(db_session)
    locations = (await call_project_query(execute_gql, project_id, orderBy=None))[
        "locations"
    ]
    locations_ids = [i["id"] for i in locations if i["id"] in expected_order]
    assert set(locations_ids) == set(expected_order)

    locations = (await call_project_query(execute_gql, project_id, orderBy=[]))[
        "locations"
    ]
    locations_ids = [i["id"] for i in locations if i["id"] in expected_order]
    assert set(locations_ids) == set(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_locations_asc_order_on_project(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check locations asc order on project query"""

    project_id, expected_order = await create_project_locations_for_sort(db_session)
    locations = (
        await call_project_query(
            execute_gql, project_id, orderBy=[{"field": "NAME", "direction": "ASC"}]
        )
    )["locations"]
    locations_ids = [i["id"] for i in locations if i["id"] in expected_order]
    assert locations_ids == expected_order


@pytest.mark.asyncio
@pytest.mark.integration
async def test_locations_desc_order_on_project(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check locations desc order on project query"""

    project_id, expected_order = await create_project_locations_for_sort(db_session)
    locations = (
        await call_project_query(
            execute_gql, project_id, orderBy=[{"field": "NAME", "direction": "DESC"}]
        )
    )["locations"]
    locations_ids = [i["id"] for i in locations if i["id"] in expected_order]
    assert locations_ids == desc_order(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_projects_duplicated_name(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    expected_order = await create_projects_for_order_by(db_session, name="cenas")
    projects = await call_projects_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "ID", "direction": "ASC"},
        ],
        filter_ids=expected_order,
    )
    assert [i["id"] for i in projects] == asc_order(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_location_fetch_on_project(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    project_id, expected_order = await create_project_locations_for_sort(db_session)
    locations = (
        await call_project_query(execute_gql, project_id, locationId=expected_order[0])
    )["locations"]
    locations_ids = [i["id"] for i in locations if i["id"] in expected_order]
    assert locations_ids == [expected_order[0]]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_invalid_location_fetch_on_project(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    project_id, _ = await create_project_locations_for_sort(db_session)
    _, expected_order = await create_project_locations_for_sort(db_session)
    locations = (
        await call_project_query(execute_gql, project_id, locationId=expected_order[0])
    )["locations"]
    assert not locations

    tenant_id = (await TenantFactory.persist(db_session)).id
    _, expected_sec_order = await create_project_locations_for_sort(
        db_session, tenant_id=tenant_id
    )
    locations = (
        await call_project_query(
            execute_gql, project_id, locationId=expected_sec_order[0]
        )
    )["locations"]
    assert not locations


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_minimum_and_maximum_task_dates(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    (
        project_id,
        expected_minimum_date,
        expected_maximum_date,
    ) = await create_tasks_for_project_min_max_dates(db_session)

    project = await call_project_query(execute_gql, project_id)

    assert project["minimumTaskDate"] == str(expected_minimum_date)
    assert project["maximumTaskDate"] == str(expected_maximum_date)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_minimum_and_maximum_task_dates_respect_deleted_tasks(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    (
        project_id,
        task_id,
        expected_minimum_date,
        expected_maximum_date,
        initial_minimum_date,
        initial_maximum_date,
    ) = await setup_tasks_for_project_min_max_dates_for_deleted_tasks(
        db_session=db_session
    )

    project = await call_project_query(execute_gql, project_id)
    assert project["minimumTaskDate"] == str(initial_minimum_date)
    assert project["maximumTaskDate"] == str(initial_maximum_date)

    delete_task_mutation = {
        "operation_name": "DeleteTask",
        "query": "mutation DeleteTask($id: UUID!) { task: deleteTask(id: $id) }",
    }

    await execute_gql(**delete_task_mutation, variables={"id": task_id})

    project = await call_project_query(execute_gql, project_id)

    assert project["minimumTaskDate"] == str(expected_minimum_date)
    assert project["maximumTaskDate"] == str(expected_maximum_date)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_query_depth(execute_gql: ExecuteGQL, db_session: AsyncSession) -> None:
    project_id = str((await WorkPackageFactory.persist(db_session)).id)
    await LocationFactory.persist(db_session, project_id=project_id)

    def extend_query(query: str, set_project: bool, depth: int) -> str:
        if set_project:
            query += "project { id "
        else:
            query += "locations { id "
        if depth > 0:
            query = extend_query(query, not set_project, depth - 1)
        query += "}"
        return query

    main_query = (
        "query TestQuery($projectId: UUID!) { project(projectId: $projectId) { id "
    )

    # Slow be allowed
    query = (
        extend_query(
            main_query, set_project=False, depth=settings.GRAPHQL_MAX_QUERY_DEPTH - 2
        )
        + "}}"
    )
    data = await execute_gql(query=query, variables={"projectId": project_id})
    assert data["project"]

    # Not allowed
    query = (
        extend_query(
            main_query, set_project=False, depth=settings.GRAPHQL_MAX_QUERY_DEPTH - 1
        )
        + "}}"
    )
    with pytest.raises(Exception):
        data = await execute_gql(query=query, variables={"projectId": project_id})
