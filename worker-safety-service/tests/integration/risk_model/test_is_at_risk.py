import asyncio
from typing import Awaitable, Callable, Literal
from uuid import UUID

import pytest

from tests.factories import (
    ContractorFactory,
    CrewFactory,
    SupervisorFactory,
    TenantFactory,
)
from tests.integration.helpers import update_configuration
from worker_safety_service.dal.configurations import ACTIVITY_CONFIG
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models import AsyncSession
from worker_safety_service.risk_model.is_at_risk import (
    is_contractor_at_risk,
    is_crew_at_risk,
    is_supervisor_at_risk,
)
from worker_safety_service.risk_model.metrics.contractor.contractor_safety_score import (
    ContractorSafetyScore,
)
from worker_safety_service.risk_model.metrics.contractor.global_contractor_safety_score import (
    GlobalContractorSafetyScore,
)
from worker_safety_service.risk_model.metrics.crew.crew_relative_precursor_risk import (
    CrewRelativePrecursorRisk,
)
from worker_safety_service.risk_model.metrics.crew.global_crew_relative_precursor_risk import (
    GlobalCrewRelativePrecursorRisk,
)
from worker_safety_service.risk_model.metrics.global_supervisor_enganement_factor import (
    GlobalSupervisorEngagementFactor,
)
from worker_safety_service.risk_model.metrics.supervisor_engagement_factor import (
    SupervisorEngagementFactor,
)


def _assert_all_false(values: list[bool], length: int) -> None:
    assert len(values) == length
    for el in values:
        assert el is False


async def _is_at_risk(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    person_type: Literal["Contractor", "Supervisor", "Crew"],
) -> None:
    """
    Initial Set Up

    Setting up typing and assigning based on the 'person_type' argument value
    """
    factory: type[ContractorFactory] | type[SupervisorFactory] | type[CrewFactory]
    global_score: type[GlobalContractorSafetyScore] | type[
        GlobalSupervisorEngagementFactor
    ] | type[GlobalCrewRelativePrecursorRisk]
    base_score: type[ContractorSafetyScore] | type[SupervisorEngagementFactor] | type[
        CrewRelativePrecursorRisk
    ]
    is_at_risk_metric: Callable[
        [RiskModelMetricsManager, list[UUID]], Awaitable[list[bool]]
    ]

    if person_type == "Contractor":
        factory = ContractorFactory
        global_score = GlobalContractorSafetyScore
        base_score = ContractorSafetyScore
        is_at_risk_metric = is_contractor_at_risk
    elif person_type == "Crew":
        factory = CrewFactory
        global_score = GlobalCrewRelativePrecursorRisk
        base_score = CrewRelativePrecursorRisk
        is_at_risk_metric = is_crew_at_risk
    else:
        factory = SupervisorFactory
        global_score = GlobalSupervisorEngagementFactor
        base_score = SupervisorEngagementFactor
        is_at_risk_metric = is_supervisor_at_risk

    """
    Variable instantiation

    This creates 3 tenants, as well as some contractors/supervisors that _will_
    be used, and some that won't be used.
    """
    tenants = await TenantFactory.persist_many(db_session, size=3)
    persons = await factory.persist_many(db_session, tenant_id=tenants[0].id, size=6)
    extra_tenant_1 = await factory.persist_many(
        db_session, tenant_id=tenants[1].id, size=7
    )
    extra_tenant_2 = await factory.persist_many(
        db_session, tenant_id=tenants[2].id, size=8
    )

    if person_type == "Crew":
        for tenant in tenants:
            await update_configuration(
                metrics_manager.configurations_manager,
                tenant.id,
                ACTIVITY_CONFIG,
                required_fields=["crew"],
            )

    """
    Checking for extra tenants

    The global_score that is stored that should return False regardless of the metric
    because they are being stored using tenants that do not pertain to the
    contractors/supervisors being tested.
    """
    await global_score.store(
        metrics_manager, tenant_id=tenants[1].id, avg=10, stddev=20
    )
    await global_score.store(
        metrics_manager, tenant_id=tenants[2].id, avg=-100, stddev=-200
    )
    extra_at_risk_1 = await is_at_risk_metric(
        metrics_manager, [person.id for person in extra_tenant_1]
    )
    extra_at_risk_2 = await is_at_risk_metric(
        metrics_manager, [person.id for person in extra_tenant_2]
    )
    _assert_all_false(extra_at_risk_1, 7)
    _assert_all_false(extra_at_risk_2, 8)

    """
    Storing "valid" scores as the tenant to be tested is used.
    """
    await global_score.store(metrics_manager, tenant_id=tenants[0].id, avg=1, stddev=2)
    is_at_risk = await is_at_risk_metric(
        metrics_manager, [person.id for person in persons]
    )
    _assert_all_false(is_at_risk, 6)

    """
    Storing "base" scores.

    The ContractorSafetyScore or SupervisorEngagementFactor is being stored below.
    Since the "global" score above is set with a sum of 3 and since the lists below
    zip to form a list of length 6, there will be some situations where the
    contractor/supervisor will show as at risk
    """
    scores = []
    for i, (person, extra_1, extra_2) in enumerate(
        zip(persons, extra_tenant_1, extra_tenant_2)
    ):
        scores.append(base_score.store(metrics_manager, person.id, i))
        scores.append(base_score.store(metrics_manager, extra_1.id, i))
        scores.append(base_score.store(metrics_manager, extra_2.id, i))

    await asyncio.gather(*scores)

    """
    Some will show as at risk

    The `is_at_risk` metric is calculated by checking if a given contractor/supervisor's
    score is higher than the avg + stddev. The values below should show is_at_risk is
    True for entries whose list index is > 3
    """
    is_at_risk = await is_at_risk_metric(
        metrics_manager, [person.id for person in persons]
    )
    assert len(is_at_risk) == 6
    for i, item in enumerate(is_at_risk):
        if i <= 3:
            assert item is False
        else:
            assert item is True

    """
    The average and standard deviations for the tenants are as follows
    tenants[0]: avg = 1, stddev = 2
    tenants[1]: avg = 10, stddev = 20
    tenants[2]: avg = -100, stddev = -200

    The following individual persons have the following scores
    persons[0]: score = 0 -> is_at_risk = False
    persons[5]: score = 5 -> is_at_risk = True
    extra_tenant_1[0]: score = 0 -> is_at_risk = False
    extra_tenant_2[0]: score = 0 -> is_at_risk = True
    """
    is_at_risk = await is_at_risk_metric(
        metrics_manager,
        [
            persons[0].id,
            persons[5].id,
            extra_tenant_1[0].id,
            extra_tenant_2[0].id,
        ],
    )

    assert len(is_at_risk) == 4
    assert is_at_risk[0] is False
    assert is_at_risk[1] is True
    assert is_at_risk[2] is False
    assert is_at_risk[3] is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_is_contractor_at_risk(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
) -> None:
    await _is_at_risk(db_session, metrics_manager, "Contractor")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_is_supervisor_at_risk(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
) -> None:
    await _is_at_risk(db_session, metrics_manager, "Supervisor")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_is_crew_at_risk(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
) -> None:
    await _is_at_risk(db_session, metrics_manager, "Crew")
