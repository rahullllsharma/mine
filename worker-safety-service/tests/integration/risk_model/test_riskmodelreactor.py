import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pendulum
import pytest
from dependency_injector import providers

from tests.factories import (
    ActivityFactory,
    ContractorFactory,
    LibraryTaskFactory,
    LocationFactory,
    TaskFactory,
    TenantFactory,
    WorkPackageFactory,
)
from worker_safety_service.dal.contractors import (
    ContractorHistory,
    ContractorsManager,
    CSHIncident,
)
from worker_safety_service.dal.incidents import IncidentData, IncidentsManager
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models import (
    AsyncSession,
    ContractorProjectExecutionModel,
    ContractorSafetyHistoryModel,
    GblContractorProjectHistoryBaselineModel,
    GblContractorProjectHistoryBaselineModelStdDev,
)
from worker_safety_service.risk_model.metrics.project.project_safety_climate_multiplier import (
    ProjectSafetyClimateMultiplier,
)
from worker_safety_service.risk_model.metrics.project.project_site_conditions_multiplier import (
    ProjectLocationSiteConditionsMultiplier,
)
from worker_safety_service.risk_model.metrics.project.total_project_location_risk_score import (
    TotalProjectLocationRiskScore,
)
from worker_safety_service.risk_model.metrics.project.total_project_risk_score import (
    TotalProjectRiskScore,
)
from worker_safety_service.risk_model.metrics.tasks.project_location_total_task_riskscore import (
    ProjectLocationTotalTaskRiskScore,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_riskscore import (
    TaskSpecificRiskScore,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_safety_climate_multiplier import (
    TaskSpecificSafetyClimateMultiplier,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_site_conditions_multiplier import (
    TaskSpecificSiteConditionsMultiplier,
)
from worker_safety_service.risk_model.riskmodel_container import RiskModelContainer
from worker_safety_service.risk_model.triggers.contractor_data_changed import (
    ContractorDataChanged,
)
from worker_safety_service.risk_model.triggers.contractor_data_changed_for_tenant import (
    ContractorDataChangedForTenant,
)
from worker_safety_service.risk_model.triggers.library_task_data_changed import (
    LibraryTaskDataChanged,
)
from worker_safety_service.site_conditions import SiteConditionsEvaluator


@pytest.mark.asyncio
async def test_reactor(
    db_session: AsyncSession,
    app_container: RiskModelContainer,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    contractors = await ContractorFactory.persist_many(
        db_session, size=3, tenant_id=tenant.id
    )
    contractors_ids = [i.id for i in contractors]
    contractors_history = [
        ContractorHistory(n_safety_observations=50, n_action_items=0),
        ContractorHistory(n_safety_observations=80, n_action_items=3),
        ContractorHistory(n_safety_observations=30, n_action_items=1),
    ]
    contractors_csh = [
        CSHIncident(
            near_miss=10,
            first_aid=3,
            recordable=5,
            restricted=1,
            lost_time=2,
            sum_of_project_cost=50.0,
        ),
        CSHIncident(
            first_aid=5,
            recordable=1,
            lost_time=5,
            p_sif=0,
            sif=3,
            sum_of_project_cost=20.0,
        ),
        CSHIncident(
            restricted=3, lost_time=1, p_sif=1, sif=0, sum_of_project_cost=100.0
        ),
    ]

    for contractor in contractors:
        project = await WorkPackageFactory.persist(
            db_session, contractor_id=contractor.id
        )
        await LocationFactory.persist(db_session, project_id=project.id)

    site_condition_evaluator: SiteConditionsEvaluator = object.__new__(
        SiteConditionsEvaluator
    )

    contractors_manager = ContractorsManager(db_session)
    contractors_manager.get_contractors_history = AsyncMock(  # type: ignore
        side_effect=lambda t: iter(contractors_history) if t == tenant.id else []
    )
    contractors_manager.get_contractor_history = AsyncMock(  # type: ignore
        side_effect=lambda u: contractors_history[contractors_ids.index(u)]
    )
    contractors_manager.get_contractor_experience_years = AsyncMock(  # type: ignore
        side_effect=lambda u: contractors_ids.index(u) + 0.5
    )
    contractors_manager.get_csh_incident_data = AsyncMock(  # type: ignore
        side_effect=lambda u: contractors_csh[contractors_ids.index(u)]
    )

    with app_container.override_providers(
        contractors_manager=providers.Object(contractors_manager),
        site_conditions_manager=providers.Object(site_condition_evaluator),
    ):
        risk_model_manager = app_container.risk_model_metrics_manager()
        my_reactor = await app_container.risk_model_reactor()
        reactor_worker = await app_container.risk_model_reactor_worker()

        # Check no values present
        stored_metric = await risk_model_manager.load(
            GblContractorProjectHistoryBaselineModel, tenant_id=tenant.id
        )
        assert stored_metric is None

        # Store a base value just to create entropy
        await risk_model_manager.store(
            GblContractorProjectHistoryBaselineModel(tenant_id=tenant.id, value=1.0)
        )

        # Add fuel to the reactor
        await my_reactor.add(ContractorDataChangedForTenant(tenant.id))
        for contractor in contractors:
            await my_reactor.add(ContractorDataChanged(contractor.id))

        # Start the reactor
        await reactor_worker.start()

        gcphb = await risk_model_manager.load(
            GblContractorProjectHistoryBaselineModel, tenant_id=tenant.id
        )
        assert gcphb
        assert gcphb.value == 0.025

        gcphb_stddev = await risk_model_manager.load(
            GblContractorProjectHistoryBaselineModelStdDev, tenant_id=tenant.id
        )
        assert gcphb_stddev
        assert round(gcphb_stddev.value, 3) == 0.017

        expected_cpes = [1, 0.5, 0]
        for i, expected in enumerate(expected_cpes):
            cpe = await risk_model_manager.load(
                ContractorProjectExecutionModel, contractor_id=contractors[i].id
            )
            assert cpe
            assert cpe.value == expected

        expected_csh = [0.726, 3.515, 0.266]
        for i, expected in enumerate(expected_csh):
            csh = await risk_model_manager.load(
                ContractorSafetyHistoryModel, contractor_id=contractors[i].id
            )
            assert csh
            assert round(csh.value, 3) == expected


task_incident_data = IncidentData(
    near_miss=3, first_aid=5, recordable=3, restricted=1, lost_time=3, p_sif=1, sif=3
)


@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_reactor_with_library_data_changed(
    app_container: RiskModelContainer,
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
) -> None:
    # This task should be: "In- trench welding", 413
    library_task_id = (await LibraryTaskFactory.persist(db_session, hesp=413)).id
    library_task_trigger = LibraryTaskDataChanged(library_task_id)

    start_date = datetime.now(timezone.utc) + timedelta(days=1)
    end_date = datetime.now(timezone.utc) + timedelta(days=3)

    project = await WorkPackageFactory.persist(
        db_session,
        start_date=pendulum.today().date(),
        end_date=pendulum.today().add(months=1, days=1).date(),
    )
    location = await LocationFactory.persist(db_session, project_id=project.id)
    assert location.project_id
    (activity, _, _) = await ActivityFactory.with_project_and_location(
        db_session,
        project=project,
        location=location,
        activity_kwargs={"start_date": start_date, "end_date": end_date},
    )
    (
        (task1, _, _),
        (task2, _, _),
        (task3, _, _),
    ) = await TaskFactory.batch_with_project_and_location(
        db_session,
        [
            {
                "project": project,
                "location": location,
                "activity": activity,
                "task_kwargs": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "library_task_id": library_task_id,
                },
            },
            {
                "project": project,
                "location": location,
                "activity": activity,
                "task_kwargs": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "library_task_id": library_task_id,
                },
            },
            {
                "project": project,
                "location": location,
                "activity": activity,
                "task_kwargs": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "library_task_id": library_task_id,
                },
            },
        ],
    )
    tasks = [task1, task2, task3]

    max_date = tasks[0].end_date
    min_date = tasks[0].start_date
    for task in tasks:
        min_date = min(min_date, task.start_date)
        max_date = max(max_date, task.end_date)
        await asyncio.gather(
            *[
                TaskSpecificSiteConditionsMultiplier.store(
                    metrics_manager, task.id, _date, value=0.5
                )
                for _date in pendulum.Interval(task.start_date, task.end_date)
            ]
        )

    max_time_window_date = pendulum.today().add(days=14).date()
    max_date = min(max_date, max_time_window_date)

    await asyncio.gather(
        ProjectSafetyClimateMultiplier.store(metrics_manager, location.id, 0.1),
        *[
            ProjectLocationSiteConditionsMultiplier.store(
                metrics_manager, location.id, _date, 0.5
            )
            for _date in pendulum.Interval(min_date, max_time_window_date)
        ],
    )

    site_condition_evaluator: SiteConditionsEvaluator = object.__new__(
        SiteConditionsEvaluator
    )

    incidents_manager: IncidentsManager = IncidentsManager(None, None, None, None)  # type: ignore
    incidents_manager.get_tasks_incident_data = AsyncMock(return_value=task_incident_data)  # type: ignore

    with app_container.override_providers(
        incidents_manager=incidents_manager,
        site_conditions_manager=providers.Object(site_condition_evaluator),
    ):
        my_reactor = await app_container.risk_model_reactor()
        reactor_worker = await app_container.risk_model_reactor_worker()

        await my_reactor.add(library_task_trigger)

        await reactor_worker.start()

        metric = await TaskSpecificSafetyClimateMultiplier.load(
            metrics_manager, library_task_id, location.tenant_id
        )
        assert metric is not None
        assert metric.library_task_id == library_task_id
        assert metric.value == 0.771

        # TODO: Check that the HESP is still 413
        for task in tasks:
            for _date in pendulum.Interval(
                task.start_date, min(task.end_date, max_date)
            ):
                _metric = await TaskSpecificRiskScore.load(
                    metrics_manager, task.id, _date
                )
                assert _metric is not None
                assert _metric.project_task_id == task.id
                assert _metric.value == 937.923

        for _date in pendulum.Interval(min_date, max_date):
            _m = await ProjectLocationTotalTaskRiskScore.load(
                metrics_manager, location.id, _date
            )
            assert _m is not None
            assert _m.project_location_id == location.id
            assert (
                round(_m.value, 3) == 937.923
            )  # TODO: Change the task to have a different avg

        for _date in pendulum.Interval(min_date, max_date):
            __m = await TotalProjectLocationRiskScore.load(
                metrics_manager, location.id, _date
            )
            assert __m is not None
            assert __m.project_location_id == location.id
            # TODO: Check if the values are accurate

        for _date in pendulum.Interval(min_date, max_date):
            ___m = await TotalProjectRiskScore.load(
                metrics_manager, location.project_id, _date
            )
            assert ___m is not None
            assert ___m.project_id == location.project_id
            # TODO: Check if the values are accurate


def __test_reactor_with_overnight_trigger() -> None:
    # TODO: Implement!!
    """
    # Call TaskSpecificSiteConditionsMultiplier to change the tasks on a specific day.
    _min = pendulum.today().date()
    _max = max_date
    for task in tasks:
        _min = max(_min, task.start_date)
        _max = min(_min, task.end_date)
    date_to_update = choice([pendulum.period(_min, max_date)])

    for task in tasks:
        metric_calculation = TaskSpecificSiteConditionsMultiplier(metrics_manager, task_manager, work_package_manager, site_condition_evaluator, task.id, date_to_update)
        my_reactor.add(metric_calculation)

    my_reactor.start()

    assert True
    """
