from datetime import date, datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import pytest

from tests.factories import (
    AdminUserFactory,
    DailyReportFactory,
    EnergyBasedObservationFactory,
    FormDefinitionFactory,
    JobSafetyBriefingFactory,
    JSBSupervisorLinkFactory,
    LocationFactory,
    NatGridJobSafetyBriefingFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.daily_report.helpers import execute_report
from tests.integration.job_safety_briefing.helpers import (
    build_jsb_data,
    execute_complete_jsb,
    execute_reopen_jsb,
    execute_save_jsb,
)
from worker_safety_service.models import AsyncSession
from worker_safety_service.models.forms import FormDefinitionStatus

form_definitions_query = """
    query FormDefinitions {
        formDefinitions {
            id
            name
            status
            externalKey
        }
    }
"""

forms_query = """
    query GetFormsList(
        $limit: Int,
        $offset: Int,
        $search: String,
        $formName: [String!],
        $formId: [String!],
        $formStatus: [FormStatus!],
        $projectIds: [UUID!],
        $createdByIds: [UUID!],
        $updatedByIds: [UUID!],
        $locationIds: [UUID!],
        $orderBy: [FormListOrderBy!],
        $startCreatedAt: Date,
        $endCreatedAt: Date,
        $startUpdatedAt: Date,
        $endUpdatedAt: Date,
        $startCompletedAt: Date,
        $endCompletedAt: Date,
        $startReportDate: Date,
        $endReportDate: Date,
        $adHoc: Boolean,
    ) {
        formsList(
            limit: $limit,
            offset: $offset,
            search: $search,
            orderBy: $orderBy,
            formName: $formName,
            formId: $formId,
            formStatus: $formStatus,
            projectIds: $projectIds,
            locationIds: $locationIds,
            createdByIds: $createdByIds,
            updatedByIds: $updatedByIds,
            startCreatedAt: $startCreatedAt,
            endCreatedAt: $endCreatedAt,
            startUpdatedAt: $startUpdatedAt,
            endUpdatedAt: $endUpdatedAt,
            startReportDate: $startReportDate,
            endReportDate: $endReportDate
            startCompletedAt: $startCompletedAt,
            endCompletedAt: $endCompletedAt,
            adHoc: $adHoc,
        ) {
            id
            status
            createdAt
            completedAt
            workPackage {
                name
                id
            }
            location {
                id
                name
            }
            createdBy {
                id
                name
            }
            formId
            updatedAt
            multipleLocation
        }
    }
"""

forms_list_count_query = """
    query GetFormsListCount(
        $search: String,
        $formName: [String!],
        $formId: [String!],
        $formStatus: [FormStatus!],
        $projectIds: [UUID!],
        $createdByIds: [UUID!],
        $updatedByIds: [UUID!],
        $locationIds: [UUID!],
        $startCreatedAt: Date,
        $endCreatedAt: Date,
        $startUpdatedAt: Date,
        $endUpdatedAt: Date,
        $startCompletedAt: Date,
        $endCompletedAt: Date,
        $startReportDate: Date,
        $endReportDate: Date,
        $adHoc: Boolean,
    ) {
        formsListCount(
            search: $search,
            formName: $formName,
            formId: $formId,
            formStatus: $formStatus,
            projectIds: $projectIds,
            locationIds: $locationIds,
            createdByIds: $createdByIds,
            updatedByIds: $updatedByIds,
            startCreatedAt: $startCreatedAt,
            endCreatedAt: $endCreatedAt,
            startUpdatedAt: $startUpdatedAt,
            endUpdatedAt: $endUpdatedAt,
            startReportDate: $startReportDate,
            endReportDate: $endReportDate
            startCompletedAt: $startCompletedAt,
            endCompletedAt: $endCompletedAt,
            adHoc: $adHoc,
        )
    }
"""

test_forms_list_filter_options_query = """
query GetFormsListFilterOptions(
        $limit: Int,
        $offset: Int,
        $filterSearch: FormListFilterSearchInput
    ) {
    formsListFilterOptions(
            limit: $limit,
            offset: $offset,
            filterSearch: $filterSearch
        ) {
        formIds
        formNames
        operatingHqs
        updatedByUsers {
            name
            id
        }
        workPackages {
            name
            id
        }
        createdByUsers {
            name
            id
        }
        locations {
            name
            id
        }
        supervisors {
            id
            name
        }
    }
}
"""

forms_list_for_filter_query = """
    query GetFormList {
      formsList {
        formId
        __typename
        operatingHq
        createdBy {
          id
          name
        }
        updatedBy {
          id
          name
        }
        location {
          id
          name
        }
        workPackage {
          id
          name
        }
        supervisor {
            id
            name
        }
      }
    }
"""


async def call_forms_list_query(execute_gql: ExecuteGQL, **kwargs: Any) -> list[dict]:
    user = kwargs.pop("user", None)

    data = await execute_gql(
        query=forms_list_for_filter_query, variables=kwargs, user=user
    )
    forms: list[dict] = data["formsList"]
    return forms


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_form_definitions(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    [
        first_form_definition,
        second_form_definition,
    ] = await FormDefinitionFactory.persist_many(
        db_session,
        size=2,
        per_item_kwargs=[
            {"name": "First JSB", "status": FormDefinitionStatus.ACTIVE},
            {"name": "Second JSB", "status": FormDefinitionStatus.INACTIVE},
        ],
    )

    response = await execute_gql(
        operation_name="FormDefinitions",
        query=form_definitions_query,
    )

    first_form_definitions_data = response["formDefinitions"][0]
    second_form_definition_data = response["formDefinitions"][1]

    assert first_form_definitions_data
    assert first_form_definitions_data["name"] == first_form_definition.name
    assert first_form_definitions_data["status"] == FormDefinitionStatus.ACTIVE.name

    assert second_form_definition_data
    assert second_form_definition_data["name"] == second_form_definition.name
    assert second_form_definition_data["status"] == FormDefinitionStatus.INACTIVE.name


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_adhoc_workpackage_filter(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    await JobSafetyBriefingFactory.persist_many(db_session, 2)
    await EnergyBasedObservationFactory.persist_many(db_session, 3)
    await DailyReportFactory.persist_many(db_session, 4)

    resp = await execute_gql(
        operation_name="GetFormsList",
        query=forms_query,
        variables={
            "limit": 50,
            "offset": 0,
            "orderBy": [{"field": "UPDATED_AT", "direction": "DESC"}],
            "adHoc": True,
            "createdByIds": None,
            "updatedByIds": None,
            "formName": ["DailyReport", "EnergyBasedObservation", "JobSafetyBriefing"],
            "formId": None,
            "locationIds": None,
            "formStatus": None,
            "projectIds": None,
            "startCreatedAt": None,
            "endCreatedAt": None,
            "startUpdatedAt": None,
            "endUpdatedAt": None,
            "startCompletedAt": None,
            "endCompletedAt": None,
            "startReportDate": None,
            "endReportDate": None,
        },
    )

    assert resp
    assert resp["formsList"]
    assert len(resp["formsList"]) == 5


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_forms_list_count_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    await JobSafetyBriefingFactory.persist_many(db_session, 2)
    await EnergyBasedObservationFactory.persist_many(db_session, 3)
    await DailyReportFactory.persist_many(db_session, 5)

    resp = await execute_gql(
        operation_name="GetFormsListCount",
        query=forms_list_count_query,
        variables={"formName": ["DailyReport"]},
    )

    assert resp
    assert resp["formsListCount"]
    assert resp["formsListCount"] == 5


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_forms_created_at_filter(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    resp = await created_at_filter(execute_gql, db_session, "GetFormsList", forms_query)

    assert resp
    assert resp["formsList"]
    assert len(resp["formsList"]) == 10


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_forms_count_created_at_filter(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    resp = await created_at_filter(
        execute_gql, db_session, "GetFormsListCount", forms_list_count_query
    )

    assert resp
    assert resp["formsListCount"]
    assert resp["formsListCount"] == 10


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_forms_completed_at_filter(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    resp = await completed_at_filter(
        execute_gql, db_session, "GetFormsList", forms_query
    )

    assert resp
    assert resp["formsList"]
    assert len(resp["formsList"]) == 3


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_forms_count_completed_at_filter(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    resp = await completed_at_filter(
        execute_gql, db_session, "GetFormsListCount", forms_list_count_query
    )

    assert resp
    assert resp["formsListCount"]
    assert resp["formsListCount"] == 3


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_forms_report_date_filter(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    resp = await report_date_filter(
        execute_gql, db_session, "GetFormsList", forms_query
    )

    assert resp
    assert resp["formsList"]
    assert len(resp["formsList"]) == 6


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_forms_count_report_date_filter(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    resp = await report_date_filter(
        execute_gql, db_session, "GetFormsListCount", forms_list_count_query
    )

    assert resp
    assert resp["formsListCount"]
    assert resp["formsListCount"] == 6


async def created_at_filter(
    execute_gql: ExecuteGQL, db_session: AsyncSession, operation_name: str, query: str
) -> Any:
    now = datetime.now(timezone.utc)
    jsb_created_at = now - timedelta(days=5)
    start_created_at = date.today() - timedelta(days=1)

    await JobSafetyBriefingFactory.persist_many(
        db_session,
        2,
        per_item_kwargs=[{"created_at": jsb_created_at}, {"created_at": now}],
    )
    await EnergyBasedObservationFactory.persist_many(db_session, 3)
    await DailyReportFactory.persist_many(db_session, 4)
    await NatGridJobSafetyBriefingFactory.persist_many(db_session, 2)

    resp = await execute_gql(
        operation_name=operation_name,
        query=query,
        variables={
            "limit": 50,
            "offset": 0,
            "orderBy": [{"field": "UPDATED_AT", "direction": "DESC"}],
            "adHoc": False,
            "createdByIds": None,
            "formName": [
                "DailyReport",
                "EnergyBasedObservation",
                "JobSafetyBriefing",
                "NatGridJobSafetyBriefing",
            ],
            "formId": None,
            "locationIds": None,
            "formStatus": None,
            "projectIds": None,
            "startCreatedAt": start_created_at,
            "endCreatedAt": None,
            "updatedByIds": None,
            "startUpdatedAt": None,
            "endUpdatedAt": None,
            "startCompletedAt": None,
            "endCompletedAt": None,
            "startReportDate": None,
            "endReportDate": None,
        },
    )

    return resp


async def completed_at_filter(
    execute_gql: ExecuteGQL, db_session: AsyncSession, operation_name: str, query: str
) -> Any:
    now = datetime.now(timezone.utc)
    jsb_completed_at = now - timedelta(days=5)
    ebo_completed_at = now - timedelta(days=3)
    start_completed_at = date.today() - timedelta(days=7)

    await JobSafetyBriefingFactory.persist_many(
        db_session,
        2,
        per_item_kwargs=[{"completed_at": jsb_completed_at}, {"completed_at": now}],
    )
    await EnergyBasedObservationFactory.persist_many(
        db_session, 1, per_item_kwargs=[{"completed_at": ebo_completed_at}]
    )
    await DailyReportFactory.persist_many(db_session, 4)

    resp = await execute_gql(
        operation_name=operation_name,
        query=query,
        variables={
            "limit": 50,
            "offset": 0,
            "orderBy": [{"field": "UPDATED_AT", "direction": "DESC"}],
            "adHoc": False,
            "createdByIds": None,
            "formName": ["DailyReport", "EnergyBasedObservation", "JobSafetyBriefing"],
            "formId": None,
            "locationIds": None,
            "formStatus": None,
            "projectIds": None,
            "startCreatedAt": None,
            "endCreatedAt": None,
            "updatedByIds": None,
            "startUpdatedAt": None,
            "endUpdatedAt": None,
            "startCompletedAt": start_completed_at,
            "endCompletedAt": None,
            "startReportDate": None,
            "endReportDate": None,
        },
    )

    return resp


async def report_date_filter(
    execute_gql: ExecuteGQL, db_session: AsyncSession, operation_name: str, query: str
) -> Any:
    today = date.today()

    await JobSafetyBriefingFactory.persist_many(
        db_session, 2, None, **{"date_for": today - timedelta(days=2)}
    )
    await EnergyBasedObservationFactory.persist_many(
        db_session, 1, None, **{"date_for": today - timedelta(days=3)}
    )
    await DailyReportFactory.persist_many(
        db_session, 4, None, **{"date_for": today - timedelta(days=4)}
    )
    await NatGridJobSafetyBriefingFactory.persist_many(
        db_session, 3, None, **{"date_for": today - timedelta(days=2)}
    )

    resp = await execute_gql(
        operation_name=operation_name,
        query=query,
        variables={
            "limit": 50,
            "offset": 0,
            "orderBy": [{"field": "UPDATED_AT", "direction": "DESC"}],
            "adHoc": False,
            "createdByIds": None,
            "formName": [
                "DailyReport",
                "EnergyBasedObservation",
                "JobSafetyBriefing",
                "NatGridJobSafetyBriefing",
            ],
            "formId": None,
            "locationIds": None,
            "formStatus": None,
            "projectIds": None,
            "startCreatedAt": None,
            "endCreatedAt": None,
            "updatedByIds": None,
            "startUpdatedAt": None,
            "endUpdatedAt": None,
            "startCompletedAt": None,
            "endCompletedAt": None,
            "startReportDate": today - timedelta(days=3),
            "endReportDate": today,
        },
    )

    return resp


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_adhoc_natgrid_workpackage_filter(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    await JobSafetyBriefingFactory.persist_many(db_session, 2)
    await EnergyBasedObservationFactory.persist_many(db_session, 3)
    await DailyReportFactory.persist_many(db_session, 4)
    await NatGridJobSafetyBriefingFactory.persist_many(db_session, 2)

    resp = await execute_gql(
        operation_name="GetFormsList",
        query=forms_query,
        variables={
            "limit": 50,
            "offset": 0,
            "orderBy": [{"field": "UPDATED_AT", "direction": "DESC"}],
            "adHoc": True,
            "createdByIds": None,
            "updatedByIds": None,
            "formName": [
                "DailyReport",
                "EnergyBasedObservation",
                "JobSafetyBriefing",
                "NatGridJobSafetyBriefing",
            ],
            "formId": None,
            "locationIds": None,
            "formStatus": None,
            "projectIds": None,
            "startCreatedAt": None,
            "endCreatedAt": None,
            "startUpdatedAt": None,
            "endUpdatedAt": None,
            "startCompletedAt": None,
            "endCompletedAt": None,
            "startReportDate": None,
            "endReportDate": None,
        },
    )

    assert resp
    assert resp["formsList"]
    assert len(resp["formsList"]) == 7


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_forms_list_natgrid_jsb_count_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    await JobSafetyBriefingFactory.persist_many(db_session, 2)
    await EnergyBasedObservationFactory.persist_many(db_session, 3)
    await DailyReportFactory.persist_many(db_session, 5)
    await NatGridJobSafetyBriefingFactory.persist_many(db_session, 6)

    resp = await execute_gql(
        operation_name="GetFormsListCount",
        query=forms_list_count_query,
        variables={"formName": ["NatGridJobSafetyBriefing"]},
    )

    assert resp
    assert resp["formsListCount"]
    assert resp["formsListCount"] == 6


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_forms_list_filter_options(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Arrange
    actor = await AdminUserFactory.persist(db_session)
    project_location = await LocationFactory.persist(db_session)
    jsbs = await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=2,
        created_by_id=actor.id,
        completed_by_id=actor.id,
        completed_at=datetime.now(timezone.utc),
        project_location_id=project_location.id,
        contents={
            "work_location": {
                "city": "",
                "state": "Georgia",
                "address": "test-adhoc-address-1",
                "description": "test-adhoc-loc-1",
                "operating_hq": "Test adhoc operating hq",
            }
        },
    )
    per_item_kwargs = [
        {"jsb_id": jsb.id, "manager_id": str(uuid4()), "tenant_id": jsb.tenant_id}
        for jsb in jsbs
    ]
    await JSBSupervisorLinkFactory.persist_many(
        db_session, 2, manager_id=str(uuid4()), per_item_kwargs=per_item_kwargs
    )
    await EnergyBasedObservationFactory.persist_many(db_session, 2)
    daily_reports = await DailyReportFactory.persist_many(db_session, 2)
    await execute_report(
        execute_gql,
        {
            "id": daily_reports[0].id,
            "projectLocationId": daily_reports[0].project_location_id,
            "date": daily_reports[0].date_for + timedelta(days=1),
        },
    )
    await execute_report(
        execute_gql,
        {
            "id": daily_reports[1].id,
            "projectLocationId": daily_reports[1].project_location_id,
            "date": daily_reports[1].date_for + timedelta(days=1),
        },
    )
    await NatGridJobSafetyBriefingFactory.persist_many(db_session, 2)

    # Act
    response = await execute_gql(
        operation_name="GetFormsListFilterOptions",
        query=test_forms_list_filter_options_query,
    )

    # Assert
    forms = await execute_gql(
        operation_name="GetFormList", query=forms_list_for_filter_query
    )

    assert response, response
    assert "formsListFilterOptions" in response, response
    formIds = {form["formId"] for form in forms["formsList"] if form["formId"]}
    formNames = {
        form["__typename"] for form in forms["formsList"] if form["__typename"]
    }
    operatingHqs = {
        form["operatingHq"] for form in forms["formsList"] if form["operatingHq"]
    }
    createdByUsers = {
        form["createdBy"]["id"]: form["createdBy"]["name"]
        for form in forms["formsList"]
        if form["createdBy"]
    }
    createdByUsersList = [
        {"id": id, "name": createdByUsers[id]} for id in createdByUsers.keys()
    ]
    updatedByUsers = {
        form["updatedBy"]["id"]: form["updatedBy"]["name"]
        for form in forms["formsList"]
        if form["updatedBy"]
    }
    updatedByUsersList = [
        {"id": id, "name": updatedByUsers[id]} for id in updatedByUsers.keys()
    ]
    workPackages = {
        form["workPackage"]["id"]: form["workPackage"]["name"]
        for form in forms["formsList"]
        if form["workPackage"]
    }
    workPackagesList = [
        {"id": id, "name": workPackages[id]} for id in workPackages.keys()
    ]
    locations = {
        form["location"]["id"]: form["location"]["name"]
        for form in forms["formsList"]
        if form["location"]
    }
    locationsList = [{"id": id, "name": locations[id]} for id in locations.keys()]
    supervisorsList = [
        {"id": supervisor["id"], "name": supervisor["name"]}
        for form in forms["formsList"]
        if form.get("supervisor")
        for supervisor in form["supervisor"]
        if supervisor
    ]

    assert formIds
    assert formNames
    assert operatingHqs
    assert createdByUsersList
    assert updatedByUsersList
    assert workPackagesList
    assert locationsList
    assert supervisorsList

    assert response["formsListFilterOptions"] == {
        "formIds": sorted(formIds, reverse=True),
        "formNames": sorted(formNames),
        "operatingHqs": sorted(operatingHqs),
        "createdByUsers": sorted(createdByUsersList, key=lambda x: x["name"]),
        "updatedByUsers": sorted(updatedByUsersList, key=lambda x: x["name"]),
        "workPackages": sorted(workPackagesList, key=lambda x: x["name"]),
        "locations": sorted(locationsList, key=lambda x: x["name"]),
        "supervisors": sorted(supervisorsList, key=lambda x: x["name"]),
    }


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_forms_list_filter_options_with_search(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Arrange
    created_by_user = await AdminUserFactory.persist(
        db_session, first_name="SearchCreated", last_name="User"
    )
    updated_by_user = await AdminUserFactory.persist(
        db_session, first_name="SearchUpdated", last_name="User"
    )

    # Persist JobSafetyBriefing records
    await JobSafetyBriefingFactory.persist_many(
        db_session,
        2,
        per_item_kwargs=[
            {"created_by_id": created_by_user.id},
            {"created_by_id": created_by_user.id},
        ],
    )

    # Search for created_by_user
    response_created_by = await execute_gql(
        operation_name="GetFormsListFilterOptions",
        query=test_forms_list_filter_options_query,
        variables={
            "filterSearch": {
                "searchColumn": "created_by_user",
                "searchValue": "SearchCreated",
            }
        },
    )

    # Assert for created_by_user
    assert response_created_by
    assert "formsListFilterOptions" in response_created_by

    # Validate that the search results match the expected createdBy user
    assert any(
        user["name"] == "SearchCreated User"
        for user in response_created_by["formsListFilterOptions"]["createdByUsers"]
    )
    assert not any(
        user["name"] == "SearchUpdated User"
        for user in response_created_by["formsListFilterOptions"]["createdByUsers"]
    )
    assert len(response_created_by["formsListFilterOptions"]["formIds"]) == 2

    response_updated_by = await execute_gql(
        operation_name="GetFormsListFilterOptions",
        query=test_forms_list_filter_options_query,
        variables={
            "filterSearch": {
                "searchColumn": "updated_by_user",
                "searchValue": "SearchUpdated",
            }
        },
    )

    # Assert for updated_by_user
    assert response_updated_by
    assert "formsListFilterOptions" in response_updated_by
    assert not any(
        user["name"] == "SearchUpdated User"
        for user in response_updated_by["formsListFilterOptions"]["updatedByUsers"]
    )
    assert not any(
        user["name"] == "SearchCreated User"
        for user in response_updated_by["formsListFilterOptions"]["updatedByUsers"]
    )
    assert len(response_updated_by["formsListFilterOptions"]["formIds"]) == 0

    # Persist new JSB
    jsb_request, *_ = await build_jsb_data(db_session)
    jsb_response = await execute_save_jsb(
        execute_gql, jsb_request, user=created_by_user
    )

    # Save JSB
    jsb_request["jsbId"] = jsb_response["id"]
    jsb_response = await execute_complete_jsb(
        execute_gql, jsb_request, user=created_by_user
    )

    # Reopen JSB
    jsb_id = jsb_response["id"]
    await execute_reopen_jsb(execute_gql, jsb_id)

    # Save JSB by different User
    jsb_request["jsbId"] = jsb_response["id"]
    await execute_complete_jsb(execute_gql, jsb_request, user=updated_by_user)

    # Search for updated_by_user
    response_updated_by = await execute_gql(
        operation_name="GetFormsListFilterOptions",
        query=test_forms_list_filter_options_query,
        variables={
            "filterSearch": {
                "searchColumn": "updated_by_user",
                "searchValue": "SearchUpdated",
            }
        },
    )

    # Assert for updated_by_user
    assert response_updated_by
    assert "formsListFilterOptions" in response_updated_by

    # Validate that the search results match the expected updatedBy user
    assert any(
        user["name"] == "SearchUpdated User"
        for user in response_updated_by["formsListFilterOptions"]["updatedByUsers"]
    )
    assert not any(
        user["name"] == "SearchCreated User"
        for user in response_updated_by["formsListFilterOptions"]["updatedByUsers"]
    )
    assert len(response_updated_by["formsListFilterOptions"]["formIds"]) == 1


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_forms_list_filter_options_with_limit(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Arrange
    await JobSafetyBriefingFactory.persist_many(db_session, 5)

    # Act
    response = await execute_gql(
        operation_name="GetFormsListFilterOptions",
        query=test_forms_list_filter_options_query,
        variables={"limit": 3},
    )

    # Assert
    assert response
    assert "formsListFilterOptions" in response
    assert len(response["formsListFilterOptions"]["formIds"]) <= 3


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_forms_list_filter_options_with_offset(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Arrange
    await JobSafetyBriefingFactory.persist_many(db_session, 5)

    # Act
    response_with_offset_0 = await execute_gql(
        operation_name="GetFormsListFilterOptions",
        query=test_forms_list_filter_options_query,
        variables={"offset": 0, "limit": 2},
    )
    response_with_offset_2 = await execute_gql(
        operation_name="GetFormsListFilterOptions",
        query=test_forms_list_filter_options_query,
        variables={"offset": 2, "limit": 2},
    )

    # Assert
    assert response_with_offset_0
    assert response_with_offset_2
    assert "formsListFilterOptions" in response_with_offset_0
    assert "formsListFilterOptions" in response_with_offset_2
    assert (
        response_with_offset_0["formsListFilterOptions"]["formIds"]
        != response_with_offset_2["formsListFilterOptions"]["formIds"]
    )
