import datetime
import uuid
from datetime import datetime as datetimenow

import pytest
from fastapi.encoders import jsonable_encoder

from tests.db_data import DBData
from tests.factories import EnergyBasedObservationFactory, SupervisorUserFactory
from tests.integration.conftest import ExecuteGQL
from tests.integration.energy_based_observations.helpers import (
    build_custom_ebo_data,
    build_ebo_data,
    execute_complete_ebo,
    execute_delete_ebo,
    execute_reopen_ebo,
    execute_save_ebo,
    execute_update_ebo,
)
from worker_safety_service.graphql.types import FormStatus
from worker_safety_service.models import AsyncSession


@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_energy_based_observation_mutation(
    execute_gql: ExecuteGQL, db_session: AsyncSession, db_data: DBData
) -> None:
    ebo_request = await build_ebo_data(db_session)
    ebo_response = await execute_save_ebo(execute_gql, ebo_request)
    db_ebo = await db_data.ebo(ebo_response["id"])
    ebo_contents = jsonable_encoder(db_ebo.contents)
    ebo_res_contents = jsonable_encoder(ebo_response["contents"])
    assert str(db_ebo.id) == ebo_response["id"]
    assert (
        ebo_contents["additional_information"]
        == ebo_res_contents["additionalInformation"]
    )
    assert (
        ebo_contents["activities"][0]["name"]
        == ebo_res_contents["activities"][0]["name"]
    )
    assert (
        ebo_contents["personnel"][0]["name"] == ebo_res_contents["personnel"][0]["name"]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_energy_based_observation_mutation(
    execute_gql: ExecuteGQL, db_session: AsyncSession, db_data: DBData
) -> None:
    ebo = await EnergyBasedObservationFactory.persist(db_session)
    ebo_data = await build_ebo_data(db_session)
    ebo_request = {"id": ebo.id, "energyBasedObservationInput": ebo_data}
    ebo_response = await execute_update_ebo(execute_gql, ebo_request)
    assert ebo_response["id"] == str(ebo.id)

    db_ebo = await db_data.ebo(ebo_id=ebo.id)

    await db_session.refresh(db_ebo)
    ebo_contents = jsonable_encoder(db_ebo.contents)
    ebo_res_contents = jsonable_encoder(ebo_response["contents"])
    assert str(db_ebo.id) == ebo_response["id"]
    assert (
        ebo_contents["additional_information"]
        == ebo_res_contents["additionalInformation"]
    )
    assert (
        ebo_contents["activities"][0]["name"]
        == ebo_res_contents["activities"][0]["name"]
    )
    assert (
        ebo_contents["personnel"][0]["name"] == ebo_res_contents["personnel"][0]["name"]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_complete_energy_based_observation_mutation(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    # Persist new EBO
    user = await SupervisorUserFactory.persist(db_session)
    ebo = await EnergyBasedObservationFactory.persist(db_session, created_by_id=user.id)
    assert ebo.status == FormStatus.IN_PROGRESS
    assert ebo.contents == {}
    assert ebo.created_by_id == user.id
    assert ebo.completed_by_id is None
    assert ebo.completed_at is None

    # Change Status to Completed
    ebo_contents = await build_ebo_data(db_session)
    ebo_request = {"id": ebo.id, "energyBasedObservationInput": ebo_contents}
    ebo_response = await execute_complete_ebo(execute_gql, ebo_request, user=user)

    assert ebo.id == uuid.UUID(ebo_response["id"])
    assert ebo_response["status"] == "COMPLETE"
    assert ebo_response["completedBy"]["id"] == str(user.id)
    assert ebo_response["completedAt"] is not None
    completed_at = datetime.datetime.fromisoformat(ebo_response["completedAt"])
    assert (
        ebo_contents["additionalInformation"]
        == ebo_response["contents"]["additionalInformation"]
    )
    assert (
        ebo_contents["activities"]["name"]
        == ebo_response["contents"]["activities"][0]["name"]
    )
    assert (
        ebo_contents["personnel"]["name"]
        == ebo_response["contents"]["personnel"][0]["name"]
    )
    await db_session.refresh(ebo)
    assert ebo.status == FormStatus.COMPLETE
    assert ebo.completed_by_id == user.id
    assert ebo.completed_at == completed_at
    assert ebo.archived_at is None
    assert ebo.contents
    assert len(ebo.contents["completions"]) == 1
    assert ebo.contents["completions"][0]["completed_by_id"] == str(user.id)
    assert ebo.contents["completions"][0]["completed_at"] == completed_at.isoformat()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_reopen_energy_based_observation_mutation(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    # Persist new EBO
    user = await SupervisorUserFactory.persist(db_session)
    ebo = await EnergyBasedObservationFactory.persist(db_session, created_by_id=user.id)
    assert ebo.status == FormStatus.IN_PROGRESS
    assert ebo.contents == {}
    assert ebo.created_by_id == user.id
    assert ebo.completed_by_id is None
    assert ebo.completed_at is None

    # Change status to Complete
    ebo_contents = await build_ebo_data(db_session)
    ebo_request = {"id": ebo.id, "energyBasedObservationInput": ebo_contents}
    ebo_response = await execute_complete_ebo(execute_gql, ebo_request, user=user)
    assert ebo_response["status"] == "COMPLETE"
    assert ebo_response["completedBy"]["id"] == str(user.id)
    assert ebo_response["completedAt"] is not None
    completed_at = datetime.datetime.fromisoformat(ebo_response["completedAt"])
    await db_session.refresh(ebo)
    assert ebo.status == FormStatus.COMPLETE
    assert ebo.completed_by_id == user.id
    assert ebo.completed_at == completed_at
    assert ebo.archived_at is None
    assert ebo.contents
    assert len(ebo.contents["completions"]) == 1
    assert ebo.contents["completions"][0]["completed_by_id"] == str(user.id)
    assert ebo.contents["completions"][0]["completed_at"] == completed_at.isoformat()

    # Change status to In Progress
    reopened_ebo = await execute_reopen_ebo(execute_gql, ebo.id)
    assert reopened_ebo["status"] == "IN_PROGRESS"
    assert reopened_ebo["completedBy"]["id"] == str(
        user.id
    )  # still using original user
    assert (
        reopened_ebo["completedAt"] == completed_at.isoformat()
    )  # still using original completed_at
    await db_session.refresh(ebo)
    assert ebo.status == FormStatus.IN_PROGRESS
    assert ebo.completed_by_id == user.id
    assert ebo.completed_at == completed_at
    assert ebo.archived_at is None
    assert ebo.contents
    assert len(ebo.contents["completions"]) == 1
    assert ebo.contents["completions"][0]["completed_by_id"] == str(user.id)
    assert ebo.contents["completions"][0]["completed_at"] == completed_at.isoformat()

    # Change status to Complete
    other_user = await SupervisorUserFactory.persist(db_session)
    ebo_contents = await build_ebo_data(db_session)
    ebo_request = {"id": ebo.id, "energyBasedObservationInput": ebo_contents}
    ebo_response = await execute_complete_ebo(execute_gql, ebo_request, user=other_user)
    assert ebo_response["status"] == "COMPLETE"
    assert ebo_response["completedBy"]["id"] == str(user.id)
    assert ebo_response["completedAt"] == completed_at.isoformat()
    await db_session.refresh(ebo)
    assert ebo.status == FormStatus.COMPLETE
    assert ebo.completed_by_id == user.id
    assert ebo.completed_at == completed_at
    assert ebo.archived_at is None
    assert ebo.contents
    assert len(ebo.contents["completions"]) == 2
    assert ebo.contents["completions"][0]["completed_by_id"] == str(user.id)
    assert ebo.contents["completions"][0]["completed_at"] == completed_at.isoformat()
    assert ebo.contents["completions"][1]["completed_by_id"] == str(other_user.id)
    assert (
        datetime.datetime.fromisoformat(ebo.contents["completions"][1]["completed_at"])
        > completed_at
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_reopen_not_completed_energy_based_observation_mutation(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    ebo_request = await build_ebo_data(db_session)
    ebo_response = await execute_save_ebo(execute_gql, ebo_request)
    ebo_id = ebo_response["id"]
    with pytest.raises(Exception):
        await execute_reopen_ebo(execute_gql, ebo_id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_energy_based_observation_mutation(
    execute_gql: ExecuteGQL, db_session: AsyncSession, db_data: DBData
) -> None:
    ebo = await EnergyBasedObservationFactory.persist(db_session)
    ebo_response = await execute_delete_ebo(execute_gql, ebo.id)

    assert ebo_response is True

    data_ebo = await db_data.ebo(ebo.id)

    await db_session.refresh(data_ebo)

    assert data_ebo.archived_at is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_success_heca_calculation_energy_based_observation_mutation(
    execute_gql: ExecuteGQL, db_session: AsyncSession, db_data: DBData
) -> None:
    ebo = await EnergyBasedObservationFactory.persist(db_session)
    ebo_contents = await build_custom_ebo_data(db_session)
    ebo_request = {"id": ebo.id, "energyBasedObservationInput": ebo_contents}
    ebo_response = await execute_complete_ebo(execute_gql, ebo_request)

    assert ebo.id == uuid.UUID(ebo_response["id"])
    assert ebo_response["status"] == "COMPLETE"
    assert ebo_response["contents"]["highEnergyTasks"][0]["hecaScoreTask"] == "Success"
    assert (
        ebo_response["contents"]["highEnergyTasks"][0]["hecaScoreTaskPercentage"]
        == 100.0
    )
    assert (
        ebo_response["contents"]["highEnergyTasks"][0]["hazards"][0]["hecaScoreHazard"]
        == "Success"
    )
    assert (
        ebo_response["contents"]["highEnergyTasks"][0]["hazards"][0][
            "hecaScoreHazardPercentage"
        ]
        == 100
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_success_and_exposure_heca_calculation_energy_based_observation_mutation(
    execute_gql: ExecuteGQL, db_session: AsyncSession, db_data: DBData
) -> None:
    ebo = await EnergyBasedObservationFactory.persist(db_session)
    ebo_contents = await build_custom_ebo_data(
        db_session, direct_controls_implemented=False
    )
    ebo_request = {"id": ebo.id, "energyBasedObservationInput": ebo_contents}
    ebo_response = await execute_complete_ebo(execute_gql, ebo_request)

    assert ebo.id == uuid.UUID(ebo_response["id"])
    assert ebo_response["status"] == "COMPLETE"
    assert (
        ebo_response["contents"]["highEnergyTasks"][0]["hecaScoreTask"]
        == "Success + Exposure"
    )
    assert (
        ebo_response["contents"]["highEnergyTasks"][0]["hecaScoreTaskPercentage"] == 0
    )
    assert (
        ebo_response["contents"]["highEnergyTasks"][0]["hazards"][0]["hecaScoreHazard"]
        == "Success + Exposure"
    )
    assert (
        ebo_response["contents"]["highEnergyTasks"][0]["hazards"][0][
            "hecaScoreHazardPercentage"
        ]
        == 0
    )


# Test to check appVersion and sourceInfo is captured
@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_energy_based_observation_mutation_with_sourceInfo(
    execute_gql: ExecuteGQL, db_session: AsyncSession, db_data: DBData
) -> None:
    ebo_request = await build_ebo_data(db_session)
    ebo_response = await execute_save_ebo(execute_gql, ebo_request)
    db_ebo = await db_data.ebo(ebo_response["id"])
    assert str(db_ebo.id) == ebo_response["id"]
    assert ebo_response["contents"]["sourceInfo"]["appVersion"] == "V2.0.0"
    assert ebo_response["contents"]["sourceInfo"]["sourceInformation"] == "WEB_PORTAL"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_form_id_generation_save_energy_based_observation_mutation(
    execute_gql: ExecuteGQL, db_session: AsyncSession, db_data: DBData
) -> None:
    ebo_ids = []
    for _ in range(3):
        ebo_request = await build_ebo_data(db_session)
        ebo_response = await execute_save_ebo(execute_gql, ebo_request)
        ebo_ids.append(ebo_response["id"])

    year_month = datetimenow.now().strftime("%y%m")
    for i, ebo_id in enumerate(ebo_ids, start=1):
        expected_form_id = f"{year_month}{i:05}"
        db_ebo = await db_data.ebo(ebo_id)
        assert db_ebo.form_id == expected_form_id
