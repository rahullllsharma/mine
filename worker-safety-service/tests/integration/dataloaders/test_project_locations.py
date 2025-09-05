import dataclasses
import uuid
from datetime import datetime, timezone

import pytest

from tests.factories import (
    DailyReportFactory,
    LocationFactory,
    TenantFactory,
    WorkPackageFactory,
)
from tests.integration.dataloaders.conftest import (
    LoaderFactory,
    SiteConditionsInit,
    TasksInit,
    assert_dataloader_filter_tenants,
    assert_dataloader_return_right_order,
    assert_mocked_dataloader_return_right_order,
)
from worker_safety_service.graphql.data_loaders.project_locations import (
    TenantProjectLocationLoader,
)
from worker_safety_service.models import AsyncSession, DailyReport, Location, Tenant


class TestProjectLocations:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_archived_locations(
        self,
        db_session: AsyncSession,
        project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
    ) -> None:
        project = await WorkPackageFactory.persist(db_session)
        location: Location = await LocationFactory.persist(
            db_session, project_id=project.id
        )
        archive_time = datetime.now(timezone.utc)
        archived: Location = await LocationFactory.persist(
            db_session, project_id=project.id, archived_at=archive_time
        )

        tenant = await TenantFactory.default_tenant(db_session)
        loader = project_location_loader_factory(tenant.id)

        l1 = await loader.with_archived.load(location.id)
        assert l1
        assert l1.archived_at is None
        l_archived = await loader.with_archived.load(archived.id)
        assert l_archived
        assert l_archived.archived_at == archive_time
        l_all = await loader.with_archived.load_many([location.id, archived.id])
        assert l_all[0] == l1 and l_all[1] == l_archived


class TestProjectLocationTasks:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tenants(
        self,
        tasks_init: TasksInit,
        project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
    ) -> None:
        """Make sure dataloaders filter tenants"""

        x = tasks_init
        await assert_dataloader_filter_tenants(
            project_location_loader_factory,
            "load_tasks",
            "tasks",
            [
                # Tenant 1 should only see tenant 1 tasks
                (
                    x.tenant_1.id,
                    [x.location_13.id, x.location_21.id],
                    [[x.task_13_item], []],
                ),
                # Tenant 2 should only see tenant 2 tasks
                (
                    x.tenant_2.id,
                    [x.location_13.id, x.location_21.id],
                    [[], [x.task_21_item]],
                ),
                # Invalid tenant
                (
                    x.tenant_3.id,
                    [x.location_13.id, x.location_21.id],
                    [[], []],
                ),
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_order(
        self,
        db_session: AsyncSession,
        tasks_init: TasksInit,
        project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
    ) -> None:
        """Make sure order returned by dataloaders match request"""

        x = tasks_init
        await assert_mocked_dataloader_return_right_order(
            db_session,
            project_location_loader_factory,
            "load_tasks",
            "tasks",
            x.tenant_1.id,
            filter_ids=[x.location_11.id, x.location_13.id],
            expected_result=[
                [x.task_112_item, x.task_11_item],
                [x.task_13_item],
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_missing(
        self,
        tasks_init: TasksInit,
        project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
    ) -> None:
        """Return empty list and don't raise an error when location don't exists"""

        x = tasks_init
        await assert_dataloader_return_right_order(
            project_location_loader_factory,
            "load_tasks",
            "tasks",
            x.tenant_1.id,
            filter_ids=[x.location_13.id, uuid.uuid4()],
            expected_result=[[x.task_13_item], []],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_empty(
        self,
        tasks_init: TasksInit,
        project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
    ) -> None:
        """If an empty list is sent don't return anything"""
        x = tasks_init
        items = await project_location_loader_factory(x.tenant_1.id).load_tasks([])
        assert items == []


class TestProjectLocationSiteConditions:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tenants(
        self,
        site_conditions_init: SiteConditionsInit,
        project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
    ) -> None:
        """Make sure dataloaders filter tenants"""

        x = site_conditions_init
        await assert_dataloader_filter_tenants(
            project_location_loader_factory,
            "load_site_conditions",
            "site_conditions",
            [
                # Tenant 1 should only see tenant 1 site conditions
                (
                    x.tenant_1.id,
                    [x.location_13.id, x.location_21.id],
                    [[x.site_condition_13_item], []],
                ),
                # Tenant 2 should only see tenant 2 site conditions
                (
                    x.tenant_2.id,
                    [x.location_13.id, x.location_21.id],
                    [[], [x.site_condition_21_item]],
                ),
                # Invalid tenant
                (
                    x.tenant_3.id,
                    [x.location_13.id, x.location_21.id],
                    [[], []],
                ),
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_order(
        self,
        db_session: AsyncSession,
        site_conditions_init: SiteConditionsInit,
        project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
    ) -> None:
        """Make sure order returned by dataloaders match request"""

        x = site_conditions_init
        await assert_mocked_dataloader_return_right_order(
            db_session,
            project_location_loader_factory,
            "load_site_conditions",
            "site_conditions",
            x.tenant_1.id,
            filter_ids=[x.location_11.id, x.location_13.id],
            expected_result=[
                [x.site_condition_12_item, x.site_condition_11_item],
                [x.site_condition_13_item],
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_missing(
        self,
        site_conditions_init: SiteConditionsInit,
        project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
    ) -> None:
        """Return empty list and don't raise an error when location don't exists"""

        x = site_conditions_init
        await assert_dataloader_return_right_order(
            project_location_loader_factory,
            "load_site_conditions",
            "site_conditions",
            x.tenant_1.id,
            filter_ids=[x.location_13.id, uuid.uuid4()],
            expected_result=[[x.site_condition_13_item], []],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_empty(
        self,
        site_conditions_init: SiteConditionsInit,
        project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
    ) -> None:
        """If an empty list is sent don't return anything"""
        x = site_conditions_init
        items = await project_location_loader_factory(
            x.tenant_1.id
        ).load_site_conditions([])
        assert items == []


@dataclasses.dataclass
class DailyReportInit:
    tenant_1: Tenant
    location_11: Location
    daily_report_11: DailyReport
    daily_report_12: DailyReport
    location_13: Location
    daily_report_13: DailyReport
    tenant_2: Tenant
    location_21: Location
    daily_report_21: DailyReport
    tenant_3: Tenant


@pytest.fixture
async def project_location_daily_reports_init(
    db_session_no_expire: AsyncSession,
) -> DailyReportInit:
    session = db_session_no_expire
    tenant_1, tenant_2, tenant_3 = await TenantFactory.persist_many(session, size=3)
    project_11 = await WorkPackageFactory.persist(session, tenant_id=tenant_1.id)
    location_11 = await LocationFactory.persist(session, project_id=project_11.id)
    (
        (daily_report_11, _, _),
        (daily_report_12, _, _),
        (
            daily_report_13,
            _,
            location_13,
        ),
        (
            daily_report_21,
            _,
            location_21,
        ),
    ) = await DailyReportFactory.batch_with_project_and_location(
        session,
        [
            {"project": project_11, "location": location_11},
            {"project": project_11, "location": location_11},
            {"project_kwargs": {"tenant_id": tenant_1.id}},
            {"project_kwargs": {"tenant_id": tenant_2.id}},
        ],
    )
    return DailyReportInit(
        tenant_1=tenant_1,
        location_11=location_11,
        daily_report_11=daily_report_11,
        daily_report_12=daily_report_12,
        location_13=location_13,
        daily_report_13=daily_report_13,
        tenant_2=tenant_2,
        location_21=location_21,
        daily_report_21=daily_report_21,
        tenant_3=tenant_3,
    )


class TestProjectLocationDailyReport:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tenants(
        self,
        project_location_daily_reports_init: DailyReportInit,
        project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
    ) -> None:
        """Make sure dataloaders filter tenants"""

        x = project_location_daily_reports_init
        await assert_dataloader_filter_tenants(
            project_location_loader_factory,
            "load_daily_reports",
            "daily_reports",
            [
                # Tenant 1 should only see tenant 1 site conditions
                (
                    x.tenant_1.id,
                    [x.location_13.id, x.location_21.id],
                    [[x.daily_report_13], []],
                ),
                # Tenant 2 should only see tenant 2 site conditions
                (
                    x.tenant_2.id,
                    [x.location_13.id, x.location_21.id],
                    [[], [x.daily_report_21]],
                ),
                # Invalid tenant
                (
                    x.tenant_3.id,
                    [x.location_13.id, x.location_21.id],
                    [[], []],
                ),
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_order(
        self,
        db_session: AsyncSession,
        project_location_daily_reports_init: DailyReportInit,
        project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
    ) -> None:
        """Make sure order returned by dataloaders match request"""

        x = project_location_daily_reports_init
        await assert_mocked_dataloader_return_right_order(
            db_session,
            project_location_loader_factory,
            "load_daily_reports",
            "daily_reports",
            x.tenant_1.id,
            filter_ids=[x.location_11.id, x.location_13.id],
            expected_result=[
                [x.daily_report_12, x.daily_report_11],
                [x.daily_report_13],
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_missing(
        self,
        project_location_daily_reports_init: DailyReportInit,
        project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
    ) -> None:
        """Return empty list and don't raise an error when location don't exists"""

        x = project_location_daily_reports_init
        await assert_dataloader_return_right_order(
            project_location_loader_factory,
            "load_daily_reports",
            "daily_reports",
            x.tenant_1.id,
            filter_ids=[x.location_13.id, uuid.uuid4()],
            expected_result=[[x.daily_report_13], []],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_empty(
        self,
        project_location_daily_reports_init: DailyReportInit,
        project_location_loader_factory: LoaderFactory[TenantProjectLocationLoader],
    ) -> None:
        """If an empty list is sent don't return anything"""
        x = project_location_daily_reports_init
        items = await project_location_loader_factory(x.tenant_1.id).load_daily_reports(
            []
        )
        assert items == []
