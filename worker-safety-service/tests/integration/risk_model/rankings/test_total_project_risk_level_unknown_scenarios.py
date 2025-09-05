from typing import Awaitable, Callable

import pendulum
import pytest

from tests.integration.risk_model.utils.common_project_factories import (
    ProjectWithContext,
    project_not_active,
    project_with_location_but_no_active_tasks,
    project_with_location_but_no_tasks,
    project_with_location_with_active_tasks_but_archived,
    project_without_locations,
)
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models import AsyncSession, RiskLevel
from worker_safety_service.risk_model.rankings import total_project_risk_level_bulk


@pytest.mark.parametrize(
    "context",
    [
        (project_not_active),
        (project_without_locations),
        (project_with_location_but_no_tasks),
        (project_with_location_but_no_active_tasks),
        (project_with_location_with_active_tasks_but_archived),
    ],
)
@pytest.mark.asyncio
@pytest.mark.integration
async def test_expecting_unknown(
    db_session: AsyncSession,
    context: Callable[[AsyncSession], Awaitable[ProjectWithContext]],
    risk_model_metrics_manager: RiskModelMetricsManager,
) -> None:
    ctx = await context(db_session)
    project_id = ctx["project"].id
    tenant_id = ctx["project"].tenant_id

    today = pendulum.today().date()

    rankings = await total_project_risk_level_bulk(
        risk_model_metrics_manager, [project_id], tenant_id, today
    )
    assert rankings == [RiskLevel.UNKNOWN]
