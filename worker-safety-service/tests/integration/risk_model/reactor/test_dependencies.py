import datetime
from contextlib import ExitStack
from typing import Awaitable, Callable
from unittest import mock
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.orm import sessionmaker

from tests.factories import (
    ActivityFactory,
    LocationFactory,
    TaskFactory,
    WorkPackageFactory,
)
from tests.integration.risk_model.configs.helpers_tenant_factories import h1_tenant_mock
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models import AsyncSession
from worker_safety_service.risk_model.metrics.project.project_site_conditions_multiplier import (
    ProjectLocationSiteConditionsMultiplier,
)
from worker_safety_service.risk_model.metrics.project.total_project_location_risk_score import (
    TotalProjectLocationRiskScore,
)
from worker_safety_service.risk_model.metrics.project.total_project_risk_score import (
    TotalProjectRiskScore,
)
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_activity_site_condition_relative_precursor_risk import (
    StochasticActivitySiteConditionRelativePrecursorRiskScore,
)
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_activity_total_task_riskscore import (
    StochasticActivityTotalTaskRiskScore,
)
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_location_total_task_riskscore import (
    StochasticLocationTotalTaskRiskScore,
)
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_task_specific_risk_score import (
    StochasticTaskSpecificRiskScore,
)
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_total_location_risk_score import (
    StochasticTotalLocationRiskScore,
)
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_total_work_package_risk_score import (
    StochasticTotalWorkPackageRiskScore,
)
from worker_safety_service.risk_model.metrics.stochastic_model.total_activity_risk_score import (
    TotalActivityRiskScore,
)
from worker_safety_service.risk_model.metrics.tasks.project_location_total_task_riskscore import (
    ProjectLocationTotalTaskRiskScore,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_riskscore import (
    TaskSpecificRiskScore,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_site_conditions_multiplier import (
    TaskSpecificSiteConditionsMultiplier,
)
from worker_safety_service.risk_model.riskmodel_container import RiskModelContainer
from worker_safety_service.risk_model.riskmodelreactor import MetricCalculation
from worker_safety_service.risk_model.triggers import (
    ActivityChanged,
    ActivityDeleted,
    ProjectLocationSiteConditionsChanged,
    TaskChanged,
    TaskDeleted,
)


async def task_changed_rule_based(app_container: RiskModelContainer) -> TaskChanged:
    session_factory: sessionmaker = app_container.session_factory()
    async with session_factory() as db_session:
        a_task = await TaskFactory.persist(db_session)

    return TaskChanged(a_task.id)


async def task_changed_stochastic(app_container: RiskModelContainer) -> TaskChanged:
    configurations_manager = app_container.configurations_manager()
    session_factory: sessionmaker = app_container.session_factory()
    async with session_factory() as db_session:
        tenant_id = await h1_tenant_mock(db_session, configurations_manager)
        a_project = await WorkPackageFactory.persist(db_session, tenant_id=tenant_id)
        a_location = await LocationFactory.persist(db_session, project_id=a_project.id)
        a_activity = await ActivityFactory.persist(
            db_session, location_id=a_location.id
        )
        a_task = await TaskFactory.persist(
            db_session, activity_id=a_activity.id, location_id=a_location.id
        )

    return TaskChanged(a_task.id)


async def activity_deleted_stochastic(
    app_container: RiskModelContainer,
) -> ActivityDeleted:
    configurations_manager = app_container.configurations_manager()
    session_factory: sessionmaker = app_container.session_factory()
    async with session_factory() as db_session:
        tenant_id = await h1_tenant_mock(db_session, configurations_manager)
        a_project = await WorkPackageFactory.persist(db_session, tenant_id=tenant_id)
        a_location = await LocationFactory.persist(db_session, project_id=a_project.id)
        a_activity = await ActivityFactory.persist(
            db_session, location_id=a_location.id, archived_at=datetime.datetime.now()
        )

        await TaskFactory.persist(
            db_session,
            activity_id=a_activity.id,
            location_id=a_location.id,
            archived_at=datetime.datetime.now(),
        )

    return ActivityDeleted(a_activity.id)


async def task_deleted_stochastic(app_container: RiskModelContainer) -> TaskDeleted:
    configurations_manager = app_container.configurations_manager()
    session_factory: sessionmaker = app_container.session_factory()
    async with session_factory() as db_session:
        tenant_id = await h1_tenant_mock(db_session, configurations_manager)
        a_project = await WorkPackageFactory.persist(db_session, tenant_id=tenant_id)
        a_location = await LocationFactory.persist(db_session, project_id=a_project.id)
        a_activity = await ActivityFactory.persist(
            db_session, location_id=a_location.id
        )
        a_task = await TaskFactory.persist(
            db_session,
            activity_id=a_activity.id,
            location_id=a_location.id,
            archived_at=datetime.datetime.now(),
        )

    return TaskDeleted(a_task.id)


async def activity_changed_rule_based(
    app_container: RiskModelContainer,
) -> ActivityChanged:
    session_factory: sessionmaker = app_container.session_factory()
    async with session_factory() as db_session:
        a_activity = await ActivityFactory.persist(db_session)

    return ActivityChanged(a_activity.id)


async def activity_changed_stochastic(
    app_container: RiskModelContainer,
) -> ActivityChanged:
    configurations_manager = app_container.configurations_manager()
    session_factory: sessionmaker = app_container.session_factory()
    async with session_factory() as db_session:
        tenant_id = await h1_tenant_mock(db_session, configurations_manager)
        a_project = await WorkPackageFactory.persist(db_session, tenant_id=tenant_id)
        a_location = await LocationFactory.persist(db_session, project_id=a_project.id)
        a_activity = await ActivityFactory.persist(
            db_session, location_id=a_location.id
        )

    return ActivityChanged(a_activity.id)


async def location_site_conditions_changed_rule_based(
    app_container: RiskModelContainer,
) -> ProjectLocationSiteConditionsChanged:
    session_factory: sessionmaker = app_container.session_factory()
    async with session_factory() as db_session:
        a_location = await LocationFactory.persist(db_session)

    return ProjectLocationSiteConditionsChanged(a_location.id)


async def location_site_conditions_changed_stochastic(
    app_container: RiskModelContainer,
) -> ProjectLocationSiteConditionsChanged:
    configurations_manager = app_container.configurations_manager()
    session_factory: sessionmaker = app_container.session_factory()
    async with session_factory() as db_session:
        tenant_id = await h1_tenant_mock(db_session, configurations_manager)
        a_project = await WorkPackageFactory.persist(db_session, tenant_id=tenant_id)
        a_location = await LocationFactory.persist(db_session, project_id=a_project.id)
        _ = await ActivityFactory.persist_many(
            db_session, location_id=a_location.id, size=2
        )

    return ProjectLocationSiteConditionsChanged(a_location.id)


@pytest.mark.parametrize(
    "trigger_metric_supplier, expected_called_metrics",
    [
        (
            task_changed_rule_based,
            [
                (TaskSpecificSiteConditionsMultiplier, 15),
                (TaskSpecificRiskScore, 15),
                (ProjectLocationTotalTaskRiskScore, 15),
                (TotalProjectLocationRiskScore, 15),
                (TotalProjectRiskScore, 15),
                (StochasticTaskSpecificRiskScore, 0),
                (StochasticTotalWorkPackageRiskScore, 0),
            ],
        ),
        (
            task_changed_stochastic,
            [
                (StochasticTaskSpecificRiskScore, 15),
                (StochasticActivityTotalTaskRiskScore, 15),
                (StochasticLocationTotalTaskRiskScore, 15),
                (StochasticActivitySiteConditionRelativePrecursorRiskScore, 0),
                (TotalActivityRiskScore, 15),
                (StochasticTotalLocationRiskScore, 15),
                (StochasticTotalWorkPackageRiskScore, 15),
                (TaskSpecificSiteConditionsMultiplier, 0),
                (TaskSpecificRiskScore, 0),
            ],
        ),
        (
            task_deleted_stochastic,
            [
                (StochasticActivityTotalTaskRiskScore, 15),
                (StochasticLocationTotalTaskRiskScore, 15),
                (StochasticActivitySiteConditionRelativePrecursorRiskScore, 0),
                (TotalActivityRiskScore, 15),
                (StochasticTotalLocationRiskScore, 15),
                (StochasticTotalWorkPackageRiskScore, 15),
                (TaskSpecificSiteConditionsMultiplier, 0),
                (TaskSpecificRiskScore, 0),
            ],
        ),
        (
            activity_deleted_stochastic,
            [
                (StochasticLocationTotalTaskRiskScore, 15),
                (StochasticTotalLocationRiskScore, 15),
            ],
        ),
        (
            location_site_conditions_changed_rule_based,
            [
                (ProjectLocationSiteConditionsMultiplier, 15),
                (TotalProjectLocationRiskScore, 15),
                (TotalProjectRiskScore, 15),
                (StochasticActivitySiteConditionRelativePrecursorRiskScore, 0),
            ],
        ),
        (
            location_site_conditions_changed_stochastic,
            [
                (StochasticTaskSpecificRiskScore, 0),
                (StochasticActivityTotalTaskRiskScore, 0),
                (StochasticLocationTotalTaskRiskScore, 0),
                (StochasticActivitySiteConditionRelativePrecursorRiskScore, 30),
                (TotalActivityRiskScore, 30),
                (StochasticTotalLocationRiskScore, 15),
                (StochasticTotalWorkPackageRiskScore, 15),
                (TotalProjectLocationRiskScore, 0),
                (TotalProjectRiskScore, 0),
            ],
        ),
        (
            activity_changed_rule_based,
            [
                (StochasticActivitySiteConditionRelativePrecursorRiskScore, 0),
            ],
        ),
        (
            activity_changed_stochastic,
            [
                (StochasticActivitySiteConditionRelativePrecursorRiskScore, 15),
            ],
        ),
    ],
)
@pytest.mark.asyncio
async def test_reactor_dependency_resolution(
    app_container: RiskModelContainer,
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    trigger_metric_supplier: Callable[
        [RiskModelContainer], Awaitable[MetricCalculation]
    ],
    expected_called_metrics: list[tuple[MetricCalculation, int]],
) -> None:
    # TODO: Expand to the other metrics
    my_reactor = await app_container.risk_model_reactor()
    reactor_worker = await app_container.risk_model_reactor_worker()

    trigger_metric = await trigger_metric_supplier(app_container)
    await my_reactor.add(trigger_metric)

    with ExitStack() as stack:
        mocks_to_assert = []
        for metric, expected_call_count in expected_called_metrics:
            mocked_ctx = mock.patch.object(metric, "run")
            mocked_metric_run = stack.enter_context(mocked_ctx)

            # Disable the metrics run method so that it does not have side effects
            # Makes this test manageable
            mocked_metric_run.side_effect = AsyncMock()
            mocks_to_assert.append((metric, mocked_metric_run, expected_call_count))

        await reactor_worker.start()

        for metric, mocked_method, expected_call_count in mocks_to_assert:
            assert (
                mocked_method.call_count == expected_call_count
            ), f"Expected calls to metric: {metric}"
