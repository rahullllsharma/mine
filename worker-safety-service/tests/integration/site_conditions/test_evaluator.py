import random
from collections.abc import Iterable
from datetime import date as DATE
from datetime import datetime
from operator import attrgetter, itemgetter
from unittest.mock import AsyncMock, Mock

import pytest

from tests.factories import LocationFactory, SiteConditionFactory
from tests.integration.site_conditions.type_evaluator.helpers import (
    call_world_data_side_effect,
)
from worker_safety_service.dal.library_site_conditions import (
    LibrarySiteConditionManager,
)
from worker_safety_service.dal.site_conditions import SiteConditionManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.models import AsyncSession, LibrarySiteCondition
from worker_safety_service.models import Location as ProjectLocation
from worker_safety_service.site_conditions import SiteConditionsEvaluator
from worker_safety_service.site_conditions.world_data import LocationResponse


@pytest.mark.asyncio
async def test_evaluate_location_only_saves_automatic_evaluations(
    db_session: AsyncSession,
    library_site_condition_manager: LibrarySiteConditionManager,
) -> None:
    location = await LocationFactory.persist(db_session)
    _date = datetime.today()

    all_site_conditions = (
        await library_site_condition_manager.get_library_site_conditions(
            allow_archived=False
        )
    )

    manually_added_site_conditions = random.sample(all_site_conditions, k=3)
    for lsc in manually_added_site_conditions:
        all_site_conditions.remove(lsc)

    site_condition_manager = AsyncMock()
    site_condition_manager.get_manually_added_site_conditions.return_value = [
        # The second value should not be needed
        (lsc, None)
        for lsc in manually_added_site_conditions
    ]

    site_conditions_evaluator = SiteConditionsEvaluator(
        work_package_manager=AsyncMock(),
        site_conditions_manager=site_condition_manager,
        task_manager=AsyncMock(),
        library_site_condition_manager=library_site_condition_manager,
    )

    site_conditions_evaluator.call_world_data = AsyncMock(  # type: ignore
        side_effect=call_world_data_side_effect
    )

    result = await site_conditions_evaluator.evaluate_location(location, _date)

    # Only auto site conditions should be saved
    site_condition_manager.set_evaluated_site_conditions.assert_called_once()
    args = site_condition_manager.set_evaluated_site_conditions.call_args

    library_site_condition_ids_to_store = [
        lsc.id
        for lsc, _ in result
        if lsc.id not in map(attrgetter("id"), manually_added_site_conditions)
    ]

    site_conditions_ids_to_store = list(
        map(attrgetter("id"), map(itemgetter(0), args.kwargs["site_conditions"]))
    )

    assert site_conditions_ids_to_store == library_site_condition_ids_to_store


@pytest.mark.asyncio
@pytest.mark.integration
async def test_evaluate_project_location_must_check_all_site_conditions(
    db_session: AsyncSession,
    work_package_manager: WorkPackageManager,
    library_site_condition_manager: LibrarySiteConditionManager,
    site_condition_manager: SiteConditionManager,
    task_manager: TaskManager,
) -> None:
    today = DATE.today()
    project_location: ProjectLocation = await LocationFactory.persist(db_session)

    all_site_conditions = (
        await library_site_condition_manager.get_library_site_conditions(
            allow_archived=False
        )
    )
    manually_added_site_conditions = random.sample(all_site_conditions, k=3)

    for library_site_condition in manually_added_site_conditions:
        await SiteConditionFactory.persist(
            db_session,
            location_id=project_location.id,
            library_site_condition_id=library_site_condition.id,
        )

    site_conditions_to_evaluate = [
        lsc for lsc in all_site_conditions if lsc not in manually_added_site_conditions
    ]

    site_conditions_evaluator = SiteConditionsEvaluator(
        work_package_manager=work_package_manager,
        site_conditions_manager=site_condition_manager,
        task_manager=task_manager,
        library_site_condition_manager=library_site_condition_manager,
    )
    site_conditions_evaluator.call_world_data = AsyncMock(  # type: ignore
        side_effect=call_world_data_side_effect
    )

    def return_empty_array(
        site_conditions: Iterable[LibrarySiteCondition],
        world_data: dict[int, LocationResponse],
    ) -> list:
        return []

    site_conditions_evaluator.evaluate_manual_site_conditions = Mock(  # type: ignore
        return_value=[]
    )
    site_conditions_evaluator.evaluate_automatic_site_conditions = AsyncMock(  # type: ignore
        side_effect=return_empty_array
    )

    await site_conditions_evaluator.evaluate_location(project_location, today)

    site_conditions_evaluator.evaluate_manual_site_conditions.assert_called_once()
    site_conditions_evaluator.evaluate_automatic_site_conditions.assert_called_once()

    evaluate_manual_args = (
        site_conditions_evaluator.evaluate_manual_site_conditions.call_args.args[0]
    )
    evaluated_manual_ids = {i.id for i in evaluate_manual_args}
    expected_manual_ids = {i.id for i in manually_added_site_conditions}

    assert len(evaluate_manual_args) == len(manually_added_site_conditions)
    assert evaluated_manual_ids == expected_manual_ids

    evaluate_automatic_args = (
        site_conditions_evaluator.evaluate_automatic_site_conditions.call_args.args[0]
    )
    evaluated_automatic_ids = {i.id for i in evaluate_automatic_args}
    expected_automatic_ids = {i.id for i in site_conditions_to_evaluate}

    assert len(evaluate_automatic_args) == len(site_conditions_to_evaluate)
    assert evaluated_automatic_ids == expected_automatic_ids
