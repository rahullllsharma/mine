from datetime import datetime, timezone

import pytest

from tests.factories import (
    AdminUserFactory,
    CrewLeaderFactory,
    NatGridJobSafetyBriefingFactory,
    TenantFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.natgrid_job_safety_briefing.helpers import (
    build_natgrid_jsb_data,
    execute_get_last_natgrid_jsb,
    execute_get_natgrid_jsb_by_id,
    execute_get_recently_used_crew_leader,
    execute_save_natgrid_jsb,
)
from worker_safety_service.graphql.types import FormStatus
from worker_safety_service.models import AsyncSession


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_natgrid_jsb_by_id(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    # Arrange
    date = datetime.now(timezone.utc)
    natgrid_jsb = await NatGridJobSafetyBriefingFactory.persist(
        db_session,
        date_for=date,
    )

    # Act
    response = await execute_get_natgrid_jsb_by_id(execute_gql, natgrid_jsb.id)

    # Assert
    assert response["id"] == str(natgrid_jsb.id), response


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_natgrid_jsb_by_id_energy_source_control(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    # Arrange
    natgrid_jsb_request, *_ = await build_natgrid_jsb_data(db_session)
    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_request["energySourceControl"] = {
        "energized": True,
        "deEnergized": True,
        "controls": [{"id": 1, "name": "c1"}],
        "clearanceTypes": {"id": 2, "clearanceTypes": "Clearance Type -1"},
        "pointsOfProtection": [
            {"id": 2, "name": "Reclosers", "details": "Non-reclose device ID 345"},
            {"id": 6, "name": "Switching Limits", "details": "12kv"},
        ],
    }
    jsb_save_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )

    # Act
    jsb_query_response = await execute_get_natgrid_jsb_by_id(
        execute_gql, jsb_save_response["id"]
    )

    # Assert
    assert jsb_save_response["id"] == jsb_query_response["id"]
    assert (
        jsb_query_response["contents"]["energySourceControl"]
        == natgrid_jsb_request["energySourceControl"]
    )


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_natgrid_recent_used_crew(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    =======
    Test that the saveJobSafetyBriefing mutation updated the crew leader will get fetched in recent used crew.
    """
    tenant = await TenantFactory.default_tenant(db_session)
    user = await AdminUserFactory.persist(db_session, tenant_id=tenant.id)
    _ = await CrewLeaderFactory.persist(db_session, tenant_id=tenant.id, name="abc")
    natgrid_jsb_request, *_ = await build_natgrid_jsb_data(db_session)
    status = {"status": FormStatus.PENDING_POST_JOB_BRIEF.name}
    natgrid_jsb_request["crewSignOff"] = {
        "crewSign": {
            "crewDetails": {
                "id": "33a27b72-082a-4397-9b36-1074083c7d7e",
                "name": "abc",
                "email": "abc@urbint.com",
            },
            "discussionConducted": True,
        },
        "multipleCrews": {
            "multipleCrewInvolved": False,
            "crewDiscussion": True,
        },
    }
    await execute_save_natgrid_jsb(
        execute_gql=execute_gql, data=natgrid_jsb_request, status=status, user=user
    )
    recent_used_crew = await execute_get_recently_used_crew_leader(
        execute_gql=execute_gql, user=user
    )
    assert (
        recent_used_crew[0]["name"]
        == natgrid_jsb_request["crewSignOff"]["crewSign"]["crewDetails"]["name"]
    )
    assert (
        recent_used_crew[0]["id"]
        == natgrid_jsb_request["crewSignOff"]["crewSign"]["crewDetails"]["id"]
    )


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_last_natgrid_jsb(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.default_tenant(db_session)
    user = await AdminUserFactory.persist(db_session, tenant_id=tenant.id)
    date = datetime.now(timezone.utc)
    await NatGridJobSafetyBriefingFactory.persist_many(
        db_session, date_for=date, user=user
    )
    natgrid_jsb_request, *_ = await build_natgrid_jsb_data(db_session)
    status = {"status": FormStatus.PENDING_POST_JOB_BRIEF.name}
    result = await execute_save_natgrid_jsb(
        execute_gql=execute_gql, data=natgrid_jsb_request, status=status, user=user
    )
    last_natgrid_jsb = await execute_get_last_natgrid_jsb(
        execute_gql=execute_gql, user=user
    )
    assert result["id"] == last_natgrid_jsb["id"]
    assert result["createdBy"]["id"] == last_natgrid_jsb["createdBy"]["id"]


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_natgrid_jsb_by_id_medical_information_primary_fire_supression_location(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    # Arrange
    natgrid_jsb_request, *_ = await build_natgrid_jsb_data(db_session)
    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_request["medicalInformation"] = {
        "primaryFireSupressionLocation": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "primaryFireSupressionLocationName": "Main Fire Station",
        },
        "customPrimaryFireSupressionLocation": None,
    }

    jsb_save_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )

    # Act
    jsb_query_response = await execute_get_natgrid_jsb_by_id(
        execute_gql, jsb_save_response["id"]
    )

    # Assert
    assert jsb_save_response["id"] == jsb_query_response["id"]
    assert (
        jsb_query_response["contents"]["medicalInformation"]
        == natgrid_jsb_request["medicalInformation"]
    )
    assert (
        jsb_query_response["contents"]["medicalInformation"][
            "primaryFireSupressionLocation"
        ]["id"]
        == "550e8400-e29b-41d4-a716-446655440000"
    )
    assert (
        jsb_query_response["contents"]["medicalInformation"][
            "primaryFireSupressionLocation"
        ]["primaryFireSupressionLocationName"]
        == "Main Fire Station"
    )


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_natgrid_jsb_by_id_medical_information_custom_primary_fire_supression_location(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    # Arrange
    natgrid_jsb_request, *_ = await build_natgrid_jsb_data(db_session)
    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_request["medicalInformation"] = {
        "customPrimaryFireSupressionLocation": {
            "address": "123 Custom Fire Station, Emergency Lane, Safety City, NY 12345",
        },
        "primaryFireSupressionLocation": None,
    }

    jsb_save_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )

    # Act
    jsb_query_response = await execute_get_natgrid_jsb_by_id(
        execute_gql, jsb_save_response["id"]
    )

    # Assert
    assert jsb_save_response["id"] == jsb_query_response["id"]
    assert (
        jsb_query_response["contents"]["medicalInformation"]
        == natgrid_jsb_request["medicalInformation"]
    )
    assert (
        jsb_query_response["contents"]["medicalInformation"][
            "customPrimaryFireSupressionLocation"
        ]["address"]
        == "123 Custom Fire Station, Emergency Lane, Safety City, NY 12345"
    )
