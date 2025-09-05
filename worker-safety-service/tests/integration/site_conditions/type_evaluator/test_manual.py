import pytest

from worker_safety_service.dal.library_site_conditions import (
    LibrarySiteConditionManager,
)
from worker_safety_service.site_conditions import SiteConditionsEvaluator


@pytest.mark.asyncio
@pytest.mark.integration
async def test_manual_site_conditions(
    evaluator: SiteConditionsEvaluator,
    library_site_condition_manager: LibrarySiteConditionManager,
) -> None:
    """Manual site conditions should always apply and have a multiplier set to its default multiplier"""
    library_site_conditions = (
        await library_site_condition_manager.get_library_site_conditions(
            allow_archived=False
        )
    )

    response = evaluator.evaluate_manual_site_conditions(
        site_conditions=library_site_conditions
    )
    assert len(response) == len(library_site_conditions)

    for library_site_condition, site_condition_result in response:
        assert (
            site_condition_result.condition_name == library_site_condition.handle_code
        )
        assert site_condition_result.condition_value is None
        assert site_condition_result.condition_applies is True
        assert (
            site_condition_result.multiplier
            == library_site_condition.default_multiplier
        )
        assert site_condition_result.alert is True
