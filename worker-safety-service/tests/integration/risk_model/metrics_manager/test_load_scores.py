import random
import uuid
from collections import defaultdict
from typing import Awaitable, Callable, NamedTuple, Optional

import pytest

from tests.factories import (
    ContractorFactory,
    CrewFactory,
    SupervisorFactory,
    TenantFactory,
)
from worker_safety_service.configs.base_configuration_model import store_partial
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.risk_model import IsAtRiskMetric, RiskModelMetricsManager
from worker_safety_service.models import (
    AsyncSession,
    AverageContractorSafetyScoreModel,
    AverageCrewRiskModel,
    AverageSupervisorEngagementFactorModel,
    AverageSupervisorRelativePrecursorRiskModel,
    StdDevContractorSafetyScoreModel,
    StdDevCrewRiskModel,
    StdDevSupervisorEngagementFactorModel,
    StdDevSupervisorRelativePrecursorRiskModel,
    Tenant,
)
from worker_safety_service.models.risk_model import TenantRiskModelBase
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    SupervisorRiskScoreMetricConfig,
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
from worker_safety_service.risk_model.metrics.global_supervisor_relative_precursor_risk import (
    GlobalSupervisorRelativePrecursorRisk,
)
from worker_safety_service.risk_model.metrics.supervisor_engagement_factor import (
    SupervisorEngagementFactor,
)
from worker_safety_service.risk_model.metrics.supervisor_relative_precursor_risk import (
    SupervisorRelativePrecursorRisk,
)


class ScoreConfigs(NamedTuple):
    score_loader_method: Callable[
        [RiskModelMetricsManager, list[uuid.UUID]],
        Awaitable[dict[uuid.UUID, IsAtRiskMetric]],
    ]

    entity_factory: type[ContractorFactory] | type[SupervisorFactory] | type[
        CrewFactory
    ]
    entity_score_type: type[ContractorSafetyScore] | type[
        SupervisorEngagementFactor
    ] | type[SupervisorRelativePrecursorRisk] | type[CrewRelativePrecursorRisk]
    tenant_score_type: type[GlobalContractorSafetyScore] | type[
        GlobalSupervisorEngagementFactor
    ] | type[GlobalSupervisorRelativePrecursorRisk] | type[
        GlobalCrewRelativePrecursorRisk
    ]
    tenant_average_score_model: type[TenantRiskModelBase]
    tenant_stddev_score_model: type[TenantRiskModelBase]
    prepare_tenant: Callable[[ConfigurationsManager, Tenant], Awaitable[None]] | None


async def update_risk_supervisor_relative_precusor_config(
    manager: ConfigurationsManager, tenant: Tenant
) -> None:
    await store_partial(
        manager,
        SupervisorRiskScoreMetricConfig,
        tenant.id,
        type="STOCHASTIC_MODEL",
    )


CONTRACTOR_SAFETY_SCORE = ScoreConfigs(
    RiskModelMetricsManager.load_contractor_scores,
    ContractorFactory,
    ContractorSafetyScore,
    GlobalContractorSafetyScore,
    AverageContractorSafetyScoreModel,
    StdDevContractorSafetyScoreModel,
    None,
)
SUPERVISOR_ENGAGEMENT_FACTOR = ScoreConfigs(
    RiskModelMetricsManager.load_supervisor_scores,
    SupervisorFactory,
    SupervisorEngagementFactor,
    GlobalSupervisorEngagementFactor,
    AverageSupervisorEngagementFactorModel,
    StdDevSupervisorEngagementFactorModel,
    None,
)
SUPERVISOR_RELATIVE_RISK = ScoreConfigs(
    RiskModelMetricsManager.load_supervisor_scores,
    SupervisorFactory,
    SupervisorRelativePrecursorRisk,
    GlobalSupervisorRelativePrecursorRisk,
    AverageSupervisorRelativePrecursorRiskModel,
    StdDevSupervisorRelativePrecursorRiskModel,
    update_risk_supervisor_relative_precusor_config,
)
CREW_RISK = ScoreConfigs(
    RiskModelMetricsManager.load_crew_scores,
    CrewFactory,
    CrewRelativePrecursorRisk,
    GlobalCrewRelativePrecursorRisk,
    AverageCrewRiskModel,
    StdDevCrewRiskModel,
    None,
)


class TenantScore(NamedTuple):
    avg: Optional[float]
    stddev: Optional[float]


Score = Optional[float]


async def populate_database(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    scores_by_tenant: dict[TenantScore, list[Score]],
    score_configs: ScoreConfigs,
) -> defaultdict[uuid.UUID, dict[uuid.UUID, IsAtRiskMetric | None]]:
    ret_contractors_score_map: defaultdict[
        uuid.UUID, dict[uuid.UUID, IsAtRiskMetric | None]
    ] = defaultdict(dict)
    for tenant_score, contractor_scores in scores_by_tenant.items():
        tenant = await TenantFactory.persist(db_session)
        if score_configs.prepare_tenant:
            await score_configs.prepare_tenant(
                metrics_manager.configurations_manager, tenant
            )

        tenant_has_valid_score = (
            tenant_score is not None
            and tenant_score.avg is not None
            and tenant_score.stddev is not None
        )
        if tenant_has_valid_score:
            assert tenant_score.avg
            assert tenant_score.stddev
            await score_configs.tenant_score_type.store(
                metrics_manager, tenant.id, tenant_score.avg, tenant_score.stddev
            )
        elif tenant_score is not None and tenant_score.stddev is not None:
            await metrics_manager.store(
                score_configs.tenant_stddev_score_model(
                    tenant_id=tenant.id, value=tenant_score.stddev
                )
            )
        elif tenant_score is not None and tenant_score.avg is not None:
            await metrics_manager.store(
                score_configs.tenant_average_score_model(
                    tenant_id=tenant.id, value=tenant_score.avg
                )
            )

        for contractor_score in contractor_scores:
            contractor = await score_configs.entity_factory.persist(
                session=db_session, tenant_id=tenant.id
            )

            if contractor_score is not None:
                await score_configs.entity_score_type.store(
                    metrics_manager, contractor.id, contractor_score
                )

                if tenant_has_valid_score:
                    at_risk = IsAtRiskMetric(
                        score=contractor_score,
                        average=tenant_score.avg,
                        st_dev=tenant_score.stddev,
                    )
                else:
                    at_risk = None

                ret_contractors_score_map[tenant.id][contractor.id] = at_risk

    return ret_contractors_score_map


SCORE_TYPE_PARAMS = [
    pytest.param(CONTRACTOR_SAFETY_SCORE, id="contractor"),
    pytest.param(SUPERVISOR_ENGAGEMENT_FACTOR, id="supervisor"),
    pytest.param(SUPERVISOR_RELATIVE_RISK, id="supervisor_relative"),
    pytest.param(CREW_RISK, id="crew"),
]


@pytest.mark.parametrize("score_type", SCORE_TYPE_PARAMS)
@pytest.mark.asyncio
async def test_load_scores_fail_unknown_contractor(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    score_type: ScoreConfigs,
) -> None:
    # If the contractor is Unknown it should not return anything.
    ret = await score_type.score_loader_method(metrics_manager, [uuid.uuid4()])
    assert len(ret) == 0


@pytest.mark.parametrize(
    "scores_by_tenant",
    [
        {TenantScore(avg=5.0, stddev=2.0): [None]},
        {TenantScore(avg=None, stddev=2.0): [10.0]},
        {TenantScore(avg=10.5, stddev=None): [10.0, 8.5, 3.1]},
        {None: [10.0]},
    ],
)
@pytest.mark.parametrize("score_type", SCORE_TYPE_PARAMS)
@pytest.mark.asyncio
async def test_load_scores_fail_missing_dependencies(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    scores_by_tenant: dict[TenantScore, list[Score]],
    score_type: ScoreConfigs,
) -> None:
    actual = await populate_database(
        db_session, metrics_manager, scores_by_tenant, score_type
    )

    ret = await score_type.score_loader_method(
        metrics_manager, [i for v in actual.values() for i in v]
    )
    assert len(ret) == 0


@pytest.mark.parametrize(
    "scores_by_tenant",
    [
        {TenantScore(avg=10.5, stddev=2.0): [10.0]},
        {TenantScore(avg=10.5, stddev=2.0): [10.0, 8.5, 3.1]},
        {
            TenantScore(avg=10.5, stddev=2.0): [3.0],
            TenantScore(avg=5.0, stddev=2.1): [5.0],
        },
        {
            TenantScore(avg=5.0, stddev=2.5): [3.0, 4.5, 6.0],
            TenantScore(avg=10.0, stddev=3.0): [6.0, 5.5, 3.0],
        },
    ],
)
@pytest.mark.parametrize("score_type", SCORE_TYPE_PARAMS)
@pytest.mark.asyncio
async def test_load_scores_success(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    scores_by_tenant: dict[TenantScore, list[Score]],
    score_type: ScoreConfigs,
) -> None:
    actual = await populate_database(
        db_session, metrics_manager, scores_by_tenant, score_type
    )

    ret = await score_type.score_loader_method(
        metrics_manager, [i for v in actual.values() for i in v]
    )
    expected = {k: v for i in actual.values() for k, v in i.items() if v is not None}

    assert len(ret) == len(
        expected
    ), "The number of returned elements must match the expected ones."
    assert ret == expected


@pytest.mark.parametrize(
    "scores_by_tenant",
    [
        {
            TenantScore(avg=5.0, stddev=2.5): [3.0, None, 6.5],
            TenantScore(avg=10.0, stddev=3.0): [6.2, 5.3, 3.4],
            TenantScore(avg=None, stddev=3.0): [4.0, 2.0, 1.0],
        }
    ],
)
@pytest.mark.parametrize("score_type", SCORE_TYPE_PARAMS)
@pytest.mark.asyncio
async def test_load_scores_success_partial(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    scores_by_tenant: dict[TenantScore, list[Score]],
    score_type: ScoreConfigs,
) -> None:
    actual = await populate_database(
        db_session, metrics_manager, scores_by_tenant, score_type
    )
    partial_query = list(
        random.choices(
            [(t, k, v) for t, i in actual.items() for k, v in i.items()], k=3
        )
    )

    expected = {}
    ids = []
    for _, entity_id, metric in partial_query:
        ids.append(entity_id)
        if metric is not None:
            expected[entity_id] = metric

    ret = await score_type.score_loader_method(metrics_manager, ids)

    assert len(ret) == len(
        expected
    ), "The number of returned elements must match the expected ones."
    assert ret == expected
