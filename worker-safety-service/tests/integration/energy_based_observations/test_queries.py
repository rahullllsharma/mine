from datetime import datetime, timezone

import pytest

from tests.factories import EnergyBasedObservationFactory, SupervisorUserFactory
from tests.integration.conftest import ExecuteGQL
from tests.integration.energy_based_observations.helpers import (
    build_ebo_data,
    execute_complete_ebo,
    execute_get_ebo_by_id,
    execute_reopen_ebo,
)
from worker_safety_service.models import AsyncSession


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_ebo_by_id(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    date = datetime.now(timezone.utc)
    ebo = await EnergyBasedObservationFactory.persist(
        db_session,
        date_for=date,
    )

    ebo_by_id = await execute_get_ebo_by_id(execute_gql, ebo.id)

    assert ebo_by_id["id"] == str(ebo.id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_energy_based_observation_completions(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Assert
    user = await SupervisorUserFactory.persist(db_session)
    other_user = await SupervisorUserFactory.persist(db_session)
    ebo = await EnergyBasedObservationFactory.persist(db_session)
    ebo_contents = await build_ebo_data(db_session)
    ebo_request = {"id": ebo.id, "energyBasedObservationInput": ebo_contents}
    await execute_complete_ebo(execute_gql, ebo_request, user=user)
    await db_session.refresh(ebo)
    completed_at = ebo.completed_at
    await execute_reopen_ebo(execute_gql, ebo.id)
    await execute_complete_ebo(execute_gql, ebo_request, user=user)
    await execute_reopen_ebo(execute_gql, ebo.id)
    await execute_complete_ebo(execute_gql, ebo_request, user=other_user)

    # Act
    response = await execute_get_ebo_by_id(execute_gql, ebo.id)

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
