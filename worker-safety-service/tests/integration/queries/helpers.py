import datetime
from itertools import count
from typing import Any

from tests.factories import (
    LibraryControlFactory,
    LibraryHazardFactory,
    LibrarySiteConditionFactory,
    LibrarySiteConditionRecommendationsFactory,
    LibraryTaskFactory,
    LibraryTaskRecommendationsFactory,
    LocationFactory,
    SiteConditionFactory,
    TaskFactory,
    TenantFactory,
    TotalProjectRiskScoreModelFactory,
    WorkPackageFactory,
    WorkTypeFactory,
    WorkTypeTaskLinkFactory,
)
from tests.integration.helpers import valid_project_request
from worker_safety_service.models import AsyncSession, TaskStatus

UNIQUE_MINUTES = count()


async def build_library_tasks_for_order_by(
    db_session: AsyncSession, name: str | None = None
) -> tuple[str, str, str]:
    items = await LibraryTaskFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {"name": name or "á 1", "category": "a 3"},
            {"name": name or "A 2", "category": "A 2"},
            {"name": name or "a 3", "category": "á 1"},
        ],
    )

    # creating tenant
    tenant_id = (await TenantFactory.default_tenant(db_session)).id

    # creating work type and linking with tenant
    work_id = (
        await WorkTypeFactory.tenant_work_type(session=db_session, tenant_id=tenant_id)
    ).id

    # linking worktype with the library tasks
    await WorkTypeTaskLinkFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {"task_id": items[0].id, "work_type_id": work_id},
            {"task_id": items[1].id, "work_type_id": work_id},
            {"task_id": items[2].id, "work_type_id": work_id},
        ],
    )
    return str(items[0].id), str(items[1].id), str(items[2].id)


async def build_library_site_conditions_for_order_by(
    db_session: AsyncSession,
    name: str | None = None,
) -> tuple[str, str, str]:
    items = await LibrarySiteConditionFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {"name": name or "á 1"},
            {"name": name or "A 2"},
            {"name": name or "a 3"},
        ],
    )
    return str(items[0].id), str(items[1].id), str(items[2].id)


async def build_library_hazards_for_order_by(
    db_session: AsyncSession,
    size: int = 1,
) -> list[str]:
    items = await LibraryHazardFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {"name": "á 1"},
            {"name": "A 2"},
            {"name": "a 3"},
        ]
        * size,
    )
    for item in items:
        await LibraryHazardFactory.link_to_tenant_settings(db_session, item)
    return [str(i.id) for i in items]


async def build_library_controls_for_order_by(
    db_session: AsyncSession,
    size: int = 1,
) -> list[str]:
    items = await LibraryControlFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {"name": "á 1"},
            {"name": "A 2"},
            {"name": "a 3"},
        ]
        * size,
    )
    for item in items:
        await LibraryControlFactory.link_to_tenant_settings(db_session, item)
    return [str(i.id) for i in items]


async def set_library_site_conditions_relations(
    db_session: AsyncSession,
    site_conditions: list[str],
    hazards: list[str],
    controls: list[str],
) -> None:
    await LibrarySiteConditionRecommendationsFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {
                "library_site_condition_id": site_condition,
                "library_hazard_id": hazard,
                "library_control_id": control,
            }
            for site_condition in site_conditions
            for hazard in hazards
            for control in controls
        ],
    )


async def set_library_tasks_relations(
    db_session: AsyncSession,
    tasks: list[str],
    hazards: list[str],
    controls: list[str],
) -> None:
    await LibraryTaskRecommendationsFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {
                "library_task_id": task,
                "library_hazard_id": hazard,
                "library_control_id": control,
            }
            for task in tasks
            for hazard in hazards
            for control in controls
        ],
    )


def asc_order(items: list[str]) -> list[str]:
    return items


def desc_order(items: list[str]) -> list[str]:
    return list(reversed(items))


async def create_projects_for_order_by(
    db_session: AsyncSession, name: str | None = None
) -> list[str]:
    items = await WorkPackageFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {"name": name or "á 1"},
            {"name": name or "A 2"},
            {"name": name or "a 3"},
        ],
    )
    expected_order = [str(i.id) for i in items]
    return sorted(expected_order) if name else expected_order


async def create_projects_risk_level_for_order_by(
    db_session: AsyncSession,
) -> tuple[list[str], list[str]]:
    today = datetime.datetime.utcnow().date()
    start_date = today - datetime.timedelta(days=5)
    end_date = today + datetime.timedelta(days=5)

    kwargs = {"start_date": start_date, "end_date": end_date}
    items = await TaskFactory.batch_with_project_and_location(
        db_session,
        [
            {"task_kwargs": kwargs, "project_kwargs": {"name": "á 1", **kwargs}},
            {"task_kwargs": kwargs, "project_kwargs": {"name": "A 2", **kwargs}},
            {"task_kwargs": kwargs, "project_kwargs": {"name": "a 3", **kwargs}},
            {"task_kwargs": kwargs, "project_kwargs": {"name": "a 3", **kwargs}},
        ],
    )
    project_1 = str(items[0][1].id)
    project_2 = str(items[1][1].id)
    project_3 = str(items[2][1].id)
    project_4 = str(items[3][1].id)

    today_order = [project_4, project_3, project_2, project_1]
    yesterday_order = [project_1, project_2, project_3, project_4]

    for date, expected_order in [
        (today, today_order),
        (today - datetime.timedelta(days=1), yesterday_order),
    ]:
        used_date = datetime.datetime(
            date.year,
            date.month,
            date.day,
            12,
            next(UNIQUE_MINUTES),
            0,
            tzinfo=datetime.timezone.utc,
        )

        # This first scores should be ignored
        # Lets add a different order, so we make sure it's not being used
        value = 1
        reversed_order = list(reversed(expected_order))
        for project_id in reversed_order[:-1]:
            value *= 10
            await TotalProjectRiskScoreModelFactory.persist(
                db_session,
                project_id=project_id,
                value=value,
                date=date,
                calculated_at=used_date - datetime.timedelta(seconds=value),
            )
        # Create same risk to make order by value
        value += 1
        await TotalProjectRiskScoreModelFactory.persist(
            db_session,
            project_id=reversed_order[-1],
            value=value,
            date=date,
            calculated_at=used_date - datetime.timedelta(seconds=value),
        )

        # This scores should be the ones in used
        value = 1
        for project_id in expected_order[:-1]:
            value *= 10
            await TotalProjectRiskScoreModelFactory.persist(
                db_session,
                project_id=project_id,
                value=value,
                date=date,
                calculated_at=used_date + datetime.timedelta(seconds=value),
            )
        # Create same risk to make order by value
        value += 1
        await TotalProjectRiskScoreModelFactory.persist(
            db_session,
            project_id=expected_order[-1],
            value=value,
            date=date,
            calculated_at=used_date + datetime.timedelta(seconds=value),
        )

    return today_order, yesterday_order


async def create_project_locations_for_sort(
    db_session: AsyncSession, name: str | None = None, **kwargs: Any
) -> tuple[str, list[str]]:
    project_id = str((await WorkPackageFactory.persist(db_session, **kwargs)).id)
    location_1 = str(
        (
            await LocationFactory.persist(
                db_session, project_id=project_id, name=name or "á 1"
            )
        ).id
    )
    location_2 = str(
        (
            await LocationFactory.persist(
                db_session, project_id=project_id, name=name or "A 2"
            )
        ).id
    )
    location_3 = str(
        (
            await LocationFactory.persist(
                db_session, project_id=project_id, name=name or "a 3"
            )
        ).id
    )
    expected_order = [location_1, location_2, location_3]
    return project_id, sorted(expected_order) if name else expected_order


async def create_site_conditions_for_sort(
    db_session: AsyncSession, name: str | None = None
) -> tuple[str, list[str]]:
    expected_order = []
    project_data = await valid_project_request(db_session, persist=True)
    location_id = project_data["locations"][0]["id"]
    for library_site_condition_id in await build_library_site_conditions_for_order_by(
        db_session, name=name
    ):
        site_condition = await SiteConditionFactory.persist(
            db_session,
            location_id=location_id,
            library_site_condition_id=library_site_condition_id,
        )
        expected_order.append(str(site_condition.id))

    return location_id, sorted(expected_order) if name else expected_order


async def create_tasks_for_sort(
    db_session: AsyncSession, name: str | None = None
) -> tuple[str, list[str]]:
    expected_order = []
    project_data = await valid_project_request(db_session, persist=True)
    location_id = project_data["locations"][0]["id"]
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=10)
    status_reverse_order = [
        TaskStatus.NOT_STARTED,
        TaskStatus.NOT_COMPLETED,
        TaskStatus.IN_PROGRESS,
        TaskStatus.COMPLETE,
    ]
    for i, library_task_id in enumerate(
        await build_library_tasks_for_order_by(db_session, name=name)
    ):
        task = await TaskFactory.persist(
            db_session,
            location_id=location_id,
            library_task_id=library_task_id,
            start_date=start_date - datetime.timedelta(days=i + 1),
            end_date=end_date - datetime.timedelta(days=i + 1),
            status=status_reverse_order[i],
        )
        expected_order.append(str(task.id))

    return location_id, sorted(expected_order) if name else expected_order


async def create_tasks_for_project_min_max_dates(
    db_session: AsyncSession,
) -> tuple[str, datetime.date, datetime.date]:
    project_data = await valid_project_request(db_session, persist=True)
    project_id = project_data["id"]
    location_id = project_data["locations"][0]["id"]
    base_date = datetime.date.today()
    expected_minimum_date = base_date - datetime.timedelta(days=9)
    expected_maximum_date = base_date + datetime.timedelta(days=1)

    library_task = await LibraryTaskFactory.persist(db_session)
    for i, a_date in enumerate(
        base_date - datetime.timedelta(days=x) for x in range(10)
    ):
        await TaskFactory.persist(
            db_session,
            location_id=location_id,
            library_task_id=library_task.id,
            start_date=a_date,
            end_date=a_date + datetime.timedelta(days=i + 1),
            status=TaskStatus.IN_PROGRESS,
        )

    return project_id, expected_minimum_date, expected_maximum_date


async def setup_tasks_for_project_min_max_dates_for_deleted_tasks(
    db_session: AsyncSession,
) -> tuple[str, str, datetime.date, datetime.date, datetime.date, datetime.date]:
    project_data = await valid_project_request(db_session, persist=True)
    project_id = project_data["id"]
    location_id = project_data["locations"][0]["id"]
    base_date = datetime.date.today()

    initial_minimum_date = base_date + datetime.timedelta(days=3)
    initial_maximum_date = base_date + datetime.timedelta(days=20)
    expected_minimum_date = base_date + datetime.timedelta(days=5)
    expected_maximum_date = base_date + datetime.timedelta(days=10)

    library_task = await LibraryTaskFactory.persist(db_session)
    await TaskFactory.persist(
        db_session,
        location_id=location_id,
        library_task_id=library_task.id,
        start_date=expected_minimum_date,
        end_date=expected_maximum_date,
        status=TaskStatus.IN_PROGRESS,
    )

    task = await TaskFactory.persist(
        db_session,
        location_id=location_id,
        library_task_id=library_task.id,
        start_date=initial_minimum_date,
        end_date=initial_maximum_date,
        status=TaskStatus.IN_PROGRESS,
    )

    return (
        project_id,
        str(task.id),
        expected_minimum_date,
        expected_maximum_date,
        initial_minimum_date,
        initial_maximum_date,
    )
