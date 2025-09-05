import pytest

from tests.integration.site_conditions.type_evaluator.helpers import (
    generate_location_response,
    get_library_site_condition,
)
from worker_safety_service.models import AsyncSession
from worker_safety_service.site_conditions import SiteConditionsEvaluator
from worker_safety_service.site_conditions.types import (
    MajorRoadwayClassification,
    SiteConditionHandleCode,
)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "data",
    [
        (0.0, [], []),
        # multiplier uses biggest multiplier
        (
            0.1,
            [MajorRoadwayClassification.motorway, MajorRoadwayClassification.busway],
            [MajorRoadwayClassification.motorway, MajorRoadwayClassification.busway],
        ),
        (
            0.1,
            [MajorRoadwayClassification.motorway, "minor_classification_1"],
            [MajorRoadwayClassification.motorway],
        ),
        (0.0, ["minor_classification_1", "minor_classification_2"], []),
    ],
)
async def test_roadway(
    data: tuple[
        float, list[MajorRoadwayClassification], list[MajorRoadwayClassification]
    ],
    db_session: AsyncSession,
    evaluator: SiteConditionsEvaluator,
) -> None:
    (multiplier, classifications, major_classifications) = data
    applies = bool(multiplier)
    library_site_condition = await get_library_site_condition(
        db_session, SiteConditionHandleCode.roadway
    )
    world_data = generate_location_response(
        sources={"roadway"}, roadway_classifications=classifications  # type: ignore
    )
    world_data_dict = {0: world_data}
    response = await evaluator.evaluate_automatic_site_conditions(
        [library_site_condition], world_data_dict
    )
    assert len(response) == 1
    site_condition = response[0][1]
    assert site_condition.condition_name == SiteConditionHandleCode.roadway
    assert site_condition.condition_value["classifications"] == classifications
    assert set(site_condition.condition_value["major_classifications"]) == set(
        major_classifications
    )
    assert site_condition.condition_applies == applies
    assert site_condition.multiplier == multiplier
    assert site_condition.alert is applies
