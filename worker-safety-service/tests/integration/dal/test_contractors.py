import pendulum
import pytest
from faker import Faker

from tests.factories import ContractorFactory
from worker_safety_service.dal.contractors import ContractorHistory, ContractorsManager
from worker_safety_service.models import AsyncSession, Observation

# TODO: Improve these tests!!!


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_contractor_history(
    db_session: AsyncSession,
    contractor_manager: ContractorsManager,
) -> None:
    contractor = await ContractorFactory.persist(db_session)

    fake = Faker()
    now = pendulum.now(tz="UTC")

    _dates = [
        fake.date_time_between(start_date=now.subtract(years=5), end_date=now)
        for _ in range(0, 5)
    ]
    _dates.extend(
        [
            fake.date_time_between(end_date=now.subtract(days=1, years=5))
            for _ in range(0, 3)
        ]
    )

    for _date in _dates:
        o = Observation(
            contractor_involved_id=contractor.id,
            observation_datetime=_date,
            observation_id="",
            tenant_id=contractor.tenant_id,
        )
        db_session.add(o)
    await db_session.commit()

    c_hist = await contractor_manager.get_contractor_history(
        contractor_id=contractor.id
    )
    assert c_hist == ContractorHistory(n_safety_observations=5, n_action_items=0)
