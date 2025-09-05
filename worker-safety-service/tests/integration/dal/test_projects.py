import asyncio
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from faker import Faker

from tests.db_data import DBData
from tests.factories import (
    ActivityFactory,
    DailyReportFactory,
    LibraryProjectTypeFactory,
    LibraryRegionFactory,
    LocationFactory,
    SupervisorUserFactory,
    TenantFactory,
    WorkPackageFactory,
    WorkTypeFactory,
)
from worker_safety_service.dal.audit_events import AuditContext
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.models import AsyncSession, AuditEventType, FormStatus, User
from worker_safety_service.risk_model.metrics.project.total_project_risk_score import (
    TotalProjectRiskScore,
)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_get_projects_search_by_name(
    db_session: AsyncSession, work_package_manager: WorkPackageManager
) -> None:
    """WorkPackageManager.get_projects is searchable by Project.name"""
    projects = await WorkPackageFactory.persist_many(db_session, size=3)
    tenant_id = (await TenantFactory.default_tenant(db_session)).id

    results = await work_package_manager.get_projects()
    # TODO: state shouldn't leak between tests
    scoped_results = [r for r in results if r.id in [p.id for p in projects]]
    assert len(scoped_results) == 3

    results = await work_package_manager.get_projects(
        search=projects[0].name, tenant_id=tenant_id
    )
    assert len(results) == 1
    assert projects[0].id == results[0].id


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
@pytest.mark.fresh_db
async def test_get_projects_search_by_risk_level(
    db_session: AsyncSession,
    work_package_manager: WorkPackageManager,
    risk_model_metrics_manager: RiskModelMetricsManager,
) -> None:
    fake = Faker()
    Faker.seed(0)

    today = datetime.utcnow().date()

    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    projects = await WorkPackageFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {
                "start_date": today - timedelta(days=10),
                "end_date": today - timedelta(days=1),
            },
            {"start_date": fake.past_date(), "end_date": fake.future_date()},
            {"start_date": fake.past_date(), "end_date": fake.future_date()},
            {"start_date": fake.past_date(), "end_date": fake.future_date()},
            {"start_date": fake.past_date(), "end_date": fake.future_date()},
            {"start_date": fake.past_date(), "end_date": fake.future_date()},
        ],
    )

    # Create one task in the project
    locations = await LocationFactory.persist_many(
        db_session,
        per_item_kwargs=[{"project_id": i.id} for i in projects],
    )
    await ActivityFactory.persist_many_with_task(
        db_session,
        per_item_kwargs=[
            {
                "location_id": location.id,
                "start_date": project.start_date,
                "end_date": project.end_date,
            }
            for project, location in zip(projects, locations)
        ],
    )

    await asyncio.gather(
        TotalProjectRiskScore.store(
            risk_model_metrics_manager, projects[1].id, today, 99
        ),  # LOW
        TotalProjectRiskScore.store(
            risk_model_metrics_manager, projects[2].id, today, 100
        ),  # MED
        TotalProjectRiskScore.store(
            risk_model_metrics_manager, projects[3].id, today, 249
        ),  # MED
        TotalProjectRiskScore.store(
            risk_model_metrics_manager, projects[4].id, today, 250
        ),  # HIGH
    )

    results = await work_package_manager.get_projects()

    assert len(results) == 6

    results = await work_package_manager.get_projects(search="med", tenant_id=tenant_id)
    result_ids = [p.id for p in results]

    assert projects[2].id in result_ids
    assert projects[3].id in result_ids


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_get_projects_search_by_region_name(
    db_session: AsyncSession, work_package_manager: WorkPackageManager
) -> None:
    """WorkPackageManager.get_projects is searchable by region.name"""
    library_region = await LibraryRegionFactory.persist(db_session)

    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    projects = await WorkPackageFactory.persist_many(db_session, size=2)
    target_projects = await WorkPackageFactory.persist_many(
        db_session, size=2, region_id=library_region.id
    )

    results = await work_package_manager.get_projects()
    scoped_results = [
        r for r in results if r.id in [p.id for p in [*projects, *target_projects]]
    ]
    assert len(scoped_results) == 4

    results = await work_package_manager.get_projects(
        search=library_region.name, tenant_id=tenant_id
    )
    assert len(results) == 2
    expected_ids = [p.id for p in target_projects]
    assert results[0].id in expected_ids
    assert results[1].id in expected_ids


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_get_projects_search_by_project_type_name(
    db_session: AsyncSession, work_package_manager: WorkPackageManager
) -> None:
    """WorkPackageManager.get_projects is searchable by project_type.name"""

    project_type = await LibraryProjectTypeFactory.persist(db_session)
    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    projects = await WorkPackageFactory.persist_many(db_session, size=2)
    target_projects = await WorkPackageFactory.persist_many(
        db_session, size=2, work_type_id=project_type.id
    )

    results = await work_package_manager.get_projects()
    scoped_results = [
        r for r in results if r.id in [p.id for p in [*projects, *target_projects]]
    ]
    assert len(scoped_results) == 4

    results = await work_package_manager.get_projects(
        search=project_type.name, tenant_id=tenant_id
    )
    assert len(results) == 2
    expected_ids = [p.id for p in target_projects]
    assert results[0].id in expected_ids
    assert results[1].id in expected_ids


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_get_projects_search_by_work_type_name(
    db_session: AsyncSession, work_package_manager: WorkPackageManager
) -> None:
    """WorkPackageManager.get_projects is searchable by project_type.name"""
    work_type = await WorkTypeFactory.persist(db_session)
    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    projects = await WorkPackageFactory.persist_many(db_session, size=2)
    target_projects = await WorkPackageFactory.persist_many(
        db_session, size=2, work_type_ids=[work_type.id]
    )

    results = await work_package_manager.get_projects()
    scoped_results = [
        r for r in results if r.id in [p.id for p in [*projects, *target_projects]]
    ]
    assert len(scoped_results) == 4

    results = await work_package_manager.get_projects(
        search=work_type.name, tenant_id=tenant_id
    )
    assert len(results) == 2
    expected_ids = [p.id for p in target_projects]
    assert results[0].id in expected_ids
    assert results[1].id in expected_ids


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
@pytest.mark.timeout(30)
async def test_get_projects_search_by_supervisor_name(
    db_session: AsyncSession, work_package_manager: WorkPackageManager
) -> None:
    """WorkPackageManager.get_projects is searchable by supervisor.name"""
    supervisor = await SupervisorUserFactory.persist(db_session)

    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    projects = await WorkPackageFactory.persist_many(db_session, size=2)
    target_projects = await WorkPackageFactory.persist_many(
        db_session, size=2, primary_assigned_user_id=supervisor.id
    )

    results = await work_package_manager.get_projects()
    scoped_results = [
        r for r in results if r.id in [p.id for p in [*projects, *target_projects]]
    ]
    assert len(scoped_results) == 4

    results = await work_package_manager.get_projects(
        search=supervisor.first_name, tenant_id=tenant_id
    )
    assert len(results) == 2
    expected_ids = [p.id for p in target_projects]
    assert results[0].id in expected_ids
    assert results[1].id in expected_ids


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
@pytest.mark.timeout(30)
async def test_get_projects_search_by_supervisor_partial_name(
    db_session: AsyncSession,
    work_package_manager: WorkPackageManager,
) -> None:
    """WorkPackageManager.get_projects is searchable by supervisor.name even if partial"""

    supervisor = await SupervisorUserFactory.persist(db_session)

    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    projects = await WorkPackageFactory.persist_many(db_session, size=2)
    target_projects = await WorkPackageFactory.persist_many(
        db_session, size=2, primary_assigned_user_id=supervisor.id
    )

    results = await work_package_manager.get_projects()
    scoped_results = [
        r for r in results if r.id in [p.id for p in [*projects, *target_projects]]
    ]
    assert len(scoped_results) == 4

    search_key = f"{supervisor.first_name[-2:]} {supervisor.last_name[:2]}"

    results = await work_package_manager.get_projects(
        search=search_key, tenant_id=tenant_id
    )
    assert len(results) == 2
    expected_ids = [p.id for p in target_projects]
    assert results[0].id in expected_ids
    assert results[1].id in expected_ids


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_get_projects_search_is_case_insensitive(
    db_session: AsyncSession, work_package_manager: WorkPackageManager
) -> None:
    """WorkPackageManager.get_projects search is case insensitive"""

    library_region = await LibraryRegionFactory.persist(db_session)
    supervisor = await SupervisorUserFactory.persist(db_session)
    work_type = await WorkTypeFactory.persist(db_session)
    project_type = await LibraryProjectTypeFactory.persist(db_session)

    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    projects = await WorkPackageFactory.persist_many(db_session, size=3)
    target_project = await WorkPackageFactory.persist(
        db_session,
        region_id=library_region.id,
        primary_assigned_user_id=supervisor.id,
        work_type_ids=[work_type.id],
        work_type_id=project_type.id,
    )

    results = await work_package_manager.get_projects()
    scoped_results = [r for r in results if r.id in [p.id for p in projects]]
    assert len(scoped_results) == 3

    results = await work_package_manager.get_projects(
        search=target_project.name.upper(), tenant_id=tenant_id
    )
    assert len(results) == 1
    assert target_project.id == results[0].id

    results = await work_package_manager.get_projects(
        search=library_region.name.upper(), tenant_id=tenant_id
    )
    assert len(results) == 1
    assert target_project.id == results[0].id

    results = await work_package_manager.get_projects(
        search=f"{supervisor.first_name.upper()} {supervisor.last_name.upper()}",
        tenant_id=tenant_id,
    )
    assert len(results) == 1
    assert target_project.id == results[0].id

    results = await work_package_manager.get_projects(
        search=work_type.name.upper(), tenant_id=tenant_id
    )
    assert len(results) == 1
    assert target_project.id == results[0].id

    results = await work_package_manager.get_projects(
        search=project_type.name.upper(), tenant_id=tenant_id
    )
    assert len(results) == 1
    assert target_project.id == results[0].id


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
@pytest.mark.timeout(30)
async def test_get_projects_search_doesnt_require_full_string(
    db_session: AsyncSession,
    work_package_manager: WorkPackageManager,
) -> None:
    """WorkPackageManager.get_projects search is case insensitive"""

    library_region = await LibraryRegionFactory.persist(
        db_session,
        name="TargetRegion",
    )
    supervisor = await SupervisorUserFactory.persist(
        db_session, first_name="TargetSupervisor"
    )
    work_type = await WorkTypeFactory.persist(db_session, name="TargetType")
    project_type = await LibraryProjectTypeFactory.persist(
        db_session, name="TargetType"
    )

    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    projects = await WorkPackageFactory.persist_many(db_session, size=3)
    target_project = await WorkPackageFactory.persist(
        db_session,
        name="TargetProject",
        region_id=library_region.id,
        primary_assigned_user_id=supervisor.id,
        work_type_ids=[work_type.id],
        work_type_id=project_type.id,
    )

    results = await work_package_manager.get_projects()
    scoped_results = [r for r in results if r.id in [p.id for p in projects]]
    assert len(scoped_results) == 3

    results = await work_package_manager.get_projects(
        search=target_project.name[:-1], tenant_id=tenant_id
    )
    assert len(results) == 1
    assert target_project.id == results[0].id

    results = await work_package_manager.get_projects(
        search=library_region.name[:-1], tenant_id=tenant_id
    )
    assert len(results) == 1
    assert target_project.id == results[0].id

    results = await work_package_manager.get_projects(
        search=supervisor.first_name[:-1], tenant_id=tenant_id
    )
    assert len(results) == 1
    assert target_project.id == results[0].id

    results = await work_package_manager.get_projects(
        search=work_type.name[:-1], tenant_id=tenant_id
    )
    assert len(results) == 1
    assert target_project.id == results[0].id

    results = await work_package_manager.get_projects(
        search=project_type.name[:-1], tenant_id=tenant_id
    )
    assert len(results) == 1
    assert target_project.id == results[0].id


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_get_projects_search_ignores_spaces(
    db_session: AsyncSession,
    work_package_manager: WorkPackageManager,
) -> None:
    """WorkPackageManager.get_projects search ignores spaces"""

    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    projects = await WorkPackageFactory.persist_many(db_session, size=3)
    target_project = await WorkPackageFactory.persist(
        db_session,
    )

    results = await work_package_manager.get_projects()
    scoped_results = [r for r in results if r.id in [p.id for p in projects]]
    assert len(scoped_results) == 3

    results = await work_package_manager.get_projects(
        search=f" {target_project.name}", tenant_id=tenant_id
    )
    assert len(results) == 1
    assert target_project.id == results[0].id

    results = await work_package_manager.get_projects(
        search=f"{target_project.name} ", tenant_id=tenant_id
    )
    assert len(results) == 1
    assert target_project.id == results[0].id

    results = await work_package_manager.get_projects(
        search=f" {target_project.name} ", tenant_id=tenant_id
    )
    assert len(results) == 1
    assert target_project.id == results[0].id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_project_with_locations_raises_on_location_delete_with_active_daily_report(
    db_session: AsyncSession,
    work_package_manager: WorkPackageManager,
    test_user: User,
    db_data: DBData,
) -> None:
    """
    Locations cannot be deleted if a daily inspection report is associated
    """

    project_id = (await WorkPackageFactory.persist(db_session)).id
    locations = await LocationFactory.persist_many(
        db_session, size=2, project_id=project_id
    )
    await DailyReportFactory.persist(
        db_session,
        project_location_id=locations[0].id,
        status=FormStatus.COMPLETE,
    )

    project = await db_data.project(project_id, load_locations=True)

    db_locations = {i.id: i for i in project.locations}
    with AuditContext(db_session), pytest.raises(ValueError) as e:
        await work_package_manager.locations_manager.edit_locations(project, db_locations, locations=[locations[1]])  # type: ignore
        await work_package_manager.session.commit()
    assert e.match(f"Project location {locations[0].id} has 1 active daily reports.")
    assert locations[0].archived_at is None
    assert locations[1].archived_at is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_project_with_locations_deletes_location_with_no_reports(
    db_session: AsyncSession,
    work_package_manager: WorkPackageManager,
    test_user: User,
    db_data: DBData,
) -> None:
    """
    Locations cannot be deleted if a daily inspection report is associated
    """

    project_id = (await WorkPackageFactory.persist(db_session)).id
    locations = await LocationFactory.persist_many(
        db_session, size=2, project_id=project_id
    )
    assert locations[0].archived_at is None
    assert locations[1].archived_at is None

    project = await work_package_manager.get_project(project_id, load_locations=True)
    assert project
    db_locations = {i.id: i for i in project.locations}
    with AuditContext(work_package_manager.session) as audit:
        await work_package_manager.locations_manager.edit_locations(project, db_locations, locations=[locations[0]])  # type: ignore
        await audit.create(AuditEventType.project_updated, test_user)
        await work_package_manager.session.commit()

    await db_session.refresh(locations[0])
    await db_session.refresh(locations[1])
    assert locations[0].archived_at is None
    assert locations[1].archived_at is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_projects_by_external_keys(
    db_session: AsyncSession,
    work_package_manager: WorkPackageManager,
) -> None:
    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    external_key1 = str(uuid4())
    external_key2 = str(uuid4())
    p1 = await WorkPackageFactory.persist(db_session, external_key=external_key1)
    p2 = await WorkPackageFactory.persist(db_session, external_key=external_key2)
    p3 = await WorkPackageFactory.persist(db_session, external_key=str(uuid4()))

    expected_ids = [p1.id, p2.id]

    results = await work_package_manager.get_projects(
        external_keys=[external_key1, external_key2], tenant_id=tenant_id
    )

    assert len(results) == 2
    assert results[0].id in expected_ids
    assert results[1].id in expected_ids
    assert p3.id not in [r.id for r in results]
