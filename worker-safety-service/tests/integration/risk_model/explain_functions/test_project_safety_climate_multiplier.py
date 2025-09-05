import datetime
import uuid

import pytest

from tests.db_data import DBData
from tests.factories import ContractorFactory, SupervisorUserFactory
from tests.integration.risk_model.explain_functions import (
    check_data,
    check_dependency,
    check_error,
    check_has_dependencies,
    check_input,
    check_inputs_errors_length,
    check_no_dependencies,
    check_successful_test,
)
from tests.integration.risk_model.utils.common_project_factories import (
    project_with_location_but_no_tasks,
)
from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.models import (
    AsyncSession,
    ContractorSafetyScoreModel,
    Location,
    ProjectSafetyClimateMultiplierModel,
    SupervisorEngagementFactorModel,
)
from worker_safety_service.risk_model.metrics.project.project_safety_climate_multiplier import (
    ProjectSafetyClimateMultiplier,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_safety_climate_multiplier_explain_method(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    work_package_manager: WorkPackageManager,
    contractors_manager: ContractorsManager,
    db_data: DBData,
) -> None:
    location_id = uuid.uuid4()
    data = await ProjectSafetyClimateMultiplier.explain(
        metrics_manager,
        project_location_id=location_id,
        work_package_manager=work_package_manager,
        contractors_manager=contractors_manager,
    )
    check_data(data, ["Project Safety Climate Multiplier"])
    check_inputs_errors_length(data, [0], [1])
    check_error(data[0].errors[0], Location)

    # Set up project, supervisor, contractor, etc
    supervisor = await SupervisorUserFactory.persist(db_session)
    contractor = await ContractorFactory.persist(db_session)
    ctx = await project_with_location_but_no_tasks(db_session)
    project = ctx["project"]
    project.primary_assigned_user_id = supervisor.id
    project.contractor_id = contractor.id

    location = (await db_data.project_locations(project.id))[0]
    location.supervisor_id = supervisor.id
    await db_session.commit()

    data = await ProjectSafetyClimateMultiplier.explain(
        metrics_manager,
        project_location_id=location.id,
        work_package_manager=work_package_manager,
        contractors_manager=contractors_manager,
    )

    check_inputs_errors_length(data, [0], [1])
    check_error(
        data[0].errors[0],
        ProjectSafetyClimateMultiplierModel,
        {"project_location_id": location.id, "calculated_before": None},
    )

    # Error when no parameters are in the table
    db_session.add(
        ProjectSafetyClimateMultiplierModel(
            project_location_id=location.id,
            value=123,
            calculated_at=datetime.datetime(2021, 12, 1, tzinfo=datetime.timezone.utc),
        )
    )
    await db_session.commit()

    data = await ProjectSafetyClimateMultiplier.explain(
        metrics_manager,
        project_location_id=location.id,
        work_package_manager=work_package_manager,
        contractors_manager=contractors_manager,
    )
    check_inputs_errors_length(data, [0], [2])
    check_error(
        data[0].errors[0],
        SupervisorEngagementFactorModel,
        {
            "supervisor_id": supervisor.id,
            "calculated_before": datetime.datetime(
                2021, 12, 1, 0, 0, tzinfo=datetime.timezone.utc
            ),
        },
    )
    check_error(
        data[0].errors[1],
        ContractorSafetyScoreModel,
        {
            "contractor_id": contractor.id,
            "calculated_before": datetime.datetime(
                2021, 12, 1, 0, 0, tzinfo=datetime.timezone.utc
            ),
        },
    )
    check_no_dependencies(data)

    # Error when Supervisor Engagement Factor multiplier doesn't exist
    db_session.add(
        ProjectSafetyClimateMultiplierModel(
            project_location_id=location.id,
            value=123,
            calculated_at=datetime.datetime(2021, 12, 2, tzinfo=datetime.timezone.utc),
        )
    )
    await db_session.commit()

    data = await ProjectSafetyClimateMultiplier.explain(
        metrics_manager,
        project_location_id=location.id,
        work_package_manager=work_package_manager,
        contractors_manager=contractors_manager,
    )
    check_inputs_errors_length(data, [0], [2])
    check_error(
        data[0].errors[0],
        SupervisorEngagementFactorModel,
        {
            "supervisor_id": supervisor.id,
            "calculated_before": datetime.datetime(
                2021, 12, 2, 0, 0, tzinfo=datetime.timezone.utc
            ),
        },
    )
    check_error(
        data[0].errors[1],
        ContractorSafetyScoreModel,
        {
            "contractor_id": contractor.id,
            "calculated_before": datetime.datetime(
                2021, 12, 2, 0, 0, tzinfo=datetime.timezone.utc
            ),
        },
    )
    check_no_dependencies(data)

    # Error when Contractor Safety Score multiplier doesn't exist
    db_session.add(
        ProjectSafetyClimateMultiplierModel(
            project_location_id=location.id,
            value=123,
            calculated_at=datetime.datetime(2021, 12, 3, tzinfo=datetime.timezone.utc),
        )
    )
    await db_session.commit()
    data = await ProjectSafetyClimateMultiplier.explain(
        metrics_manager,
        project_location_id=location.id,
        work_package_manager=work_package_manager,
        contractors_manager=contractors_manager,
    )
    check_inputs_errors_length(data, [0], [2])
    check_error(
        data[0].errors[0],
        SupervisorEngagementFactorModel,
        {
            "supervisor_id": supervisor.id,
            "calculated_before": datetime.datetime(
                2021, 12, 3, 0, 0, tzinfo=datetime.timezone.utc
            ),
        },
    )
    check_error(
        data[0].errors[1],
        ContractorSafetyScoreModel,
        {
            "contractor_id": contractor.id,
            "calculated_before": datetime.datetime(
                2021, 12, 3, 0, 0, tzinfo=datetime.timezone.utc
            ),
        },
    )
    check_no_dependencies(data)

    # Error when Supervisor Engagement Factor does not exist
    db_session.add(
        ProjectSafetyClimateMultiplierModel(
            project_location_id=location.id,
            value=123,
            calculated_at=datetime.datetime(2021, 12, 4, tzinfo=datetime.timezone.utc),
        )
    )
    await db_session.commit()
    data = await ProjectSafetyClimateMultiplier.explain(
        metrics_manager,
        project_location_id=location.id,
        work_package_manager=work_package_manager,
        contractors_manager=contractors_manager,
    )
    check_inputs_errors_length(data, [0], [2])
    check_error(
        data[0].errors[0],
        SupervisorEngagementFactorModel,
        {
            "supervisor_id": supervisor.id,
            "calculated_before": datetime.datetime(
                2021, 12, 4, 0, 0, tzinfo=datetime.timezone.utc
            ),
        },
    )
    check_error(
        data[0].errors[1],
        ContractorSafetyScoreModel,
        {
            "contractor_id": contractor.id,
            "calculated_before": datetime.datetime(
                2021, 12, 4, 0, 0, tzinfo=datetime.timezone.utc
            ),
        },
    )
    check_no_dependencies(data)

    # Store SupervisorEngagementFactor and ContractorSafetyScore, but
    # calculated AFTER the main metric was saved
    db_session.add(
        SupervisorEngagementFactorModel(
            supervisor_id=supervisor.id,
            value=1,
            calculated_at=datetime.datetime(2021, 12, 31, tzinfo=datetime.timezone.utc),
        )
    )
    db_session.add(
        ContractorSafetyScoreModel(
            contractor_id=contractor.id,
            value=2,
            calculated_at=datetime.datetime(2022, 1, 30, tzinfo=datetime.timezone.utc),
        )
    )
    await db_session.commit()
    data = await ProjectSafetyClimateMultiplier.explain(
        metrics_manager,
        project_location_id=location.id,
        work_package_manager=work_package_manager,
        contractors_manager=contractors_manager,
    )
    check_inputs_errors_length(data, [0], [2])
    check_error(
        data[0].errors[0],
        SupervisorEngagementFactorModel,
        {
            "supervisor_id": supervisor.id,
            "calculated_before": datetime.datetime(
                2021, 12, 4, 0, 0, tzinfo=datetime.timezone.utc
            ),
        },
    )
    check_error(
        data[0].errors[1],
        ContractorSafetyScoreModel,
        {
            "contractor_id": contractor.id,
            "calculated_before": datetime.datetime(
                2021, 12, 4, 0, 0, tzinfo=datetime.timezone.utc
            ),
        },
    )
    check_no_dependencies(data)

    # Store a new ProjectSafetyClimateMultiplier saved
    # after the SupervisorEngagementFactor, but before ContractorSafetyScore
    db_session.add(
        ProjectSafetyClimateMultiplierModel(
            project_location_id=location.id,
            value=123,
            calculated_at=datetime.datetime(2022, 1, 5, tzinfo=datetime.timezone.utc),
        )
    )
    await db_session.commit()
    data = await ProjectSafetyClimateMultiplier.explain(
        metrics_manager,
        project_location_id=location.id,
        work_package_manager=work_package_manager,
        contractors_manager=contractors_manager,
    )

    check_inputs_errors_length(data, [1], [1])
    check_error(
        data[0].errors[0],
        ContractorSafetyScoreModel,
        {
            "contractor_id": contractor.id,
            "calculated_before": datetime.datetime(
                2022, 1, 5, 0, 0, tzinfo=datetime.timezone.utc
            ),
        },
    )
    check_input(data[0].inputs[0], SupervisorEngagementFactorModel, dict(value=1))
    check_has_dependencies(data[0], 1)
    if data[0].dependencies is not None:
        check_dependency(data[0].dependencies[0], ["Supervisor Engagement Factor"], [1])

    # Now everything should work properly
    db_session.add(
        ProjectSafetyClimateMultiplierModel(
            project_location_id=location.id,
            value=123,
            calculated_at=datetime.datetime(2022, 2, 1, tzinfo=datetime.timezone.utc),
        )
    )
    await db_session.commit()

    data = await ProjectSafetyClimateMultiplier.explain(
        metrics_manager,
        project_location_id=location.id,
        work_package_manager=work_package_manager,
        contractors_manager=contractors_manager,
    )
    check_successful_test(data, ["Project Safety Climate Multiplier"], [123])
    check_inputs_errors_length(data, [2])
    check_input(data[0].inputs[0], SupervisorEngagementFactorModel, dict(value=1))
    check_input(data[0].inputs[1], ContractorSafetyScoreModel, dict(value=2))
    if data[0].dependencies is not None:
        check_has_dependencies(data[0], 2)
        for dep in data[0].dependencies:
            check_dependency(
                dep,
                ["Supervisor Engagement Factor", "Contractor Safety Score"],
                [1, 2],
            )

    data = await ProjectSafetyClimateMultiplier.explain(
        metrics_manager,
        project_location_id=location.id,
        work_package_manager=work_package_manager,
        contractors_manager=contractors_manager,
        verbose=False,
    )
    check_no_dependencies(data)
