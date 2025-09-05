import asyncio
import uuid
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional
from unittest import TestCase

import pytest
from faker import Faker

from tests.factories import (
    ActivityFactory,
    ContractorFactory,
    LibraryDivisionFactory,
    LibraryProjectTypeFactory,
    LibraryRegionFactory,
    LocationFactory,
    SiteConditionFactory,
    SupervisorUserFactory,
    TaskFactory,
    TenantFactory,
    TotalProjectLocationRiskScoreModelFactory,
    WorkPackageFactory,
    WorkTypeFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.helpers import create_project
from tests.integration.queries.helpers import (
    asc_order,
    build_library_site_conditions_for_order_by,
    build_library_tasks_for_order_by,
    create_project_locations_for_sort,
    desc_order,
)
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.graphql.types import RiskLevel
from worker_safety_service.models import (
    AsyncSession,
    Contractor,
    Location,
    Supervisor,
    Tenant,
    User,
    WorkPackage,
)
from worker_safety_service.risk_model.metrics.contractor.contractor_safety_score import (
    ContractorSafetyScore,
)
from worker_safety_service.risk_model.metrics.contractor.global_contractor_safety_score import (
    GlobalContractorSafetyScore,
)
from worker_safety_service.risk_model.metrics.global_supervisor_enganement_factor import (
    GlobalSupervisorEngagementFactor,
)
from worker_safety_service.risk_model.metrics.project.total_project_location_risk_score import (
    TotalProjectLocationRiskScore,
)
from worker_safety_service.risk_model.metrics.supervisor_engagement_factor import (
    SupervisorEngagementFactor,
)
from worker_safety_service.risk_model.metrics.tasks.project_location_total_task_riskscore import (
    ProjectLocationTotalTaskRiskScore,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_riskscore import (
    TaskSpecificRiskScore,
)
from worker_safety_service.types import Point

project_with_locations_query = """
query TestQuery($projectId: UUID!) {
  project(projectId: $projectId) {
    id name locations { id }
  }
}
"""

projects_with_locations_query = """
query TestQuery($projectId: UUID!) {
  projects(id: $projectId) {
    id name
    locations {
        id
        supervisor { id name }
        additionalSupervisors { id name }
    }
  }
}
"""

all_projects_with_locations_query = """
query TestQuery {
  projects {
    id name locations { id }
  }
}
"""

locations_query = """
query TestQuery (
  $id: UUID,
  $orderBy: [ProjectLocationOrderBy!],
  $tasksOrderBy: [TaskOrderBy!],
  $siteConditionsOrderBy: [OrderBy!],
  $limit: Int,
  $offset: Int
) {
  projectLocations (id: $id, orderBy: $orderBy, limit: $limit, offset: $offset) {
    id
    supervisor { id name }
    additionalSupervisors { id name }
    tasks (orderBy: $tasksOrderBy) { id name }
    siteConditions (orderBy: $siteConditionsOrderBy) { id name }
  }
}
"""

locations_ranking_query = """
query TestQuery($locationId: UUID!, $date: Date) {
  projectLocations(id: $locationId) {
    id
    riskCalculation(date :$date) {
        totalTaskRiskLevel
    }
  }
}
"""

locations_ranking_query_no_date = """
query TestQuery($locationId: UUID!) {
  projectLocations(id: $locationId) {
    id
    riskCalculation {
        totalTaskRiskLevel
    }
  }
}
"""

contractor_at_risk_query = """
query TestQuery($locationId: UUID!) {
  projectLocations(id: $locationId) {
    id
    riskCalculation {
        isContractorAtRisk
    }
  }
}
"""

supervisor_at_risk_query = """
query TestQuery($locationId: UUID!) {
  projectLocations(id: $locationId) {
    id
    riskCalculation {
        isSupervisorAtRisk
    }
  }
}
"""

locations_risk_level_query = """
query TestQuery($locationId: UUID!, $date: Date) {
  projectLocations(id: $locationId) {
    id
    riskLevel(date :$date)
  }
}
"""

locations_risk_level_query_no_date = """
query TestQuery($locationId: UUID!) {
  projectLocations(id: $locationId) {
    id
    riskLevel
  }
}
"""

locations_tasks_ranking_query_no_date = """
query TestQuery($locationId: UUID!) {
  projectLocations(id: $locationId) {
    id
    tasks {
        id
        riskLevel
    }
  }
}
"""

locations_with_filter_by = """
query TestQuery($filterBy: [LocationFilterBy!]) {
  projectLocations(filterBy: $filterBy) {
    id
    name
    project {
        id
        libraryDivision {
            id
            name
        }
        libraryRegion {
            id
            name
        }
        libraryProjectType {
            id
            name
        }
        workTypes {
            id
            name
        }
    }
    risk
  }
}
"""


async def call_project_locations_query(
    execute_gql: ExecuteGQL, **kwargs: Any
) -> list[dict]:
    data = await execute_gql(query=locations_query, variables=kwargs)
    locations: list[dict] = data["projectLocations"]
    return locations


async def execute_locations_with_filter_by(
    execute_gql: ExecuteGQL,
    filters_by: list[dict],
    raw: bool = False,
) -> Any:
    post_data = {
        "operation_name": "TestQuery",
        "query": locations_with_filter_by,
        "variables": {"filterBy": filters_by},
    }
    data = await execute_gql(**post_data, raw=raw)
    if raw:
        return data
    else:
        return data["projectLocations"]


async def fetch_locations_ids_with_filter_by(
    execute_gql: ExecuteGQL, filters_by: list[dict]
) -> set[str]:
    data = await execute_locations_with_filter_by(execute_gql, filters_by)
    return {str(i["id"]) for i in data}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_with_locations_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    _, project_data = await create_project(execute_gql, db_session)
    location = project_data["locations"][0]

    post_data = {
        "operation_name": "TestQuery",
        "query": projects_with_locations_query,
        "variables": {"projectId": project_data["id"]},
    }
    data = await execute_gql(**post_data)
    project = data["projects"][0]
    assert project["id"] == project_data["id"]
    assert len(project["locations"]) == 1

    location_data = project["locations"][0]
    assert location["id"] == location_data["id"]
    assert location["supervisor"]["id"] == location_data["supervisor"]["id"]
    assert {i["id"] for i in location["additionalSupervisors"]} == {
        i["id"] for i in location_data["additionalSupervisors"]
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_location_by_id_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    _, project_data = await create_project(execute_gql, db_session)
    location = project_data["locations"][0]

    locations = await call_project_locations_query(execute_gql, id=location["id"])
    assert len(locations) == 1

    location_data = locations[0]
    assert location["id"] == location_data["id"]
    assert location["supervisor"]["id"] == location_data["supervisor"]["id"]
    assert {i["id"] for i in location["additionalSupervisors"]} == {
        i["id"] for i in location_data["additionalSupervisors"]
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_locations_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    _, project_data = await create_project(execute_gql, db_session)
    location = project_data["locations"][0]

    locations_by_id = {
        i["id"]: i
        for i in await call_project_locations_query(execute_gql, id=location["id"])
    }

    location_data = locations_by_id[location["id"]]
    assert location["id"] == location_data["id"]
    assert location["supervisor"]["id"] == location_data["supervisor"]["id"]
    assert {i["id"] for i in location["additionalSupervisors"]} == {
        i["id"] for i in location_data["additionalSupervisors"]
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_locations_query_with_archiving(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Queries for project locations on a project, using a few cases of the project
    and projects queries:
    - `project(projectId)` - fetch a single project
    - `projects(id)` - fetch a list of projects, filtering by project id
    - `projects()` - fetch all projects
    - `projectLocations()` - fetch all locations
    - `projectLocations(id)` - fetch a list of locations, filtering by location id

    Asserts that archived project_locations are not included in results.
    """

    # create project
    project: WorkPackage = await WorkPackageFactory.persist(db_session)

    # create 4 locations on the project
    locations: list[Location] = await LocationFactory.persist_many(
        db_session, project_id=project.id, size=4
    )
    expected_location_ids = set(map(lambda x: str(x.id), locations))
    await db_session.refresh(project)

    post_data = {
        "operation_name": "TestQuery",
        "query": project_with_locations_query,
        "variables": {"projectId": str(project.id)},
    }

    data = await execute_gql(**post_data)
    assert data["project"]["id"] == str(project.id)  # sanity check
    project_data = data["project"]

    fetched_locations = project_data["locations"]
    fetched_location_ids: set[uuid.UUID] = {i["id"] for i in fetched_locations}

    assert len(fetched_locations) == 4
    assert expected_location_ids == fetched_location_ids

    ###########################################################
    # archive two of the locations, then query again

    archived_locs = [locations[0], locations[2]]
    archived_loc_ids = set()
    for loc in archived_locs:
        loc.archived_at = datetime.now(timezone.utc)
        expected_location_ids.remove(str(loc.id))
        archived_loc_ids.add(str(loc.id))
    await db_session.commit()

    data = await execute_gql(**post_data)
    assert data["project"]["id"] == str(project.id)  # sanity check
    fetched_locations = data["project"]["locations"]
    fetched_location_ids = {i["id"] for i in fetched_locations}

    assert len(fetched_locations) == 2
    assert expected_location_ids == fetched_location_ids

    ###########################################################
    # ensure similar filtering when requesting multiple projects

    post_data = {
        "operation_name": "TestQuery",
        "query": projects_with_locations_query,
        "variables": {"projectId": str(project.id)},
    }
    data = await execute_gql(**post_data)
    assert data["projects"][0]["id"] == str(project.id)  # sanity check
    fetched_locations = data["projects"][0]["locations"]
    fetched_location_ids = {i["id"] for i in fetched_locations}

    assert len(fetched_locations) == 2
    assert expected_location_ids == fetched_location_ids

    ###########################################################
    # ensure similar filtering when requesting 'all' projects

    post_data = {
        "operation_name": "TestQuery",
        "query": all_projects_with_locations_query,
    }
    data = await execute_gql(**post_data)
    project_data = list(filter(lambda x: x["id"] == str(project.id), data["projects"]))[
        0
    ]
    assert project_data  # sanity check
    fetched_locations = project_data["locations"]
    fetched_location_ids = {i["id"] for i in fetched_locations}

    assert len(fetched_locations) == 2
    assert expected_location_ids == fetched_location_ids

    ###########################################################
    # ensure none of the archived locations returned are returned

    fetched_locations = await call_project_locations_query(execute_gql)
    fetched_location_ids = {i["id"] for i in fetched_locations}

    # ensure some locations are returned
    assert fetched_location_ids
    # there should be no intersection of these ids
    assert not set(archived_loc_ids).intersection(fetched_location_ids)

    ###########################################################
    # fetch a location using an archived location id

    archived_loc_id = list(archived_loc_ids)[0]
    fetched_locations = await call_project_locations_query(
        execute_gql, id=archived_loc_id
    )
    # assert that archived locations are not fetched, even by id.
    # this behavior is debatable - if we'd rather, we can reverse this assertion
    # and update the app's logic
    assert len(fetched_locations) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_locations_query_with_risk_rankings(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    risk_model_metrics_manager: RiskModelMetricsManager,
) -> None:
    fake = Faker()

    # Risk Model Calc Time-Range
    today = datetime.utcnow().date()
    two_weeks_from_today = today + timedelta(days=14)

    # create project & location
    supervisor = await SupervisorUserFactory.persist(db_session)
    contractor = await ContractorFactory.persist(db_session)

    project: WorkPackage = await WorkPackageFactory.persist(
        db_session,
        start_date=fake.date_between(start_date="-7d", end_date="+1d"),
        contractor_id=contractor.id,
    )
    location = await LocationFactory.persist(
        db_session, project_id=project.id, primary_assigned_user_id=supervisor.id
    )
    await ActivityFactory.persist_many_with_task(
        db_session,
        location_id=location.id,
        start_date=project.start_date,
        end_date=project.end_date,
        size=3,
    )

    # TODO: Find why this hack was needed, faker was spitting 3 times the same date before starting to randomize them
    dates: list[date] = []
    while len(dates) < 3:
        # To test date = None scenario we want "today"
        # to not be included in risk scores we set
        d = fake.date_between(today + timedelta(days=1), two_weeks_from_today)
        if d not in dates:
            dates.append(d)

    await asyncio.gather(
        ProjectLocationTotalTaskRiskScore.store(
            risk_model_metrics_manager, location.id, dates[0], 80
        ),
        ProjectLocationTotalTaskRiskScore.store(
            risk_model_metrics_manager, location.id, dates[1], 100
        ),
        ProjectLocationTotalTaskRiskScore.store(
            risk_model_metrics_manager, location.id, dates[2], 210
        ),
    )

    # Execute
    async def execute_test(
        query_date: Optional[date], expect_total_risk_level: str
    ) -> None:
        post_data = {
            "operation_name": "TestQuery",
            "query": (
                locations_ranking_query
                if query_date is not None
                else locations_ranking_query_no_date
            ),
            "variables": {"locationId": str(location.id), "date": str(query_date)},
        }
        data = await execute_gql(**post_data)
        fetched_locations = data["projectLocations"]
        assert len(fetched_locations) == 1
        assert fetched_locations[0]["riskCalculation"] == {
            "totalTaskRiskLevel": expect_total_risk_level
        }

    await execute_test(
        None, "RECALCULATING"
    )  # Evaluates for today which is within the risk model calc time-range
    await execute_test(dates[0], "LOW")
    await execute_test(dates[1], "MEDIUM")
    await execute_test(dates[2], "HIGH")
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
async def test_project_locations_query_with_task_risk_rankings(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    risk_model_metrics_manager: RiskModelMetricsManager,
) -> None:
    fake = Faker()
    # create project & location
    contractor: Contractor = await ContractorFactory.persist(db_session)

    project: WorkPackage = await WorkPackageFactory.persist(
        db_session,
        start_date=fake.date_between(start_date="+1d", end_date="+7d"),
        contractor_id=contractor.id,
    )
    location: Location = await LocationFactory.persist(
        db_session, project_id=project.id
    )

    # Set task specific risk scores
    # Tasks 1 to 3 must have their respective risk score as defined in values
    # Tasks 4 to 5 are outside the reference date, although they wrongly have a value defined, they should UNKNOWN
    # Tasks 6 to 8 must show RECALCULATING because we are not defining a risk score for them
    reference_date = datetime.utcnow().date()
    task_dates = [
        {"start_date": reference_date, "end_date": reference_date + timedelta(days=3)},
        {"start_date": reference_date - timedelta(days=3), "end_date": reference_date},
        {
            "start_date": reference_date - timedelta(days=3),
            "end_date": reference_date + timedelta(days=3),
        },
        {
            "start_date": reference_date - timedelta(days=3),
            "end_date": reference_date - timedelta(days=1),
        },
        {
            "start_date": reference_date + timedelta(days=1),
            "end_date": reference_date + timedelta(days=3),
        },
        {"start_date": reference_date, "end_date": reference_date + timedelta(days=3)},
        {"start_date": reference_date - timedelta(days=3), "end_date": reference_date},
        {
            "start_date": reference_date - timedelta(days=3),
            "end_date": reference_date + timedelta(days=3),
        },
    ]
    tasks = [
        await TaskFactory.persist(db_session, location_id=location.id, **kwargs)
        for kwargs in task_dates
    ]
    values = [80.0, 100.0, 210.0, 100, 100]
    await asyncio.gather(
        *[
            TaskSpecificRiskScore.store(
                risk_model_metrics_manager, tasks[n].id, reference_date, values[n]
            )
            for n in range(0, 5)
        ]
    )

    expected = [
        {"id": str(tasks[0].id), "riskLevel": "LOW"},
        {"id": str(tasks[1].id), "riskLevel": "MEDIUM"},
        {"id": str(tasks[2].id), "riskLevel": "HIGH"},
        {"id": str(tasks[3].id), "riskLevel": "UNKNOWN"},
        {"id": str(tasks[4].id), "riskLevel": "UNKNOWN"},
        {"id": str(tasks[5].id), "riskLevel": "RECALCULATING"},
        {"id": str(tasks[6].id), "riskLevel": "RECALCULATING"},
        {"id": str(tasks[7].id), "riskLevel": "RECALCULATING"},
    ]

    async def execute_test(query_date: Optional[date]) -> Any:
        post_data = {
            "operation_name": "TestQuery",
            "query": locations_tasks_ranking_query_no_date,
            "variables": {"locationId": str(location.id), "date": str(query_date)},
        }
        _data = await execute_gql(**post_data)
        fetched_locations = _data["projectLocations"]
        assert len(fetched_locations) == 1
        return fetched_locations

    # Execute
    data = await execute_test(
        None
    )  # Evaluates for today which should be outside the project boundaries
    test = TestCase()
    test.assertCountEqual(data[0]["tasks"], expected, "Must contain the same elements")

    fetched_tasks = data[0]["tasks"]
    tasks_data = {d["id"]: d["riskLevel"] for d in fetched_tasks}

    assert expected  # make sure we don't pass b/c expected is empty
    for e in expected:
        fetched_risk = tasks_data[e["id"]]
        assert fetched_risk == e["riskLevel"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_locations_query_risk_level(
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
        size=3,
    )

    dates: list[date] = []
    while len(dates) < 4:
        # To test date = None scenario we want "today"
        # to not be included in risk scores we set
        d = fake.date_between(today + timedelta(days=1), two_weeks_from_today)
        if d not in dates:
            dates.append(d)

    await asyncio.gather(
        TotalProjectLocationRiskScore.store(
            risk_model_metrics_manager, location.id, dates[0], 99
        ),
        TotalProjectLocationRiskScore.store(
            risk_model_metrics_manager, location.id, dates[1], 100
        ),
        TotalProjectLocationRiskScore.store(
            risk_model_metrics_manager, location.id, dates[2], 249
        ),
        TotalProjectLocationRiskScore.store(
            risk_model_metrics_manager, location.id, dates[3], 250
        ),
    )

    # Execute
    async def execute_test(
        query_date: Optional[date], expected_risk_level: str
    ) -> None:
        post_data = {
            "operation_name": "TestQuery",
            "query": (
                locations_risk_level_query
                if query_date is not None
                else locations_risk_level_query_no_date
            ),
            "variables": {"locationId": str(location.id), "date": str(query_date)},
        }
        data = await execute_gql(**post_data)
        fetched_locations = data["projectLocations"]
        assert len(fetched_locations) == 1
        assert fetched_locations[0]["riskLevel"] == expected_risk_level

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
async def test_project_locations_no_sort(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check project locations without order"""

    _, expected_order = await create_project_locations_for_sort(db_session)
    locations = await call_project_locations_query(execute_gql, orderBy=None)
    locations_ids = [i["id"] for i in locations if i["id"] in expected_order]
    assert set(locations_ids) == set(expected_order)

    locations = await call_project_locations_query(execute_gql, orderBy=[])
    locations_ids = [i["id"] for i in locations if i["id"] in expected_order]
    assert set(locations_ids) == set(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_locations_asc_sort(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check project locations with asc order"""

    _, expected_order = await create_project_locations_for_sort(db_session)
    locations = await call_project_locations_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "ASC"}]
    )
    locations_ids = [i["id"] for i in locations if i["id"] in expected_order]
    assert locations_ids == expected_order


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_locations_desc_sort(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check project locations with desc order"""

    _, expected_order = await create_project_locations_for_sort(db_session)
    locations = await call_project_locations_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "DESC"}]
    )
    locations_ids = [i["id"] for i in locations if i["id"] in expected_order]
    assert locations_ids == desc_order(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_locations_with_multiple_order_by(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check project locations with duplicated fields order"""

    _, expected_order = await create_project_locations_for_sort(db_session)
    locations = await call_project_locations_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
    )
    locations_ids = [i["id"] for i in locations if i["id"] in expected_order]
    assert locations_ids == expected_order

    locations = await call_project_locations_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "NAME", "direction": "ASC"},
        ],
    )
    locations_ids = [i["id"] for i in locations if i["id"] in expected_order]
    assert locations_ids == desc_order(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_order_on_project_location(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check tasks order on project locations query"""

    project_id = str((await WorkPackageFactory.persist(db_session)).id)
    location_1 = str(
        (
            await LocationFactory.persist(db_session, project_id=project_id, name="á 1")
        ).id
    )
    location_2 = str(
        (
            await LocationFactory.persist(db_session, project_id=project_id, name="A 2")
        ).id
    )
    location_3 = str(
        (
            await LocationFactory.persist(db_session, project_id=project_id, name="a 3")
        ).id
    )
    expected_order = [location_1, location_2, location_3]

    expected_tasks_order: defaultdict[str, list[str]] = defaultdict(list)
    library_task_ids = await build_library_tasks_for_order_by(db_session)
    for location_id in expected_order:
        for library_task_id in library_task_ids:
            expected_tasks_order[location_id].append(
                str(
                    (
                        await TaskFactory.persist(
                            db_session,
                            location_id=location_id,
                            library_task_id=library_task_id,
                        )
                    ).id
                )
            )

    available_order = [("ASC", asc_order), ("DESC", desc_order)]
    tasks_available_order = [
        ("NAME", "ASC", asc_order),
        ("NAME", "DESC", desc_order),
        ("CATEGORY", "ASC", desc_order),
        ("CATEGORY", "DESC", asc_order),
    ]
    for direction, set_order in available_order:
        for task_field, task_direction, task_set_order in tasks_available_order:
            locations = await call_project_locations_query(
                execute_gql,
                orderBy=[{"field": "NAME", "direction": direction}],
                tasksOrderBy=[{"field": task_field, "direction": task_direction}],
            )
            locations_by_id = {
                i["id"]: i for i in locations if i["id"] in expected_order
            }
            assert set_order(list(locations_by_id.keys())) == expected_order
            for location in locations_by_id.values():
                tasks_ids = [i["id"] for i in location["tasks"]]
                assert task_set_order(tasks_ids) == expected_tasks_order[location["id"]]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_site_conditions_order_on_project_location(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check site conditions order on project locations query"""

    project_id = str((await WorkPackageFactory.persist(db_session)).id)
    location_1 = str(
        (
            await LocationFactory.persist(db_session, project_id=project_id, name="á 1")
        ).id
    )
    location_2 = str(
        (
            await LocationFactory.persist(db_session, project_id=project_id, name="A 2")
        ).id
    )
    location_3 = str(
        (
            await LocationFactory.persist(db_session, project_id=project_id, name="a 3")
        ).id
    )
    expected_order = [location_1, location_2, location_3]

    expected_site_conditions_order: defaultdict[str, list[str]] = defaultdict(list)
    library_site_condition_ids = await build_library_site_conditions_for_order_by(
        db_session
    )
    for location_id in expected_order:
        for library_site_condition_id in library_site_condition_ids:
            expected_site_conditions_order[location_id].append(
                str(
                    (
                        await SiteConditionFactory.persist(
                            db_session,
                            location_id=location_id,
                            library_site_condition_id=library_site_condition_id,
                        )
                    ).id
                )
            )

    available_order = [("ASC", asc_order), ("DESC", desc_order)]
    for direction, set_order in available_order:
        for site_condition_direction, site_condition_set_order in available_order:
            locations = await call_project_locations_query(
                execute_gql,
                orderBy=[{"field": "NAME", "direction": direction}],
                siteConditionsOrderBy=[
                    {"field": "NAME", "direction": site_condition_direction}
                ],
            )
            locations_by_id = {
                i["id"]: i for i in locations if i["id"] in expected_order
            }
            assert set_order(list(locations_by_id.keys())) == expected_order
            for location in locations_by_id.values():
                site_conditions_ids = [i["id"] for i in location["siteConditions"]]
                assert (
                    site_condition_set_order(site_conditions_ids)
                    == expected_site_conditions_order[location["id"]]
                )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_project_locations_duplicated_name(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    _, expected_order = await create_project_locations_for_sort(
        db_session, name="cenas"
    )
    locations = await call_project_locations_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "ID", "direction": "ASC"},
        ],
    )
    locations_ids = [i["id"] for i in locations if i["id"] in expected_order]
    assert locations_ids == expected_order


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_project_locations_pagination(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check project locations pagination is working"""
    location_ids = [
        str(i.id)
        for i in await LocationFactory.persist_many(
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
        (0, 2, location_ids[:2]),
        (2, 2, location_ids[2:4]),
        (0, 100, location_ids),
        # Invalid limit defaults to 1
        (0, -100, location_ids[:1]),
        # Invalid offset defaults to 0
        (-100, 2, location_ids[:2]),
        # After number of entries, nothing is returned
        (100, 2, []),
    ]:
        locations = await call_project_locations_query(
            execute_gql,
            limit=limit,
            offset=offset,
            orderBy=[{"field": "NAME", "direction": "ASC"}],
        )
        assert [i["id"] for i in locations] == expected_ids


@pytest.mark.asyncio
@pytest.mark.integration
async def test_is_contractor_at_risk(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    risk_model_metrics_manager: RiskModelMetricsManager,
) -> None:
    fake = Faker()

    tenant: Tenant = await TenantFactory.default_tenant(db_session)
    contractor: Contractor = await ContractorFactory.persist(
        db_session, tenant_id=tenant.id
    )
    project: WorkPackage = await WorkPackageFactory.persist(
        db_session,
        start_date=fake.date_between(start_date="+1d", end_date="+7d"),
        contractor_id=contractor.id,
    )

    location: Location = await LocationFactory.persist(
        db_session, project_id=project.id
    )

    async def execute_test(expect_contractor_is_at_risk: bool) -> None:
        post_data = {
            "operation_name": "TestQuery",
            "query": contractor_at_risk_query,
            "variables": {"locationId": str(location.id)},
        }
        data = await execute_gql(**post_data)
        fetched_locations = data["projectLocations"]
        assert len(fetched_locations) == 1
        assert (
            fetched_locations[0]["riskCalculation"]["isContractorAtRisk"]
            == expect_contractor_is_at_risk
        )

    expected: list[tuple[float, float, float, bool]] = [
        (11.234, 6.43, 0.78, True),
        (23.9295, 2.3211, 2.758, True),
        (4.5216, 20.9755, 0.8365, False),
        (4.2949, 8.1748, 2.8987, False),
        (8.5248, 8.9754, 3.1235, False),
        (17.538, 12.9943, 1.7705, True),
    ]

    for item in expected:
        await asyncio.gather(
            ContractorSafetyScore.store(
                risk_model_metrics_manager, contractor.id, item[0]
            ),
            GlobalContractorSafetyScore.store(
                risk_model_metrics_manager, tenant.id, item[1], item[2]
            ),
        )
        await execute_test(item[3])


# TODO: Refactor this to better handle factories
#  once https://github.com/urbint/worker-safety-service/pull/259 has merged
@pytest.mark.asyncio
@pytest.mark.integration
async def test_is_supervisor_at_risk(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    risk_model_metrics_manager: RiskModelMetricsManager,
) -> None:
    fake = Faker()

    tenant: Tenant = await TenantFactory.default_tenant(db_session)

    user_supervisor: User = await SupervisorUserFactory.persist(db_session)
    supervisor: Supervisor = Supervisor(
        id=user_supervisor.id, external_key=uuid.uuid4().hex, tenant_id=tenant.id
    )
    db_session.add(supervisor)
    await db_session.commit()
    await db_session.refresh(supervisor)

    project = await WorkPackageFactory.persist(
        db_session,
        start_date=fake.date_between(start_date="+1d", end_date="+7d"),
    )
    location = Location(
        project_id=project.id,
        supervisor_id=supervisor.id,
        project=project,
        name=fake.name(),
        geom=Point(fake.longitude(), fake.latitude()),
        additional_supervisor_ids=[],
        tenant_id=tenant.id,
        clustering=[],
    )
    db_session.add(location)
    await db_session.commit()
    await db_session.refresh(location)

    async def execute_test(expect_supervisor_is_at_risk: bool) -> None:
        post_data = {
            "operation_name": "TestQuery",
            "query": supervisor_at_risk_query,
            "variables": {"locationId": str(location.id)},
        }
        data = await execute_gql(**post_data)
        fetched_locations = data["projectLocations"]
        assert len(fetched_locations) == 1
        assert (
            fetched_locations[0]["riskCalculation"]["isSupervisorAtRisk"]
            == expect_supervisor_is_at_risk
        )

    expected: list[tuple[float, float, float, bool]] = [
        (15.1842, 16.2352, 3.2541, False),
        (16.2412, 0.9458, 2.9234, True),
        (18.5125, 11.4973, 1.7866, True),
        (21.4568, 21.2004, 2.0498, False),
        (0.4471, 10.6334, 3.7703, False),
        (24.7561, 22.0951, 0.3092, True),
    ]

    for item in expected:
        await asyncio.gather(
            SupervisorEngagementFactor.store(
                risk_model_metrics_manager, supervisor.id, item[0]
            ),
            GlobalSupervisorEngagementFactor.store(
                risk_model_metrics_manager, tenant.id, item[1], item[2]
            ),
        )
        await execute_test(item[3])


location_order_by_risk_name = """
query TestQuery($orderBy: [ProjectLocationOrderBy!], $date: Date) {
  projectLocations(orderBy: $orderBy) {
    id
    riskLevel(date: $date)
    name
    project {
      id
      name
    }
  }
}
"""


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_project_location_orders_by_risk_level_and_name(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    risks = ["LOW", "LOW", "MEDIUM", "MEDIUM", "HIGH", "HIGH"]
    names = ["alfa", "bravo", "charlie", "delta", "echo", "foxtrot"]
    project = await WorkPackageFactory.persist(db_session)
    locations = await LocationFactory.persist_many(
        db_session,
        per_item_kwargs=[{"project_id": project.id, "name": name} for name in names],
    )
    await TotalProjectLocationRiskScoreModelFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {
                "project_location_id": location.id,
                "value": risk,
                "date": project.start_date + timedelta(days=1),
                "calculated_at": datetime.now(timezone.utc).replace(microsecond=risk),
            }
            for location, risk in zip(locations, [40, 90, 150, 200, 251, 300])
        ],
    )
    await TaskFactory.batch_with_project_and_location(
        db_session,
        [
            {
                "project": project,
                "location": location,
                "task_kwargs": {
                    "start_date": project.start_date,
                    "end_date": project.end_date,
                    "status": "in_progress",
                },
            }
            for location in locations
        ],
    )

    post_data = {
        "operation_name": "TestQuery",
        "query": location_order_by_risk_name,
        "variables": {
            "orderBy": [
                {"field": "RISK_LEVEL", "direction": "ASC"},
                {"field": "NAME", "direction": "ASC"},
            ],
            "date": project.start_date + timedelta(days=1),
        },
    }
    data = await execute_gql(**post_data)
    # The projectLocations query gets data for _all_ locations
    # including locations created in other tests.
    # Limit data to the project from this test (ie: treat other records as deleted).
    asc_data = [
        d for d in data["projectLocations"] if d["project"]["id"] == str(project.id)
    ]
    assert len(asc_data) == 6
    assert names == [pl["name"] for pl in asc_data]
    assert risks == [pl["riskLevel"] for pl in asc_data]

    post_data = {
        "operation_name": "TestQuery",
        "query": location_order_by_risk_name,
        "variables": {
            "orderBy": [
                {"field": "RISK_LEVEL", "direction": "DESC"},
                {"field": "NAME", "direction": "DESC"},
            ],
            "date": project.start_date + timedelta(days=1),
        },
    }
    data = await execute_gql(**post_data)
    desc_pls = [
        d for d in data["projectLocations"] if d["project"]["id"] == str(project.id)
    ]
    assert len(desc_pls) == 6
    assert [r for r in reversed(risks)] == [pl["riskLevel"] for pl in desc_pls]
    assert [n for n in reversed(names)] == [pl["name"] for pl in desc_pls]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_location_filters_empty_data(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    # create 8 projects with 1 location each
    project_types = [
        await LibraryProjectTypeFactory.persist(db_session, name="pt_type_one"),
        await LibraryProjectTypeFactory.persist(db_session, name="two"),
    ]
    work_types = [
        await WorkTypeFactory.persist(db_session, name="wt_type_one"),
        await WorkTypeFactory.persist(db_session, name="two"),
    ]
    divisions = [
        await LibraryDivisionFactory.persist(db_session, name="division_one"),
        await LibraryDivisionFactory.persist(db_session, name="division_two"),
    ]
    regions = [
        await LibraryRegionFactory.persist(db_session, name="region_one"),
        await LibraryRegionFactory.persist(db_session, name="region_one"),
    ]

    projects = await WorkPackageFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {
                "work_type_id": project_type.id,
                "work_type_ids": [type.id for type in work_types],
                "region_id": region.id,
                "division_id": division.id,
            }
            for project_type in project_types
            for division in divisions
            for region in regions
        ],
    )
    await LocationFactory.persist_many(
        db_session, per_item_kwargs=[{"project_id": i.id} for i in projects]
    )

    # create a type, division, and region without projects or locations
    empty_project_type = {
        "field": "TYPES",
        "values": [str((await LibraryProjectTypeFactory.persist(db_session)).id)],
    }
    empty_work_type = {
        "field": "WORK_TYPES",
        "values": [str((await WorkTypeFactory.persist(db_session)).id)],
    }
    empty_division = {
        "field": "DIVISIONS",
        "values": [str((await LibraryDivisionFactory.persist(db_session)).id)],
    }
    empty_region = {
        "field": "REGIONS",
        "values": [str((await LibraryRegionFactory.persist(db_session)).id)],
    }
    actual_project_type = {"field": "TYPES", "values": [str(project_types[0].id)]}
    actual_work_type = {"field": "WORK_TYPES", "values": [str(work_types[0].id)]}
    actual_division = {"field": "DIVISIONS", "values": [str(divisions[0].id)]}
    actual_region = {"field": "REGIONS", "values": [str(regions[0].id)]}

    # for various combinations assert we find no data
    # when using a filter value that has no locations / projects
    filters = [
        [empty_project_type],
        [empty_work_type],
        [empty_division],
        [empty_region],
        [empty_project_type, empty_division],
        [empty_project_type, empty_region],
        [empty_work_type, empty_division],
        [empty_work_type, empty_region],
        [empty_division, empty_region],
        [empty_project_type, empty_region, empty_division],
        [empty_project_type, actual_division],
        [empty_work_type, empty_region, empty_division],
        [empty_work_type, actual_division],
        [empty_division, actual_project_type],
        [empty_division, actual_work_type],
        [empty_region, actual_division],
        [empty_project_type, actual_division, actual_region],
        [empty_project_type, actual_region, actual_division],
        [empty_work_type, actual_division, actual_region],
        [empty_work_type, actual_region, actual_division],
        [empty_division, actual_region, actual_project_type],
        [empty_division, actual_region, actual_work_type],
    ]
    for filter_by in filters:
        data = await execute_locations_with_filter_by(execute_gql, filter_by)
        assert data == []


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_project_location_filters_single_field(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    project_types = await LibraryProjectTypeFactory.persist_many(
        db_session, per_item_kwargs=[{"name": "pt_type_one"}, {"name": "pt_two"}]
    )
    work_types = await WorkTypeFactory.persist_many(
        db_session, per_item_kwargs=[{"name": "wt_type_one"}, {"name": "wt_two"}]
    )
    divisions = await LibraryDivisionFactory.persist_many(
        db_session, per_item_kwargs=[{"name": "division_one"}, {"name": "division_two"}]
    )
    regions = await LibraryRegionFactory.persist_many(
        db_session, per_item_kwargs=[{"name": "region_one"}, {"name": "region_one"}]
    )
    projects = await WorkPackageFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {
                "work_type_id": project_type.id,
                "work_type_ids": [work_type.id],
                "region_id": region.id,
                "division_id": division.id,
            }
            for project_type in project_types
            for work_type in work_types
            for division in divisions
            for region in regions
        ],
    )
    await LocationFactory.persist_many(
        db_session, per_item_kwargs=[{"project_id": project.id} for project in projects]
    )

    project_type_filter = [
        {"field": "TYPES", "values": [str(pt.id)]} for pt in project_types
    ]
    work_types_filter = [
        {"field": "WORK_TYPES", "values": [str(pt.id)]} for pt in work_types
    ]
    division_filter = [
        {"field": "DIVISIONS", "values": [str(pd.id)]} for pd in divisions
    ]
    region_filter = [{"field": "REGIONS", "values": [str(pr.id)]} for pr in regions]

    filters = zip(
        project_type_filter + work_types_filter + region_filter + division_filter,
        ["libraryProjectType"] * 2
        + ["workTypes"] * 2
        + ["libraryRegion"] * 2
        + ["libraryDivision"] * 2,
    )
    for filter_value, key in filters:
        data = await execute_locations_with_filter_by(execute_gql, [filter_value])
        assert len(data) == 8
        # get the filter ID value
        filter_id = filter_value["values"][0]
        # and ensure it is in all the data results
        if key == "workTypes":
            assert all([pl["project"][key][0]["id"] == filter_id for pl in data])
        else:
            assert all([pl["project"][key]["id"] == filter_id for pl in data])


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_location_filters_many_fields(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    project_types = [
        await LibraryProjectTypeFactory.persist(db_session, name="pt_type_one"),
        await LibraryProjectTypeFactory.persist(db_session, name="pt_type_two"),
    ]
    work_types = [
        await WorkTypeFactory.persist(db_session, name="wt_type_one"),
        await WorkTypeFactory.persist(db_session, name="wt_type_two"),
    ]
    divisions = [
        await LibraryDivisionFactory.persist(db_session, name="division_one"),
        await LibraryDivisionFactory.persist(db_session, name="division_two"),
    ]
    regions = [
        await LibraryRegionFactory.persist(db_session, name="region_one"),
        await LibraryRegionFactory.persist(db_session, name="region_one"),
    ]
    projects = await WorkPackageFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {
                "work_type_id": type.id,
                "work_type_ids": [work_type.id],
                "region_id": region.id,
                "division_id": division.id,
            }
            for type in project_types
            for work_type in work_types
            for division in divisions
            for region in regions
        ],
    )
    await LocationFactory.persist_many(
        db_session, per_item_kwargs=[{"project_id": i.id} for i in projects]
    )

    project_type_filter = {"field": "TYPES", "values": [str(project_types[0].id)]}
    work_types_filter = {"field": "WORK_TYPES", "values": [str(work_types[0].id)]}
    division_filter = {"field": "DIVISIONS", "values": [str(divisions[0].id)]}
    region_filter = {"field": "REGIONS", "values": [str(regions[0].id)]}

    data = await execute_locations_with_filter_by(
        execute_gql, [project_type_filter, division_filter]
    )
    assert len(data) == 4
    assert all(
        [
            pl["project"]["libraryProjectType"]["id"] == str(project_types[0].id)
            for pl in data
        ]
    )
    assert all(
        [pl["project"]["libraryDivision"]["id"] == str(divisions[0].id) for pl in data]
    )

    data = await execute_locations_with_filter_by(
        execute_gql, [work_types_filter, division_filter]
    )
    assert len(data) == 4
    assert all(
        [pl["project"]["workTypes"][0]["id"] == str(work_types[0].id) for pl in data]
    )
    assert all(
        [pl["project"]["libraryDivision"]["id"] == str(divisions[0].id) for pl in data]
    )

    data = await execute_locations_with_filter_by(
        execute_gql, [project_type_filter, region_filter]
    )
    assert len(data) == 4
    assert all(
        [
            pl["project"]["libraryProjectType"]["id"] == str(project_types[0].id)
            for pl in data
        ]
    )
    assert all(
        [pl["project"]["libraryRegion"]["id"] == str(regions[0].id) for pl in data]
    )

    data = await execute_locations_with_filter_by(
        execute_gql, [region_filter, division_filter]
    )
    assert len(data) == 4
    assert all(
        [pl["project"]["libraryRegion"]["id"] == str(regions[0].id) for pl in data]
    )
    assert all(
        [pl["project"]["libraryDivision"]["id"] == str(divisions[0].id) for pl in data]
    )

    data = await execute_locations_with_filter_by(
        execute_gql, [project_type_filter, division_filter, region_filter]
    )
    assert len(data) == 2
    assert all(
        [
            pl["project"]["libraryProjectType"]["id"] == str(project_types[0].id)
            for pl in data
        ]
    )
    assert all(
        [pl["project"]["libraryDivision"]["id"] == str(divisions[0].id) for pl in data]
    )
    assert all(
        [pl["project"]["libraryRegion"]["id"] == str(regions[0].id) for pl in data]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_location_filters_project(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    project1_id = str((await WorkPackageFactory.persist(db_session)).id)
    location1_id = str(
        (await LocationFactory.persist(db_session, project_id=project1_id)).id
    )
    project2_id = str((await WorkPackageFactory.persist(db_session)).id)
    location2_id = str(
        (await LocationFactory.persist(db_session, project_id=project2_id)).id
    )

    # Return all
    filter_by = {"field": "PROJECT", "values": [project1_id, project2_id]}
    location_ids = await fetch_locations_ids_with_filter_by(execute_gql, [filter_by])
    assert {location1_id, location2_id} == location_ids

    # One project
    filter_by = {"field": "PROJECT", "values": [project1_id]}
    location_ids = await fetch_locations_ids_with_filter_by(execute_gql, [filter_by])
    assert {location1_id} == location_ids

    # Invalid project
    filter_by = {"field": "PROJECT", "values": [str(uuid.uuid4())]}
    location_ids = await fetch_locations_ids_with_filter_by(execute_gql, [filter_by])
    assert set() == location_ids
    filter_by = {"field": "PROJECT", "values": ["invalid-uuid"]}
    response = await execute_locations_with_filter_by(
        execute_gql, [filter_by], raw=True
    )
    assert response.json()["errors"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_location_filters_contractor(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    contractor1_id = str((await ContractorFactory.persist(db_session)).id)
    project1_id = str(
        (await WorkPackageFactory.persist(db_session, contractor_id=contractor1_id)).id
    )
    location1_id = str(
        (await LocationFactory.persist(db_session, project_id=project1_id)).id
    )
    contractor2_id = str((await ContractorFactory.persist(db_session)).id)
    project2_id = str(
        (await WorkPackageFactory.persist(db_session, contractor_id=contractor2_id)).id
    )
    location2_id = str(
        (await LocationFactory.persist(db_session, project_id=project2_id)).id
    )

    # Return all
    filter_by = {"field": "CONTRACTOR", "values": [contractor1_id, contractor2_id]}
    location_ids = await fetch_locations_ids_with_filter_by(execute_gql, [filter_by])
    assert {location1_id, location2_id} == location_ids

    # One contractor
    filter_by = {"field": "CONTRACTOR", "values": [contractor1_id]}
    location_ids = await fetch_locations_ids_with_filter_by(execute_gql, [filter_by])
    assert {location1_id} == location_ids

    # Invalid contractor
    filter_by = {"field": "CONTRACTOR", "values": [str(uuid.uuid4())]}
    location_ids = await fetch_locations_ids_with_filter_by(execute_gql, [filter_by])
    assert set() == location_ids
    filter_by = {"field": "CONTRACTOR", "values": ["invalid-uuid"]}
    response = await execute_locations_with_filter_by(
        execute_gql, [filter_by], raw=True
    )
    assert response.json()["errors"]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_project_location_filters_supervisor(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    supervisor11_id = str((await SupervisorUserFactory.persist(db_session)).id)
    supervisor12_id = str((await SupervisorUserFactory.persist(db_session)).id)
    supervisor13_id = str((await SupervisorUserFactory.persist(db_session)).id)
    supervisor14_id = str((await SupervisorUserFactory.persist(db_session)).id)
    project1_id = str(
        (
            await WorkPackageFactory.persist(
                db_session,
                primary_assigned_user_id=supervisor11_id,
                additional_assigned_users_ids=[supervisor12_id],
            )
        ).id
    )
    location1_id = str(
        (
            await LocationFactory.persist(
                db_session,
                project_id=project1_id,
                supervisor_id=supervisor13_id,
                additional_supervisor_ids=[supervisor14_id],
            )
        ).id
    )
    supervisor21_id = str((await SupervisorUserFactory.persist(db_session)).id)
    supervisor22_id = str((await SupervisorUserFactory.persist(db_session)).id)
    supervisor23_id = str((await SupervisorUserFactory.persist(db_session)).id)
    supervisor24_id = str((await SupervisorUserFactory.persist(db_session)).id)
    project2_id = str(
        (
            await WorkPackageFactory.persist(
                db_session,
                primary_assigned_user_id=supervisor21_id,
                additional_assigned_users_ids=[supervisor22_id],
            )
        ).id
    )
    location2_id = str(
        (
            await LocationFactory.persist(
                db_session,
                project_id=project2_id,
                supervisor_id=supervisor23_id,
                additional_supervisor_ids=[supervisor24_id],
            )
        ).id
    )

    # Return all
    filter_by = {
        "field": "SUPERVISOR",
        "values": [
            supervisor11_id,
            supervisor12_id,
            supervisor13_id,
            supervisor14_id,
            supervisor21_id,
            supervisor22_id,
            supervisor23_id,
            supervisor24_id,
        ],
    }
    location_ids = await fetch_locations_ids_with_filter_by(execute_gql, [filter_by])
    assert {location1_id, location2_id} == location_ids

    # One supervisor
    for supervisor_id in [
        supervisor11_id,
        supervisor12_id,
        supervisor13_id,
        supervisor14_id,
    ]:
        filter_by = {"field": "SUPERVISOR", "values": [supervisor_id]}
        location_ids = await fetch_locations_ids_with_filter_by(
            execute_gql, [filter_by]
        )
        assert {location1_id} == location_ids

    # Invalid supervisor
    filter_by = {"field": "SUPERVISOR", "values": [str(uuid.uuid4())]}
    location_ids = await fetch_locations_ids_with_filter_by(execute_gql, [filter_by])
    assert set() == location_ids
    filter_by = {"field": "SUPERVISOR", "values": ["invalid-uuid"]}
    response = await execute_locations_with_filter_by(
        execute_gql, [filter_by], raw=True
    )
    assert response.json()["errors"]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_project_location_filters_supervisor_risk(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    today = datetime.utcnow().date()
    project = await WorkPackageFactory.persist(
        db_session,
        start_date=today - timedelta(days=1),
        end_date=today + timedelta(days=1),
    )

    # These risk values correspond to "LOW", "LOW", "MEDIUM", "MEDIUM", "HIGH", "HIGH"
    risks = [40, 90, 150, 200, 251, 300]
    locations = await LocationFactory.persist_many(
        db_session,
        size=len(risks),
        project_id=project.id,
        per_item_kwargs=[
            {"risk": risk}
            for risk in ["low", "low", "medium", "medium", "high", "high"]
        ],
    )
    tests_location_ids = [str(i.id) for i in locations]
    await TotalProjectLocationRiskScoreModelFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {
                "project_location_id": location.id,
                "value": risk,
                "date": today,
                "calculated_at": datetime.now(timezone.utc).replace(microsecond=idx),
            }
            for risk, (idx, location) in zip(risks, enumerate(locations))
        ],
    )
    await TaskFactory.batch_with_project_and_location(
        db_session,
        [
            {
                "project": project,
                "location": location,
                "task_kwargs": {
                    "start_date": project.start_date,
                    "end_date": project.end_date,
                    "status": "in_progress",
                },
            }
            for location in locations
        ],
    )

    # Return all
    filter_by = {
        "field": "RISK",
        "values": list(RiskLevel.__members__.keys()),
    }
    location_ids = await fetch_locations_ids_with_filter_by(execute_gql, [filter_by])
    assert set(tests_location_ids) == location_ids

    # Only one
    filter_by = {"field": "RISK", "values": ["LOW"]}
    location_ids = await fetch_locations_ids_with_filter_by(execute_gql, [filter_by])
    assert set(tests_location_ids[:2]) == location_ids
    filter_by = {"field": "RISK", "values": ["HIGH"]}
    location_ids = await fetch_locations_ids_with_filter_by(execute_gql, [filter_by])
    assert set(tests_location_ids[-2:]) == location_ids

    # Valid type but no locations
    filter_by = {"field": "RISK", "values": ["RECALCULATING"]}
    location_ids = await fetch_locations_ids_with_filter_by(execute_gql, [filter_by])
    assert set() == location_ids

    # Invalid level
    filter_by = {"field": "SUPERVISOR", "values": ["invalid"]}
    response = await execute_locations_with_filter_by(
        execute_gql, [filter_by], raw=True
    )
    assert response.json()["errors"]


location_search_query = """
query TestQuery($search: String, $date: Date) {
  projectLocations(search: $search) {
    name
    riskLevel(date :$date)
    project {
      name
      workTypes {
        name
      }
      supervisor {
         name
         firstName
         lastName
       }
    }
  }
}
"""


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_project_locations_search_by_location_name(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    names = ["alfa", "bravo", "charlie", "delta", "echo", "foxtrot"]
    project_a = await WorkPackageFactory.persist(db_session)
    project_b = await WorkPackageFactory.persist(db_session)

    for name in names:
        await LocationFactory.persist(db_session, project_id=project_a.id, name=name)
        await LocationFactory.persist(db_session, project_id=project_b.id, name=name)

    search_string = names[0]
    post_data = {
        "operation_name": "TestQuery",
        "query": location_search_query,
        "variables": {
            "search": search_string,
        },
    }

    data = await execute_gql(**post_data)
    project_locations: list[dict] = data["projectLocations"]
    project_location_names: list[str] = [pl["name"] for pl in project_locations]
    assert len(project_locations) >= 2
    assert len(project_location_names) == 2
    assert all([pl["name"] == names[0] for pl in project_locations])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_locations_search_by_location_name_and_project_name(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    project_names = ["Apples", "Oranges"]

    location_names = [
        "How do you like them apples",
        "Hungry for apples",
        "Navel Oranges",
    ]

    for project_name in project_names:
        project = await WorkPackageFactory.persist(db_session, name=project_name)
        for name in location_names:
            await LocationFactory.persist(db_session, project_id=project.id, name=name)

    search_string = "apples"
    post_data = {
        "operation_name": "TestQuery",
        "query": location_search_query,
        "variables": {
            "search": search_string,
        },
    }

    data = await execute_gql(**post_data)
    project_locations: list[dict] = data["projectLocations"]
    assert len(project_locations) == 5
    for pl in project_locations:
        assert any(
            [
                search_string in text.lower()
                for text in (pl["name"], pl["project"]["name"])
            ]
        )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_project_locations_search_by_location_risk_level_and_location_name(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    names = ["alfa", "bravo", "charlie", "delta", "echo", "Below Deck"]
    today = datetime.utcnow().date()
    project = await WorkPackageFactory.persist(
        db_session,
        start_date=today - timedelta(days=1),
        end_date=today + timedelta(days=1),
    )
    locations = await LocationFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {"project_id": project.id, "name": name, "risk": risk}
            for name, risk in zip(
                names, ["low", "low", "medium", "medium", "high", "high"]
            )
        ],
    )

    # These risk values correspond to "LOW", "LOW", "MEDIUM", "MEDIUM", "HIGH", "HIGH"
    await TotalProjectLocationRiskScoreModelFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {
                "project_location_id": location.id,
                "value": risk,
                "date": today,
                "calculated_at": datetime.now(timezone.utc).replace(microsecond=risk),
            }
            for location, risk in zip(locations, [40, 90, 150, 200, 251, 300])
        ],
    )

    await TaskFactory.batch_with_project_and_location(
        db_session,
        [
            {
                "project": project,
                "location": location,
                "task_kwargs": {
                    "start_date": project.start_date,
                    "end_date": project.end_date,
                    "status": "in_progress",
                },
            }
            for location in locations
        ],
    )

    search_string = "low"
    post_data = {
        "operation_name": "TestQuery",
        "query": location_search_query,
        "variables": {
            "search": search_string,
            "date": today,
        },
    }

    data = await execute_gql(**post_data)
    project_locations: list[dict] = data["projectLocations"]
    assert len(project_locations) == 3
    for pl in project_locations:
        assert any(
            [search_string in text.lower() for text in (pl["riskLevel"], pl["name"])]
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_locations_search_by_location_name_and_supervisor_name(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    names = ["alfa", "bravobravo", "charlie", "delta", "echo", "foxtrot"]
    supervisor_a, supervisor_b = await SupervisorUserFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {"first_name": "Bravobravod", "last_name": "Charlie"},
            {"first_name": "Match", "last_name": "Match"},
        ],
    )
    project_a, project_b = await WorkPackageFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {"primary_assigned_user_id": supervisor_a.id},
            {"primary_assigned_user_id": supervisor_b.id},
        ],
    )
    await LocationFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {"project_id": project.id, "name": name}
            for name in names
            for project in [project_a, project_b]
        ],
    )

    search_string = "bravobravo"
    post_data = {
        "operation_name": "TestQuery",
        "query": location_search_query,
        "variables": {
            "search": search_string,
        },
    }

    data = await execute_gql(**post_data)
    project_locations: list[dict] = data["projectLocations"]
    assert len(project_locations) == 7
    for pl in project_locations:
        assert any(
            [
                search_string in text.lower()
                for text in (pl["name"], pl["project"]["supervisor"]["name"])
            ]
        )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_project_locations_search_by_project_type(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    names = ["alfa", "bravo", "charlie", "delta", "echo", "foxtrot"]

    type_a = await WorkTypeFactory.persist(db_session, name="type_one")
    project_a = await WorkPackageFactory.persist(db_session, work_type_ids=[type_a.id])
    type_b = await WorkTypeFactory.persist(db_session, name="type_two")
    project_b = await WorkPackageFactory.persist(db_session, work_type_ids=[type_b.id])

    for name in names:
        await LocationFactory.persist(db_session, project_id=project_a.id, name=name)
        await LocationFactory.persist(db_session, project_id=project_b.id, name=name)

    search_string = "type_one"
    post_data = {
        "operation_name": "TestQuery",
        "query": location_search_query,
        "variables": {
            "search": search_string,
        },
    }

    data = await execute_gql(**post_data)
    project_locations: list[dict] = data["projectLocations"]
    assert len(project_locations) == 6
    assert all(
        [
            pl["project"]["workTypes"][0]["name"] == search_string
            for pl in project_locations
        ]
    )


location_search_and_order_by_risk_name = """
query TestQuery($orderBy: [ProjectLocationOrderBy!], $search: String, $date: Date) {
  projectLocations(orderBy: $orderBy, search: $search) {
    id
    riskLevel(date: $date)
    name
    project {
      id
      name
    }
  }
}
"""


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_project_locations_search_and_order_by_with_risk(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    names = ["alfa", "bravo", "charlie", "delta", "echo", "Below Deck"]
    today = datetime.utcnow().date()
    project = await WorkPackageFactory.persist(
        db_session,
        start_date=today - timedelta(days=1),
        end_date=today + timedelta(days=1),
    )
    locations = await LocationFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {"project_id": project.id, "name": name, "risk": risk}
            for name, risk in zip(
                names, ["low", "medium", "medium", "medium", "medium", "high"]
            )
        ],
    )

    # These risk values correspond to "LOW", "MEDIUM", "MEDIUM", "MEDIUM", "MEDIUM", "HIGH"
    await TotalProjectLocationRiskScoreModelFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {
                "project_location_id": location.id,
                "value": risk,
                "date": today,
                "calculated_at": datetime.now(timezone.utc).replace(microsecond=risk),
            }
            for location, risk in zip(locations, [90, 150, 151, 199, 200, 300])
        ],
    )
    await TaskFactory.batch_with_project_and_location(
        db_session,
        [
            {
                "project": project,
                "location": location,
                "task_kwargs": {
                    "start_date": project.start_date,
                    "end_date": project.end_date,
                    "status": "in_progress",
                },
            }
            for location in locations
        ],
    )

    post_data = {
        "operation_name": "TestQuery",
        "query": location_search_and_order_by_risk_name,
        "variables": {
            "orderBy": [
                {"field": "NAME", "direction": "ASC"},
            ],
            "search": "MEDIUM",
            "date": project.start_date + timedelta(days=1),
        },
    }
    data = await execute_gql(**post_data)
    api_locations = data["projectLocations"]
    assert all([loc["riskLevel"] == "MEDIUM" for loc in api_locations])
    assert [loc["name"] for loc in api_locations] == names[1:5]

    post_data = {
        "operation_name": "TestQuery",
        "query": location_search_and_order_by_risk_name,
        "variables": {
            "orderBy": [
                {"field": "NAME", "direction": "DESC"},
            ],
            "search": "MEDIUM",
            "date": project.start_date + timedelta(days=1),
        },
    }
    data = await execute_gql(**post_data)
    api_locations = data["projectLocations"]
    assert all([loc["riskLevel"] == "MEDIUM" for loc in api_locations])
    assert [loc["name"] for loc in api_locations] == names[1:5][::-1]
