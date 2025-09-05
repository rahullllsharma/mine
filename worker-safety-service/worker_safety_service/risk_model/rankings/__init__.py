import datetime
import uuid
from uuid import UUID

from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models import RiskLevel
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    LocationTotalTaskRiskScoreMetricConfig,
    RankedMetricConfig,
    TaskSpecificRiskScoreMetricConfig,
    TotalLocationRiskScoreMetricConfig,
    TotalProjectRiskScoreMetricConfig,
)
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


async def __load_risk_rankings_for_entity(
    metrics_manager: RiskModelMetricsManager,
    risk_classification_type: type[RankedMetricConfig],
    entity_ids: list[UUID],
    tenant_id: uuid.UUID,
    date: datetime.date,
) -> list[RiskLevel]:
    if len(entity_ids) == 0:
        return []

    rankings = await metrics_manager.load_risk_rankings(
        risk_classification_type, entity_ids, tenant_id, date
    )

    ret = []
    for _id in entity_ids:
        level = RiskLevel[rankings[_id]]
        ret.append(level)

    return ret


async def total_task_risk_score_ranking_bulk(
    metrics_manager: RiskModelMetricsManager,
    project_location_ids: list[UUID],
    tenant_id: UUID,
    date: datetime.date,
) -> list[RiskLevel]:
    return await __load_risk_rankings_for_entity(
        metrics_manager,
        LocationTotalTaskRiskScoreMetricConfig,
        project_location_ids,
        tenant_id,
        date,
    )


async def task_specific_risk_score_ranking_bulk(
    metrics_manager: RiskModelMetricsManager,
    project_task_ids: list[UUID],
    tenant_id: UUID,
    date: datetime.date,
) -> list[RiskLevel]:
    return await __load_risk_rankings_for_entity(
        metrics_manager,
        TaskSpecificRiskScoreMetricConfig,
        project_task_ids,
        tenant_id,
        date,
    )


async def project_location_risk_level_bulk(
    metrics_manager: RiskModelMetricsManager,
    project_location_ids: list[UUID],
    tenant_id: UUID,
    date: datetime.date,
) -> list[RiskLevel]:
    logger.info("Locations ids are ---->", project_location_ids=project_location_ids)
    data = await __load_risk_rankings_for_entity(
        metrics_manager,
        TotalLocationRiskScoreMetricConfig,
        project_location_ids,
        tenant_id,
        date,
    )

    logger.info("Data is -------->", data=data)

    return data


async def total_project_risk_level_bulk(
    metrics_manager: RiskModelMetricsManager,
    project_ids: list[UUID],
    tenant_id: UUID,
    date: datetime.date,
) -> list[RiskLevel]:
    return await __load_risk_rankings_for_entity(
        metrics_manager,
        TotalProjectRiskScoreMetricConfig,
        project_ids,
        tenant_id,
        date,
    )
