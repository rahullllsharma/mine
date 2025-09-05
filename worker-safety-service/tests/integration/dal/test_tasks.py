import uuid
from random import choice
from typing import Optional, Tuple

import pytest

from tests.factories import (
    ActivityFactory,
    LibraryTaskFactory,
    LocationFactory,
    TaskFactory,
    TenantFactory,
    WorkPackageFactory,
)
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.models import (
    AsyncSession,
    LibraryTask,
    Location,
    Task,
    TaskCreate,
    TaskStatus,
    WorkPackage,
)


def random_case_string(val: str = "") -> str:
    return "".join(map(choice, zip(val.lower(), val.upper())))


async def setup_project_and_location(
    db_session: AsyncSession,
    project: Optional[WorkPackage] = None,
    location: Optional[Location] = None,
) -> Tuple[WorkPackage, Location]:
    project = project or await WorkPackageFactory.persist(db_session)
    location = location or await LocationFactory.persist(
        db_session, project_id=project.id
    )
    return project, location


async def setup_test(
    db_session: AsyncSession,
    project: Optional[WorkPackage] = None,
    location: Optional[Location] = None,
    name: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[TaskStatus] = None,
) -> Tuple[LibraryTask, uuid.UUID, str, TaskStatus]:
    if project is None or location is None:
        project, location = await setup_project_and_location(
            db_session, project=project, location=location
        )

    task_kwargs = dict(category=category)
    if not category:
        category = uuid.uuid4().hex
        task_kwargs["category"] = category
    if name is not None:
        task_kwargs["name"] = name
    library_task = await LibraryTaskFactory.persist(db_session, **task_kwargs)

    if not status:
        status = TaskStatus.NOT_STARTED

    task = await TaskFactory.persist(
        db_session,
        library_task_id=library_task.id,
        library_task=library_task,
        location_id=location.id,
        location=location,
        status=status,
    )
    return (
        library_task,
        task.location.id,
        category,
        task.status,
    )


async def check_equality(
    task_manager: TaskManager,
    search: str,
    task_id: uuid.UUID,
    location_id: uuid.UUID | None = None,
    tenant_id: uuid.UUID | None = None,
    results_length: int = 1,
) -> None:
    results = await task_manager.get_tasks(
        location_ids=[location_id] if location_id else None,
        tenant_id=tenant_id,
        search=search,
    )
    assert len(results) == results_length
    assert results[-1][0].id == task_id


async def check_no_equality(
    task_manager: TaskManager,
    location_id: uuid.UUID | None = None,
    tenant_id: uuid.UUID | None = None,
    search: Optional[str] = None,
) -> None:
    if search is None:
        search = uuid.uuid4().hex
    no_results = await task_manager.get_tasks(
        location_ids=[location_id] if location_id else None,
        search=search,
        tenant_id=tenant_id,
    )
    assert len(no_results) == 0


async def check_case_insensitive_equality(
    task_manager: TaskManager,
    search: str,
    task_id: uuid.UUID,
    location_id: uuid.UUID | None = None,
    tenant_id: uuid.UUID | None = None,
    results_length: int = 1,
) -> None:
    results = await task_manager.get_tasks(
        location_ids=[location_id] if location_id else None,
        search=random_case_string(search),
        tenant_id=tenant_id,
    )
    assert len(results) == results_length
    assert results[-1][0].id == task_id


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_get_tasks_search_by_name(
    db_session: AsyncSession, task_manager: TaskManager
) -> None:
    task, location_id, _, _ = await setup_test(db_session)
    await check_equality(
        task_manager, search=task.name, task_id=task.id, location_id=location_id
    )
    await check_no_equality(task_manager, location_id=location_id)
    await check_case_insensitive_equality(
        task_manager, search=task.name, task_id=task.id, location_id=location_id
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_get_tasks_search_by_category(
    db_session: AsyncSession, task_manager: TaskManager
) -> None:
    task, location_id, category, _ = await setup_test(db_session)
    await check_equality(
        task_manager, search=category, task_id=task.id, location_id=location_id
    )
    await check_no_equality(task_manager, location_id=location_id)
    await check_case_insensitive_equality(
        task_manager, search=category, task_id=task.id, location_id=location_id
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_get_tasks_search_by_status(
    db_session: AsyncSession, task_manager: TaskManager
) -> None:
    task, location_id, _, status = await setup_test(db_session)
    await check_equality(
        task_manager, search=status, task_id=task.id, location_id=location_id
    )
    await check_no_equality(task_manager, location_id=location_id)
    await check_case_insensitive_equality(
        task_manager, search=status, task_id=task.id, location_id=location_id
    )

    await check_no_equality(task_manager, search="complete", location_id=location_id)
    await check_no_equality(
        task_manager, search="not_completed", location_id=location_id
    )
    await check_no_equality(
        task_manager, search="Not Completed", location_id=location_id
    )
    await check_no_equality(task_manager, search="in_progress", location_id=location_id)
    await check_no_equality(task_manager, search="In-Progress", location_id=location_id)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_get_tasks_search_by_status_no_location_filter(
    db_session: AsyncSession, task_manager: TaskManager
) -> None:
    tenant = await TenantFactory.persist(db_session)
    project = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)

    task, _, _, status = await setup_test(db_session, project=project)
    await check_equality(
        task_manager, search=status, task_id=task.id, tenant_id=tenant.id
    )
    await check_no_equality(task_manager, tenant_id=tenant.id)
    await check_case_insensitive_equality(
        task_manager, search=status, task_id=task.id, tenant_id=tenant.id
    )

    await check_no_equality(task_manager, search="complete", tenant_id=tenant.id)
    await check_no_equality(task_manager, search="not_completed", tenant_id=tenant.id)
    await check_no_equality(task_manager, search="Not Completed", tenant_id=tenant.id)
    await check_no_equality(task_manager, search="in_progress", tenant_id=tenant.id)
    await check_no_equality(task_manager, search="In-Progress", tenant_id=tenant.id)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_partial_text_search(
    db_session: AsyncSession, task_manager: TaskManager
) -> None:
    names = [
        "Aliquam erat complete volutpat.",
        "Pellentesquenot commodo lorem",
        "Proin started et mauris",
        "Maecenas in-progress ornare sem",
        "Quisque facilisis arcu",
    ]
    categories = [
        "nunc mattis iaculis",
        "ullamcorper etprog id erat",
        "vitae completeddictum bibendum",
        "in finibus pharetra",
        "iaculisstarted elit vitae",
    ]
    statuses = [
        None,
        TaskStatus.NOT_STARTED,
        TaskStatus.COMPLETE,
        TaskStatus.IN_PROGRESS,
        TaskStatus.NOT_COMPLETED,
    ]  # "not StaRted", "completed", "In Progress", "complete"]

    created_items = []
    project, location = await setup_project_and_location(db_session)
    for name, category, status in zip(names, categories, statuses):
        task, _, cat, stat = await setup_test(
            db_session,
            project=project,
            location=location,
            name=name,
            category=category,
            status=status,
        )
        created_items.append(
            dict(task=task, location_id=location.id, category=cat, status=stat)
        )
    _tests = [
        ("completed", 2),
        ("not", 3),
        ("started", 4),
        ("In Progress", 1),
        ("prog", 2),
        ("com", 4),
    ]
    for _test in _tests:
        results = await task_manager.get_tasks(
            location_ids=[location.id], search=_test[0]
        )
        assert len(results) == _test[1]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_validate_task(
    db_session: AsyncSession, task_manager: TaskManager
) -> None:
    location = await LocationFactory.persist(db_session)
    activity = await ActivityFactory.persist(db_session, location_id=location.id)
    lt_1, lt_2 = await LibraryTaskFactory.persist_many(db_session, size=2)
    task = await TaskFactory.persist(
        db_session,
        activity_id=activity.id,
        location_id=location.id,
        library_task_id=lt_1.id,
        start_date=activity.start_date,
        end_date=activity.end_date,
    )

    task_create = [
        TaskCreate(activity_id=activity.id, hazards=[], library_task_id=lt_1.id),
        TaskCreate(activity_id=activity.id, hazards=[], library_task_id=lt_2.id),
    ]
    create, existing = await task_manager.validate_tasks(
        task_create, location.tenant_id
    )
    assert len(create) == 1
    assert isinstance(create[0], TaskCreate)
    assert create[0].start_date == activity.start_date
    assert create[0].end_date == activity.end_date
    assert create[0].location_id == location.id
    assert create[0].library_task_id == lt_2.id
    assert len(existing) == 1
    assert isinstance(existing[0], Task)
    assert existing[0].start_date == activity.start_date
    assert existing[0].end_date == activity.end_date
    assert existing[0].location_id == location.id
    assert existing[0].library_task_id == lt_1.id
    assert existing[0].id == task.id

    tenant = await TenantFactory.persist(db_session)
    with pytest.raises(ResourceReferenceException):
        create, existing = await task_manager.validate_tasks(task_create, tenant.id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_validate_task_with_duplicates(
    db_session: AsyncSession, task_manager: TaskManager
) -> None:
    location = await LocationFactory.persist(db_session)
    activity = await ActivityFactory.persist(db_session, location_id=location.id)
    lt_1, lt_2 = await LibraryTaskFactory.persist_many(db_session, size=2)
    await TaskFactory.persist(
        db_session,
        activity_id=activity.id,
        location_id=location.id,
        library_task_id=lt_2.id,
        start_date=activity.start_date,
        end_date=activity.end_date,
    )

    task_create = [
        TaskCreate(activity_id=activity.id, hazards=[], library_task_id=lt_1.id),
        TaskCreate(activity_id=activity.id, hazards=[], library_task_id=lt_1.id),
        TaskCreate(activity_id=activity.id, hazards=[], library_task_id=lt_1.id),
        TaskCreate(activity_id=activity.id, hazards=[], library_task_id=lt_2.id),
        TaskCreate(activity_id=activity.id, hazards=[], library_task_id=lt_2.id),
        TaskCreate(activity_id=activity.id, hazards=[], library_task_id=lt_2.id),
    ]

    create, existing = await task_manager.validate_tasks(
        task_create, location.tenant_id
    )
    assert len(create) == 1
    assert create[0].library_task_id == lt_1.id
    assert create[0].activity_id == activity.id
    assert len(existing) == 1
    assert existing[0].library_task_id == lt_2.id
    assert existing[0].activity_id == activity.id
