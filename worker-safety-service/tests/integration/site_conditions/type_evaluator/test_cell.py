import pytest

from tests.integration.site_conditions.type_evaluator.helpers import (
    generate_location_response,
    get_library_site_condition,
)
from worker_safety_service.models import AsyncSession
from worker_safety_service.site_conditions import SiteConditionsEvaluator
from worker_safety_service.site_conditions.types import (
    MajorCarrier,
    SiteConditionHandleCode,
)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "data",
    [
        (0.05, [], set()),
        (0.0, [MajorCarrier.att], [MajorCarrier.att]),
        (
            0.0,
            [MajorCarrier.att, MajorCarrier.tmobile],
            [MajorCarrier.att, MajorCarrier.tmobile],
        ),
        (0.05, ["unknown_carrier"], []),
        (0.05, ["unknown_carrier_1", "unknown_carrier_2"], []),
        (0.0, [MajorCarrier.att, "unknown_carrier"], [MajorCarrier.att]),
    ],
)
async def test_cellular_coverage(
    data: tuple[float, list[str], set[MajorCarrier]],
    db_session: AsyncSession,
    evaluator: SiteConditionsEvaluator,
) -> None:
    (multiplier, carriers, major_carriers) = data
    applies = bool(multiplier)

    library_site_condition = await get_library_site_condition(
        db_session, SiteConditionHandleCode.cell_coverage
    )
    world_data = generate_location_response(sources={"cellCoverage"}, carriers=carriers)
    world_data_dict = {0: world_data}
    response = await evaluator.evaluate_automatic_site_conditions(
        [library_site_condition], world_data_dict
    )

    assert len(response) == 1
    site_condition = response[0][1]
    assert site_condition.condition_name == SiteConditionHandleCode.cell_coverage
    assert site_condition.condition_value["carriers"] == carriers
    assert set(site_condition.condition_value["major_carriers"]) == set(major_carriers)
    assert site_condition.condition_applies == applies
    assert site_condition.multiplier == multiplier
    assert site_condition.alert is applies
