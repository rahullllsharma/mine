from datetime import datetime

import pytest
from faker import Faker

from tests.db_data import DBData
from tests.factories import (
    DailyReportFactory,
    LocationFactory,
    SiteConditionFactory,
    TaskFactory,
    TenantFactory,
    WorkPackageFactory,
)
from tests.integration.dataloaders.conftest import LoaderFactory
from tests.integration.helpers import assert_recent_datetime
from tests.integration.mutations.audit_events.helpers import (
    assert_created_at,
    audit_events_for_object,
)
from worker_safety_service.dal.exceptions import EntityNotFoundException
from worker_safety_service.exceptions import ResourceReferenceException, TenantException
from worker_safety_service.graphql.data_loaders.project_locations import (
    TenantProjectLocationLoader,
)
from worker_safety_service.graphql.data_loaders.site_conditions import (
    TenantSiteConditionLoader,
)
from worker_safety_service.graphql.data_loaders.work_packages import (
    TenantWorkPackageLoader,
)
from worker_safety_service.models import (
    AsyncSession,
    AuditDiffType,
    AuditEventType,
    FormStatus,
    LocationCreate,
    ProjectStatus,
    User,
    WorkPackage,
    WorkPackageCreate,
    WorkPackageEdit,
)
from worker_safety_service.models.base import SiteConditionCreate, TaskCreate
from worker_safety_service.types import Point

fake = Faker()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_load_projects_respects_tenants(
    db_session: AsyncSession,
    project_loader_factory: LoaderFactory[TenantWorkPackageLoader],
) -> None:
    prim_tenant = await TenantFactory.default_tenant(db_session)
    sec_tenant = await TenantFactory.persist(db_session)
    dataloader = project_loader_factory(prim_tenant.id)

    projects = await WorkPackageFactory.persist_many(
        db_session, size=5, tenant_id=sec_tenant.id
    )

    ps = await dataloader.load_projects(list(map(lambda p: p.id, projects)))

    assert ps == [None, None, None, None, None]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_load_project_locations_respects_tenants(
    db_session: AsyncSession,
    project_loader_factory: LoaderFactory[TenantWorkPackageLoader],
) -> None:
    prim_tenant = await TenantFactory.default_tenant(db_session)
    sec_tenant = await TenantFactory.persist(db_session)
    dataloader = project_loader_factory(prim_tenant.id)

    project = await WorkPackageFactory.persist(
        db_session, size=5, tenant_id=sec_tenant.id
    )
    await LocationFactory.persist_many(db_session, size=2, project_id=project.id)

    pls = await dataloader.load_project_locations([project.id])

    assert pls == [[]]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_locations_respects_tenants(
    db_session: AsyncSession,
    project_loader_factory: LoaderFactory[TenantWorkPackageLoader],
) -> None:
    prim_tenant = await TenantFactory.default_tenant(db_session)
    sec_tenant = await TenantFactory.persist(db_session)
    dataloader = project_loader_factory(prim_tenant.id)

    project = await WorkPackageFactory.persist(db_session, tenant_id=sec_tenant.id)
    await LocationFactory.persist_many(db_session, size=2, project_id=project.id)

    p = await dataloader.locations().load(project.id)

    assert p == []


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_projects_respects_tenants(
    db_session: AsyncSession,
    project_loader_factory: LoaderFactory[TenantWorkPackageLoader],
) -> None:
    prim_tenant = await TenantFactory.default_tenant(db_session)
    sec_tenant = await TenantFactory.persist(db_session)
    dataloader = project_loader_factory(prim_tenant.id)

    project = await WorkPackageFactory.persist(db_session, tenant_id=sec_tenant.id)

    ps = await dataloader.get_projects()
    assert project.id not in map(lambda p: p.id, ps)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_locations_respects_tenants(
    db_session: AsyncSession,
    project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
) -> None:
    prim_tenant = await TenantFactory.default_tenant(db_session)
    sec_tenant = await TenantFactory.persist(db_session)
    dataloader = project_location_loader_factory(prim_tenant.id)

    project = await WorkPackageFactory.persist(db_session, tenant_id=sec_tenant.id)
    await LocationFactory.persist_many(db_session, size=2, project_id=project.id)

    pls = await dataloader.get_locations()
    assert project.id not in map(lambda pl: pl.project_id, pls)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_project_location_respects_tenants(
    db_session: AsyncSession,
    project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
) -> None:
    prim_tenant = await TenantFactory.default_tenant(db_session)
    sec_tenant = await TenantFactory.persist(db_session)
    dataloader = project_location_loader_factory(prim_tenant.id)

    project = await WorkPackageFactory.persist(db_session, tenant_id=sec_tenant.id)
    pl = await LocationFactory.persist(db_session, project_id=project.id)

    pl2 = await dataloader.me.load(pl.id)
    assert pl2 is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_work_package_respects_tenants(
    db_session: AsyncSession,
    project_loader_factory: LoaderFactory[TenantWorkPackageLoader],
    test_user: User,
    project: WorkPackage,
) -> None:
    prim_tenant = await TenantFactory.default_tenant(db_session)
    sec_tenant = await TenantFactory.persist(db_session)
    dataloader = project_loader_factory(prim_tenant.id)

    pc = WorkPackageCreate(
        name="tenant test project",
        description=fake.paragraph(),
        start_date=project.start_date,
        end_date=project.end_date,
        external_key=project.external_key,
        region_id=project.region_id,
        division_id=project.division_id,
        work_type_ids=project.work_type_ids,
        manager_id=project.manager_id,
        primary_assigned_user_id=project.primary_assigned_user_id,
        additional_assigned_users_ids=[],
        contractor_id=project.contractor_id,
        tenant_id=sec_tenant.id,
    )

    with pytest.raises(TenantException):
        await dataloader.create_work_packages(
            projects=[pc],
            user=test_user,
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_work_package_creates_multiple_work_packages(
    db_session: AsyncSession,
    project_loader_factory: LoaderFactory[TenantWorkPackageLoader],
    project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
    test_user: User,
    project: WorkPackage,
) -> None:
    prim_tenant = await TenantFactory.default_tenant(db_session)
    dataloader = project_loader_factory(prim_tenant.id)
    location_loader = project_location_loader_factory(prim_tenant.id)

    pc = WorkPackageCreate(
        name="tenant test project",
        description=fake.paragraph(),
        start_date=project.start_date,
        end_date=project.end_date,
        region_id=project.region_id,
        division_id=project.division_id,
        work_type_id=project.work_type_id,
        work_type_ids=project.work_type_ids,
        manager_id=project.manager_id,
        primary_assigned_user_id=project.primary_assigned_user_id,
        additional_assigned_users_ids=[],
        contractor_id=project.contractor_id,
        tenant_id=prim_tenant.id,
        external_key="wp1",
    )

    loc1 = LocationCreate(
        tenant_id=prim_tenant.id,
        address=fake.address(),
        supervisor_id=project.primary_assigned_user_id,
        name="location",
        geom=Point(0, 0),
        additional_supervisor_ids=[],
    )

    loc2 = LocationCreate(
        tenant_id=prim_tenant.id,
        address=fake.address(),
        supervisor_id=project.primary_assigned_user_id,
        name="another location",
        geom=Point(1, 1),
        additional_supervisor_ids=[],
    )

    pc2 = WorkPackageCreate(
        name="tenant test project2",
        description=fake.paragraph(),
        start_date=project.start_date,
        end_date=project.end_date,
        region_id=project.region_id,
        division_id=project.division_id,
        work_type_id=project.work_type_id,
        work_type_ids=project.work_type_ids,
        manager_id=project.manager_id,
        primary_assigned_user_id=project.primary_assigned_user_id,
        additional_assigned_users_ids=[],
        contractor_id=project.contractor_id,
        tenant_id=prim_tenant.id,
        external_key="wp2",
        status=ProjectStatus.ACTIVE,
        location_creates=[loc1, loc2],
    )

    wps = await dataloader.create_work_packages([pc, pc2])
    assert len(wps) == 2

    wp1 = list(filter(lambda x: x.name == "tenant test project", wps))
    assert wp1[0].status == pc.status
    assert wp1[0].external_key == pc.external_key

    wp2 = list(filter(lambda x: x.name == "tenant test project2", wps))
    assert wp2[0].status == pc2.status
    assert wp2[0].external_key == pc2.external_key

    locations = await location_loader.get_locations(project_ids=[wp1[0].id, wp2[0].id])
    assert len(locations) == 2
    assert not any(location.project_id == wp1[0].id for location in locations)

    location1 = list(filter(lambda x: x.name == "location", locations))
    assert location1[0].geom == loc1.geom

    location2 = list(filter(lambda x: x.name == "another location", locations))
    assert location2[0].geom == loc2.geom


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_project_with_locations_respects_tenants(
    db_session: AsyncSession,
    project_loader_factory: LoaderFactory[TenantWorkPackageLoader],
    test_user: User,
    project: WorkPackage,
) -> None:
    sec_tenant = await TenantFactory.persist(db_session)
    dataloader = project_loader_factory(sec_tenant.id)

    # Project is created in default tenant, which is the primary
    pe = WorkPackageEdit(
        id=project.id,
        name="Update name tenant test project",
        start_date=project.start_date,
        end_date=project.end_date,
        external_key=project.external_key,
        region_id=project.region_id,
        division_id=project.division_id,
        work_type_ids=project.work_type_ids,
        manager_id=project.manager_id,
        primary_assigned_user_id=project.primary_assigned_user_id,
        additional_assigned_users_ids=[],
        contractor_id=project.contractor_id,
        tenant_id=sec_tenant.id,
    )

    with pytest.raises(TenantException):
        await dataloader.edit_project_with_locations(
            db_project=project,
            project=pe,
            locations=[],
            user=test_user,
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_task_respects_tenants(
    db_session: AsyncSession,
    project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
    test_user: User,
    project: WorkPackage,
) -> None:
    sec_tenant = await TenantFactory.persist(db_session)
    dataloader = project_location_loader_factory(sec_tenant.id)
    extra_task = await TaskFactory.persist(db_session)

    location = await LocationFactory.persist(db_session, project_id=project.id)

    pltc = TaskCreate(
        location_id=location.id, library_task_id=extra_task.library_task_id, hazards=[]
    )

    with pytest.raises(ResourceReferenceException):
        await dataloader.create_task(
            task=pltc,
            user=test_user,
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_task_respects_tenants(
    db_session: AsyncSession,
    project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
    test_user: User,
) -> None:
    sec_tenant = await TenantFactory.persist(db_session)
    dataloader = project_location_loader_factory(sec_tenant.id)

    # Exists in primary tenant
    task = await TaskFactory.persist(db_session)

    with pytest.raises(ResourceReferenceException):
        await dataloader.edit_task(
            db_task=task,
            hazards=[],
            user=test_user,
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_task_respects_tenants(
    db_session: AsyncSession,
    project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
    test_user: User,
    project: WorkPackage,
) -> None:
    sec_tenant = await TenantFactory.persist(db_session)
    dataloader = project_location_loader_factory(sec_tenant.id)

    # Exists in primary tenant
    task = await TaskFactory.persist(db_session)

    with pytest.raises(ResourceReferenceException):
        await dataloader.archive_task(db_task=task, user=test_user)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_site_condition_respects_tenants(
    db_session: AsyncSession,
    project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
    test_user: User,
    project: WorkPackage,
) -> None:
    sec_tenant = await TenantFactory.persist(db_session)
    dataloader = project_location_loader_factory(sec_tenant.id)
    extra_sc = await SiteConditionFactory.persist(db_session)

    location = await LocationFactory.persist(db_session, project_id=project.id)

    plscc = SiteConditionCreate(
        location_id=location.id,
        library_site_condition_id=extra_sc.library_site_condition_id,
        is_manually_added=True,
    )

    with pytest.raises(ResourceReferenceException):
        await dataloader.create_site_condition(
            plscc,
            hazards=[],
            user=test_user,
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_site_condition_respects_tenants(
    db_session: AsyncSession,
    project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
    test_user: User,
    project: WorkPackage,
) -> None:
    sec_tenant = await TenantFactory.persist(db_session)
    dataloader = project_location_loader_factory(sec_tenant.id)

    # Exists in primary tenant
    site_condition = await SiteConditionFactory.persist(db_session)

    with pytest.raises(ResourceReferenceException):
        await dataloader.edit_site_condition(
            db_site_condition=site_condition,
            hazards=[],
            user=test_user,
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_site_condition_respects_tenants(
    db_session: AsyncSession,
    site_condition_loader_factory: LoaderFactory[TenantSiteConditionLoader],
    test_user: User,
    project: WorkPackage,
) -> None:
    sec_tenant = await TenantFactory.persist(db_session)
    dataloader = site_condition_loader_factory(sec_tenant.id)

    # Exists in primary tenant
    site_condition = await SiteConditionFactory.persist(db_session)

    with pytest.raises(EntityNotFoundException):
        await dataloader.archive_site_condition(id=site_condition.id, user=test_user)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_get_locations_filters(
    db_session: AsyncSession,
    project: WorkPackage,
    project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
) -> None:
    tenant = await TenantFactory.default_tenant(db_session)
    dataloader = project_location_loader_factory(tenant.id)

    other_project = await WorkPackageFactory.persist(
        db_session,
        tenant_id=tenant.id,
        region_id=project.region_id,
        work_type_ids=project.work_type_ids,
    )
    await LocationFactory.persist_many(db_session, size=2, project_id=project.id)
    await LocationFactory.persist_many(db_session, size=5, project_id=other_project.id)

    assert project.region_id, "Must have a library region defined"
    filtered_results = await dataloader.get_locations(
        library_region_ids=[project.region_id]
    )
    assert len(filtered_results) == 7

    assert project.division_id, "Must have a library division defined"
    filtered_results = await dataloader.get_locations(
        library_division_ids=[project.division_id]
    )
    assert len(filtered_results) == 2

    assert other_project.work_type_ids
    filtered_results = await dataloader.get_locations(
        work_type_ids=other_project.work_type_ids
    )
    assert len(filtered_results) == 7


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_project_and_cascade(
    db_session: AsyncSession,
    project_loader_factory: LoaderFactory[TenantWorkPackageLoader],
    test_user: User,
    db_data: DBData,
) -> None:
    """
    Locations cannot be deleted if a daily inspection report is associated
    """
    tenant = await TenantFactory.default_tenant(db_session)
    dataloader = project_loader_factory(tenant.id)

    project = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    assert project.archived_at is None
    locations = await LocationFactory.persist_many(
        db_session, size=2, project_id=project.id
    )
    assert locations[0].archived_at is None
    assert locations[1].archived_at is None

    daily_report = await DailyReportFactory.persist(
        db_session,
        project_location_id=locations[0].id,
        status=FormStatus.COMPLETE,
    )
    assert daily_report.archived_at is None

    await dataloader.archive_project(project, test_user)

    await db_session.refresh(project)
    assert project.archived_at is not None

    await db_session.refresh(daily_report)
    assert daily_report.archived_at is not None

    await db_session.refresh(locations[0])
    await db_session.refresh(locations[1])
    assert locations[0].archived_at is not None
    assert locations[1].archived_at is not None

    # fetch the event for the removed location
    events = await audit_events_for_object(
        db_session,
        id=project.id,
        event_type=AuditEventType.project_archived,
    )
    assert len(events) == 1
    event = events[0]
    assert event.user_id == test_user.id
    await assert_created_at(db_session, event)
    assert event.event_type == AuditEventType.project_archived

    # ensure involved objs still exist in the db, and have archived_at set
    event_diffs = await db_data.audit_event_diffs(event.id)
    assert len(event_diffs) == 4  # 1 project + 2 locations + 1 daily report
    for d in event_diffs:
        assert d.diff_type == AuditDiffType.archived
        assert d.new_values
        assert d.old_values
        assert "archived_at" in list(d.new_values.keys()), list(d.new_values.keys())
        assert "archived_at" in list(d.old_values.keys()), list(d.old_values.keys())

        assert_recent_datetime(datetime.fromisoformat(d.new_values["archived_at"]))
