import uuid
from datetime import date
from typing import Any, Callable, Coroutine, Dict, Optional, Tuple, TypeVar
from unittest.mock import MagicMock

import pytest
from sqlmodel import select

from worker_safety_service.context import Info
from worker_safety_service.dal.site_conditions import SiteConditionManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.graphql.common import OrderByInput
from worker_safety_service.graphql.queries.resolvers import (  # get_tasks_for_project_location,
    get_project_by_id,
    get_site_conditions,
)
from worker_safety_service.graphql.types import (  # TaskType,
    ProjectType,
    SiteConditionType,
)
from worker_safety_service.models import (
    AsyncSession,
    LibraryDivision,
    LibraryProjectType,
    LibraryRegion,
    LibrarySiteCondition,
    SiteCondition,
    WorkPackage,
    WorkType,
)

T = TypeVar("T")
U = TypeVar("U")

LIBRARY_SITE_CONDITION_ID_1 = LibrarySiteCondition(
    id=uuid.uuid4(), name="cnd_1", handle_code="code_1"
)
LIBRARY_SITE_CONDITION_ID_2 = LibrarySiteCondition(
    id=uuid.uuid4(), name="cnd_2", handle_code="code_2"
)


# Base method that sets up the mocking environment and checks the list is properly constructed according to the
# specified adapter and if None values are properly mapped to an empty list.
@pytest.mark.asyncio
@pytest.mark.unit
async def __test_resolver_list_method(
    known_data: list[T],
    entity_manager_type: type,
    method: Callable[
        [Info, Optional[uuid.UUID], Optional[uuid.UUID], Optional[list[OrderByInput]]],
        Coroutine[Any, Any, list[SiteConditionType]],
    ],
    result_adapter: Callable[[T], U],
) -> None:
    mocked_methods_lookup_table: Dict[type, Tuple[str, str]] = {
        SiteConditionManager: ("site_condition_manager", "get_site_conditions"),
        TaskManager: ("task_manager", "get_tasks"),
    }

    assert entity_manager_type in mocked_methods_lookup_table
    (manager_name, getter_name) = mocked_methods_lookup_table[entity_manager_type]

    scm = MagicMock(spec=entity_manager_type)
    scm.__getattr__(getter_name).return_value = known_data
    info = MagicMock()
    info.context = {manager_name: scm}

    # TODO: Test multiple options id+date OR id OR location_id+date OR location_id
    location_id = uuid.uuid4()
    # Should have tested with date = null but mypy didn't allow
    r = method(info, None, location_id, None)

    expected = [] if known_data is None else [result_adapter(sc) for sc in known_data]
    assert r == expected


# TODO: Check when the context raises an Error. Strawberry will expose the errors in the API directly.
# Looking at the documentation if the project does not exist we should raise a custom exception.
@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.skip(reason="get_project_by_id requires an async test framework")
async def test_get_project_by_id_success(db_session: AsyncSession) -> None:
    project_id = uuid.uuid4()
    library_region = (await db_session.exec(select(LibraryRegion))).first()
    assert library_region
    library_division = (await db_session.exec(select(LibraryDivision))).first()
    assert library_division
    library_project_type = (await db_session.exec(select(LibraryProjectType))).first()
    assert library_project_type
    work_type = (await db_session.exec(select(WorkType))).first()
    assert work_type

    a_project = WorkPackage(
        id=project_id,
        name="test_project",
        start_date=date(year=2000, month=1, day=1),
        end_date=date(year=2001, month=1, day=1),
        number="0",
        region_id=library_region.id,
        division_id=library_division.id,
        work_type_id=library_project_type.id,
        work_type_ids=[work_type.id],
        locations=[],
    )
    # Started Mocking
    pm = MagicMock(spec=WorkPackageManager)
    pm.get_project.return_value = a_project

    info = MagicMock()
    info.context = {"work_package_manager": pm}
    # Ended mocking!!!

    r = get_project_by_id(info, project_id)

    pm.get_project.assert_called_with(project_id)

    # TODO: This is basically copy pasta.
    # Need to check if there is a away to specify this object most be the same as the other one by fields.
    assert r == ProjectType.from_orm(a_project)


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.skip(
    reason="should this be migrated to integrations? it's calling an graphql query, easier if just done on integrations"
)
@pytest.mark.parametrize(
    "known_site_conditions",
    [
        ([]),
        (
            [
                (
                    LIBRARY_SITE_CONDITION_ID_1,
                    SiteCondition(
                        id=uuid.uuid4(),
                        library_site_condition_id=LIBRARY_SITE_CONDITION_ID_1.id,
                        date=date.today(),
                        is_manually_added=False,
                    ),
                ),
                (
                    LIBRARY_SITE_CONDITION_ID_2,
                    SiteCondition(
                        id=uuid.uuid4(),
                        library_site_condition_id=LIBRARY_SITE_CONDITION_ID_2.id,
                        date=date.today(),
                        is_manually_added=False,
                    ),
                ),
            ]
        ),
    ],
)
async def test_get_site_conditions_for_project_location(
    known_site_conditions: list[tuple[LibrarySiteCondition, SiteCondition]],
) -> None:
    def expected_adapter(
        a_site_condition: tuple[LibrarySiteCondition, SiteCondition],
    ) -> SiteConditionType:
        assert a_site_condition is not None
        _, site_condition = a_site_condition
        assert site_condition.id is not None
        return SiteConditionType.from_orm(site_condition)

    await __test_resolver_list_method(
        known_site_conditions,
        SiteConditionManager,
        get_site_conditions,
        expected_adapter,
    )


# @pytest.mark.unit
# @pytest.mark.parametrize(
#     "known_tasks",
#     [
#         (None),
#         ([]),
#         ([Task(id=uuid.uuid4(), name="task_1"), Task(id=uuid.uuid4(), name="task_2")]),
#     ],
# )
# def test_get_tasks_for_project_location(known_tasks: list[Task]) -> None:
#     def expected_adapter(a_task: Task) -> TaskType:
#         assert a_task.id is not None
#         return TaskType(id=a_task.id, name=a_task.name, risk_level=RiskLevel.HIGH)

#     __test_resolver_list_method(
#         known_tasks, TaskManager, get_tasks_for_project_location, expected_adapter
#     )
