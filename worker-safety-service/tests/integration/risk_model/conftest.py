import datetime
from typing import AsyncGenerator, TypedDict

import pytest
from faker import Faker
from sqlalchemy.orm import sessionmaker

from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.incidents import IncidentsManager
from worker_safety_service.dal.library import LibraryManager
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.site_conditions import SiteConditionManager
from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.risk_model import riskmodel_container
from worker_safety_service.risk_model.riskmodel_container import RiskModelContainer


@pytest.mark.asyncio
@pytest.fixture(autouse=True)
async def app_container(
    async_sessionmaker: sessionmaker,
) -> AsyncGenerator[RiskModelContainer, None]:
    async with riskmodel_container.create_and_wire_with_context(
        async_sessionmaker,
    ) as container:
        container.wire(packages=["..risk_model"])
        yield container


@pytest.fixture
def metrics_manager(app_container: RiskModelContainer) -> RiskModelMetricsManager:
    return app_container.risk_model_metrics_manager()


@pytest.fixture
def library_manager(app_container: RiskModelContainer) -> LibraryManager:
    return app_container.library_manager()


@pytest.fixture
def task_manager(app_container: RiskModelContainer) -> TaskManager:
    return app_container.task_manager()


@pytest.fixture
def work_package_manager(app_container: RiskModelContainer) -> WorkPackageManager:
    return app_container.work_package_manager()


@pytest.fixture
def contractors_manager(app_container: RiskModelContainer) -> ContractorsManager:
    return app_container.contractors_manager()


@pytest.fixture
def supervisors_manager(app_container: RiskModelContainer) -> SupervisorsManager:
    return app_container.supervisors_manager()


@pytest.fixture
def incidents_manager(app_container: RiskModelContainer) -> IncidentsManager:
    return app_container.incidents_manager()


@pytest.fixture
def site_condition_manager(
    app_container: RiskModelContainer,
) -> SiteConditionManager:
    return app_container.site_conditions_manager()


class DateTuple(TypedDict):
    start_date: datetime.date
    end_date: datetime.date


fake = Faker()


def current_period() -> DateTuple:
    return DateTuple(start_date=fake.past_date(), end_date=fake.future_date())


def past_period() -> DateTuple:
    # Add parameters to tune the date range.
    start = fake.date_between(start_date="-30d", end_date="-20d")  # noqa: E731
    end = fake.date_between(start_date="-19d", end_date="-10d")  # noqa: E731
    return DateTuple(start_date=start, end_date=end)


def future_period() -> DateTuple:
    # Add parameters to tune the date range.
    start = fake.date_between(start_date="+1d", end_date="+7d")  # noqa: E731
    end = fake.date_between(start_date="+8d", end_date="+10d")  # noqa: E731
    return DateTuple(start_date=start, end_date=end)
