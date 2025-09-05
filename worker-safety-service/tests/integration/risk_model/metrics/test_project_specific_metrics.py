import asyncio
import datetime
import random
import uuid
from typing import NamedTuple
from unittest.mock import AsyncMock, Mock

import pytest
from faker import Faker

from tests.db_data import DBData
from tests.factories import LocationFactory, WorkPackageFactory
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.site_conditions import SiteConditionManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.models import (
    AsyncSession,
    LibrarySiteCondition,
    ProjectLocationSiteConditionsMultiplierModel,
    TotalProjectLocationRiskScoreModel,
    WorkPackage,
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
from worker_safety_service.risk_model.metrics.tasks.project_location_total_task_riskscore import (
    ProjectLocationTotalTaskRiskScore,
)
from worker_safety_service.site_conditions import (
    SiteConditionResult,
    SiteConditionsEvaluator,
)

fake = Faker()


class SampleProject(NamedTuple):
    project: WorkPackage


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_site_conditions_multiplier(
    metrics_manager: RiskModelMetricsManager,
    work_package_manager: WorkPackageManager,
    sample_project: SampleProject,
) -> None:
    project_location = sample_project.project.locations[1]
    today = datetime.date.today()

    sc1 = LibrarySiteCondition(name="sc1", handle_code="sc_1")
    sc2 = LibrarySiteCondition(name="sc2", handle_code="sc_2")
    sc3 = LibrarySiteCondition(name="sc3", handle_code="sc_3")
    site_conditions_evaluations: list[
        tuple[LibrarySiteCondition, SiteConditionResult]
    ] = [
        (
            sc1,
            SiteConditionResult(
                condition_name="sc1",
                condition_value=str(random.randrange(100)),
                condition_applies=True,
                multiplier=48,
            ),
        ),
        (
            sc2,
            SiteConditionResult(
                condition_name="sc2",
                condition_value=str(random.randrange(100)),
                condition_applies=True,
                multiplier=2,
            ),
        ),
        (
            sc3,
            SiteConditionResult(
                condition_name="sc3",
                condition_value=str(random.randrange(100)),
                condition_applies=False,
                multiplier=16,
            ),
        ),
    ]

    site_conditions: list[tuple[LibrarySiteCondition, None]] = [
        (sc1, None),
        (sc2, None),
        (sc3, None),
    ]

    site_conditions_manager: SiteConditionManager = Mock(spec=SiteConditionManager)
    site_conditions_manager.get_site_conditions = AsyncMock(return_value=site_conditions)  # type: ignore

    site_conditions_evaluator: SiteConditionsEvaluator = Mock(
        spec=SiteConditionsEvaluator
    )
    site_conditions_evaluator.evaluate_location = AsyncMock(return_value=site_conditions_evaluations)  # type: ignore

    metric = ProjectLocationSiteConditionsMultiplier(
        metrics_manager,
        work_package_manager,
        site_conditions_manager,
        site_conditions_evaluator,
        project_location.id,
        today,
    )

    await metric.run()

    actual = await ProjectLocationSiteConditionsMultiplier.load(
        metrics_manager, project_location.id, today
    )
    expected = ProjectLocationSiteConditionsMultiplierModel(
        project_location_id=project_location.id, date=today, value=50
    )
    assert (
        actual.project_location_id == expected.project_location_id
        and actual.date == expected.date
        and actual.value == expected.value
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_total_project_location_risk_score(
    metrics_manager: RiskModelMetricsManager,
    work_package_manager: WorkPackageManager,
    sample_project: SampleProject,
) -> None:
    date = datetime.date.today()

    contractor_id = uuid.uuid4()
    supervisor_id = uuid.uuid4()
    project_location_id = sample_project.project.locations[1].id

    await asyncio.gather(
        ProjectSafetyClimateMultiplier.store(
            metrics_manager,
            project_location_id,
            1.234,
            contractor_id,
            supervisor_id,
        ),
        ProjectLocationSiteConditionsMultiplier.store(
            metrics_manager, project_location_id, date, 0.75
        ),
        ProjectLocationTotalTaskRiskScore.store(
            metrics_manager, project_location_id, date, 80
        ),
    )

    metric = TotalProjectLocationRiskScore(
        metrics_manager,
        work_package_manager,
        project_location_id,
        date,
    )

    await metric.run()

    actual = await TotalProjectLocationRiskScore.load(
        metrics_manager, project_location_id, date
    )
    expected = TotalProjectLocationRiskScoreModel(
        project_location_id=project_location_id, date=date, value=238.72
    )

    assert (
        actual.project_location_id == expected.project_location_id
        and actual.date == expected.date
        and actual.value == expected.value
    )


@pytest.fixture
async def sample_project(db_session: AsyncSession) -> SampleProject:
    project: WorkPackage = await WorkPackageFactory.persist(
        db_session, start_date=fake.date_between(start_date="+0d", end_date="+7d")
    )
    await LocationFactory.persist_many(db_session, size=3, project_id=project.id)
    return SampleProject(
        await DBData(db_session).project(project.id, load_locations=True)
    )
