import datetime
import uuid
from datetime import datetime as datetimenow
from typing import Any

import pytest
from sqlmodel import select

from tests.db_data import DBData
from tests.factories import (
    JobSafetyBriefingFactory,
    JSBSupervisorLinkFactory,
    SupervisorUserFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.job_safety_briefing.helpers import (
    build_jsb_data,
    build_jsb_data_with_crew_info,
    build_jsb_data_without_date,
    execute_complete_jsb,
    execute_delete_jsb,
    execute_reopen_jsb,
    execute_save_jsb,
)
from tests.utils import assert_data_equal_case_insensitive
from worker_safety_service.graphql.types import RiskLevel
from worker_safety_service.models import AsyncSession, JobSafetyBriefingLayout
from worker_safety_service.models.jsb_supervisor import JSBSupervisorLink


@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_job_safety_briefing_mutation(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation creates a new job safety briefing.
    """
    jsb_request, *_ = await build_jsb_data(db_session)
    jsb_response = await execute_save_jsb(execute_gql, jsb_request)
    db_jsb = await db_data.jsb(jsb_response["id"])
    assert db_jsb.id == uuid.UUID(jsb_response["id"])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_job_safety_briefing_mutation_without_date(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation creates a new job safety briefing
    when no date is provided.
    """
    jsb_request, *_ = await build_jsb_data_without_date(db_session)
    jsb_response = await execute_save_jsb(execute_gql, jsb_request)

    assert jsb_response["id"] is not None

    db_jsb = await db_data.jsb(jsb_response["id"])

    assert db_jsb.id == uuid.UUID(jsb_response["id"])
    assert db_jsb.date_for == datetime.date.today()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_job_safety_briefing_briefing_date_time(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation updates the expected fields and tables
    when changing the briefingDateTime.
    """
    jsb_request, *_ = await build_jsb_data_without_date(db_session)
    jsb_response = await execute_save_jsb(execute_gql, jsb_request)
    jsb_request["jsbId"] = jsb_response["id"]
    date = str(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    )
    jsb_request["jsbMetadata"] = {"briefingDateTime": date}

    updated_jsb_response = await execute_save_jsb(execute_gql, jsb_request)

    db_jsb = await db_data.jsb(updated_jsb_response["id"])

    contents = JobSafetyBriefingLayout.parse_obj(db_jsb.contents)

    assert contents.jsb_metadata
    assert str(contents.jsb_metadata.briefing_date_time) == date
    assert contents.jsb_metadata.briefing_date_time.date() == db_jsb.date_for


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_job_safety_briefing_control_assessment_selections_with_control_ids(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation updates the expected content
    when changing the deprecated controlIds.
    """
    # Arrange
    jsb_request, *_ = await build_jsb_data(db_session)
    jsb_response = await execute_save_jsb(execute_gql, jsb_request)
    control_id_1 = str(uuid.uuid4())
    control_id_2 = str(uuid.uuid4())
    control_id_3 = str(uuid.uuid4())
    control_id_4 = str(uuid.uuid4())
    hazard_id_1 = str(uuid.uuid4())
    hazard_id_2 = str(uuid.uuid4())
    update_jsb_request = {
        "jsbId": jsb_response["id"],
        "controlAssessmentSelections": [
            {
                "hazardId": hazard_id_1,
                "controlIds": [
                    control_id_1,
                    control_id_2,
                    control_id_3,
                ],
            },
            {
                "hazardId": hazard_id_2,
                "controlIds": [
                    control_id_4,
                ],
            },
        ],
    }

    # Act
    updated_jsb_response = await execute_save_jsb(execute_gql, update_jsb_request)

    # Assert
    expected_control_assessment_selections = [
        {
            "hazardId": hazard_id_1,
            "controlIds": [
                control_id_1,
                control_id_2,
                control_id_3,
            ],
            "controlSelections": [
                {"id": control_id_1, "recommended": None, "selected": None},
                {"id": control_id_2, "recommended": None, "selected": None},
                {"id": control_id_3, "recommended": None, "selected": None},
            ],
        },
        {
            "hazardId": hazard_id_2,
            "controlIds": [
                control_id_4,
            ],
            "controlSelections": [
                {"id": control_id_4, "recommended": None, "selected": None},
            ],
        },
    ]

    assert "contents" in updated_jsb_response, updated_jsb_response
    assert (
        "controlAssessmentSelections" in updated_jsb_response["contents"]
    ), updated_jsb_response
    response_control_assessment_selections = updated_jsb_response["contents"][
        "controlAssessmentSelections"
    ]
    assert (
        response_control_assessment_selections == expected_control_assessment_selections
    ), updated_jsb_response


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_job_safety_briefing_control_assessment_selections_with_empty_control_ids(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation updates the expected content
    when changing the deprecated controlIds to empty.
    """
    # Arrange
    jsb_request, *_ = await build_jsb_data(db_session)
    jsb_response = await execute_save_jsb(execute_gql, jsb_request)
    hazard_id_1 = str(uuid.uuid4())
    update_jsb_request = {
        "jsbId": jsb_response["id"],
        "controlAssessmentSelections": [
            {
                "hazardId": hazard_id_1,
                "controlIds": [],
            }
        ],
    }

    # Act
    updated_jsb_response = await execute_save_jsb(execute_gql, update_jsb_request)

    # Assert
    expected_control_assessment_selections = [
        {
            "hazardId": hazard_id_1,
            "controlIds": [],
            "controlSelections": [],
        },
    ]

    assert "contents" in updated_jsb_response, updated_jsb_response
    assert (
        "controlAssessmentSelections" in updated_jsb_response["contents"]
    ), updated_jsb_response
    response_control_assessment_selections = updated_jsb_response["contents"][
        "controlAssessmentSelections"
    ]
    assert (
        response_control_assessment_selections == expected_control_assessment_selections
    ), updated_jsb_response


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_job_safety_briefing_control_assessment_selections_with_control_selections(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation updates the expected content
    when changing controlSelections.
    """
    # Arrange
    jsb_request, *_ = await build_jsb_data(db_session)
    jsb_response = await execute_save_jsb(execute_gql, jsb_request)
    control_id_1 = str(uuid.uuid4())
    control_id_2 = str(uuid.uuid4())
    control_id_3 = str(uuid.uuid4())
    control_id_4 = str(uuid.uuid4())
    control_id_5 = str(uuid.uuid4())
    hazard_id_1 = str(uuid.uuid4())
    hazard_id_2 = str(uuid.uuid4())
    hazard_id_3 = str(uuid.uuid4())
    request_control_assessment_selections = [
        {
            "hazardId": hazard_id_1,
            "controlIds": None,
            "controlSelections": [
                {"id": control_id_1, "recommended": False, "selected": True},
                {"id": control_id_2, "recommended": False, "selected": False},
                {"id": control_id_3, "recommended": True, "selected": True},
            ],
        },
        {
            "hazardId": hazard_id_2,
            "controlIds": None,
            "controlSelections": [
                {"id": control_id_4, "recommended": False, "selected": False},
            ],
        },
        {
            "hazardId": hazard_id_3,
            "controlIds": None,
            "controlSelections": [
                {"id": control_id_5, "recommended": None, "selected": None},
            ],
        },
    ]
    update_jsb_request = {
        "jsbId": jsb_response["id"],
        "controlAssessmentSelections": request_control_assessment_selections,
    }

    # Act
    updated_jsb_response = await execute_save_jsb(execute_gql, update_jsb_request)

    # Assert
    expected_control_assessment_selections = [
        {
            "hazardId": hazard_id_1,
            "controlIds": [control_id_1, control_id_2, control_id_3],
            "controlSelections": [
                {"id": control_id_1, "recommended": False, "selected": True},
                {"id": control_id_2, "recommended": False, "selected": False},
                {"id": control_id_3, "recommended": True, "selected": True},
            ],
        },
        {
            "hazardId": hazard_id_2,
            "controlIds": [control_id_4],
            "controlSelections": [
                {"id": control_id_4, "recommended": False, "selected": False},
            ],
        },
        {
            "hazardId": hazard_id_3,
            "controlIds": [control_id_5],
            "controlSelections": [
                {"id": control_id_5, "recommended": None, "selected": None},
            ],
        },
    ]
    assert "contents" in updated_jsb_response, updated_jsb_response
    assert (
        "controlAssessmentSelections" in updated_jsb_response["contents"]
    ), updated_jsb_response
    response_control_assessment_selections = updated_jsb_response["contents"][
        "controlAssessmentSelections"
    ]
    assert (
        response_control_assessment_selections == expected_control_assessment_selections
    ), updated_jsb_response


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_job_safety_briefing_control_assessment_selections_with_empty_control_selections(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation updates the expected content
    when changing controlSelections to empty.
    """
    # Arrange
    jsb_request, *_ = await build_jsb_data(db_session)
    jsb_response = await execute_save_jsb(execute_gql, jsb_request)
    hazard_id_1 = str(uuid.uuid4())
    request_control_assessment_selections: list[dict[str, Any]] = [
        {
            "hazardId": hazard_id_1,
            "controlIds": None,
            "controlSelections": [],
        }
    ]
    update_jsb_request = {
        "jsbId": jsb_response["id"],
        "controlAssessmentSelections": request_control_assessment_selections,
    }

    # Act
    updated_jsb_response = await execute_save_jsb(execute_gql, update_jsb_request)

    # Assert
    expected_control_assessment_selections = [
        {
            "hazardId": hazard_id_1,
            "controlIds": [],
            "controlSelections": [],
        }
    ]
    assert "contents" in updated_jsb_response, updated_jsb_response
    assert (
        "controlAssessmentSelections" in updated_jsb_response["contents"]
    ), updated_jsb_response
    response_control_assessment_selections = updated_jsb_response["contents"][
        "controlAssessmentSelections"
    ]
    assert (
        response_control_assessment_selections == expected_control_assessment_selections
    ), updated_jsb_response


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_job_safety_briefing_task_selections(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation updates the expected content
    when changing the taskSelections.
    """
    # Arrange
    jsb_request, *_ = await build_jsb_data(db_session)
    jsb_response = await execute_save_jsb(execute_gql, jsb_request)
    task_selections = [
        {
            "id": str(uuid.uuid4()),
            "name": None,
            "riskLevel": RiskLevel.HIGH.name,
            "fromWorkOrder": True,
        }
    ]
    update_jsb_request = {
        "jsbId": jsb_response["id"],
        "taskSelections": task_selections,
        "activities": [{"name": "activity name", "tasks": task_selections}],
    }

    # Act
    updated_jsb_response = await execute_save_jsb(execute_gql, update_jsb_request)
    db_jsb = await db_data.jsb(updated_jsb_response["id"])

    # Assert
    assert "contents" in updated_jsb_response, updated_jsb_response
    assert "taskSelections" in updated_jsb_response["contents"], updated_jsb_response
    assert (
        updated_jsb_response["contents"]["taskSelections"]
        == update_jsb_request["taskSelections"]
    ), updated_jsb_response
    assert db_jsb.contents
    update_jsb_request["taskSelections"][0]["riskLevel"] = "high"
    assert_data_equal_case_insensitive(
        db_jsb.contents["task_selections"],
        update_jsb_request["taskSelections"],
    )
    assert_data_equal_case_insensitive(
        db_jsb.contents["activities"],
        update_jsb_request["activities"],
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_job_safety_briefing_task_selections_with_defaults(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation updates the expected content
    when changing the taskSelections with defaults.
    """
    # Arrange
    jsb_request, *_ = await build_jsb_data(db_session)
    jsb_response = await execute_save_jsb(execute_gql, jsb_request)
    task_id_1 = str(uuid.uuid4())
    task_selections = [
        {
            "id": task_id_1,
            "name": None,
            "riskLevel": RiskLevel.HIGH.name,
            "fromWorkOrder": True,
        }
    ]
    update_jsb_request = {
        "jsbId": jsb_response["id"],
        "taskSelections": task_selections,
        "activities": [{"name": "activity name", "tasks": task_selections}],
    }

    # Act
    updated_jsb_response = await execute_save_jsb(execute_gql, update_jsb_request)
    db_jsb = await db_data.jsb(updated_jsb_response["id"])

    # Assert
    expected_task_selections = [
        {
            "id": task_id_1,
            "name": None,
            "riskLevel": RiskLevel.HIGH.name,
            "fromWorkOrder": True,
        }
    ]
    expected_activities = [{"name": "activity name", "tasks": expected_task_selections}]
    assert "contents" in updated_jsb_response, updated_jsb_response
    assert "taskSelections" in updated_jsb_response["contents"], updated_jsb_response
    assert (
        updated_jsb_response["contents"]["taskSelections"] == expected_task_selections
    ), updated_jsb_response
    assert db_jsb.contents
    expected_task_selections[0]["riskLevel"] = "high"
    assert_data_equal_case_insensitive(
        db_jsb.contents["task_selections"],
        expected_task_selections,
    )
    assert_data_equal_case_insensitive(
        db_jsb.contents["activities"],
        expected_activities,
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_job_safety_briefing_with_none_sections_should_maintain_previous_value(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    jsb_request, *_ = await build_jsb_data(db_session)
    jsb_response = await execute_save_jsb(execute_gql, jsb_request)
    jsb_request["jsbId"] = jsb_response["id"]
    jsb_request["jsbMetadata"] = None
    jsb_request["workLocation"] = {
        "description": "test",
        "address": "test",
        "city": "test",
        "state": "test",
        "operatingHq": "test",
    }
    updated_jsb_response = await execute_save_jsb(execute_gql, jsb_request)

    assert (
        jsb_response["contents"]["jsbMetadata"]
        == updated_jsb_response["contents"]["jsbMetadata"]
    )
    assert (
        updated_jsb_response["contents"]["workLocation"] == jsb_request["workLocation"]
    )
    assert jsb_response["contents"]["workLocation"] is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_job_safety_briefing_with_new_geo_coordinates_should_empty_nearest_medical_facility(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    jsb_request, *_ = await build_jsb_data(db_session)
    jsb_response = await execute_save_jsb(execute_gql, jsb_request)

    jsb_request["jsbId"] = jsb_response["id"]
    jsb_request["gpsCoordinates"] = {"latitude": 29.0, "longitude": 17.39}

    updated_jsb_response = await execute_save_jsb(execute_gql, jsb_request)

    assert updated_jsb_response["contents"]["nearestMedicalFacility"] is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_job_safety_briefing(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    jsb_request, *_ = await build_jsb_data(db_session)
    jsb_response = await execute_save_jsb(execute_gql, jsb_request)
    jsb_id = jsb_response["id"]
    delete_result = await execute_delete_jsb(execute_gql, jsb_id)

    assert delete_result is True

    db_jsb = await db_data.jsb(jsb_id)

    assert db_jsb.archived_at is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_complete_job_safety_briefing(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    # Arrange
    user = await SupervisorUserFactory.persist(db_session)
    jsb_request, *_ = await build_jsb_data(db_session)
    jsb_response = await execute_save_jsb(execute_gql, jsb_request, user=user)
    jsb_request["jsbId"] = jsb_response["id"]

    # Act
    jsb_response = await execute_complete_jsb(execute_gql, jsb_request, user=user)

    # Assert
    assert jsb_response["status"] == "COMPLETE"
    assert jsb_response["completedBy"]["id"] == str(user.id)
    assert jsb_response["completedAt"] is not None
    completed_at = datetime.datetime.fromisoformat(jsb_response["completedAt"])
    assert len(jsb_response["contents"]["completions"]) == 1
    assert jsb_response["contents"]["completions"][0]["completedBy"]["id"] == str(
        user.id
    )
    assert (
        jsb_response["contents"]["completions"][0]["completedAt"]
        == completed_at.isoformat()
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_reopen_job_safety_briefing(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    # Persist new JSB
    user = await SupervisorUserFactory.persist(db_session)
    jsb_request, *_ = await build_jsb_data(db_session)
    jsb_response = await execute_save_jsb(execute_gql, jsb_request, user=user)
    assert jsb_response["status"] == "IN_PROGRESS"
    assert jsb_response["completedBy"] is None
    assert jsb_response["completedAt"] is None

    # Change status to Complete
    jsb_request["jsbId"] = jsb_response["id"]
    jsb_response = await execute_complete_jsb(execute_gql, jsb_request, user=user)
    assert jsb_response["status"] == "COMPLETE"
    assert jsb_response["completedBy"]["id"] == str(user.id)
    assert jsb_response["completedAt"] is not None
    completed_at = datetime.datetime.fromisoformat(jsb_response["completedAt"])
    assert len(jsb_response["contents"]["completions"]) == 1
    assert jsb_response["contents"]["completions"][0]["completedBy"]["id"] == str(
        user.id
    )
    assert (
        jsb_response["contents"]["completions"][0]["completedAt"]
        == completed_at.isoformat()
    )

    # Change status to In Progress
    jsb_id = jsb_response["id"]
    reopened_jsb = await execute_reopen_jsb(execute_gql, jsb_id)
    assert reopened_jsb["status"] == "IN_PROGRESS"
    assert reopened_jsb["completedBy"]["id"] == str(user.id)
    assert reopened_jsb["completedAt"] == completed_at.isoformat()
    assert len(jsb_response["contents"]["completions"]) == 1
    assert jsb_response["contents"]["completions"][0]["completedBy"]["id"] == str(
        user.id
    )
    assert (
        jsb_response["contents"]["completions"][0]["completedAt"]
        == completed_at.isoformat()
    )

    # Change status to Complete
    other_user = await SupervisorUserFactory.persist(db_session)
    jsb_request["jsbId"] = jsb_response["id"]
    jsb_response = await execute_complete_jsb(execute_gql, jsb_request, user=other_user)
    assert jsb_response["status"] == "COMPLETE"
    assert jsb_response["completedBy"]["id"] == str(user.id)
    assert jsb_response["completedAt"] == completed_at.isoformat()
    assert len(jsb_response["contents"]["completions"]) == 2
    assert jsb_response["contents"]["completions"][0]["completedBy"]["id"] == str(
        user.id
    )
    assert (
        jsb_response["contents"]["completions"][0]["completedAt"]
        == completed_at.isoformat()
    )
    assert jsb_response["contents"]["completions"][1]["completedBy"]["id"] == str(
        other_user.id
    )
    assert (
        datetime.datetime.fromisoformat(
            jsb_response["contents"]["completions"][1]["completedAt"]
        )
        > completed_at
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_reopen_not_completed_job_safety_briefing(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    jsb_request, *_ = await build_jsb_data(db_session)
    jsb_response = await execute_save_jsb(execute_gql, jsb_request)
    jsb_id = jsb_response["id"]
    with pytest.raises(Exception):
        await execute_reopen_jsb(execute_gql, jsb_id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_job_safety_briefing_with_custom_nmf(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    jsb_request, *_ = await build_jsb_data(db_session)
    jsb_response = await execute_save_jsb(execute_gql, jsb_request)
    assert jsb_response["contents"]["customNearestMedicalFacility"] is None

    jsb_request["jsbId"] = jsb_response["id"]
    jsb_request["customNearestMedicalFacility"] = {
        "address": "test",
    }
    updated_jsb_response = await execute_save_jsb(execute_gql, jsb_request)

    assert (
        updated_jsb_response["contents"]["customNearestMedicalFacility"]
        == jsb_request["customNearestMedicalFacility"]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_job_safety_briefing_mutation_with_source_info(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation creates a new job safety briefing with Source Info.
    """
    jsb_request, *_ = await build_jsb_data(db_session)
    jsb_response = await execute_save_jsb(execute_gql, jsb_request)
    db_jsb = await db_data.jsb(jsb_response["id"])
    assert db_jsb.id == uuid.UUID(jsb_response["id"])
    assert jsb_response["contents"]["sourceInfo"]["appVersion"] == "V1.1.1"
    assert jsb_response["contents"]["sourceInfo"]["sourceInformation"] == "WEB_PORTAL"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_form_id_generation_save_job_safety_briefing_mutation(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that form_id is getting generated for the saveJobSafetyBriefing mutation while creating a new job safety briefing.
    """
    jsb_ids = []
    current_date = datetimenow.now()
    year_month = current_date.strftime("%y%m")

    for i in range(4):
        jsb_request, *_ = await build_jsb_data(db_session)
        jsb_response = await execute_save_jsb(execute_gql, jsb_request)
        jsb_ids.append(jsb_response["id"])

    for i, jsb_id in enumerate(jsb_ids, start=1):
        expected_form_id = f"{year_month}{i:05}"
        db_jsb = await db_data.jsb(jsb_id)
        assert db_jsb.form_id == expected_form_id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_nearest_medical_facility_when_other_is_null(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Test for WORK-3322 and WORK-3286
    This is a test for making sure that either
    nearestMedicalFacility is null when customNearestMedicalFacility(other option in UI) is selected. And
    customNearestMedicalFacility is null when nearestMedicalFacility
    """
    jsb1 = await JobSafetyBriefingFactory.persist(
        session=db_session,
        kwargs={
            "contents": {
                "nearest_medical_facility": {
                    "zip": 36049,
                    "city": "LUVERNE",
                    "state": "AL",
                    "address": "101 HOSPITAL CIRCLE",
                    "description": "CRENSHAW COMMUNITY HOSPITAL",
                    "phone_number": "(334) 335-1154",
                    "distance_from_job": 19.358814933154918,
                },
                "custom_nearest_medical_facility": None,
            }
        },
    )

    jsb_request1 = {
        "jsbId": str(jsb1.id),
        "nearestMedicalFacility": None,
        "customNearestMedicalFacility": {"address": "St. James Hospital"},
    }
    jsb_response1 = await execute_save_jsb(execute_gql, jsb_request1)

    assert jsb_response1["contents"]["nearestMedicalFacility"] is None
    assert jsb_response1["contents"][
        "customNearestMedicalFacility"
    ] == jsb_request1.get("customNearestMedicalFacility")

    jsb2 = await JobSafetyBriefingFactory.persist(
        session=db_session,
        kwargs={
            "contents": {
                "nearest_medical_facility": None,
                "custom_nearest_medical_facility": {"address": "St. John's Hospital"},
            }
        },
    )

    jsb_request2 = {
        "jsbId": str(jsb2.id),
        "nearestMedicalFacility": {
            "zip": 36049,
            "city": "LUVERNE",
            "state": "AL",
            "address": "101 HOSPITAL CIRCLE",
            "description": "CRENSHAW COMMUNITY HOSPITAL",
            "phoneNumber": "(334) 335-1154",
            "distanceFromJob": 19.358814933154918,
        },
        "customNearestMedicalFacility": None,
    }

    jsb_response2 = await execute_save_jsb(execute_gql, jsb_request2)

    assert (
        jsb_response2["contents"]["nearestMedicalFacility"]["description"]
        == "CRENSHAW COMMUNITY HOSPITAL"
    )
    assert jsb_response2["contents"]["customNearestMedicalFacility"] is None


# @pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_jsb_supervisor_link_data_complete_job_safety_briefing(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    jsb_request = await build_jsb_data_with_crew_info(db_session)
    await execute_save_jsb(execute_gql, jsb_request)
    results = await db_session.exec(select(JSBSupervisorLink))
    jsb_supervisors = results.all()
    assert len(jsb_supervisors) == len(jsb_request["crewSignOff"])
    manager_ids = [str(js.manager_id) for js in jsb_supervisors]
    requested_manager_ids = [
        str(obj["managerId"]) for obj in jsb_request["crewSignOff"]
    ]
    assert sorted(manager_ids) == sorted(requested_manager_ids)
    await JSBSupervisorLinkFactory.delete_many(db_session, jsb_supervisors)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_jsb_supervisor_delete_on_complete_jsb(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Makes three mutation calls and then queries to check that the result of supervisors
    for a jsb_id matches the result of the most recent mutation call
    """
    await build_jsb_data_with_crew_info(db_session)
    await build_jsb_data_with_crew_info(db_session)
    jsb_request = await build_jsb_data_with_crew_info(db_session)

    await execute_save_jsb(execute_gql, jsb_request)
    results = await db_session.exec(
        select(JSBSupervisorLink).where(
            JSBSupervisorLink.jsb_id == jsb_request["jsbId"]
        )
    )
    jsb_supervisors = results.all()
    assert len(jsb_supervisors) == len(jsb_request["crewSignOff"])
    manager_ids = [str(js.manager_id) for js in jsb_supervisors]
    requested_manager_ids = [
        str(obj["managerId"]) for obj in jsb_request["crewSignOff"]
    ]
    assert sorted(manager_ids) == sorted(requested_manager_ids)
    await JSBSupervisorLinkFactory.delete_many(db_session, jsb_supervisors)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_jsb_supervisor_link_on_save_job_safety_briefing_mutation(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that jsb supervisor link records are correctly created on saveJobSafettBriefing mutation.
    """

    jsb_request = await build_jsb_data_with_crew_info(db_session)
    await execute_save_jsb(execute_gql, jsb_request)
    results = await db_session.exec(select(JSBSupervisorLink))
    jsb_supervisors = results.all()
    assert len(jsb_supervisors) == len(jsb_request["crewSignOff"])
    manager_ids = [str(js.manager_id) for js in jsb_supervisors]
    requested_manager_ids = [
        str(obj["managerId"]) for obj in jsb_request["crewSignOff"]
    ]
    assert sorted(manager_ids) == sorted(requested_manager_ids)
    await JSBSupervisorLinkFactory.delete_many(db_session, jsb_supervisors)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_empty_jsb_supervisor_link_on_save_job_safety_briefing_mutation(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that jsb supervisor link records are *not* created on saveJobSafettBriefing mutation.
    """

    jsb_request, *_ = await build_jsb_data(db_session)
    await execute_save_jsb(execute_gql, jsb_request)
    results = await db_session.exec(select(JSBSupervisorLink))
    jsb_supervisors = results.all()
    assert len(jsb_supervisors) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_jsb_supervisor_link_conflict_on_save_job_safety_briefing_mutation(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that jsb supervisor link records duplicates are correctly managed on saveJobSafettBriefing mutation.
    """

    jsb_request = await build_jsb_data_with_crew_info(db_session)
    old_manager_name = jsb_request["crewSignOff"][0]["managerName"]
    old_manager_email = jsb_request["crewSignOff"][0]["managerEmail"]
    await execute_save_jsb(execute_gql, jsb_request)
    jsb_request["crewSignOff"][0]["managerName"] = "New Name"
    jsb_request["crewSignOff"][0]["managerEmail"] = "New Email"
    await execute_save_jsb(execute_gql, jsb_request)
    results = await db_session.exec(select(JSBSupervisorLink))
    jsb_supervisors = results.all()
    assert len(jsb_supervisors) == len(jsb_request["crewSignOff"])
    manager_ids = [str(js.manager_id) for js in jsb_supervisors]
    requested_manager_ids = [obj["managerId"] for obj in jsb_request["crewSignOff"]]
    assert jsb_request["crewSignOff"][0]["managerName"] == "New Name"
    assert jsb_request["crewSignOff"][0]["managerEmail"] == "New Email"
    assert old_manager_name != "New Name"
    assert old_manager_email != "New Email"
    assert sorted(manager_ids) == sorted(requested_manager_ids)
    await JSBSupervisorLinkFactory.delete_many(db_session, jsb_supervisors)
