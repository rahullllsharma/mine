from uuid import UUID

from worker_safety_service.dal.risk_model import IsAtRiskMetric, RiskModelMetricsManager


def is_at_risk(ids: list[UUID], items: dict[UUID, IsAtRiskMetric]) -> list[bool]:
    at_risk: list[bool] = []
    for _id in ids:
        item = items.get(_id)
        if item is None:
            at_risk.append(False)
        else:
            avg = item.average
            st_dev = item.st_dev
            score = item.score
            if avg is None or st_dev is None or score is None:
                at_risk.append(False)
            else:
                at_risk.append(score > avg + st_dev)
    return at_risk


async def is_contractor_at_risk(
    metrics_manager: RiskModelMetricsManager, ids: list[UUID]
) -> list[bool]:
    return is_at_risk(ids, (await metrics_manager.load_contractor_scores(ids)))


async def is_supervisor_at_risk(
    metrics_manager: RiskModelMetricsManager, ids: list[UUID]
) -> list[bool]:
    return is_at_risk(ids, (await metrics_manager.load_supervisor_scores(ids)))


async def is_crew_at_risk(
    metrics_manager: RiskModelMetricsManager, ids: list[UUID]
) -> list[bool]:
    return is_at_risk(ids, (await metrics_manager.load_crew_scores(ids)))
