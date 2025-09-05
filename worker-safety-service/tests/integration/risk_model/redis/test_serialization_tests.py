import datetime
import uuid
from typing import Any, Callable
from unittest.mock import Mock

import pytest
from dependency_injector.wiring import Provide, inject

from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.locations import LocationsManager
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.risk_model.metrics.contractor.gbl_contractor_project_history_bsl import (
    GlobalContractorProjectHistoryBaseline,
)
from worker_safety_service.risk_model.metrics.project.total_project_risk_score import (
    TotalProjectRiskScore,
)
from worker_safety_service.risk_model.metrics.supervisor_engagement_factor import (
    SupervisorEngagementFactor,
)
from worker_safety_service.risk_model.riskmodelreactor_redis import (
    RiskModelReactorRedisImpl,
)
from worker_safety_service.risk_model.triggers.contractor_data_changed import (
    ContractorDataChanged,
)


@inject
def global_contractor_project_history_baseline(
    metrics_manager: RiskModelMetricsManager = Provide["risk_model_metrics_manager"],
    contractors_manager: ContractorsManager = Provide["contractors_manager"],
) -> Any:
    contractor_id = uuid.uuid4()
    return GlobalContractorProjectHistoryBaseline(
        metrics_manager, contractors_manager, contractor_id
    )


@inject
def total_project_risk_score(
    metrics_manager: RiskModelMetricsManager = Provide["risk_model_metrics_manager"],
    configurations_manager: ConfigurationsManager = Provide["configurations_manager"],
    work_package_manager: WorkPackageManager = Provide["work_package_manager"],
    task_manager: TaskManager = Provide["task_manager"],
    locations_manager: LocationsManager = Provide["locations_manager"],
) -> Any:
    project_id = uuid.uuid4()
    date = datetime.date.today()
    return TotalProjectRiskScore(
        metrics_manager,
        configurations_manager,
        work_package_manager,
        task_manager,
        locations_manager,
        project_id,
        date,
    )


@inject
def supervisor_engagement_factor(
    metrics_manager: RiskModelMetricsManager = Provide["risk_model_metrics_manager"],
    supervisors_manager: SupervisorsManager = Provide["supervisors_manager"],
) -> Any:
    supervisor_id = uuid.uuid4()
    return SupervisorEngagementFactor(
        metrics_manager, supervisors_manager, supervisor_id
    )


@pytest.mark.parametrize(
    "object_supplier",
    [
        (lambda: ContractorDataChanged(uuid.uuid4())),
        (total_project_risk_score),
        (supervisor_engagement_factor),
        (global_contractor_project_history_baseline),
    ],
)
@pytest.mark.integration
def test_encode_decode_class(object_supplier: Callable[[], Any]) -> None:
    reactor = RiskModelReactorRedisImpl(Mock())

    input_object = object_supplier()

    encoded_data = reactor.encode(input_object)
    loaded_class = reactor.decode(encoded_data)

    assert loaded_class == input_object
    assert loaded_class.__dict__ == input_object.__dict__
