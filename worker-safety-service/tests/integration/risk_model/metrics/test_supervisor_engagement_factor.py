import datetime
import uuid

import pytest
from faker import Faker

from tests.factories import (
    LocationFactory,
    SupervisorUserFactory,
    TenantFactory,
    WorkPackageFactory,
)
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.models import (
    AsyncSession,
    Observation,
    Supervisor,
    Tenant,
    User,
    WorkPackage,
)
from worker_safety_service.risk_model.metrics.supervisor_engagement_factor import (
    SupervisorEngagementFactor,
)

fake = Faker()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_supervisor_engagement_factor(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    supervisors_manager: SupervisorsManager,
) -> None:
    project: WorkPackage = await WorkPackageFactory.persist(
        db_session, start_date=fake.date_between(start_date="+0d", end_date="+7d")
    )
    await LocationFactory.persist_many(db_session, size=3, project_id=project.id)
    tenant: Tenant = await TenantFactory.persist(db_session)

    user_supervisor: User = await SupervisorUserFactory.persist(db_session)
    supervisor: Supervisor = Supervisor(
        id=user_supervisor.id, external_key=uuid.uuid4().hex, tenant_id=tenant.id
    )
    db_session.add(supervisor)
    await db_session.commit()
    await db_session.refresh(supervisor)
    project.primary_assigned_user_id = supervisor.id

    async def execute_test(
        date: datetime.datetime, expected_supervisor_engagement_factor: float
    ) -> None:
        await SupervisorEngagementFactor(
            metrics_manager, supervisors_manager, supervisor.id
        ).run(date)
        actual = await SupervisorEngagementFactor.load(metrics_manager, supervisor.id)
        assert 0 <= actual.value <= 6
        assert round(expected_supervisor_engagement_factor, 8) == round(actual.value, 8)

    items = [
        dict(date=datetime.datetime(2021, 1, 1), type="Observation"),
        dict(date=datetime.datetime(2021, 1, 10), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 1, 28), type="Observation"),
        dict(date=datetime.datetime(2021, 2, 10), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 2, 10), type="Observation"),
        dict(date=datetime.datetime(2021, 2, 10), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 3, 15), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 3, 30), type="Observation"),
        dict(date=datetime.datetime(2021, 3, 30), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 3, 31), type="Observation"),
        dict(date=datetime.datetime(2021, 4, 1), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 4, 5), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 4, 7), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 4, 7), type="Observation"),
        dict(date=datetime.datetime(2021, 4, 10), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 4, 15), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 4, 18), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 4, 19), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 4, 20), type="Observation"),
        dict(date=datetime.datetime(2021, 4, 21), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 4, 24), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 5, 5), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 5, 5), type="Observation"),
        dict(date=datetime.datetime(2021, 5, 5), type="Observation"),
        dict(date=datetime.datetime(2021, 5, 9), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 5, 9), type="Observation"),
        dict(date=datetime.datetime(2021, 5, 25), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 5, 31), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 6, 30), type="Observation"),
        dict(date=datetime.datetime(2021, 6, 30), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 7, 1), type="Observation"),
        dict(date=datetime.datetime(2021, 7, 3), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 7, 7), type="Observation"),
        dict(date=datetime.datetime(2021, 7, 9), type="Observation"),
        dict(date=datetime.datetime(2021, 7, 10), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 7, 25), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 8, 2), type="Observation"),
        dict(date=datetime.datetime(2021, 8, 4), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 8, 6), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 8, 8), type="Observation"),
        dict(date=datetime.datetime(2021, 8, 10), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 8, 12), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 8, 14), type="Observation"),
        dict(date=datetime.datetime(2021, 8, 16), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 8, 18), type="Observation"),
        dict(date=datetime.datetime(2021, 8, 20), type="Observation"),
        dict(date=datetime.datetime(2021, 8, 22), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 9, 1), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 9, 3), type="Observation"),
        dict(date=datetime.datetime(2021, 9, 5), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 9, 7), type="Observation"),
        dict(date=datetime.datetime(2021, 9, 9), type="Observation"),
        dict(date=datetime.datetime(2021, 9, 11), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 9, 13), type="Observation"),
        dict(date=datetime.datetime(2021, 10, 1), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 10, 1), type="Observation"),
        dict(date=datetime.datetime(2021, 10, 2), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 10, 3), type="Observation"),
        dict(date=datetime.datetime(2021, 10, 5), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 10, 8), type="Observation"),
        dict(date=datetime.datetime(2021, 10, 13), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 10, 21), type="Observation"),
        dict(date=datetime.datetime(2021, 10, 31), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 11, 18), type="Observation"),
        dict(date=datetime.datetime(2021, 11, 19), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 11, 19), type="Observation"),
        dict(date=datetime.datetime(2021, 11, 24), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 11, 24), type="Observation"),
        dict(date=datetime.datetime(2021, 11, 24), type="Observation"),
        dict(date=datetime.datetime(2021, 11, 24), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 11, 28), type="Observation"),
        dict(date=datetime.datetime(2021, 11, 28), type="Observation"),
        dict(date=datetime.datetime(2021, 11, 28), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 11, 29), type="Observation"),
        dict(date=datetime.datetime(2021, 12, 2), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 12, 2), type="Observation"),
        dict(date=datetime.datetime(2021, 12, 2), type="Observation"),
        dict(date=datetime.datetime(2021, 12, 5), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 12, 6), type="Observation"),
        dict(date=datetime.datetime(2021, 12, 7), type="Observation"),
        dict(date=datetime.datetime(2021, 12, 8), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 12, 9), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 12, 10), type="Observation"),
        dict(date=datetime.datetime(2021, 12, 10), type="Observation"),
        dict(date=datetime.datetime(2021, 12, 10), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 12, 13), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2021, 12, 15), type="Observation"),
        dict(date=datetime.datetime(2021, 12, 18), type="Observation"),
        dict(date=datetime.datetime(2021, 12, 19), type="Observation"),
        dict(date=datetime.datetime(2021, 12, 21), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2022, 1, 15), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2022, 1, 20), type="Observation"),
        dict(date=datetime.datetime(2022, 1, 22), type="Observation"),
        dict(date=datetime.datetime(2022, 1, 25), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2022, 1, 26), type="Observation"),
        dict(date=datetime.datetime(2022, 2, 2), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2022, 2, 2), type="Observation"),
        dict(date=datetime.datetime(2022, 2, 2), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2022, 2, 8), type="Observation"),
        dict(date=datetime.datetime(2022, 2, 9), type="Observation"),
        dict(date=datetime.datetime(2022, 2, 16), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2022, 2, 18), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2022, 2, 20), type="Observation"),
        dict(date=datetime.datetime(2022, 2, 21), type="Observation"),
        dict(date=datetime.datetime(2022, 2, 26), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2022, 3, 1), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2022, 3, 2), type="Observation"),
        dict(date=datetime.datetime(2022, 3, 2), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2022, 3, 3), type="Observation"),
        dict(date=datetime.datetime(2022, 3, 4), type="Effective Safety Discussion"),
        dict(date=datetime.datetime(2022, 3, 4), type="Observation"),
    ]
    observations = [
        Observation(
            supervisor_id=supervisor.id,
            contractor_involved_id=None,
            observation_datetime=x["date"],
            observation_type=x["type"],
            observation_id=uuid.uuid4().hex,
            tenant_id=tenant.id,
        )
        for x in items
    ]
    for observation in observations:
        db_session.add(observation)
    await db_session.commit()
    await execute_test(
        datetime.datetime(2021, 5, 15, tzinfo=datetime.timezone.utc), 59 / 12
    )
    await execute_test(
        datetime.datetime(2021, 7, 18, tzinfo=datetime.timezone.utc), 55 / 12
    )
    await execute_test(
        datetime.datetime(2021, 9, 30, tzinfo=datetime.timezone.utc), 46 / 12
    )
    await execute_test(
        datetime.datetime(2021, 10, 1, tzinfo=datetime.timezone.utc), 41 / 12
    )
    await execute_test(
        datetime.datetime(2021, 12, 10, tzinfo=datetime.timezone.utc), 32 / 12
    )
    await execute_test(
        datetime.datetime(2022, 1, 31, tzinfo=datetime.timezone.utc), 27 / 12
    )
    await execute_test(
        datetime.datetime(2022, 2, 28, tzinfo=datetime.timezone.utc), 27 / 12
    )
    await execute_test(
        datetime.datetime(2022, 3, 1, tzinfo=datetime.timezone.utc), 25 / 12
    )
