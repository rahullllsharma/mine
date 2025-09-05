import datetime
import json
import uuid

import pytest

from tests.db_data import DBData
from tests.factories import (
    DailyReportFactory,
    LocationFactory,
    SiteConditionControlFactory,
    SiteConditionFactory,
    SiteConditionHazardFactory,
    TaskControlFactory,
    TaskFactory,
    TaskHazardFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.daily_report.helpers import build_report_data, execute_report
from worker_safety_service.models import (
    AsyncSession,
    DailyReport,
    Location,
    SiteCondition,
    SiteConditionControl,
    SiteConditionHazard,
    Task,
    TaskControl,
    TaskHazard,
)
from worker_safety_service.models.daily_reports import (
    applicable_controls_analyses_by_id,
    applicable_hazard_analyses_by_id,
)


def build_task_data(
    task_id: uuid.UUID,
    hazards: list[dict] | None = None,
    notes: str | None = None,
    not_applicable_reason: str | None = None,
) -> dict:
    return {
        "id": str(task_id),
        "notes": notes,
        "notApplicableReason": not_applicable_reason,
        "performed": True,
        "hazards": hazards or [],
    }


async def build_response_task_data(
    db_session: AsyncSession, task: Task, task_data: dict
) -> dict:
    library_task = await DBData(db_session).library_task(task.library_task_id)
    return {"name": library_task.name, **task_data}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_empty(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Allows creation of daily report with job hazard analysis with:
      - siteConditions empty
      - tasks empty
    """
    report_request, _, _ = await build_report_data(db_session)
    report_request["jobHazardAnalysis"] = {"siteConditions": [], "tasks": []}

    response = await execute_report(execute_gql, report_request)
    assert response["id"] is not None
    assert response["sections"]["jobHazardAnalysis"]["siteConditions"] == []
    assert response["sections"]["jobHazardAnalysis"]["tasks"] == []


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_update(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Allows update of daily report with job hazard analysis with:
      - siteConditions empty
      - 1 task

    NOTE: I think only one update is worth checking here because the logic will be reused
    """

    report_request, _, location = await build_report_data(db_session)
    task: Task = await TaskFactory.persist(db_session, location_id=location.id)

    existing_report = await DailyReportFactory.persist(
        db_session,
        project_location_id=location.id,
        sections=json.dumps(
            {
                "job_hazard_analysis": {
                    "site_conditions": [],
                    "tasks": [build_task_data(task.id)],
                }
            }
        ),
    )

    task_2: Task = await TaskFactory.persist(db_session, location_id=location.id)

    task_2_data = build_task_data(task_2.id)

    report_request["id"] = str(existing_report.id)
    report_request["date"] = str(existing_report.date_for)
    report_request["jobHazardAnalysis"] = {
        "siteConditions": [],
        "tasks": [task_2_data],
    }

    response = await execute_report(execute_gql, report_request)
    assert response["id"] == str(existing_report.id)
    assert response["sections"]["jobHazardAnalysis"]["siteConditions"] == []
    assert response["sections"]["jobHazardAnalysis"]["tasks"] == [
        await build_response_task_data(db_session, task_2, task_2_data)
    ]


# TASK TESTS


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_creates_task(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Allows creation of daily report with job hazard analysis with:
      - siteConditions empty
      - 1 task
        - hazards empty
    """
    report_request, _, location = await build_report_data(db_session)

    task: Task = await TaskFactory.persist(db_session, location_id=location.id)

    task_data = build_task_data(task.id)
    report_request["jobHazardAnalysis"] = {"siteConditions": [], "tasks": [task_data]}

    response = await execute_report(execute_gql, report_request)
    assert response["sections"]["jobHazardAnalysis"]["siteConditions"] == []
    assert response["sections"]["jobHazardAnalysis"]["tasks"] == [
        await build_response_task_data(db_session, task, task_data)
    ]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_creates_task_with_hazards(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Allows creation of daily report with job hazard analysis with:
      - siteConditions empty
      - 1 task
        - 1 hazard
          - controls empty
    """
    report_request, _, location = await build_report_data(db_session)

    task: Task = await TaskFactory.persist(db_session, location_id=location.id)
    hazard: TaskHazard = await TaskHazardFactory.persist(db_session, task_id=task.id)
    library_hazard = await db_data.library_hazard(hazard.library_hazard_id)
    task_hazard_data = {"id": str(hazard.id), "isApplicable": True, "controls": []}

    task_data = build_task_data(task.id, hazards=[task_hazard_data])
    report_request["jobHazardAnalysis"] = {"siteConditions": [], "tasks": [task_data]}

    response = await execute_report(execute_gql, report_request)
    expected_data: dict = {
        "name": library_hazard.name,
        **task_hazard_data,
    }
    assert response["sections"]["jobHazardAnalysis"]["tasks"][0]["hazards"] == [
        expected_data
    ]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_creates_task_with_hazards_and_controls(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Allows creation of daily report with job hazard analysis with:
      - siteConditions empty
      - 1 task
        - 1 hazard
          - 2 controls : 1 implemented, 1 not implemented
    """
    report_request, _, location = await build_report_data(db_session)

    task = await TaskFactory.persist(db_session, location_id=location.id)
    hazard = await TaskHazardFactory.persist(db_session, task_id=task.id)

    impl_control = await TaskControlFactory.persist(
        db_session, task_hazard_id=hazard.id
    )
    impl_library_control = await db_data.library_control(
        impl_control.library_control_id
    )
    impl_library_control = await db_data.library_control(
        impl_control.library_control_id
    )
    not_impl_control = await TaskControlFactory.persist(
        db_session, task_hazard_id=hazard.id
    )
    not_impl_library_control = await db_data.library_control(
        not_impl_control.library_control_id
    )
    not_impl_library_control = await db_data.library_control(
        not_impl_control.library_control_id
    )

    impl_control_data = {"id": str(impl_control.id), "implemented": True}

    not_impl_control_data = {
        "id": str(not_impl_control.id),
        "implemented": False,
        "notImplementedReason": "test reason",
        "furtherExplanation": "some explanation",
    }

    task_hazard_data = {
        "id": str(hazard.id),
        "isApplicable": True,
        "controls": [impl_control_data, not_impl_control_data],
    }

    task_data = build_task_data(task.id, hazards=[task_hazard_data])
    report_request["jobHazardAnalysis"] = {"siteConditions": [], "tasks": [task_data]}

    response = await execute_report(execute_gql, report_request)

    assert (
        len(
            response["sections"]["jobHazardAnalysis"]["tasks"][0]["hazards"][0][
                "controls"
            ]
        )
        == 2
    )
    res_control_0 = response["sections"]["jobHazardAnalysis"]["tasks"][0]["hazards"][0][
        "controls"
    ][0]
    res_control_1 = response["sections"]["jobHazardAnalysis"]["tasks"][0]["hazards"][0][
        "controls"
    ][1]
    if res_control_0["id"] == str(impl_control.id):
        assert res_control_0["name"] == impl_library_control.name
        assert res_control_0["implemented"] is True
        assert res_control_0["notImplementedReason"] is None
        assert res_control_0["furtherExplanation"] is None
        assert res_control_1["name"] == not_impl_library_control.name
        assert res_control_1["implemented"] is False
        assert res_control_1["notImplementedReason"] == "test reason"
        assert res_control_1["furtherExplanation"] == "some explanation"
    else:
        assert res_control_0["name"] == impl_library_control.name
        assert res_control_0["implemented"] is False
        assert res_control_0["notImplementedReason"] == "test reason"
        assert res_control_0["furtherExplanation"] == "some explanation"
        assert res_control_1["name"] == not_impl_library_control.name
        assert res_control_1["implemented"] is True
        assert res_control_1["notImplementedReason"] is None
        assert res_control_1["furtherExplanation"] is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_creates_with_archived_tasks_hazards_and_controls(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Allows creation of daily report with job hazard analysis with:
      - siteConditions empty
      - 1 task archived
        - 1 hazard archived
          - 1 controls archived
    """
    # Arrange
    report_request, _, location = await build_report_data(db_session)
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    task = await TaskFactory.persist(
        db_session, location_id=location.id, archived_at=now
    )
    hazard = await TaskHazardFactory.persist(
        db_session, task_id=task.id, archived_at=now
    )
    control = await TaskControlFactory.persist(
        db_session, task_hazard_id=hazard.id, archived_at=now
    )
    control_data = {"id": str(control.id), "implemented": True}
    task_hazard_data = {
        "id": str(hazard.id),
        "isApplicable": True,
        "controls": [control_data],
    }
    task_data = build_task_data(task.id, hazards=[task_hazard_data])
    report_request["jobHazardAnalysis"] = {"siteConditions": [], "tasks": [task_data]}

    # Act
    response = await execute_report(execute_gql, report_request)

    # Assert
    assert (
        len(
            response["sections"]["jobHazardAnalysis"]["tasks"][0]["hazards"][0][
                "controls"
            ]
        )
        == 1
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_raises_on_duplicated_tasks(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Raises error on trying to insert duplicated tasks
    """
    report_request, _, location = await build_report_data(db_session)

    task = await TaskFactory.persist(db_session, location_id=location.id)

    task_data = build_task_data(task.id)
    report_request["jobHazardAnalysis"] = {
        "siteConditions": [],
        "tasks": [task_data, task_data],
    }

    response = await execute_report(execute_gql, report_request, raw=True)
    assert "duplicated in task analysis" in response.json().get("errors")[0]["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_raises_on_inexisting_tasks(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Raises error on trying to insert tasks that don't exist
    """
    report_request, _, _ = await build_report_data(db_session)

    task_data = build_task_data(uuid.uuid4())
    report_request["jobHazardAnalysis"] = {"siteConditions": [], "tasks": [task_data]}

    response = await execute_report(execute_gql, report_request, raw=True)
    assert (
        "don't exist in project location" in response.json().get("errors")[0]["message"]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_raises_on_tasks_that_belong_to_another_location(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Raises error on trying to insert tasks that belong to another Location
    """
    report_request, project, _ = await build_report_data(db_session)

    location = await LocationFactory.persist(db_session, project_id=project.id)
    invalid_task = await TaskFactory.persist(db_session, location_id=location.id)

    task_data = build_task_data(invalid_task.id)
    report_request["jobHazardAnalysis"] = {"siteConditions": [], "tasks": [task_data]}

    response = await execute_report(execute_gql, report_request, raw=True)
    assert (
        "don't exist in project location" in response.json().get("errors")[0]["message"]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_raises_on_duplicated_task_hazards(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Raises error on trying to insert duplicated task hazards
    """
    report_request, _, location = await build_report_data(db_session)

    task = await TaskFactory.persist(db_session, location_id=location.id)

    hazard = await TaskHazardFactory.persist(db_session, task_id=task.id)

    hazard_data = {"id": str(hazard.id), "isApplicable": True, "controls": []}

    task_data = build_task_data(task.id, hazards=[hazard_data, hazard_data])
    report_request["jobHazardAnalysis"] = {
        "siteConditions": [],
        "tasks": [task_data],
    }

    response = await execute_report(execute_gql, report_request, raw=True)
    assert "duplicated on task analysis" in response.json().get("errors")[0]["message"]
    assert "Hazard" in response.json().get("errors")[0]["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_raises_on_inexisting_task_hazards(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Raises error on trying to insert task hazards that don't exist
    """
    report_request, _, location = await build_report_data(db_session)

    task = await TaskFactory.persist(db_session, location_id=location.id)

    hazard_data = {"id": str(uuid.uuid4()), "isApplicable": True, "controls": []}

    task_data = build_task_data(task.id, hazards=[hazard_data])

    report_request["jobHazardAnalysis"] = {
        "siteConditions": [],
        "tasks": [task_data],
    }

    response = await execute_report(execute_gql, report_request, raw=True)
    assert "don't exist on task" in response.json().get("errors")[0]["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_raises_on_hazards_that_belong_to_another_task(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Raises error on trying to insert site_conditions hazards that belong to another site_condition
    """
    report_request, project, location = await build_report_data(db_session)

    task = await TaskFactory.persist(db_session, location_id=location.id)

    invalid_location = await LocationFactory.persist(db_session, project_id=project.id)

    invalid_task = await TaskFactory.persist(
        db_session, location_id=invalid_location.id
    )

    invalid_hazard = await TaskHazardFactory.persist(
        db_session, task_id=invalid_task.id
    )

    invalid_hazard_data = {
        "id": str(invalid_hazard.id),
        "isApplicable": True,
        "controls": [],
    }

    task_data = build_task_data(task.id, hazards=[invalid_hazard_data])

    report_request["jobHazardAnalysis"] = {
        "siteConditions": [],
        "tasks": [task_data],
    }

    response = await execute_report(execute_gql, report_request, raw=True)
    assert "don't exist on task" in response.json().get("errors")[0]["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_raises_on_duplicated_task_hazard_controls(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Raises error on trying to insert duplicated task hazards controls
    """
    report_request, _, location = await build_report_data(db_session)

    task = await TaskFactory.persist(db_session, location_id=location.id)

    hazard = await TaskHazardFactory.persist(db_session, task_id=task.id)
    control = await TaskControlFactory.persist(db_session, task_hazard_id=hazard.id)

    control_data = {"id": str(control.id), "implemented": True}

    hazard_data = {
        "id": str(hazard.id),
        "isApplicable": True,
        "controls": [control_data, control_data],
    }

    task_data = build_task_data(task.id, hazards=[hazard_data])

    report_request["jobHazardAnalysis"] = {
        "siteConditions": [],
        "tasks": [task_data],
    }

    response = await execute_report(execute_gql, report_request, raw=True)
    assert "duplicated on task" in response.json().get("errors")[0]["message"]
    assert "Control" in response.json().get("errors")[0]["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_raises_on_inexisting_task_hazards_controls(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Raises error on trying to insert task hazard controls that don't exist
    """
    report_request, _, location = await build_report_data(db_session)

    task: Task = await TaskFactory.persist(db_session, location_id=location.id)

    hazard: TaskHazard = await TaskHazardFactory.persist(db_session, task_id=task.id)

    control_data = {"id": str(uuid.uuid4()), "implemented": True}

    hazard_data = {
        "id": str(hazard.id),
        "isApplicable": True,
        "controls": [control_data],
    }

    task_data = build_task_data(task.id, hazards=[hazard_data])

    report_request["jobHazardAnalysis"] = {
        "siteConditions": [],
        "tasks": [task_data],
    }

    response = await execute_report(execute_gql, report_request, raw=True)
    assert "don't exist on task hazard" in response.json().get("errors")[0]["message"]
    assert "Control" in response.json().get("errors")[0]["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_raises_on_task_controls_that_belong_to_another_task_hazards(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Raises error on trying to insert controls that belong to another task hazard
    """
    report_request, _, location = await build_report_data(db_session)

    task: Task = await TaskFactory.persist(db_session, location_id=location.id)
    invalid_task: Task = await TaskFactory.persist(db_session, location_id=location.id)
    hazard: TaskHazard = await TaskHazardFactory.persist(db_session, task_id=task.id)
    invalid_hazard: TaskHazard = await TaskHazardFactory.persist(
        db_session, task_id=invalid_task.id
    )
    invalid_control: TaskControl = await TaskControlFactory.persist(
        db_session, task_hazard_id=invalid_hazard.id
    )

    control_data = {"id": str(invalid_control.id), "implemented": True}

    hazard_data = {
        "id": str(hazard.id),
        "isApplicable": True,
        "controls": [control_data],
    }

    task_data = build_task_data(task.id, hazards=[hazard_data])

    report_request["jobHazardAnalysis"] = {
        "siteConditions": [],
        "tasks": [task_data],
    }

    response = await execute_report(execute_gql, report_request, raw=True)
    assert "don't exist on task hazard" in response.json().get("errors")[0]["message"]
    assert "Control" in response.json().get("errors")[0]["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_task_not_applicable_reason(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Make sure task notApplicableReason is added and not required
    """

    report_request, _, location = await build_report_data(db_session)

    task: Task = await TaskFactory.persist(db_session, location_id=location.id)

    task_data = build_task_data(task.id, not_applicable_reason=uuid.uuid4().hex)
    report_request["jobHazardAnalysis"] = {"siteConditions": [], "tasks": [task_data]}

    response = await execute_report(execute_gql, report_request)
    assert response["sections"]["jobHazardAnalysis"]["siteConditions"] == []
    assert response["sections"]["jobHazardAnalysis"]["tasks"] == [
        await build_response_task_data(db_session, task, task_data)
    ]

    # Not defined notApplicableReason
    task_data.pop("notApplicableReason")
    response = await execute_report(execute_gql, report_request)
    assert response["sections"]["jobHazardAnalysis"]["siteConditions"] == []
    task_data["notApplicableReason"] = None  # Should be returned as NULL
    assert response["sections"]["jobHazardAnalysis"]["tasks"] == [
        await build_response_task_data(db_session, task, task_data)
    ]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_task_notes(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Make sure task notes is added and not required
    """

    report_request, _, location = await build_report_data(db_session)

    task: Task = await TaskFactory.persist(db_session, location_id=location.id)

    task_data = build_task_data(task.id, notes=uuid.uuid4().hex)
    report_request["jobHazardAnalysis"] = {"siteConditions": [], "tasks": [task_data]}

    response = await execute_report(execute_gql, report_request)
    assert response["sections"]["jobHazardAnalysis"]["siteConditions"] == []
    assert response["sections"]["jobHazardAnalysis"]["tasks"] == [
        await build_response_task_data(db_session, task, task_data)
    ]

    # Not defined notes
    task_data.pop("notes")
    response = await execute_report(execute_gql, report_request)
    assert response["sections"]["jobHazardAnalysis"]["siteConditions"] == []
    task_data["notes"] = None  # Should be returned as NULL
    assert response["sections"]["jobHazardAnalysis"]["tasks"] == [
        await build_response_task_data(db_session, task, task_data)
    ]


# SITE_CONDITION TESTS


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_creates_site_conditions(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Allows creation of daily report with job hazard analysis with:
      - tasks empty
      - 1 site condition
    """
    report_request, _, location = await build_report_data(db_session)

    site_condition: SiteCondition = await SiteConditionFactory.persist(
        db_session, location_id=location.id
    )
    library_sc = await db_data.library_site_condition(
        site_condition.library_site_condition_id
    )
    evaluated_site_condition: SiteCondition = (
        await SiteConditionFactory.persist_evaluated(
            db_session,
            location_id=location.id,
            date=report_request["date"],
        )
    )
    evaluated_library_sc = await db_data.library_site_condition(
        evaluated_site_condition.library_site_condition_id
    )

    site_condition_data = {
        "id": str(site_condition.id),
        "isApplicable": True,
        "hazards": [],
    }
    evaluated_site_condition_data = {
        "id": str(evaluated_site_condition.id),
        "isApplicable": True,
        "hazards": [],
    }
    report_request["jobHazardAnalysis"] = {
        "tasks": [],
        "siteConditions": [site_condition_data, evaluated_site_condition_data],
    }

    response = await execute_report(execute_gql, report_request)
    assert response["sections"]["jobHazardAnalysis"]["tasks"] == []
    assert response["sections"]["jobHazardAnalysis"]["siteConditions"] == [
        {"name": library_sc.name, **site_condition_data},
        {"name": evaluated_library_sc.name, **evaluated_site_condition_data},
    ]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_creates_site_conditions_with_hazard(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Allows creation of daily report with job hazard analysis with:
      - tasks empty
      - 1 site condition
        - 1 hazard
    """
    report_request, _, location = await build_report_data(db_session)

    site_condition: SiteCondition = await SiteConditionFactory.persist(
        db_session, location_id=location.id
    )

    hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session, site_condition_id=site_condition.id
    )
    library_hazard = await db_data.library_hazard(hazard.library_hazard_id)
    hazard_data = {"id": str(hazard.id), "isApplicable": True, "controls": []}

    site_condition_data = {
        "id": str(site_condition.id),
        "isApplicable": True,
        "hazards": [hazard_data],
    }
    report_request["jobHazardAnalysis"] = {
        "tasks": [],
        "siteConditions": [site_condition_data],
    }

    response = await execute_report(execute_gql, report_request)
    assert response["sections"]["jobHazardAnalysis"]["siteConditions"][0][
        "hazards"
    ] == [{"name": library_hazard.name, **hazard_data}]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_creates_site_conditions_with_hazard_and_controls(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Allows creation of daily report with job hazard analysis with:
      - tasks empty
      - 1 site condition
        - 1 hazard
          - 2 controls : 1 implemented, 1 not implemented
    """
    report_request, _, location = await build_report_data(db_session)

    site_condition: SiteCondition = await SiteConditionFactory.persist(
        db_session, location_id=location.id
    )

    hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session, site_condition_id=site_condition.id
    )

    impl_control: SiteConditionControl = await SiteConditionControlFactory.persist(
        db_session, site_condition_hazard_id=hazard.id
    )
    impl_library_control = await db_data.library_control(
        impl_control.library_control_id
    )

    not_impl_control: SiteConditionControl = await SiteConditionControlFactory.persist(
        db_session, site_condition_hazard_id=hazard.id
    )
    not_impl_library_control = await db_data.library_control(
        not_impl_control.library_control_id
    )

    impl_control_data = {"id": str(impl_control.id), "implemented": True}

    not_impl_control_data = {
        "id": str(not_impl_control.id),
        "implemented": False,
        "notImplementedReason": "test reason",
        "furtherExplanation": "some explanation",
    }

    hazard_data = {
        "id": str(hazard.id),
        "isApplicable": True,
        "controls": [impl_control_data, not_impl_control_data],
    }

    site_condition_data = {
        "id": str(site_condition.id),
        "isApplicable": True,
        "hazards": [hazard_data],
    }
    report_request["jobHazardAnalysis"] = {
        "tasks": [],
        "siteConditions": [site_condition_data],
    }

    response = await execute_report(execute_gql, report_request)

    assert (
        len(
            response["sections"]["jobHazardAnalysis"]["siteConditions"][0]["hazards"][
                0
            ]["controls"]
        )
        == 2
    )
    res_control_0 = response["sections"]["jobHazardAnalysis"]["siteConditions"][0][
        "hazards"
    ][0]["controls"][0]
    res_control_1 = response["sections"]["jobHazardAnalysis"]["siteConditions"][0][
        "hazards"
    ][0]["controls"][1]
    if res_control_0["id"] == str(impl_control.id):
        assert res_control_0["name"] == impl_library_control.name
        assert res_control_0["implemented"] is True
        assert res_control_0["notImplementedReason"] is None
        assert res_control_0["furtherExplanation"] is None
        assert res_control_1["name"] == not_impl_library_control.name
        assert res_control_1["implemented"] is False
        assert res_control_1["notImplementedReason"] == "test reason"
        assert res_control_1["furtherExplanation"] == "some explanation"
    else:
        assert res_control_0["name"] == impl_library_control.name
        assert res_control_0["implemented"] is False
        assert res_control_0["notImplementedReason"] == "test reason"
        assert res_control_0["furtherExplanation"] == "some explanation"
        assert res_control_1["name"] == not_impl_library_control.name
        assert res_control_1["implemented"] is True
        assert res_control_1["notImplementedReason"] is None
        assert res_control_1["furtherExplanation"] is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_creates_with_archived_site_conditions_hazards_and_controls(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Allows creation of daily report with job hazard analysis with:
      - tasks empty
      - 1 site condition archived
        - 1 hazard archived
          - 1 control archived
    """
    # Arrange
    report_request, _, location = await build_report_data(db_session)
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    site_condition: SiteCondition = await SiteConditionFactory.persist(
        db_session, location_id=location.id, archived_at=now
    )
    hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session, site_condition_id=site_condition.id, archived_at=now
    )
    control: SiteConditionControl = await SiteConditionControlFactory.persist(
        db_session, site_condition_hazard_id=hazard.id, archived_at=now
    )
    control_data = {"id": str(control.id), "implemented": True}
    hazard_data = {
        "id": str(hazard.id),
        "isApplicable": True,
        "controls": [control_data],
    }
    site_condition_data = {
        "id": str(site_condition.id),
        "isApplicable": True,
        "hazards": [hazard_data],
    }
    report_request["jobHazardAnalysis"] = {
        "tasks": [],
        "siteConditions": [site_condition_data],
    }

    # Act
    response = await execute_report(execute_gql, report_request)

    # Assert
    assert (
        len(
            response["sections"]["jobHazardAnalysis"]["siteConditions"][0]["hazards"][
                0
            ]["controls"]
        )
        == 1
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_raises_on_duplicated_site_conditions(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Raises error on trying to insert duplicated site_conditions
    """
    report_request, _, location = await build_report_data(db_session)

    site_condition: SiteCondition = await SiteConditionFactory.persist(
        db_session, location_id=location.id
    )

    site_condition_data = {
        "id": str(site_condition.id),
        "isApplicable": True,
        "hazards": [],
    }
    report_request["jobHazardAnalysis"] = {
        "siteConditions": [site_condition_data, site_condition_data],
        "tasks": [],
    }

    response = await execute_report(execute_gql, report_request, raw=True)
    assert "duplicated on site condition" in response.json().get("errors")[0]["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_raises_on_inexisting_site_condition(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Raises error on trying to insert site conditions that don't exist
    """
    report_request, _, _ = await build_report_data(db_session)

    site_condition_data = {
        "id": str(uuid.uuid4()),
        "isApplicable": True,
        "hazards": [],
    }
    report_request["jobHazardAnalysis"] = {
        "siteConditions": [site_condition_data],
        "tasks": [],
    }

    response = await execute_report(execute_gql, report_request, raw=True)
    assert (
        "don't exist in project location" in response.json().get("errors")[0]["message"]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_raises_on_site_conditions_that_belong_to_another_location(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Raises error on trying to insert site_conditions that belong to another Location
    """
    report_request, project, _ = await build_report_data(db_session)

    location: Location = await LocationFactory.persist(
        db_session, project_id=project.id
    )
    invalid_site_condition: SiteCondition = await SiteConditionFactory.persist(
        db_session, location_id=location.id
    )

    site_condition_data = {
        "id": str(invalid_site_condition.id),
        "isApplicable": True,
        "hazards": [],
    }
    report_request["jobHazardAnalysis"] = {
        "siteConditions": [site_condition_data],
        "tasks": [],
    }

    response = await execute_report(execute_gql, report_request, raw=True)
    assert (
        "don't exist in project location" in response.json().get("errors")[0]["message"]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_raises_on_duplicated_site_conditions_hazards(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Raises error on trying to insert duplicated site_conditions hazards
    """
    report_request, _, location = await build_report_data(db_session)

    site_condition: SiteCondition = await SiteConditionFactory.persist(
        db_session, location_id=location.id
    )
    hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session, site_condition_id=site_condition.id
    )

    hazard_data = {"id": str(hazard.id), "isApplicable": True, "controls": []}

    site_condition_data = {
        "id": str(site_condition.id),
        "isApplicable": True,
        "hazards": [hazard_data, hazard_data],
    }

    report_request["jobHazardAnalysis"] = {
        "siteConditions": [site_condition_data],
        "tasks": [],
    }

    response = await execute_report(execute_gql, report_request, raw=True)
    assert "duplicated on site condition" in response.json().get("errors")[0]["message"]
    assert "Hazard" in response.json().get("errors")[0]["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_raises_on_inexisting_site_condition_hazards(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Raises error on trying to insert site conditions hazards that don't exist
    """
    report_request, _, location = await build_report_data(db_session)

    site_condition: SiteCondition = await SiteConditionFactory.persist(
        db_session, location_id=location.id
    )

    hazard_data = {"id": str(uuid.uuid4()), "isApplicable": True, "controls": []}

    site_condition_data = {
        "id": str(site_condition.id),
        "isApplicable": True,
        "hazards": [hazard_data],
    }
    report_request["jobHazardAnalysis"] = {
        "siteConditions": [site_condition_data],
        "tasks": [],
    }

    response = await execute_report(execute_gql, report_request, raw=True)
    assert (
        "don't exist on site condition" in response.json().get("errors")[0]["message"]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_raises_on_evaluated_site_condition_from_different_day(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Raises error on trying to insert evaluated site conditions from another day
    """
    report_request, _, location = await build_report_data(db_session)

    site_condition: SiteCondition = await SiteConditionFactory.persist(
        db_session, location_id=location.id
    )
    evaluated_site_condition: SiteCondition = (
        await SiteConditionFactory.persist_evaluated(
            db_session,
            location_id=location.id,
            date=datetime.date(1980, 1, 1),
        )
    )

    site_condition_data = {
        "id": str(site_condition.id),
        "isApplicable": True,
        "hazards": [],
    }
    evaluated_site_condition_data = {
        "id": str(evaluated_site_condition.id),
        "isApplicable": True,
        "hazards": [],
    }

    report_request["jobHazardAnalysis"] = {
        "siteConditions": [site_condition_data, evaluated_site_condition_data],
        "tasks": [],
    }

    response = await execute_report(execute_gql, report_request, raw=True)
    assert "don't exist" in response.json().get("errors")[0]["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_raises_on_hazards_that_belong_to_another_site_condition(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Raises error on trying to insert site_conditions hazards that belong to another site_condition
    """
    report_request, project, location = await build_report_data(db_session)

    site_condition: SiteCondition = await SiteConditionFactory.persist(
        db_session, location_id=location.id
    )

    invalid_location: Location = await LocationFactory.persist(
        db_session, project_id=project.id
    )

    invalid_site_condition: SiteCondition = await SiteConditionFactory.persist(
        db_session, location_id=invalid_location.id
    )

    invalid_hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session, site_condition_id=invalid_site_condition.id
    )

    invalid_hazard_data = {
        "id": str(invalid_hazard.id),
        "isApplicable": True,
        "controls": [],
    }

    site_condition_data = {
        "id": str(site_condition.id),
        "isApplicable": True,
        "hazards": [invalid_hazard_data],
    }
    report_request["jobHazardAnalysis"] = {
        "siteConditions": [site_condition_data],
        "tasks": [],
    }

    response = await execute_report(execute_gql, report_request, raw=True)
    assert (
        "don't exist on site condition" in response.json().get("errors")[0]["message"]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_raises_on_duplicated_site_conditions_hazard_controls(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Raises error on trying to insert duplicated site_conditions hazards controls
    """
    report_request, _, location = await build_report_data(db_session)

    site_condition: SiteCondition = await SiteConditionFactory.persist(
        db_session, location_id=location.id
    )
    hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session, site_condition_id=site_condition.id
    )
    control: SiteConditionControl = await SiteConditionControlFactory.persist(
        db_session, site_condition_hazard_id=hazard.id
    )

    control_data = {"id": str(control.id), "implemented": True}

    hazard_data = {
        "id": str(hazard.id),
        "isApplicable": True,
        "controls": [control_data, control_data],
    }

    site_condition_data = {
        "id": str(site_condition.id),
        "isApplicable": True,
        "hazards": [hazard_data],
    }

    report_request["jobHazardAnalysis"] = {
        "siteConditions": [site_condition_data],
        "tasks": [],
    }

    response = await execute_report(execute_gql, report_request, raw=True)
    assert "duplicated on site condition" in response.json().get("errors")[0]["message"]
    assert "Control" in response.json().get("errors")[0]["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_raises_on_inexisting_site_condition_hazards_controls(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Raises error on trying to insert site_condition hazard controls that don't exist
    """
    report_request, _, location = await build_report_data(db_session)

    site_condition: SiteCondition = await SiteConditionFactory.persist(
        db_session, location_id=location.id
    )
    hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session, site_condition_id=site_condition.id
    )

    control_data = {"id": str(uuid.uuid4()), "implemented": True}

    hazard_data = {
        "id": str(hazard.id),
        "isApplicable": True,
        "controls": [control_data],
    }

    site_condition_data = {
        "id": str(site_condition.id),
        "isApplicable": True,
        "hazards": [hazard_data],
    }
    report_request["jobHazardAnalysis"] = {
        "siteConditions": [site_condition_data],
        "tasks": [],
    }

    response = await execute_report(execute_gql, report_request, raw=True)
    assert (
        "don't exist on site condition hazard"
        in response.json().get("errors")[0]["message"]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_raises_on_controls_that_belong_to_another_location_hazards(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Raises error on trying to insert controls belong to another site_condition hazard
    """
    report_request, project, location = await build_report_data(db_session)

    invalid_location = await LocationFactory.persist(db_session, project_id=project.id)
    site_condition, invalid_site_condition = await SiteConditionFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {"location_id": location.id},
            {"location_id": invalid_location.id},
        ],
    )
    hazard, invalid_hazard = await SiteConditionHazardFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {"site_condition_id": site_condition.id},
            {"site_condition_id": invalid_site_condition.id},
        ],
    )
    invalid_control = await SiteConditionControlFactory.persist(
        db_session, site_condition_hazard_id=invalid_hazard.id
    )

    invalid_control_data = {"id": str(invalid_control.id), "implemented": True}

    hazard_data = {
        "id": str(hazard.id),
        "isApplicable": True,
        "controls": [invalid_control_data],
    }
    site_condition_data = {
        "id": str(site_condition.id),
        "isApplicable": True,
        "hazards": [hazard_data],
    }
    report_request["jobHazardAnalysis"] = {
        "siteConditions": [site_condition_data],
        "tasks": [],
    }

    response = await execute_report(execute_gql, report_request, raw=True)
    assert (
        "don't exist on site condition hazard"
        in response.json().get("errors")[0]["message"]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_job_hazard_analysis_returns_name_on_archived(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    report_request, _, location = await build_report_data(db_session)

    task: Task = await TaskFactory.persist(db_session, location_id=location.id)
    library_task = await db_data.library_task(task.library_task_id)
    task_hazard: TaskHazard = await TaskHazardFactory.persist(
        db_session, task_id=task.id
    )
    task_library_hazard = await db_data.library_hazard(task_hazard.library_hazard_id)
    task_control: TaskControl = await TaskControlFactory.persist(
        db_session, task_hazard_id=task_hazard.id
    )
    task_library_control = await db_data.library_control(
        task_control.library_control_id
    )
    task_library_control = await db_data.library_control(
        task_control.library_control_id
    )
    site_condition: SiteCondition = await SiteConditionFactory.persist(
        db_session, location_id=location.id
    )
    library_sc = await db_data.library_site_condition(
        site_condition.library_site_condition_id
    )
    site_condition_hazard: SiteConditionHazard = (
        await SiteConditionHazardFactory.persist(
            db_session, site_condition_id=site_condition.id
        )
    )
    sc_library_hazard = await db_data.library_hazard(
        site_condition_hazard.library_hazard_id
    )
    site_condition_control: SiteConditionControl = (
        await SiteConditionControlFactory.persist(
            db_session,
            site_condition_hazard_id=site_condition_hazard.id,
        )
    )
    sc_library_control = await db_data.library_control(
        site_condition_control.library_control_id
    )
    report_request["jobHazardAnalysis"] = {
        "siteConditions": [
            {
                "id": str(site_condition.id),
                "isApplicable": True,
                "hazards": [
                    {
                        "id": str(site_condition_hazard.id),
                        "isApplicable": True,
                        "controls": [
                            {"id": str(site_condition_control.id), "implemented": True}
                        ],
                    }
                ],
            }
        ],
        "tasks": [
            build_task_data(
                task.id,
                hazards=[
                    {
                        "id": str(task_hazard.id),
                        "isApplicable": True,
                        "controls": [{"id": str(task_control.id), "implemented": True}],
                    }
                ],
            )
        ],
    }
    await execute_report(execute_gql, report_request)

    # Archive all types
    now = datetime.datetime.now(datetime.timezone.utc)
    task.archived_at = now
    task_hazard.archived_at = now
    task_control.archived_at = now
    site_condition.archived_at = now
    site_condition_hazard.archived_at = now
    site_condition_control.archived_at = now
    await db_session.commit()

    # Check if still have the names
    response = await execute_gql(
        query="""
          query TestQuery($projectLocationId: UUID!, $date: Date!) {
            dailyReports(projectLocationId: $projectLocationId, date: $date) {
              sections {
                jobHazardAnalysis {
                  siteConditions {
                    name
                    hazards {
                      name
                      controls {
                        name
                      }
                    }
                  }
                  tasks {
                    name
                    hazards {
                      name
                      controls {
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        """,
        variables={"projectLocationId": location.id, "date": report_request["date"]},
    )
    assert response["dailyReports"][0]["sections"]["jobHazardAnalysis"] == {
        "siteConditions": [
            {
                "name": library_sc.name,
                "hazards": [
                    {
                        "name": sc_library_hazard.name,
                        "controls": [{"name": sc_library_control.name}],
                    }
                ],
            }
        ],
        "tasks": [
            {
                "name": library_task.name,
                "hazards": [
                    {
                        "name": task_library_hazard.name,
                        "controls": [{"name": task_library_control.name}],
                    }
                ],
            }
        ],
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_jha_should_ignore_name(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    # Prepare data
    report_request, _, location = await build_report_data(db_session)
    task_id = str((await TaskFactory.persist(db_session, location_id=location.id)).id)
    task_hazard_id = str(
        (await TaskHazardFactory.persist(db_session, task_id=task_id)).id
    )
    sc_id = str(
        (await SiteConditionFactory.persist(db_session, location_id=location.id)).id
    )
    sc_hazard_id = str(
        (
            await SiteConditionHazardFactory.persist(
                db_session, site_condition_id=sc_id
            )
        ).id
    )
    report_request["jobHazardAnalysis"] = {
        "siteConditions": [
            {
                "id": sc_id,
                "isApplicable": True,
                "hazards": [
                    {
                        "id": sc_hazard_id,
                        "isApplicable": True,
                        "controls": [
                            {
                                "id": str(
                                    (
                                        await SiteConditionControlFactory.persist(
                                            db_session,
                                            site_condition_hazard_id=sc_hazard_id,
                                        )
                                    ).id
                                ),
                                "implemented": True,
                                "name": "Invalid",
                            }
                        ],
                        "name": "Invalid",
                    }
                ],
                "name": "Invalid",
            }
        ],
        "tasks": [
            {
                "id": task_id,
                "notes": None,
                "notApplicableReason": None,
                "performed": True,
                "hazards": [
                    {
                        "id": task_hazard_id,
                        "isApplicable": True,
                        "controls": [
                            {
                                "id": str(
                                    (
                                        await TaskControlFactory.persist(
                                            db_session,
                                            task_hazard_id=task_hazard_id,
                                        )
                                    ).id
                                ),
                                "implemented": True,
                                "name": "Invalid",
                            }
                        ],
                        "name": "Invalid",
                    }
                ],
            },
        ],
    }

    # Save daily report mutation should allow to send the name
    # but it should return the library name
    response = await execute_report(execute_gql, report_request)
    jha_response = response["sections"]["jobHazardAnalysis"]
    assert jha_response["siteConditions"][0]["name"] != "Invalid"
    assert jha_response["siteConditions"][0]["hazards"][0]["name"] != "Invalid"
    assert (
        jha_response["siteConditions"][0]["hazards"][0]["controls"][0]["name"]
        != "Invalid"
    )
    assert jha_response["tasks"][0]["name"] != "Invalid"
    assert jha_response["tasks"][0]["hazards"][0]["name"] != "Invalid"
    assert jha_response["tasks"][0]["hazards"][0]["controls"][0]["name"] != "Invalid"

    # We shouldn't save the name on daily report
    daily_report = await db_data.daily_report(response["id"])
    jha_data = (daily_report.sections or {})["job_hazard_analysis"]
    assert "name" not in jha_data["site_conditions"][0]
    assert "name" not in jha_data["site_conditions"][0]["hazards"][0]
    assert "name" not in jha_data["site_conditions"][0]["hazards"][0]["controls"][0]
    assert "name" not in jha_data["tasks"][0]
    assert "name" not in jha_data["tasks"][0]["hazards"][0]
    assert "name" not in jha_data["tasks"][0]["hazards"][0]["controls"][0]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_insights_get_hazard_controls_methods(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Get only controls and hazards for daily report tasks where
    - tasks were performed
    - and site conditions were applicable
    - and the hazard for the control was applicable
    """
    # Prepare data
    report_request, _, location = await build_report_data(db_session)
    task_id = str((await TaskFactory.persist(db_session, location_id=location.id)).id)
    task_hazard_id = str(
        (await TaskHazardFactory.persist(db_session, task_id=task_id)).id
    )
    task_control_id = str(
        (
            await TaskControlFactory.persist(
                db_session,
                task_hazard_id=task_hazard_id,
            )
        ).id
    )
    sc_id = str(
        (await SiteConditionFactory.persist(db_session, location_id=location.id)).id
    )
    sc_hazard_id = str(
        (
            await SiteConditionHazardFactory.persist(
                db_session, site_condition_id=sc_id
            )
        ).id
    )
    sc_control_id = str(
        (
            await SiteConditionControlFactory.persist(
                db_session,
                site_condition_hazard_id=sc_hazard_id,
            )
        ).id
    )

    def prep_report_data() -> dict:
        sc_controls = [
            {
                "id": sc_control_id,
                "implemented": True,
                "name": "Invalid",
            }
        ]
        sc_hazards = [
            {
                "id": sc_hazard_id,
                "isApplicable": True,
                "controls": sc_controls,
                "name": "Invalid",
            }
        ]

        task_controls = [
            {
                "id": task_control_id,
                "implemented": True,
                "name": "Invalid",
            }
        ]
        task_hazards = [
            {
                "id": task_hazard_id,
                "isApplicable": True,
                "controls": task_controls,
                "name": "Invalid",
            }
        ]

        site_conditions = [
            {
                "id": sc_id,
                "isApplicable": True,
                "hazards": sc_hazards,
                "name": "Invalid",
            }
        ]
        tasks = [
            {
                "id": task_id,
                "notes": None,
                "notApplicableReason": None,
                "performed": True,
                "hazards": task_hazards,
            },
        ]

        return {
            "site_conditions": site_conditions,
            "tasks": tasks,
        }

    # task and site condition apply
    sections = {"job_hazard_analysis": prep_report_data()}
    today = datetime.date.today()
    dr = DailyReport(date_for=today, sections=sections)
    hazard_ids = applicable_hazard_analyses_by_id([dr])
    assert sorted([str(id) for id in hazard_ids.keys()]) == sorted(
        [task_hazard_id, sc_hazard_id]
    )
    control_ids = applicable_controls_analyses_by_id([dr])
    assert sorted([str(id) for id in control_ids.keys()]) == sorted(
        [task_control_id, sc_control_id]
    )

    # task does not apply
    sections["job_hazard_analysis"]["tasks"][0]["performed"] = False
    dr = DailyReport(date_for=today, sections=sections)
    hazard_ids = applicable_hazard_analyses_by_id([dr])
    assert [str(id) for id in hazard_ids.keys()] == [sc_hazard_id]
    control_ids = applicable_controls_analyses_by_id([dr])
    assert [str(id) for id in control_ids.keys()] == [sc_control_id]

    # site condition hazard does not apply
    sections["job_hazard_analysis"]["site_conditions"][0]["hazards"][0][
        "isApplicable"
    ] = False
    dr = DailyReport(date_for=today, sections=sections)
    hazard_ids = applicable_hazard_analyses_by_id([dr])
    assert [str(id) for id in hazard_ids.keys()] == []
    control_ids = applicable_controls_analyses_by_id([dr])
    assert [str(id) for id in control_ids.keys()] == []

    # site condition does not apply
    sections["job_hazard_analysis"]["site_conditions"][0]["isApplicable"] = False
    sections["job_hazard_analysis"]["tasks"][0]["performed"] = True
    dr = DailyReport(date_for=today, sections=sections)
    hazard_ids = applicable_hazard_analyses_by_id([dr])
    assert [str(id) for id in hazard_ids.keys()] == [task_hazard_id]
    control_ids = applicable_controls_analyses_by_id([dr])
    assert [str(id) for id in control_ids.keys()] == [task_control_id]

    # task hazard does not apply
    sections["job_hazard_analysis"]["tasks"][0]["hazards"][0]["isApplicable"] = False
    dr = DailyReport(date_for=today, sections=sections)
    hazard_ids = applicable_hazard_analyses_by_id([dr])
    assert [str(id) for id in hazard_ids.keys()] == []
    control_ids = applicable_controls_analyses_by_id([dr])
    assert [str(id) for id in control_ids.keys()] == []
