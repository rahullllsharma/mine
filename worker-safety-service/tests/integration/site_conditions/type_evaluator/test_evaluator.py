import pytest

from tests.integration.site_conditions.type_evaluator.helpers import (
    generate_location_response,
    get_library_site_condition,
)
from worker_safety_service.models import AsyncSession
from worker_safety_service.site_conditions import SiteConditionsEvaluator
from worker_safety_service.site_conditions.types import SiteConditionHandleCode


@pytest.mark.asyncio
@pytest.mark.integration
async def test_empty(evaluator: SiteConditionsEvaluator) -> None:
    manual_response = evaluator.evaluate_manual_site_conditions([])
    assert manual_response == []

    automatic_response = await evaluator.evaluate_automatic_site_conditions([], {})
    assert automatic_response == []


@pytest.mark.asyncio
@pytest.mark.integration
async def test_missing_section_ok(
    db_session: AsyncSession, evaluator: SiteConditionsEvaluator
) -> None:
    library_site_condition = await get_library_site_condition(
        db_session, SiteConditionHandleCode.population_density
    )
    world_data = generate_location_response(sources={"slope"}, slope=10)
    world_data_dict = {0: world_data}
    response = await evaluator.evaluate_automatic_site_conditions(
        [library_site_condition], world_data_dict
    )

    assert len(response) == 0
