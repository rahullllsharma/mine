import pytest

from tests.factories import (
    DailyReportFactory,
    LocationFactory,
    TenantFactory,
    WorkPackageFactory,
)
from tests.integration.dataloaders.conftest import LoaderFactory
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.gcloud.storage import FileStorage
from worker_safety_service.graphql.data_loaders.daily_reports import (
    TenantDailyReportsLoader,
)
from worker_safety_service.models import AsyncSession, FormStatus, User

fs = FileStorage()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_daily_report_respects_tenants(
    db_session: AsyncSession,
    daily_reports_loader_factory: LoaderFactory[TenantDailyReportsLoader],
) -> None:
    sec_tenant = await TenantFactory.persist(db_session)
    dataloader = daily_reports_loader_factory(sec_tenant.id)

    report = await DailyReportFactory.persist(db_session)

    dr = await dataloader.get_daily_report(report.id)

    assert dr is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_daily_reports(
    db_session: AsyncSession,
    daily_reports_loader_factory: LoaderFactory[TenantDailyReportsLoader],
) -> None:
    sec_tenant = await TenantFactory.default_tenant(db_session)
    dataloader = daily_reports_loader_factory(sec_tenant.id)
    reports = await DailyReportFactory.persist_many(db_session, size=3)

    dr = await dataloader.me.load(reports[0].id)
    assert dr is not None
    assert dr.id == reports[0].id

    drs = await dataloader.me.load_many([r.id for r in reports])
    assert all([dr is not None and dr.id == r.id for dr, r in zip(drs, reports)])

    # check different tenant does not get the daily reports
    sec_tenant = await TenantFactory.persist(db_session)
    dataloader = daily_reports_loader_factory(sec_tenant.id)

    dr1 = await dataloader.me.load(reports[0].id)
    assert dr1 is None

    drs = await dataloader.me.load_many([r.id for r in reports])
    assert all([dr is None for dr in drs])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_respects_tenants(
    db_session: AsyncSession,
    daily_reports_loader_factory: LoaderFactory[TenantDailyReportsLoader],
    test_user: User,
) -> None:
    sec_tenant = await TenantFactory.persist(db_session)
    dataloader = daily_reports_loader_factory(sec_tenant.id)

    report = await DailyReportFactory.persist(db_session)

    with pytest.raises(ResourceReferenceException):
        await dataloader.archive_daily_report(report, test_user)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_status_respects_tenants(
    db_session: AsyncSession,
    daily_reports_loader_factory: LoaderFactory[TenantDailyReportsLoader],
    test_user: User,
) -> None:
    sec_tenant = await TenantFactory.persist(db_session)
    dataloader = daily_reports_loader_factory(sec_tenant.id)

    report = await DailyReportFactory.persist(db_session)

    with pytest.raises(ResourceReferenceException):
        await dataloader.update_status(test_user, report, FormStatus.COMPLETE)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skip  # TODO: Fix this when the project location loader is in
async def test_save_daily_report_respects_tenants(
    db_session: AsyncSession,
    daily_reports_loader_factory: LoaderFactory[TenantDailyReportsLoader],
    test_user: User,
) -> None:
    sec_tenant = await TenantFactory.persist(db_session)
    dataloader = daily_reports_loader_factory(sec_tenant.id)

    project = await WorkPackageFactory.persist(db_session, tenant_id=sec_tenant.id)
    project_location = await LocationFactory.persist(db_session, project_id=project.id)
    report = await DailyReportFactory.persist(
        db_session, project_location_id=project_location.id
    )

    with pytest.raises(ResourceReferenceException):
        await dataloader.save_daily_report(
            daily_report_id=None,
            project_location_id=report.project_location_id,
            date=report.date_for,
            created_by=test_user,
        )
