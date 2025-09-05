import dataclasses
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, AsyncGenerator

import pytest

from tests.factories import (
    AdminUserFactory,
    JobSafetyBriefingFactory,
    JSBSupervisorLinkFactory,
    LocationFactory,
    SupervisorUserFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.job_safety_briefing.helpers import (
    build_jsb_data,
    execute_complete_jsb,
    execute_get_jsb_by_id,
    execute_get_jsb_for_project_location,
    execute_last_added_adhoc_jsb,
    execute_last_added_jsb,
    execute_reopen_jsb,
    execute_save_jsb,
)
from tests.utils import assert_data_equal_case_insensitive
from worker_safety_service.models import AsyncSession
from worker_safety_service.models.base import Location, RiskLevel
from worker_safety_service.models.concepts import FormStatus
from worker_safety_service.models.forms import JobSafetyBriefing
from worker_safety_service.models.user import User


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_job_safety_briefing_by_project_location(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    location = await LocationFactory.persist(db_session)
    date = datetime.now(timezone.utc)
    await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=3,
        project_location_id=location.id,
        date_for=date,
    )

    jsb_for_project_location_response = await execute_get_jsb_for_project_location(
        execute_gql, location.id
    )

    assert len(jsb_for_project_location_response["jobSafetyBriefings"]) == 3


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_job_safety_briefing_by_project_location_does_not_include_archived(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    location = await LocationFactory.persist(db_session)
    date = datetime.now(timezone.utc)
    await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=3,
        project_location_id=location.id,
        date_for=date,
    )
    await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=2,
        project_location_id=location.id,
        date_for=date,
        archived_at=datetime.now(timezone.utc),
    )

    jsb_for_project_location_response = await execute_get_jsb_for_project_location(
        execute_gql, location.id
    )

    assert len(jsb_for_project_location_response["jobSafetyBriefings"]) == 3


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_job_safety_briefing_by_id(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    date = datetime.now(timezone.utc)
    jsb = await JobSafetyBriefingFactory.persist(
        db_session,
        date_for=date,
    )

    jsb_by_id = await execute_get_jsb_by_id(execute_gql, jsb.id)

    assert jsb_by_id["id"] == str(jsb.id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_job_safety_briefing_by_id_with_control_assessment_selections(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Test that the jobSafetyBriefing query returns the expected content
    for the controlAssessmentSelections.
    """
    # Arrange
    date = datetime.now(timezone.utc)
    control_id_1 = str(uuid.uuid4())
    control_id_2 = str(uuid.uuid4())
    control_id_3 = str(uuid.uuid4())
    hazard_id_1 = str(uuid.uuid4())
    control_assessment_selections = [
        {
            "hazard_id": hazard_id_1,
            "control_ids": [control_id_1],
            "control_selections": [
                {"id": control_id_1, "recommended": True, "selected": True},
                {"id": control_id_2, "recommended": False, "selected": True},
                {"id": control_id_3, "recommended": None, "selected": None},
            ],
        }
    ]
    jsb = await JobSafetyBriefingFactory.persist(
        db_session,
        date_for=date,
        contents={
            "control_assessment_selections": control_assessment_selections,
        },
    )

    # Act
    response_jsb = await execute_get_jsb_by_id(execute_gql, jsb.id)

    # Assert
    assert response_jsb["id"] == str(jsb.id)
    assert_data_equal_case_insensitive(
        response_jsb["contents"]["controlAssessmentSelections"],
        control_assessment_selections,
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_job_safety_briefing_by_id_with_task_selections(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Test that the jobSafetyBriefing query returns the expected content
    for the taskSelections.
    """
    # Arrange
    date = datetime.now(timezone.utc)
    jsb = await JobSafetyBriefingFactory.persist(db_session, date_for=date)
    task_selections = [
        {
            "id": str(uuid.uuid4()),
            "riskLevel": RiskLevel.HIGH.name,
            "fromWorkOrder": True,
        },
        {
            "id": str(uuid.uuid4()),
            "riskLevel": RiskLevel.LOW.name,
            "fromWorkOrder": True,
        },
    ]
    update_jsb_request = {
        "jsbId": str(jsb.id),
        "taskSelections": task_selections,
        "activities": [{"name": "activity name", "tasks": task_selections}],
    }
    await execute_save_jsb(execute_gql, update_jsb_request)

    # Act
    saved_jsb = await execute_get_jsb_by_id(execute_gql, jsb.id)

    # Assert
    assert saved_jsb["id"] == str(jsb.id)
    assert (
        saved_jsb["contents"]["taskSelections"] == update_jsb_request["taskSelections"]
    ), saved_jsb
    assert (
        saved_jsb["contents"]["activities"] == update_jsb_request["activities"]
    ), saved_jsb


@dataclasses.dataclass
class JobSafetyBriefingInit:
    actor: User
    project_location_1: Location
    project_location_2: Location
    last_jsb_on_user_id_1: JobSafetyBriefing
    last_jsb_on_user_id_2: JobSafetyBriefing
    last_jsb_on_project_loc_1: JobSafetyBriefing
    last_jsb_on_project_loc_2: JobSafetyBriefing
    last_adhoc_jsb_on_user_id_1: JobSafetyBriefing
    last_adhoc_jsb_on_user_id_2: JobSafetyBriefing


@pytest.fixture
async def last_added_jsb_init(
    db_session: AsyncSession,
) -> AsyncGenerator[JobSafetyBriefingInit, None]:
    # TODO: Is it better to move this to confest.py file?
    dateNow = datetime.now(timezone.utc)
    dateMinusOneDay = dateNow + timedelta(days=-1)
    actor = await AdminUserFactory.persist(db_session)
    project_location_1 = await LocationFactory.persist(db_session)
    project_location_2 = await LocationFactory.persist(db_session)
    completed_jsb_on_user_1 = await JobSafetyBriefingFactory.persist(
        db_session,
        created_by_id=actor.id,
        completed_by_id=actor.id,
        completed_at=dateNow,
        project_location_id=project_location_2.id,
        contents={
            "emergency_contacts": [
                {
                    "name": "adhoc emergency -1",
                    "primary": True,
                    "phone_number": "1313131312",
                },
                {
                    "name": "adhoc emergency-2",
                    "primary": False,
                    "phone_number": "1311313131",
                },
            ],
            "aed_information": {"location": "Truck driver side compartment"},
        },
    )
    completed_jsb_on_user_2 = await JobSafetyBriefingFactory.persist(
        db_session,
        created_by_id=actor.id,
        completed_by_id=actor.id,
        completed_at=dateMinusOneDay,
        project_location_id=project_location_2.id,
    )
    completed_jsb_on_location_1 = await JobSafetyBriefingFactory.persist(
        db_session,
        created_by_id=actor.id,
        completed_by_id=actor.id,
        completed_at=dateNow,
        project_location_id=project_location_1.id,
        contents={
            "work_location": {
                "city": "",
                "state": "Georgia",
                "address": "test-adhoc-address-1",
                "description": "test-adhoc-loc-1",
                "operating_hq": "Test",
            },
            "nearest_medical_facility": {
                "description": "NORTHSIDE HOSPITAL FORSYTH",
                "address": "1200 NORTHSIDE FORSYTH DRIVE",
                "city": "1200 NORTHSIDE FORSYTH DRIVE",
                "distance_from_job": 8.59622554062753,
                "phone_number": "(770) 844-3200",
                "state": "GA",
                "zip": 30041,
            },
        },
    )

    completed_jsb_on_location_2 = await JobSafetyBriefingFactory.persist(
        db_session,
        created_by_id=actor.id,
        completed_by_id=actor.id,
        completed_at=dateMinusOneDay,
        project_location_id=project_location_1.id,
    )
    # AdHoc JSBs
    completed_adhoc_jsb_on_user_1 = await JobSafetyBriefingFactory.persist(
        db_session,
        status=FormStatus.COMPLETE,
        created_by_id=actor.id,
        completed_by_id=actor.id,
        completed_at=dateNow,
        project_location_id=None,
        contents={
            "work_location": {
                "city": "",
                "state": "Georgia",
                "address": "test-adhoc-address-1",
                "description": "test-adhoc-loc-1",
                "operating_hq": "Test",
            },
            "nearest_medical_facility": {
                "description": "NORTHSIDE HOSPITAL FORSYTH",
                "address": "1200 NORTHSIDE FORSYTH DRIVE",
                "city": "1200 NORTHSIDE FORSYTH DRIVE",
                "distance_from_job": 8.59622554062753,
                "phone_number": "(770) 844-3200",
                "state": "GA",
                "zip": 30041,
            },
            "emergency_contacts": [
                {
                    "name": "adhoc emergency -1",
                    "primary": True,
                    "phone_number": "1313131312",
                },
                {
                    "name": "adhoc emergency-2",
                    "primary": False,
                    "phone_number": "1311313131",
                },
            ],
            "aed_information": {"location": "Truck driver side compartment"},
        },
    )
    # Incomplete JSB
    incomplete_adhoc_jsb_on_user_1 = await JobSafetyBriefingFactory.persist(
        db_session,
        status=FormStatus.IN_PROGRESS,
        created_by_id=actor.id,
        completed_by_id=None,
        completed_at=None,
        project_location_id=None,
        contents={
            "work_location": {
                "city": "",
                "state": "Georgia",
                "address": "test-adhoc-address-1",
                "description": "test-adhoc-loc-1",
                "operating_hq": "Test",
            },
            "nearest_medical_facility": {
                "description": "NORTHSIDE HOSPITAL FORSYTH",
                "address": "1200 NORTHSIDE FORSYTH DRIVE",
                "city": "1200 NORTHSIDE FORSYTH DRIVE",
                "distance_from_job": 8.59622554062753,
                "phone_number": "(770) 844-3200",
                "state": "GA",
                "zip": 30041,
            },
            "emergency_contacts": [
                {
                    "name": "adhoc emergency -1",
                    "primary": True,
                    "phone_number": "1313131312",
                },
                {
                    "name": "adhoc emergency-2",
                    "primary": False,
                    "phone_number": "1311313131",
                },
            ],
            "aed_information": {"location": "Truck driver side compartment"},
        },
    )
    completed_adhoc_jsb_on_user_2 = await JobSafetyBriefingFactory.persist(
        db_session,
        status=FormStatus.COMPLETE,
        created_by_id=actor.id,
        completed_by_id=actor.id,
        completed_at=dateMinusOneDay,
        project_location_id=None,
    )
    yield JobSafetyBriefingInit(
        actor=actor,
        project_location_1=project_location_1,
        project_location_2=project_location_2,
        last_jsb_on_user_id_1=completed_jsb_on_user_1,
        last_jsb_on_user_id_2=completed_jsb_on_user_2,
        last_jsb_on_project_loc_1=completed_jsb_on_location_1,
        last_jsb_on_project_loc_2=completed_jsb_on_location_2,
        last_adhoc_jsb_on_user_id_1=completed_adhoc_jsb_on_user_1,
        last_adhoc_jsb_on_user_id_2=completed_adhoc_jsb_on_user_2,
    )
    await db_session.delete(completed_jsb_on_location_2)
    await db_session.delete(completed_jsb_on_location_1)
    await db_session.delete(completed_jsb_on_user_2)
    await db_session.delete(completed_jsb_on_user_1)
    await db_session.delete(completed_adhoc_jsb_on_user_2)
    await db_session.delete(completed_adhoc_jsb_on_user_1)
    await db_session.delete(incomplete_adhoc_jsb_on_user_1)
    await db_session.delete(project_location_2)
    await db_session.delete(project_location_1)
    await db_session.delete(actor)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_last_adhoc_job_safety_briefing_by_user(
    execute_gql: ExecuteGQL, last_added_jsb_init: JobSafetyBriefingInit
) -> None:
    x: JobSafetyBriefingInit = last_added_jsb_init

    jsb_data = await execute_last_added_adhoc_jsb(
        execute_gql=execute_gql, req={}, raw=False, user=last_added_jsb_init.actor
    )

    res_contents = jsb_data["contents"]
    data_contents = (
        x.last_adhoc_jsb_on_user_id_1.contents
        if x.last_jsb_on_user_id_1.contents
        else None
    )

    compare_objects(
        res_contents.get("workLocation"), data_contents.get("work_location")  # type: ignore
    )
    compare_objects(
        res_contents.get("nearestMedicalFacility"), data_contents.get("nearest_medical_facility")  # type: ignore
    )

    for index, obj in enumerate(res_contents.get("emergencyContacts")):
        compare_objects(obj, data_contents.get("emergency_contacts")[index])  # type: ignore

    compare_objects(
        res_contents.get("aedInformation"), data_contents.get("aed_information")  # type: ignore
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_last_adhoc_job_safety_briefing_by_user_when_no_jsb_exists(
    execute_gql: ExecuteGQL,
    last_added_jsb_init: JobSafetyBriefingInit,
    db_session: AsyncSession,
) -> None:
    actor = await AdminUserFactory.persist(db_session)

    jsb_data = await execute_last_added_adhoc_jsb(
        execute_gql=execute_gql, req={}, raw=False, user=actor
    )

    res_contents = jsb_data["contents"]

    assert res_contents.get("workLocation") is None
    assert res_contents.get("nearestMedicalFacility") is None
    assert res_contents.get("emergencyContacts") is None
    assert res_contents.get("aedInformation") is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_last_job_safety_briefing_by_user(
    execute_gql: ExecuteGQL, last_added_jsb_init: JobSafetyBriefingInit
) -> None:
    x: JobSafetyBriefingInit = last_added_jsb_init
    req_data = {"filterOn": "USER_DETAILS", "projectLocationId": None}

    jsb_data = await execute_last_added_jsb(
        execute_gql=execute_gql, req=req_data, raw=False, user=last_added_jsb_init.actor
    )

    res_contents = jsb_data["contents"]
    data_contents = (
        x.last_jsb_on_user_id_1.contents if x.last_jsb_on_user_id_1.contents else None
    )

    assert jsb_data["contents"]["workLocation"] is None
    assert jsb_data["contents"]["nearestMedicalFacility"] is None

    for index, obj in enumerate(res_contents.get("emergencyContacts")):
        compare_objects(obj, data_contents.get("emergency_contacts")[index])  # type: ignore

    compare_objects(
        res_contents.get("aedInformation"), data_contents.get("aed_information")  # type: ignore
    )


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_last_job_safety_briefing_by_project_location(
    execute_gql: ExecuteGQL, last_added_jsb_init: JobSafetyBriefingInit
) -> None:
    x = last_added_jsb_init
    req_data = {
        "filterOn": "PROJECT_LOCATION",
        "projectLocationId": x.project_location_1.id,
    }
    jsb_data = await execute_last_added_jsb(
        execute_gql=execute_gql, req=req_data, raw=False, user=x.actor
    )

    res_contents: dict[Any, Any] = jsb_data["contents"]
    data_contents_on_user = x.last_jsb_on_user_id_1.contents
    data_contents_on_project_loc = x.last_jsb_on_project_loc_1.contents

    if data_contents_on_project_loc is not None:
        compare_objects(
            res_contents.get("workLocation"),
            data_contents_on_project_loc.get("work_location"),
        )
        compare_objects(
            res_contents.get("nearestMedicalFacility"),
            data_contents_on_project_loc.get("nearest_medical_facility"),
        )

    if data_contents_on_user is not None and res_contents is not None:
        for index, obj in enumerate(res_contents.get("emergencyContacts")):  # type: ignore
            compare_objects(obj, data_contents_on_user.get("emergency_contacts")[index])  # type: ignore

        compare_objects(
            res_contents.get("aedInformation"),
            data_contents_on_user.get("aed_information"),
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_last_job_safety_briefing_no_jsb_found(
    execute_gql: ExecuteGQL,
) -> None:
    req_data = {
        "filterOn": "PROJECT_LOCATION",
        "projectLocationId": uuid.uuid4(),
    }
    res_jsb = await execute_last_added_jsb(
        execute_gql=execute_gql, req=req_data, raw=False, user=None
    )

    contents: dict[Any, Any] = res_jsb["contents"]

    for key in contents.keys():
        assert contents[key] is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_last_job_safety_briefing_project_id_not_entered(
    execute_gql: ExecuteGQL,
) -> None:
    req_data = {"filterOn": "PROJECT_LOCATION", "projectLocationId": None}
    error_response = await execute_last_added_jsb(
        execute_gql=execute_gql, req=req_data, raw=True, user=None
    )
    error_response = error_response.json()

    if "errors" in error_response:
        for e in error_response["errors"]:
            assert e["message"] == "Please enter project location id"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_job_safety_briefing_completions(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Assert
    user = await SupervisorUserFactory.persist(db_session)
    other_user = await SupervisorUserFactory.persist(db_session)
    jsb_request, *_ = await build_jsb_data(db_session)
    jsb_response = await execute_save_jsb(execute_gql, jsb_request, user=user)
    jsb_id = jsb_request["jsbId"] = jsb_response["id"]
    jsb_response = await execute_complete_jsb(execute_gql, jsb_request, user=user)
    completed_at = datetime.fromisoformat(jsb_response["completedAt"])
    await execute_reopen_jsb(execute_gql, jsb_id)
    await execute_complete_jsb(execute_gql, jsb_request, user=user)
    await execute_reopen_jsb(execute_gql, jsb_id)
    await execute_complete_jsb(execute_gql, jsb_request, user=other_user)

    # Act
    response = await execute_get_jsb_by_id(execute_gql, jsb_id)

    # Assert
    assert completed_at
    completions = response["contents"]["completions"]
    assert len(completions) == 3

    assert completions[0]["completedBy"]["id"] == str(user.id)
    assert completions[0]["completedAt"] == completed_at.isoformat()

    assert completions[1]["completedBy"]["id"] == str(user.id)
    assert datetime.fromisoformat(completions[1]["completedAt"]) > completed_at

    assert completions[2]["completedBy"]["id"] == str(other_user.id)
    assert datetime.fromisoformat(
        completions[2]["completedAt"]
    ) > datetime.fromisoformat(completions[1]["completedAt"])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_jsb_supervisors(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    manager_id = str(uuid.uuid4())
    jsb_supervisor_links = await JSBSupervisorLinkFactory.persist_many(
        db_session, 2, manager_id=manager_id
    )

    get_jsb_supervisors_query = {
        "operation_name": "GetJSBSupervisors",
        "query": """
            query GetJSBSupervisors {
                jsbSupervisors{
                    id
                    name
                    email
                }
            }
            """,
    }
    response = await execute_gql(**get_jsb_supervisors_query)
    unique_managers = {str(jsl.manager_id) for jsl in jsb_supervisor_links}
    response_manager_ids = [
        supervisor["id"] for supervisor in response["jsbSupervisors"]
    ]
    assert len(unique_managers) == len(response["jsbSupervisors"])
    assert sorted(unique_managers) == sorted(set(response_manager_ids))
    await JSBSupervisorLinkFactory.delete_many(db_session, jsb_supervisor_links)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_jsb_supervisors_with_same_manager_id(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    manager_id = str(uuid.uuid4())
    jsb_supervisor_links = await JSBSupervisorLinkFactory.persist_many(
        db_session, 2, manager_id=manager_id
    )

    get_jsb_supervisors_query = {
        "operation_name": "GetJSBSupervisors",
        "query": """
            query GetJSBSupervisors {
                jsbSupervisors{
                    id
                    name
                    email
                }
            }
            """,
    }
    response = await execute_gql(**get_jsb_supervisors_query)
    unique_managers = {str(jsl.manager_id) for jsl in jsb_supervisor_links}
    response_manager_ids = [
        supervisor["id"] for supervisor in response["jsbSupervisors"]
    ]
    assert len(unique_managers) == len(response["jsbSupervisors"])
    assert sorted(unique_managers) == sorted(set(response_manager_ids))
    await JSBSupervisorLinkFactory.delete_many(db_session, jsb_supervisor_links)


def compare_objects(obj1: Any, obj2: Any) -> None:
    for key, value in obj1.items():
        snake_case_key: str = camel_case_to_snake_case(key)
        assert value == obj2[snake_case_key]


def camel_case_to_snake_case(input_str: str) -> str:
    # Use regular expression to find camelCase pattern
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    print(pattern)
    # Replace uppercase letters with underscores followed by lowercase letters
    snake_case_str = re.sub(pattern, "_", input_str).lower()
    return snake_case_str
