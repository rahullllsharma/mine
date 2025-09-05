import datetime
import uuid
from datetime import datetime as datetimenow

import pytest

from tests.db_data import DBData
from tests.factories import TenantFactory, WorkTypeFactory
from tests.integration.conftest import ExecuteGQL
from tests.integration.natgrid_job_safety_briefing.helpers import (
    build_natgrid_jsb_data,
    build_natgrid_jsb_data_with_additional_comments_and_dig_safe,
    build_natgrid_jsb_data_with_barn_location,
    build_natgrid_jsb_data_with_critical_task_and_job_description,
    build_natgrid_jsb_data_with_general_reference_materials,
    build_natgrid_jsb_data_with_historic_incidents,
    build_natgrid_jsb_data_without_date,
    build_natgrid_jsb_for_checking_backward_compatibility,
    build_natgrid_jsb_with_multilocation_field,
    execute_delete_natgrid_jsb,
    execute_reopen_natgrid_jsb,
    execute_save_natgrid_jsb,
)
from worker_safety_service.constants import GeneralConstants
from worker_safety_service.graphql.types import FormStatus
from worker_safety_service.models import AsyncSession, NatGridJobSafetyBriefingLayout


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_natgrid_job_safety_briefing_mutation(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation creates a new natgrid job safety briefing.
    """
    natgrid_jsb_request, *_ = await build_natgrid_jsb_data(db_session)
    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )
    natgrid_db_jsb = await db_data.natgrid_jsb(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.id == uuid.UUID(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.status == FormStatus.IN_PROGRESS


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_natgrid_job_safety_briefing_mutation_work_type_link(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation creates a new natgrid job safety briefing and links to ngjsb worktype.
    """
    work_type = await db_data.get_natgrid_jsb_work_type()

    tenant, admin = await TenantFactory.new_with_admin(db_session)
    tenant_id = tenant.id

    # If else is to avoid a scenario where work_type already exists
    # Using same tenant_id(in real scenario that should be from auth realm natgrid) as
    # graphql request is using this tenant when authenticating user
    if work_type:
        await db_data.update_natgrid_jsb_work_type(tenant_id)
        work_type = work_type[0]
    else:
        work_type = await WorkTypeFactory.persist(
            db_session,
            tenant_id=tenant_id,
            code=GeneralConstants.NATGRID_GENERIC_JSB_CODE,
        )

    natgrid_jsb_request, *_ = await build_natgrid_jsb_data(db_session)
    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status, user=admin
    )
    natgrid_db_jsb = await db_data.natgrid_jsb(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.id == uuid.UUID(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.status == FormStatus.IN_PROGRESS
    assert natgrid_db_jsb.work_type_id == work_type.id
    #
    natgrid_jsb_request, *_ = await build_natgrid_jsb_data(db_session)
    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status, user=admin
    )
    natgrid_db_jsb = await db_data.natgrid_jsb(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.id == uuid.UUID(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.status == FormStatus.IN_PROGRESS
    assert natgrid_db_jsb.work_type_id == work_type.id


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_natgrid_job_safety_briefing_mutation_without_date(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation creates a new natgrid job safety briefing
    when no date is provided.
    """
    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_request, *_ = await build_natgrid_jsb_data_without_date(db_session)
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )

    assert natgrid_jsb_response["id"] is not None

    natgrid_db_jsb = await db_data.natgrid_jsb(natgrid_jsb_response["id"])

    assert natgrid_db_jsb.id == uuid.UUID(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.date_for == datetime.date.today()
    assert natgrid_db_jsb.status == FormStatus.IN_PROGRESS


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_natgrid_job_safety_briefing_mutation_with_energy_control_options(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    # Arrange
    natgrid_jsb_request, *_ = await build_natgrid_jsb_data(db_session)
    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_request["energySourceControl"] = {
        "energized": True,
        "deEnergized": True,
        "controls": [{"id": 1, "name": "c1"}],
        "clearanceTypes": {"id": 2, "clearanceTypes": "Clearance Type -1"},
    }

    # Act
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )

    # Assert
    natgrid_db_jsb = await db_data.natgrid_jsb(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.id == uuid.UUID(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.status == FormStatus.IN_PROGRESS
    assert natgrid_db_jsb.contents, natgrid_db_jsb.contents
    assert "energy_source_control" in natgrid_db_jsb.contents, natgrid_db_jsb.contents
    assert (
        natgrid_db_jsb.contents["energy_source_control"]["energized"] is True
    ), natgrid_db_jsb.contents
    assert (
        natgrid_db_jsb.contents["energy_source_control"]["de_energized"] is True
    ), natgrid_db_jsb.contents


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_natgrid_job_safety_briefing_mutation_with_energy_control_options_defaults(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    # Arrange
    natgrid_jsb_request, *_ = await build_natgrid_jsb_data(db_session)
    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_request["energySourceControl"] = {
        "controls": [{"id": 1, "name": "c1"}],
        "clearanceTypes": {"id": 2, "clearanceTypes": "Clearance Type -1"},
    }

    # Act
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )

    # Assert
    natgrid_db_jsb = await db_data.natgrid_jsb(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.id == uuid.UUID(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.status == FormStatus.IN_PROGRESS
    assert natgrid_db_jsb.contents, natgrid_db_jsb.contents
    assert "energy_source_control" in natgrid_db_jsb.contents, natgrid_db_jsb.contents
    assert (
        natgrid_db_jsb.contents["energy_source_control"]["energized"] is False
    ), natgrid_db_jsb.contents
    assert (
        natgrid_db_jsb.contents["energy_source_control"]["de_energized"] is False
    ), natgrid_db_jsb.contents


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_natgrid_job_safety_briefing(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    status = {"status": FormStatus.COMPLETE.name}
    natgrid_jsb_request, *_ = await build_natgrid_jsb_data(db_session)
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )
    jsb_id = natgrid_jsb_response["id"]
    delete_result = await execute_delete_natgrid_jsb(execute_gql, jsb_id)

    assert delete_result is True

    natgrid_db_jsb = await db_data.natgrid_jsb(jsb_id)

    assert natgrid_db_jsb.archived_at is not None


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_natgrid_job_safety_briefing_briefing_date_time(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation updates the expected fields and tables
    when changing the briefingDateTime.
    """
    natgrid_jsb_request, *_ = await build_natgrid_jsb_data_without_date(db_session)
    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )
    natgrid_jsb_request["jsbId"] = natgrid_jsb_response["id"]
    date = str(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    )
    natgrid_jsb_request["jsbMetadata"] = {"briefingDateTime": date}
    updated_natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )

    db_jsb = await db_data.natgrid_jsb(updated_natgrid_jsb_response["id"])
    contents = NatGridJobSafetyBriefingLayout.parse_obj(db_jsb.contents)

    assert contents.jsb_metadata
    assert str(contents.jsb_metadata.briefing_date_time) == date
    assert contents.jsb_metadata.briefing_date_time.date() == db_jsb.date_for


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_natgrid_job_safety_briefing_critical_task_selection_with_job_description(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation updates the expected fields and tables
    when adding critical tasks with job desc and will fail if not provided .
    """
    (
        natgrid_jsb_request,
        *_,
    ) = await build_natgrid_jsb_data_with_critical_task_and_job_description(db_session)
    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )
    natgrid_jsb_request["jsbId"] = natgrid_jsb_response["id"]

    updated_natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )

    db_jsb = await db_data.natgrid_jsb(updated_natgrid_jsb_response["id"])
    contents = NatGridJobSafetyBriefingLayout.parse_obj(db_jsb.contents)
    assert contents.critical_tasks_selections
    assert (
        natgrid_jsb_request["criticalTasksSelections"]["jobDescription"]
        == contents.critical_tasks_selections.job_description
    )


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_natgrid_job_safety_briefing_with_dig_safe_and_additional_comments(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation updates the expected fields and tables
    when adding dig safe and other side conditions and comments.
    """
    (
        natgrid_jsb_request,
        *_,
    ) = await build_natgrid_jsb_data_with_additional_comments_and_dig_safe(db_session)
    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )
    natgrid_jsb_request["jsbId"] = natgrid_jsb_response["id"]

    updated_natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )
    db_jsb = await db_data.natgrid_jsb(updated_natgrid_jsb_response["id"])
    contents = NatGridJobSafetyBriefingLayout.parse_obj(db_jsb.contents)
    assert contents.site_conditions
    assert contents.site_conditions.additional_comments
    assert contents.site_conditions.site_condition_selections
    assert contents.site_conditions.dig_safe

    assert (
        contents.site_conditions.additional_comments
        == natgrid_jsb_request["siteConditions"]["additionalComments"]
    )
    assert (
        contents.site_conditions.dig_safe
        == natgrid_jsb_request["siteConditions"]["digSafe"]
    )


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_natgrid_job_safety_briefing_with_historical_incidents(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation updates the expected fields and tables
    when adding new format fo historical incidents.
    """
    (
        natgrid_jsb_request,
        *_,
    ) = await build_natgrid_jsb_data_with_historic_incidents(db_session)
    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )
    natgrid_jsb_request["jsbId"] = natgrid_jsb_response["id"]

    updated_natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )
    db_jsb = await db_data.natgrid_jsb(updated_natgrid_jsb_response["id"])
    contents = NatGridJobSafetyBriefingLayout.parse_obj(db_jsb.contents)
    assert contents.task_historic_incidents
    assert len(contents.task_historic_incidents) == 1
    assert (
        contents.task_historic_incidents[0].id
        == natgrid_jsb_request["taskHistoricIncidents"][0]["id"]
    )


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_natgrid_job_safety_briefing_with_general_reference_materials(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation updates the expected fields and tables
    when adding general_reference_materials.
    """
    (
        natgrid_jsb_request,
        *_,
    ) = await build_natgrid_jsb_data_with_general_reference_materials(db_session)
    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )
    natgrid_jsb_request["jsbId"] = natgrid_jsb_response["id"]

    updated_natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )
    db_jsb = await db_data.natgrid_jsb(updated_natgrid_jsb_response["id"])
    contents = NatGridJobSafetyBriefingLayout.parse_obj(db_jsb.contents)
    assert contents.general_reference_materials

    assert (
        contents.general_reference_materials
        == natgrid_jsb_request["generalReferenceMaterials"]
    )


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_reopen_natgrid_job_safety_briefing_mutation(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation creates a new natgrid job safety briefing.
    """
    natgrid_jsb_request, *_ = await build_natgrid_jsb_data(db_session)
    status = {"status": FormStatus.COMPLETE.name}
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )
    natgrid_db_jsb = await db_data.natgrid_jsb(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.id == uuid.UUID(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.status == FormStatus.COMPLETE
    jsb_id = natgrid_jsb_response["id"]
    reopen_form = await execute_reopen_natgrid_jsb(execute_gql, jsb_id)
    assert reopen_form["status"] == "PENDING_SIGN_OFF"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_form_id_generation_save_natgrid_job_safety_briefing_mutation(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that form_id is getting generated for the saveJobSafetyBriefing mutation while creating a new job safety briefing.
    """
    natgrid_jsb_ids = []
    current_datetime = datetimenow.now()
    year_month = current_datetime.strftime("%y%m")

    for i in range(4):
        natgrid_jsb_request, *_ = await build_natgrid_jsb_data(db_session)
        status = {"status": FormStatus.IN_PROGRESS.name}
        natgrid_jsb_response = await execute_save_natgrid_jsb(
            execute_gql, natgrid_jsb_request, status
        )
        natgrid_jsb_ids.append(natgrid_jsb_response["id"])

    for i, natgrid_jsb_id in enumerate(natgrid_jsb_ids, start=1):
        expected_form_id = f"{year_month}{i:05}"
        db_jsb = await db_data.natgrid_jsb(natgrid_jsb_id)
        assert db_jsb.form_id == expected_form_id


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_completion_date_natgrid_jsb(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    =======
    Test that the saveJobSafetyBriefing mutation updated the completion date in contents and completedAt
    CompletedAt will be updated only at first completion and if we have reopen and user completed the form.
    It will go inside Completion of NatGrid JSB Contents.
    """
    natgrid_jsb_request, *_ = await build_natgrid_jsb_data(db_session)
    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )
    natgrid_jsb_request["jsbId"] = natgrid_jsb_response["id"]
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
    natgrid_jsb_request["energySourceControl"] = {
        "clearanceNumber": "test-num",
        "clearanceTypes": {"id": 1, "clearanceTypes": "Clearance Type -2"},
        "energized": False,
        "controls": [
            {
                "id": 1,
                "name": "Control 1",
            },
            {
                "id": 2,
                "name": "Control 2",
            },
        ],
    }
    updated_status = {"status": FormStatus.COMPLETE.name}

    updated_natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, updated_status
    )

    db_jsb = await db_data.natgrid_jsb(updated_natgrid_jsb_response["id"])

    contents = NatGridJobSafetyBriefingLayout.parse_obj(db_jsb.contents)
    completed_at = datetime.datetime.fromisoformat(
        updated_natgrid_jsb_response["completedAt"]
    )

    assert contents.jsb_metadata
    assert updated_natgrid_jsb_response["completedAt"] == completed_at.isoformat()
    assert len(updated_natgrid_jsb_response["contents"]["completions"]) == 1
    assert db_jsb.contents is not None
    assert "energy_source_control" in db_jsb.contents
    assert "clearance_number" in db_jsb.contents["energy_source_control"]
    assert "clearance_types" in db_jsb.contents["energy_source_control"]
    assert contents.jsb_metadata.briefing_date_time.date() == db_jsb.date_for
    natgrid_jsb_request["crewSignOff"] = {
        "crewSign": {
            "crewDetails": {
                "id": "33a27b72-082a-4397-9b36-1074083c7d7e",
                "name": "abc",
                "email": "abc@urbint.com",
            },
            "otherCrewDetails": "Test User",
            "discussionConducted": True,
        },
        "multipleCrews": {
            "multipleCrewInvolved": False,
            "crewDiscussion": True,
        },
    }
    natgrid_jsb_request["energySourceControl"] = {
        "clearanceNumber": "test-num",
        "clearanceTypes": {"id": 2, "clearanceTypes": "Clearance Type -1"},
        "energized": False,
        "controls": [
            {
                "id": 1,
                "name": "Control 1",
            },
            {
                "id": 2,
                "name": "Control 2",
            },
        ],
    }

    updated_status = {"status": FormStatus.COMPLETE.name}

    updated_natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, updated_status
    )

    db_jsb = await db_data.natgrid_jsb(updated_natgrid_jsb_response["id"])
    contents = NatGridJobSafetyBriefingLayout.parse_obj(db_jsb.contents)
    assert updated_natgrid_jsb_response["completedAt"] == completed_at.isoformat()
    assert len(updated_natgrid_jsb_response["contents"]["completions"]) == 2
    assert db_jsb.contents is not None
    assert "energy_source_control" in db_jsb.contents
    assert "clearance_number" in db_jsb.contents["energy_source_control"]
    assert "clearance_types" in db_jsb.contents["energy_source_control"]


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_natgrid_jsb_mutation_hazard_controls(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation updates hazards and controls sections.
    """
    natgrid_jsb_request, *_ = await build_natgrid_jsb_data(db_session)
    energy_types_data = ["Electrical", "Motion", "Mechanical"]
    natgrid_jsb_request["hazardsControl"] = {
        "energyTypes": energy_types_data,
        "manuallyAddedHazards": {
            "highEnergyHazards": {
                "id": uuid.uuid4(),
                "controls": {
                    "controls": [
                        {
                            "id": "1",
                            "name": "test control",
                        }
                    ]
                },
                "controlsImplemented": True,
            }
        },
        "additionalComments": "test comments",
    }

    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )
    db_jsb = await db_data.natgrid_jsb(natgrid_jsb_response["id"])
    contents = NatGridJobSafetyBriefingLayout.parse_obj(db_jsb.contents)
    hazards_control = contents.hazards_control
    if hazards_control is not None:
        assert hazards_control.additional_comments == "test comments"
        assert hazards_control.manually_added_hazards is not None

        if hazards_control.manually_added_hazards.high_energy_hazards:
            assert (
                hazards_control.manually_added_hazards.high_energy_hazards[
                    0
                ].controls_implemented
                is True
            )
    assert db_jsb.contents
    assert (
        natgrid_jsb_response["contents"]["hazardsControl"]["energyTypes"]
        == energy_types_data
    )


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_natgrid_jsb_mutation_hazard_controls_with_user_created_hazard(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test that the saveJobSafetyBriefing mutation updates hazards and controls sections.
    """
    natgrid_jsb_request, *_ = await build_natgrid_jsb_data(db_session)
    energy_types_data = ["Electrical"]
    natgrid_jsb_request["hazardsControl"] = {
        "energyTypes": energy_types_data,
        "customHazards": {
            "lowEnergyHazards": {
                "id": uuid.uuid4(),
                "name": "test hazard",
                "energyTypes": "Electrical",
                "controls": {
                    "controls": [
                        {
                            "id": "1",
                            "name": "test control",
                        }
                    ]
                },
                "customControls": {
                    "controls": [
                        {
                            "id": "2",
                            "name": "test control 2",
                        }
                    ]
                },
                "controlsImplemented": True,
            }
        },
        "additionalComments": "test comments",
    }

    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )
    db_jsb = await db_data.natgrid_jsb(natgrid_jsb_response["id"])
    contents = NatGridJobSafetyBriefingLayout.parse_obj(db_jsb.contents)
    hazards_control = contents.hazards_control
    if hazards_control is not None:
        assert hazards_control.additional_comments == "test comments"
        assert hazards_control.custom_hazards is not None

        if hazards_control.custom_hazards.low_energy_hazards:
            assert (
                hazards_control.custom_hazards.low_energy_hazards[
                    0
                ].controls_implemented
                is True
            )
    assert db_jsb.contents
    assert (
        natgrid_jsb_response["contents"]["hazardsControl"]["energyTypes"]
        == energy_types_data
    )


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_natgrid_job_safety_briefing_mutation_with_energy_control_points_of_protection(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    # Arrange
    natgrid_jsb_request, *_ = await build_natgrid_jsb_data(db_session)
    status = {"status": FormStatus.IN_PROGRESS.name}
    points_of_protection = [
        {"id": 2, "name": "Reclosers", "details": "Non-reclose device ID 345"},
        {"id": 6, "name": "Switching Limits", "details": "12kv"},
    ]
    natgrid_jsb_request["energySourceControl"] = {
        "energized": False,
        "controls": [],
        "pointsOfProtection": points_of_protection,
        "clearanceTypes": {"id": 2, "clearanceTypes": "Clearance Type -1"},
    }

    # Act
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )

    # Assert
    natgrid_db_jsb = await db_data.natgrid_jsb(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.id == uuid.UUID(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.status == FormStatus.IN_PROGRESS
    assert natgrid_db_jsb.contents, natgrid_db_jsb.contents
    assert "energy_source_control" in natgrid_db_jsb.contents, natgrid_db_jsb.contents
    assert (
        natgrid_db_jsb.contents["energy_source_control"]["points_of_protection"]
        == points_of_protection
    )


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_creating_ngjsb_with_crew_sign_off_with_creator_sign(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    =======
    Test to check for adding creator_sign in natgrid_jsb and validate creation
    """
    natgrid_jsb_request, *_ = await build_natgrid_jsb_data(db_session)
    status = {"status": FormStatus.PENDING_SIGN_OFF.name}
    natgrid_jsb_request["crewSignOff"] = {
        "crewSign": {
            "crewDetails": {
                "id": "33a27b72-082a-4397-9b36-1074083c7d7e",
                "name": "abc",
                "email": "abc@urbint.com",
            },
            "discussionConducted": True,
        },
        "creatorSign": {
            "crewDetails": {
                "id": "8823f568-67f0-4265-bb86-ff8192d39849",
                "name": "abcd",
                "email": "abcd@urbint.com",
            },
            "discussionConducted": True,
        },
        "multipleCrews": {
            "multipleCrewInvolved": False,
            "crewDiscussion": True,
        },
    }
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )
    natgrid_db_jsb = await db_data.natgrid_jsb(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.contents
    assert natgrid_db_jsb.contents["crew_sign_off"]
    assert (
        natgrid_jsb_request["crewSignOff"]["creatorSign"]["crewDetails"]["name"]
        == natgrid_db_jsb.contents["crew_sign_off"]["creator_sign"]["crew_details"][
            "name"
        ]
    )
    assert (
        natgrid_jsb_request["crewSignOff"]["creatorSign"]["crewDetails"]["id"]
        == natgrid_db_jsb.contents["crew_sign_off"]["creator_sign"]["crew_details"][
            "id"
        ]
    )


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_jsb_with_group_discussion_page_filled(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    =======
    Test to check for adding creator_sign in natgrid_jsb and validate creation
    """
    (
        natgrid_jsb,
        *_,
    ) = await build_natgrid_jsb_data_with_critical_task_and_job_description(db_session)
    status = {"status": FormStatus.PENDING_SIGN_OFF.name}
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb, status
    )
    natgrid_jsb_request = {}
    natgrid_jsb_request["groupDiscussion"] = {
        "viewed": True,
        "groupDiscussionNotes": "Test",
    }
    natgrid_jsb_request["jsbId"] = natgrid_jsb_response["id"]
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb_request, status
    )
    natgrid_db_jsb = await db_data.natgrid_jsb(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.contents
    assert (
        natgrid_db_jsb.contents["critical_tasks_selections"][
            "special_precautions_notes"
        ]
        == natgrid_jsb_request["groupDiscussion"]["groupDiscussionNotes"]
    )


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_ngjsb_with_new_work_location_field(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    =======
    Test to check for adding creator_sign in natgrid_jsb and validate creation
    """
    (
        natgrid_jsb,
        *_,
    ) = await build_natgrid_jsb_with_multilocation_field(db_session)
    status = {"status": FormStatus.PENDING_SIGN_OFF.name}
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb, status
    )
    natgrid_db_jsb = await db_data.natgrid_jsb(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.contents
    assert natgrid_db_jsb.contents["work_location_with_voltage_info"]


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_ngjsb_with_new_work_location_field_backward_compatibilty(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    =======
    Test to check for adding creator_sign in natgrid_jsb and validate creation
    """
    (
        natgrid_jsb,
        *_,
    ) = await build_natgrid_jsb_for_checking_backward_compatibility(db_session)
    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb, status
    )
    natgrid_db_jsb = await db_data.natgrid_jsb(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.contents
    assert natgrid_db_jsb.contents["work_location_with_voltage_info"]


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_ngjsb_with_barn_location(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    =======
    Test to check for adding barn_location in natgrid_jsb and validate creation
    """
    (
        natgrid_jsb,
        *_,
    ) = await build_natgrid_jsb_data_with_barn_location(db_session)
    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb, status
    )
    natgrid_db_jsb = await db_data.natgrid_jsb(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.contents
    assert natgrid_db_jsb.contents["barn_location"] is not None
    assert natgrid_db_jsb.contents["barn_location"]["id"] is not None
    assert natgrid_db_jsb.contents["barn_location"]["name"] == "test Barn Location"


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_ngjsb_with_medical_information_primary_fire_supression_location(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test to check for adding medical_information with primary_fire_supression_location
    in natgrid_jsb and validate creation.
    """
    (
        natgrid_jsb,
        *_,
    ) = await build_natgrid_jsb_data(db_session)

    # Add medical information with primary fire suppression location
    natgrid_jsb["medicalInformation"] = {
        "primaryFireSupressionLocation": {
            "id": str(uuid.uuid4()),
            "primaryFireSupressionLocationName": "Main Fire Station",
        },
        "customPrimaryFireSupressionLocation": None,
    }

    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb, status
    )

    natgrid_db_jsb = await db_data.natgrid_jsb(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.contents
    assert natgrid_db_jsb.contents["medical_information"] is not None
    assert (
        natgrid_db_jsb.contents["medical_information"][
            "primary_fire_supression_location"
        ]
        is not None
    )
    assert (
        natgrid_db_jsb.contents["medical_information"][
            "primary_fire_supression_location"
        ]["id"]
        is not None
    )
    assert (
        natgrid_db_jsb.contents["medical_information"][
            "primary_fire_supression_location"
        ]["primary_fire_supression_location_name"]
        == "Main Fire Station"
    )


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_ngjsb_with_medical_information_custom_primary_fire_supression_location(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Test to check for adding medical_information with custom_primary_fire_supression_location
    in natgrid_jsb and validate creation.
    """
    (
        natgrid_jsb,
        *_,
    ) = await build_natgrid_jsb_data(db_session)

    # Add medical information with custom primary fire suppression location
    natgrid_jsb["medicalInformation"] = {
        "customPrimaryFireSupressionLocation": {
            "address": "123 Custom Fire Station, Emergency Lane, Safety City, NY 12345",
        },
        "primaryFireSupressionLocation": None,
    }

    status = {"status": FormStatus.IN_PROGRESS.name}
    natgrid_jsb_response = await execute_save_natgrid_jsb(
        execute_gql, natgrid_jsb, status
    )

    natgrid_db_jsb = await db_data.natgrid_jsb(natgrid_jsb_response["id"])
    assert natgrid_db_jsb.contents
    assert natgrid_db_jsb.contents["medical_information"] is not None
    assert (
        natgrid_db_jsb.contents["medical_information"][
            "custom_primary_fire_supression_location"
        ]
        is not None
    )
    assert (
        natgrid_db_jsb.contents["medical_information"][
            "custom_primary_fire_supression_location"
        ]["address"]
        == "123 Custom Fire Station, Emergency Lane, Safety City, NY 12345"
    )
