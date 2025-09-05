import itertools
import random
from typing import TypedDict

import pendulum

from tests.factories import (
    ActivityFactory,
    LocationFactory,
    TaskFactory,
    WorkPackageFactory,
)
from tests.integration.risk_model.conftest import (
    current_period,
    future_period,
    past_period,
)
from worker_safety_service.models import AsyncSession, WorkPackage


class ProjectWithContext(TypedDict, total=False):
    project: WorkPackage


async def project_not_active(db_session: AsyncSession) -> ProjectWithContext:
    project = await WorkPackageFactory.persist(session=db_session, **past_period())
    project_location = await LocationFactory.persist(db_session, project_id=project.id)
    await TaskFactory.persist(
        db_session, location_id=project_location.id, **current_period()
    )
    return ProjectWithContext(project=project)


async def project_without_locations(db_session: AsyncSession) -> ProjectWithContext:
    project = await WorkPackageFactory.persist(session=db_session, **current_period())
    return ProjectWithContext(project=project)


async def project_with_location_but_no_tasks(
    db_session: AsyncSession,
) -> ProjectWithContext:
    project = await WorkPackageFactory.persist(session=db_session, **current_period())
    await LocationFactory.persist(db_session, project_id=project.id)
    return ProjectWithContext(project=project)


async def project_with_location_but_no_active_tasks(
    db_session: AsyncSession,
) -> ProjectWithContext:
    project = await WorkPackageFactory.persist(session=db_session, **current_period())
    project_location = await LocationFactory.persist(db_session, project_id=project.id)
    await TaskFactory.persist(
        db_session, location_id=project_location.id, **past_period()
    )
    await TaskFactory.persist(
        db_session, location_id=project_location.id, **future_period()
    )
    return ProjectWithContext(project=project)


async def project_with_location_with_active_tasks_but_archived(
    db_session: AsyncSession,
) -> ProjectWithContext:
    project = await WorkPackageFactory.persist(session=db_session, **current_period())
    project_location = await LocationFactory.persist(db_session, project_id=project.id)
    await TaskFactory.persist(
        db_session,
        location_id=project_location.id,
        archived_at=pendulum.now(),
        **current_period(),
    )
    return ProjectWithContext(project=project)


async def project_with_one_task(
    db_session: AsyncSession,
) -> ProjectWithContext:
    project = await WorkPackageFactory.persist(session=db_session, **current_period())
    project_location = await LocationFactory.persist(db_session, project_id=project.id)
    activity = await ActivityFactory.persist(
        db_session,
        project=project,
        location=project_location,
        **current_period(),
    )
    await TaskFactory.persist(
        db_session,
        project=project,
        location=project_location,
        activity=activity,
        **current_period(),
    )
    return ProjectWithContext(project=project)


async def project_with_multiple_tasks(
    db_session: AsyncSession,
) -> ProjectWithContext:
    project = await WorkPackageFactory.persist(session=db_session, **current_period())
    project_location = await LocationFactory.persist(db_session, project_id=project.id)
    activity = await ActivityFactory.persist(
        db_session,
        project=project,
        location=project_location,
        **current_period(),
    )
    await TaskFactory.persist_many(
        db_session,
        project=project,
        location=project_location,
        activity=activity,
        **current_period(),
        size=3,
    )
    return ProjectWithContext(project=project)


async def project_with_multiple_locations_with_multiple_tasks(
    db_session: AsyncSession,
) -> ProjectWithContext:
    project = await WorkPackageFactory.persist(session=db_session, **current_period())
    project_locations = await LocationFactory.persist_many(
        db_session, project_id=project.id, size=3
    )
    for location in project_locations:
        activity = await ActivityFactory.persist(
            db_session,
            project=project,
            location=location,
            **current_period(),
        )
        size = random.randint(1, 3)
        await TaskFactory.persist_many(
            db_session,
            project=project,
            location=location,
            activity=activity,
            **current_period(),
            size=size,
        )

    return ProjectWithContext(project=project)


async def project_with_multiple_locations_with_multiple_tasks_with_empty_location(
    db_session: AsyncSession,
) -> ProjectWithContext:
    project = await WorkPackageFactory.persist(session=db_session, **current_period())
    project_locations = await LocationFactory.persist_many(
        db_session, project_id=project.id, size=3
    )

    locations_with_tasks = []
    location_without_tasks = random.choice(project_locations)
    for location in itertools.filterfalse(
        lambda e: e.id == location_without_tasks.id, project_locations
    ):
        size = random.randint(1, 3)
        await TaskFactory.persist_many(
            db_session, location_id=location.id, **current_period(), size=size
        )
        locations_with_tasks.append(location)

    ret = ProjectWithContext(project=project)
    ret["locations_with_tasks"] = locations_with_tasks  # type: ignore
    ret["locations_without_tasks"] = [location_without_tasks]  # type: ignore

    return ret
