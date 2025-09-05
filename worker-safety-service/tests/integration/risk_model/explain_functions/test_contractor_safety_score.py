import datetime
from unittest.mock import Mock

import pytest

from tests.factories import ContractorFactory
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
from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models import (
    AsyncSession,
    ContractorProjectExecutionModel,
    ContractorSafetyHistoryModel,
    ContractorSafetyRatingModel,
    ContractorSafetyScoreModel,
)
from worker_safety_service.risk_model.metrics.contractor.contractor_safety_score import (
    ContractorSafetyScore,
    ContractorSafetyScoreInput,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_contractor_safety_score_explain_method(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    contractors_manager: ContractorsManager,
) -> None:
    contractors_manager.get_contractor_experience_years = Mock(return_value=123456)  # type: ignore
    contractor = await ContractorFactory.persist(db_session)
    data = await ContractorSafetyScore.explain(
        metrics_manager,
        contractor_id=contractor.id,
        contractors_manager=contractors_manager,
    )
    check_data(data, ["Contractor Safety Score"])
    check_inputs_errors_length(data, [0], [1])
    check_error(
        data[0].errors[0],
        ContractorSafetyScoreModel,
        {
            "contractor_id": contractor.id,
            "calculated_before": None,
        },
    )
    check_no_dependencies(data)

    db_session.add(
        ContractorSafetyScoreModel(
            contractor_id=contractor.id,
            value=123,
            calculated_at=datetime.datetime(2021, 12, 1, tzinfo=datetime.timezone.utc),
        )
    )
    await db_session.commit()
    data = await ContractorSafetyScore.explain(
        metrics_manager,
        contractor_id=contractor.id,
        contractors_manager=contractors_manager,
    )
    check_inputs_errors_length(data, [1], [3])
    inputs: dict[str, float | None] = dict(
        contractor_safety_history=None,
        contractor_project_execution=None,
        contractor_safety_rating=None,
    )
    check_input(data[0].inputs[0], ContractorSafetyScoreInput, inputs)

    for err in data[0].errors:
        check_error(
            err,
            [
                ContractorSafetyHistoryModel,
                ContractorProjectExecutionModel,
                ContractorSafetyRatingModel,
            ],
            {
                "contractor_id": contractor.id,
                "calculated_before": datetime.datetime(
                    2021, 12, 1, 0, 0, tzinfo=datetime.timezone.utc
                ),
            },
        )
    check_no_dependencies(data)

    db_session.add(
        ContractorSafetyHistoryModel(
            contractor_id=contractor.id,
            value=1,
            calculated_at=datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc),
        )
    )
    await db_session.commit()

    data = await ContractorSafetyScore.explain(
        metrics_manager,
        contractor_id=contractor.id,
        contractors_manager=contractors_manager,
    )
    check_inputs_errors_length(data, [1], [3])
    check_input(data[0].inputs[0], ContractorSafetyScoreInput, inputs)

    for err in data[0].errors:
        check_error(
            err,
            [
                ContractorSafetyHistoryModel,
                ContractorProjectExecutionModel,
                ContractorSafetyRatingModel,
            ],
            {
                "contractor_id": contractor.id,
                "calculated_before": datetime.datetime(
                    2021, 12, 1, 0, 0, tzinfo=datetime.timezone.utc
                ),
            },
        )
    check_no_dependencies(data)

    db_session.add(
        ContractorSafetyScoreModel(
            contractor_id=contractor.id,
            value=123,
            calculated_at=datetime.datetime(2022, 1, 31, tzinfo=datetime.timezone.utc),
        )
    )
    await db_session.commit()

    data = await ContractorSafetyScore.explain(
        metrics_manager,
        contractor_id=contractor.id,
        contractors_manager=contractors_manager,
    )
    check_inputs_errors_length(data, [1], [2])
    inputs["contractor_safety_history"] = 1
    check_input(data[0].inputs[0], ContractorSafetyScoreInput, inputs)

    if data[0].errors is not None:
        for err in data[0].errors:
            check_error(
                err,
                [
                    ContractorProjectExecutionModel,
                    ContractorSafetyRatingModel,
                ],
                {
                    "contractor_id": contractor.id,
                    "calculated_before": datetime.datetime(
                        2022, 1, 31, 0, 0, tzinfo=datetime.timezone.utc
                    ),
                },
            )
    check_has_dependencies(data[0], 1)
    if data[0].dependencies is not None:
        check_dependency(data[0].dependencies[0], ["Contractor Safety History"], [1])

    db_session.add(
        ContractorProjectExecutionModel(
            contractor_id=contractor.id,
            value=2,
            calculated_at=datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc),
        )
    )
    await db_session.commit()

    data = await ContractorSafetyScore.explain(
        metrics_manager,
        contractor_id=contractor.id,
        contractors_manager=contractors_manager,
    )
    check_inputs_errors_length(data, [1], [1])
    inputs["contractor_project_execution"] = 2
    check_input(data[0].inputs[0], ContractorSafetyScoreInput, inputs)

    check_error(
        data[0].errors[0],
        ContractorSafetyRatingModel,
        {
            "contractor_id": contractor.id,
            "calculated_before": datetime.datetime(
                2022, 1, 31, 0, 0, tzinfo=datetime.timezone.utc
            ),
        },
    )

    check_has_dependencies(data[0], 2)
    if data[0].dependencies is not None:
        check_dependency(
            data[0].dependencies[0],
            ["Contractor Safety History", "Contractor Project Execution"],
            [1, 2],
        )

    db_session.add(
        ContractorSafetyRatingModel(
            contractor_id=contractor.id,
            value=3,
            calculated_at=datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc),
        )
    )
    await db_session.commit()

    data = await ContractorSafetyScore.explain(
        metrics_manager,
        contractor_id=contractor.id,
        contractors_manager=contractors_manager,
    )
    check_successful_test(data, ["Contractor Safety Score"], [123])
    check_inputs_errors_length(data, [1], [0])
    inputs["contractor_safety_rating"] = 3
    check_input(data[0].inputs[0], ContractorSafetyScoreInput, inputs)

    check_has_dependencies(data[0], 3)
    if data[0].dependencies is not None:
        check_dependency(
            data[0].dependencies[0],
            [
                "Contractor Safety History",
                "Contractor Project Execution",
                "Contractor Safety Rating",
            ],
            [1, 2, 3],
        )

    data = await ContractorSafetyScore.explain(
        metrics_manager,
        contractor_id=contractor.id,
        contractors_manager=contractors_manager,
        verbose=False,
    )
    check_no_dependencies(data)
