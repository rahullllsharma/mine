import random
import string
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

import worker_safety_service.models as models
from tests.factories import (
    DailyReportFactory,
    EnergyBasedObservationFactory,
    JobSafetyBriefingFactory,
    JSBSupervisorLinkFactory,
    LocationFactory,
    NatGridJobSafetyBriefingFactory,
    SupervisorUserFactory,
    TenantFactory,
    UserFactory,
    WorkPackageFactory,
)
from tests.integration.conftest import ExecuteGQL, tenant_id
from tests.integration.forms_list.helpers import (
    call_forms_list_count_query_with_manager_ids,
    call_forms_list_query,
    call_forms_list_query_with_manager_ids,
)
from tests.integration.job_safety_briefing.helpers import (
    build_jsb_data,
    execute_complete_jsb,
    execute_reopen_jsb,
    execute_save_jsb,
)
from worker_safety_service.dal.daily_reports import DailyReportManager
from worker_safety_service.models import AsyncSession, DailyReport, User


def random_string(length: int = 10) -> str:
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return "".join(random.choices(letters, k=length))


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize("form_counts", [(1, 1, 1), (2, 2, 2), (3, 3, 3), (1, 0, 3)])
async def test_forms_list_query(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    form_counts: tuple[int, int, int],
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    date = datetime.now(timezone.utc)
    user = await UserFactory.persist(db_session, tenant_id=tenant.id)
    [jsb_count, dr_count, ebo_count] = form_counts
    await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=jsb_count,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )

    await DailyReportFactory.persist_many(
        db_session,
        size=dr_count,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )
    await EnergyBasedObservationFactory.persist_many(
        db_session,
        size=ebo_count,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )

    forms = await call_forms_list_query(execute_gql, user=admin)
    for item in forms:
        assert "formId" in item, f"Missing formId attribute in item: {item}"
    expected_count = sum(form_counts)

    assert len(forms) == expected_count


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize("form_counts", [(1, 1, 1), (2, 2, 2), (3, 3, 3), (1, 0, 3)])
async def test_forms_list_query_with_manager_ids(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    form_counts: tuple[int, int, int],
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    date = datetime.now(timezone.utc)
    user = await UserFactory.persist(db_session, tenant_id=tenant.id)
    [jsb_count, dr_count, ebo_count] = form_counts
    jsbs = await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=jsb_count,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )

    drs = await DailyReportFactory.persist_many(
        db_session,
        size=dr_count,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )
    ebos = await EnergyBasedObservationFactory.persist_many(
        db_session,
        size=ebo_count,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )
    manager_id = str(uuid4())
    per_item_kwargs = [
        {"jsb_id": jsb.id, "manager_id": manager_id, "tenant_id": tenant_id}
        for jsb in jsbs
    ]
    jsls = await JSBSupervisorLinkFactory.persist_many(
        db_session, 2, manager_id=manager_id, per_item_kwargs=per_item_kwargs
    )
    jsb_ids = [jsl.jsb_id for jsl in jsls]

    kwargs = {"managerIds": [str(manager_id)], "formName": "JobSafetyBriefing"}
    forms = await call_forms_list_query_with_manager_ids(
        execute_gql, user=admin, **kwargs
    )
    assert len(jsb_ids) == len(forms)
    await JSBSupervisorLinkFactory.delete_many(db_session, jsls)
    await JobSafetyBriefingFactory.delete_many(db_session, jsbs)
    await DailyReportFactory.delete_many(db_session, drs)
    await EnergyBasedObservationFactory.delete_many(db_session, ebos)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize("form_counts", [(1, 1, 1), (2, 2, 2), (3, 3, 3), (1, 0, 3)])
async def test_forms_list_query_with_empty_manager_ids(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    form_counts: tuple[int, int, int],
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    date = datetime.now(timezone.utc)
    user = await UserFactory.persist(db_session, tenant_id=tenant.id)
    [jsb_count, dr_count, ebo_count] = form_counts
    jsbs = await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=jsb_count,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )

    drs = await DailyReportFactory.persist_many(
        db_session,
        size=dr_count,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )
    ebos = await EnergyBasedObservationFactory.persist_many(
        db_session,
        size=ebo_count,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )
    manager_id = str(uuid4())
    per_item_kwargs = [
        {"jsb_id": jsb.id, "manager_id": manager_id, "tenant_id": tenant_id}
        for jsb in jsbs
    ]
    jsls = await JSBSupervisorLinkFactory.persist_many(
        db_session, 2, per_item_kwargs, manager_id=manager_id
    )

    kwargs = {"managerIds": [str(uuid4())], "formName": "JobSafetyBriefing"}
    forms = await call_forms_list_query_with_manager_ids(
        execute_gql, user=admin, **kwargs
    )
    assert len(forms) == 0
    await JSBSupervisorLinkFactory.delete_many(db_session, jsls)
    await JobSafetyBriefingFactory.delete_many(db_session, jsbs)
    await DailyReportFactory.delete_many(db_session, drs)
    await EnergyBasedObservationFactory.delete_many(db_session, ebos)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_forms_list_order(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    date = datetime.now(timezone.utc)
    user = await UserFactory.persist(db_session, tenant_id=tenant.id)

    await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=3,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )
    await DailyReportFactory.persist_many(
        db_session,
        size=3,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )
    await EnergyBasedObservationFactory.persist_many(
        db_session,
        size=3,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )

    # Test date asc
    forms = await call_forms_list_query(
        execute_gql, orderBy=[{"direction": "ASC", "field": "CREATED_AT"}], user=admin
    )

    created_dates = [form["createdAt"] for form in forms]

    assert created_dates == sorted(created_dates)

    # Test date desc
    forms = await call_forms_list_query(
        execute_gql, orderBy=[{"direction": "DESC", "field": "CREATED_AT"}], user=admin
    )

    created_dates = [form["createdAt"] for form in forms]
    assert created_dates == sorted(created_dates, reverse=True)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_forms_list_search(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    date = datetime.now(timezone.utc)
    user = await UserFactory.persist(db_session, tenant_id=tenant.id)

    await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=3,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )

    await EnergyBasedObservationFactory.persist_many(
        db_session,
        size=2,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )

    test_location = await LocationFactory.persist(
        db_session, name="test_name", project_id=work_package.id, tenant_id=tenant.id
    )
    test_work_package = await WorkPackageFactory.persist(
        db_session, name="test_name", tenant_id=tenant.id
    )
    test_location_work_package = await LocationFactory.persist(
        db_session, project_id=test_work_package.id, tenant_id=tenant.id
    )
    test_user = await UserFactory.persist(
        db_session, first_name="test_name", tenant_id=tenant.id
    )

    await DailyReportFactory.persist(
        db_session,
        project_location_id=test_location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )

    await JobSafetyBriefingFactory.persist(
        db_session,
        project_location_id=test_location_work_package.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )

    await EnergyBasedObservationFactory.persist(
        db_session,
        project_location_id=test_location_work_package.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=test_user.id,
    )

    forms = await call_forms_list_query(execute_gql, search="test_name", user=admin)

    assert len(forms) == 3


@pytest.mark.asyncio
@pytest.mark.integration
async def test_forms_list_search_supervisor_jsb(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )
    date = datetime.now(timezone.utc)

    manager_id = str(uuid4())
    user = await UserFactory.persist(db_session, tenant_id=tenant.id)
    jsbs = await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=2,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )
    per_item_kwargs = [
        {"jsb_id": jsb.id, "manager_id": manager_id, "tenant_id": tenant.id}
        for jsb in jsbs
    ]
    await JSBSupervisorLinkFactory.persist_many(
        db_session,
        1,
        manager_id=manager_id,
        per_item_kwargs=per_item_kwargs,
        manager_name="test_name",
    )

    forms = await call_forms_list_query(execute_gql, search="test_name", user=admin)

    assert len(forms) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_forms_list_filter(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    date = datetime.now(timezone.utc)
    user = await UserFactory.persist(db_session, tenant_id=tenant.id)
    await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=3,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )
    await DailyReportFactory.persist_many(
        db_session,
        size=2,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )

    await DailyReportFactory.persist(
        db_session,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
        status=models.FormStatus.COMPLETE,
    )

    await EnergyBasedObservationFactory.persist_many(
        db_session,
        size=2,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )

    # Test Form Name

    forms = await call_forms_list_query(
        execute_gql, formName=["JobSafetyBriefing"], user=admin
    )
    assert len(forms) == 3
    for form in forms:
        assert form["__typename"] == "JobSafetyBriefing"

    forms = await call_forms_list_query(
        execute_gql, formName=["DailyReport"], user=admin
    )

    assert len(forms) == 3
    for form in forms:
        assert form["__typename"] == "DailyReport"

    forms = await call_forms_list_query(
        execute_gql, formName=["EnergyBasedObservation"], user=admin
    )

    assert len(forms) == 2
    for form in forms:
        assert form["__typename"] == "EnergyBasedObservation"

    # Test Form Status
    forms = await call_forms_list_query(
        execute_gql, formStatus=["COMPLETE"], user=admin
    )
    assert len(forms) == 1
    assert forms[0]["status"] == "COMPLETE"

    # Test locationId filter
    forms = await call_forms_list_query(
        execute_gql, locationIds=[location.id], user=admin
    )
    assert len(forms) == 6
    for form in forms:
        assert form["__typename"] != "EnergyBasedObservation"

    # Test work package filter
    forms = await call_forms_list_query(
        execute_gql, projectIds=[work_package.id], user=admin
    )
    assert len(forms) == 6
    for form in forms:
        assert form["__typename"] != "EnergyBasedObservation"


async def update_daily_report(
    daily_report: DailyReport,
    manager: DailyReportManager,
    user: User,
) -> None:
    await manager.save_daily_report(
        daily_report_id=daily_report.id,
        project_location_id=daily_report.project_location_id,
        date=daily_report.date_for + timedelta(days=1),
        created_by=user,
        tenant_id=daily_report.tenant_id,
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_forms_list_order_by_work_package_updated(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    daily_report_manager: DailyReportManager,
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)

    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)

    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    date = datetime.now(timezone.utc)
    user = await UserFactory.persist(db_session, tenant_id=tenant.id)
    form_1 = await DailyReportFactory.persist(
        db_session,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
        project_location_id=location.id,
    )
    form_2 = await DailyReportFactory.persist(
        db_session,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
        project_location_id=location.id,
    )

    # Update form 2 then 1
    await update_daily_report(form_2, daily_report_manager, user)
    await update_daily_report(form_1, daily_report_manager, user)

    # Relevant form should be first in ordering
    forms = await call_forms_list_query(
        execute_gql,
        orderBy=[{"direction": "DESC", "field": "UPDATED_AT"}],
        user=admin,
    )

    assert forms[0]["id"] == str(form_1.id)

    # Update form_2
    form_2.sections["additional_information"]["operating_hq"] = "New Test Operating HQ"  # type: ignore
    await update_daily_report(form_2, daily_report_manager, user)

    # form_2 should be first in ordering
    forms = await call_forms_list_query(
        execute_gql,
        orderBy=[{"direction": "DESC", "field": "UPDATED_AT"}],
        user=admin,
    )

    assert forms[0]["id"] == str(form_2.id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_forms_list_fetch_with_no_location(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    daily_report_manager: DailyReportManager,
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)

    date = datetime.now(timezone.utc)
    user = await UserFactory.persist(db_session, tenant_id=tenant.id)

    # Build without location

    form = JobSafetyBriefingFactory.build(
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )

    db_session.add(form)
    await db_session.commit()

    # Relevant form should be first in ordering
    forms = await call_forms_list_query(
        execute_gql,
        orderBy=[{"direction": "DESC", "field": "CREATED_AT"}],
        user=admin,
    )

    assert forms[0]["id"] == str(form.id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_location_name_field(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    date = datetime.now(timezone.utc)
    user = await UserFactory.persist(db_session, tenant_id=tenant.id)
    jsb_with_project_loc = await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=3,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )
    jsb_without_project_loc = await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=2,
        project_location_id=None,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
        contents={
            "work_location": {
                "address": "",
                "city": "",
                "state": "",
                "description": "test location",
            }
        },
    )
    jsb_with_no_work_location = await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=2,
        project_location_id=None,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
        contents={},
    )
    await DailyReportFactory.persist_many(
        db_session,
        size=2,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )

    await DailyReportFactory.persist(
        db_session,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
        status=models.FormStatus.COMPLETE,
    )

    await EnergyBasedObservationFactory.persist_many(
        db_session,
        size=2,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )

    # Test Form Name

    jsbs = await call_forms_list_query(
        execute_gql, formName=["JobSafetyBriefing"], user=admin
    )
    assert len(jsbs) == 7
    for jsb in jsb_with_project_loc:
        form = [d for d in jsbs if d["id"] in str(jsb.id)]
        assert form[0]["__typename"] == "JobSafetyBriefing"
        assert form[0]["locationName"] is None

    for jsb in jsb_without_project_loc:
        form = [d for d in jsbs if d["id"] in str(jsb.id)]
        assert form[0]["__typename"] == "JobSafetyBriefing"
        assert form[0]["locationName"] == "test location"

    # testing JSB when contents is empty object or work_location is None
    for jsb in jsb_with_no_work_location:
        form = [d for d in jsbs if d["id"] in str(jsb.id)]
        assert form[0]["__typename"] == "JobSafetyBriefing"
        assert form[0]["locationName"] is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_location_name_field_job_safety_briefing(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    date = datetime.now(timezone.utc)
    user = await UserFactory.persist(db_session, tenant_id=tenant.id)
    jsb_with_project_loc = await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=3,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
        contents={"work_location": {"address": "test address"}},
    )
    jsb_without_project_loc = await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=2,
        project_location_id=None,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
        contents={"work_location": {"description": "test description"}},
    )

    # Test Form Name

    jsbs = await call_forms_list_query(
        execute_gql, formName=["JobSafetyBriefing"], user=admin
    )
    assert len(jsbs) == 5
    for jsb in jsb_with_project_loc:
        form = [d for d in jsbs if d["id"] in str(jsb.id)]
        assert form[0]["__typename"] == "JobSafetyBriefing"
        assert form[0]["locationName"] == "test address"

    for jsb in jsb_without_project_loc:
        form = [d for d in jsbs if d["id"] in str(jsb.id)]
        assert form[0]["__typename"] == "JobSafetyBriefing"
        assert form[0]["locationName"] == "test description"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_location_name_field_nat_grid_job_safety_briefing(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    date = datetime.now(timezone.utc)
    user = await UserFactory.persist(db_session, tenant_id=tenant.id)
    jsb_with_project_loc = await NatGridJobSafetyBriefingFactory.persist_many(
        db_session,
        size=3,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
        contents={"work_location": {"address": "test address"}},
    )

    jsbs = await call_forms_list_query(
        execute_gql, formName=["NatGridJobSafetyBriefing"], user=admin
    )
    for jsb in jsb_with_project_loc:
        form = [d for d in jsbs if d["id"] in str(jsb.id)]
        assert form[0]["__typename"] == "NatGridJobSafetyBriefing"
        assert form[0]["locationName"] == "test address"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_location_name_field_energy_based_observation(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)

    date = datetime.now(timezone.utc)
    user = await UserFactory.persist(db_session, tenant_id=tenant.id)
    energy_based_observation = await EnergyBasedObservationFactory.persist_many(
        db_session,
        size=2,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
        contents={"details": {"work_location": "test work location"}},
    )

    # Test Form Name

    ebos = await call_forms_list_query(
        execute_gql, formName=["EnergyBasedObservation"], user=admin
    )
    assert len(ebos) == 2
    for ebo in energy_based_observation:
        form = [d for d in ebos if d["id"] in str(ebo.id)]
        assert form[0]["__typename"] == "EnergyBasedObservation"
        assert form[0]["locationName"] == "test work location"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_location_name_daily_reports(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    date = datetime.now(timezone.utc)
    user = await UserFactory.persist(db_session, tenant_id=tenant.id)
    daily_reports = await DailyReportFactory.persist_many(
        db_session,
        size=2,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )

    # Test Form Name

    reports = await call_forms_list_query(
        execute_gql, formName=["DailyReport"], user=admin
    )
    assert len(reports) == 2
    for report in daily_reports:
        form = [d for d in reports if d["id"] in str(report.id)]
        assert form[0]["__typename"] == "DailyReport"
        assert form[0]["locationName"] == location.name


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_jsb_supervisors_with_forms_list(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    jsb_count = 3
    tenant, admin = await TenantFactory.new_with_admin(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    date = datetime.now(timezone.utc)
    user = await UserFactory.persist(db_session, tenant_id=tenant.id)
    [jsb_count, dr_count, ebo_count] = [jsb_count, 2, 2]
    jsbs = await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=jsb_count,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )
    await DailyReportFactory.persist_many(
        db_session,
        size=dr_count,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )
    await EnergyBasedObservationFactory.persist_many(
        db_session,
        size=ebo_count,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )
    per_item_kwargs = [
        {"jsb_id": jsbs[0].id, "manager_id": str(uuid4()), "tenant_id": tenant_id},
        {"jsb_id": jsbs[0].id, "manager_id": str(uuid4()), "tenant_id": tenant_id},
        {"jsb_id": jsbs[0].id, "manager_id": str(uuid4()), "tenant_id": tenant_id},
        {"jsb_id": jsbs[1].id, "manager_id": str(uuid4()), "tenant_id": tenant_id},
        {"jsb_id": jsbs[2].id, "manager_id": str(uuid4()), "tenant_id": tenant_id},
    ]
    await JSBSupervisorLinkFactory.persist_many(
        db_session, 1, manager_id=str(uuid4()), per_item_kwargs=per_item_kwargs
    )
    forms = await call_forms_list_query(execute_gql, user=admin)
    supervisors = [
        form["supervisor"] for form in forms if form["supervisor"] is not None
    ]
    assert len(supervisors[0]) == 3
    assert len(supervisors[1]) == 1
    assert len(supervisors[2]) == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_jsb_supervisors_with_forms_list_count(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    jsb_count = 3
    tenant, admin = await TenantFactory.new_with_admin(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    date = datetime.now(timezone.utc)
    user = await UserFactory.persist(db_session, tenant_id=tenant.id)
    [jsb_count, dr_count, ebo_count] = [jsb_count, 2, 2]
    jsbs = await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=jsb_count,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )
    await DailyReportFactory.persist_many(
        db_session,
        size=dr_count,
        project_location_id=location.id,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )
    await EnergyBasedObservationFactory.persist_many(
        db_session,
        size=ebo_count,
        date_for=date,
        tenant_id=tenant.id,
        created_by_id=user.id,
    )
    manager_id_1 = str(uuid4())
    manager_id_2 = str(uuid4())
    manager_id_3 = str(uuid4())
    per_item_kwargs = [
        {"jsb_id": jsbs[0].id, "manager_id": manager_id_1, "tenant_id": tenant_id},
        {"jsb_id": jsbs[0].id, "manager_id": manager_id_2, "tenant_id": tenant_id},
        {"jsb_id": jsbs[0].id, "manager_id": manager_id_3, "tenant_id": tenant_id},
        {"jsb_id": jsbs[1].id, "manager_id": manager_id_1, "tenant_id": tenant_id},
        {"jsb_id": jsbs[2].id, "manager_id": manager_id_2, "tenant_id": tenant_id},
    ]
    await JSBSupervisorLinkFactory.persist_many(
        db_session, 1, manager_id=str(uuid4()), per_item_kwargs=per_item_kwargs
    )

    formsListCount = await call_forms_list_count_query_with_manager_ids(
        execute_gql,
        formName=["JobSafetyBriefing"],
        managerIds=[manager_id_1],
        user=admin,
    )
    assert formsListCount == 2

    formsListCount = await call_forms_list_count_query_with_manager_ids(
        execute_gql,
        formName=["JobSafetyBriefing"],
        managerIds=[manager_id_3],
        user=admin,
    )
    assert formsListCount == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_forms_list_default_order(
    execute_gql: ExecuteGQL,
    db_session: models.AsyncSession,
) -> None:
    """
    Test that forms are ordered by 'created_at' in ascending order when no order_by is provided.
    """
    tenant, admin = await TenantFactory.new_with_admin(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    user = await UserFactory.persist(db_session, tenant_id=tenant.id)
    now = datetime.now(timezone.utc)

    form1 = await JobSafetyBriefingFactory.persist(
        db_session,
        project_location_id=location.id,
        date_for=now,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=3),
    )
    form2 = await DailyReportFactory.persist(
        db_session,
        project_location_id=location.id,
        date_for=now + timedelta(days=1),
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=2),
    )
    form3 = await EnergyBasedObservationFactory.persist(
        db_session,
        date_for=now,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=1),
    )
    form4 = await NatGridJobSafetyBriefingFactory.persist(
        db_session,
        project_location_id=location.id,
        date_for=now - timedelta(days=1),
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now,
    )

    forms = await call_forms_list_query(execute_gql, user=admin)

    expected_order = [form1, form2, form3, form4]
    expected_order_ids = [str(form.id) for form in expected_order]
    returned_order_ids = [form["id"] for form in forms]

    assert returned_order_ids == expected_order_ids, (
        f"Default ordering failed. Expected order: {expected_order_ids}, "
        f"but got: {returned_order_ids}"
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_forms_list_default_order_with_manager_id_filter(
    execute_gql: ExecuteGQL,
    db_session: models.AsyncSession,
) -> None:
    """
    Test that when a managerId filter is applied, the returned forms are:
    1. Only JobSafetyBriefing (JSB) forms linked to the specified managerId.
    2. Other form types (NatGridJSB, EBO, DIR) are returned unfiltered.
    3. All forms are ordered by 'created_at' in ascending order.
    """
    tenant, admin = await TenantFactory.new_with_admin(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    user = await UserFactory.persist(db_session, tenant_id=tenant.id)

    manager_id = str(uuid4())

    now = datetime.now(timezone.utc)

    jsb1 = await JobSafetyBriefingFactory.persist(
        db_session,
        project_location_id=location.id,
        date_for=now,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=10),
    )
    await JobSafetyBriefingFactory.persist(
        db_session,
        project_location_id=location.id,
        date_for=now + timedelta(days=1),
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=9),
    )
    jsb3 = await JobSafetyBriefingFactory.persist(
        db_session,
        project_location_id=location.id,
        date_for=now,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=8),
    )
    await JobSafetyBriefingFactory.persist(
        db_session,
        project_location_id=location.id,
        date_for=now - timedelta(days=1),
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=7),
    )

    await JSBSupervisorLinkFactory.persist(
        db_session,
        jsb_id=jsb1.id,
        manager_id=manager_id,
        tenant_id=tenant.id,
    )
    await JSBSupervisorLinkFactory.persist(
        db_session,
        jsb_id=jsb3.id,
        manager_id=manager_id,
        tenant_id=tenant.id,
    )

    natgrid_jsb1 = await NatGridJobSafetyBriefingFactory.persist(
        db_session,
        project_location_id=location.id,
        date_for=now - timedelta(days=2),
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=6),
    )
    natgrid_jsb2 = await NatGridJobSafetyBriefingFactory.persist(
        db_session,
        project_location_id=location.id,
        date_for=now + timedelta(days=2),
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=5),
    )

    ebo1 = await EnergyBasedObservationFactory.persist(
        db_session,
        date_for=now,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=4),
    )
    ebo2 = await EnergyBasedObservationFactory.persist(
        db_session,
        date_for=now + timedelta(days=3),
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=3),
    )

    dr1 = await DailyReportFactory.persist(
        db_session,
        project_location_id=location.id,
        date_for=now,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=2),
    )
    dr2 = await DailyReportFactory.persist(
        db_session,
        project_location_id=location.id,
        date_for=now + timedelta(days=4),
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=1, hours=4),
    )

    kwargs = {"managerIds": [manager_id]}

    forms = await call_forms_list_query_with_manager_ids(
        execute_gql, user=admin, **kwargs
    )

    expected_jsb_forms = [jsb1, jsb3]
    expected_other_forms = [natgrid_jsb1, natgrid_jsb2, ebo1, ebo2, dr1, dr2]

    combined_expected_forms = expected_jsb_forms + expected_other_forms
    combined_expected_sorted = sorted(
        combined_expected_forms, key=lambda f: f.created_at
    )
    combined_expected_ids = [str(form.id) for form in combined_expected_sorted]

    returned_order_ids = [form["id"] for form in forms]
    expected_total = len(combined_expected_forms)

    assert len(forms) == expected_total, (
        f"Expected {expected_total} forms (JSBs linked to manager + other forms), "
        f"but got {len(forms)}."
    )

    for jsb_form in expected_jsb_forms:
        assert (
            str(jsb_form.id) in returned_order_ids
        ), f"JSB form with ID {jsb_form.id} linked to managerId {manager_id} was not returned."

    for other_form in expected_other_forms:
        assert (
            str(other_form.id) in returned_order_ids
        ), f"Form with ID {other_form.id} was not returned, but it should be unaffected by managerId filter."

    assert returned_order_ids == combined_expected_ids, (
        f"Default ordering with managerId filter failed. Expected order: {combined_expected_ids}, "
        f"but got: {returned_order_ids}"
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_forms_list_desc_created_at_order_with_manager_id_filter(
    execute_gql: ExecuteGQL,
    db_session: models.AsyncSession,
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )
    user = await UserFactory.persist(db_session, tenant_id=tenant.id)

    now = datetime.now(timezone.utc)
    manager_id = str(uuid4())

    jsb_linked_1 = await JobSafetyBriefingFactory.persist(
        db_session,
        project_location_id=location.id,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=10),
        date_for=now,
    )
    jsb_unlinked_1 = await JobSafetyBriefingFactory.persist(
        db_session,
        project_location_id=location.id,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=9),
        date_for=now + timedelta(days=1),
    )
    jsb_linked_2 = await JobSafetyBriefingFactory.persist(
        db_session,
        project_location_id=location.id,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=8),
        date_for=now,
    )
    jsb_unlinked_2 = await JobSafetyBriefingFactory.persist(
        db_session,
        project_location_id=location.id,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=7),
        date_for=now - timedelta(days=1),
    )

    await JSBSupervisorLinkFactory.persist(
        db_session,
        jsb_id=jsb_linked_1.id,
        manager_id=manager_id,
        tenant_id=tenant.id,
    )
    await JSBSupervisorLinkFactory.persist(
        db_session,
        jsb_id=jsb_linked_2.id,
        manager_id=manager_id,
        tenant_id=tenant.id,
    )

    natgrid_jsb_1 = await NatGridJobSafetyBriefingFactory.persist(
        db_session,
        project_location_id=location.id,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=6),
        date_for=now - timedelta(days=2),
    )
    ebo_1 = await EnergyBasedObservationFactory.persist(
        db_session,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=5),
        date_for=now,
    )
    dr_1 = await DailyReportFactory.persist(
        db_session,
        project_location_id=location.id,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=4),
        date_for=now,
    )

    forms = await call_forms_list_query_with_manager_ids(
        execute_gql,
        user=admin,
        managerIds=[manager_id],
        orderBy=[{"direction": "DESC", "field": "CREATED_AT"}],
    )

    expected_forms = [jsb_linked_1, jsb_linked_2, natgrid_jsb_1, ebo_1, dr_1]

    expected_sorted = sorted(expected_forms, key=lambda f: f.created_at, reverse=True)
    expected_ids = [str(f.id) for f in expected_sorted]
    actual_ids = [f["id"] for f in forms]

    assert len(forms) == len(
        expected_forms
    ), f"Expected {len(expected_forms)} forms total, but got {len(forms)}."
    assert (
        actual_ids == expected_ids
    ), f"Ordering by CREATED_AT DESC failed. Expected {expected_ids}, got {actual_ids}."

    for unlinked_jsb in (jsb_unlinked_1, jsb_unlinked_2):
        assert (
            str(unlinked_jsb.id) not in actual_ids
        ), f"Found JSB {unlinked_jsb.id} in results despite not being linked to manager {manager_id}."


@pytest.mark.asyncio
@pytest.mark.integration
async def test_forms_list_asc_updated_at_order_with_manager_id_filter(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    now = datetime.now(timezone.utc)
    user = await UserFactory.persist(db_session, tenant_id=tenant.id)
    manager_id = str(uuid4())

    jsb_linked_1 = await JobSafetyBriefingFactory.persist(
        db_session,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=3),
        updated_at=now - timedelta(days=3),
        date_for=now,
        project_location_id=location.id,
    )
    jsb_linked_2 = await JobSafetyBriefingFactory.persist(
        db_session,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=2),
        updated_at=now - timedelta(days=2),
        date_for=now,
        project_location_id=location.id,
    )
    jsb_unlinked = await JobSafetyBriefingFactory.persist(
        db_session,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=1),
        updated_at=now - timedelta(days=1),
        date_for=now + timedelta(days=1),
        project_location_id=location.id,
    )

    await JSBSupervisorLinkFactory.persist(
        db_session,
        jsb_id=jsb_linked_1.id,
        manager_id=manager_id,
        tenant_id=tenant.id,
    )
    await JSBSupervisorLinkFactory.persist(
        db_session,
        jsb_id=jsb_linked_2.id,
        manager_id=manager_id,
        tenant_id=tenant.id,
    )

    natgrid_jsb = await NatGridJobSafetyBriefingFactory.persist(
        db_session,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=1, hours=12),
        updated_at=now - timedelta(days=1, hours=12),
        date_for=now - timedelta(days=2),
        project_location_id=location.id,
    )
    ebo = await EnergyBasedObservationFactory.persist(
        db_session,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=1, hours=6),
        updated_at=now - timedelta(days=1, hours=6),
        date_for=now,
    )
    daily_report = await DailyReportFactory.persist(
        db_session,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=1, hours=3),
        updated_at=now - timedelta(days=1, hours=3),
        date_for=now,
        project_location_id=location.id,
    )

    jsb_linked_1.updated_at = now - timedelta(days=2, hours=20)
    natgrid_jsb.updated_at = now - timedelta(days=1, hours=8)

    await db_session.commit()

    forms = await call_forms_list_query_with_manager_ids(
        execute_gql,
        user=admin,
        managerIds=[manager_id],
        orderBy=[{"direction": "ASC", "field": "UPDATED_AT"}],
    )

    expected_jsbs = [jsb_linked_1, jsb_linked_2]
    expected_others = [natgrid_jsb, ebo, daily_report]
    combined_expected = expected_jsbs + expected_others

    combined_expected_sorted = sorted(combined_expected, key=lambda f: f.updated_at)
    expected_ids = [str(f.id) for f in combined_expected_sorted]
    actual_ids = [f["id"] for f in forms]

    assert len(forms) == len(
        combined_expected
    ), f"Expected {len(combined_expected)} forms in the result, got {len(forms)}."

    assert actual_ids == expected_ids, (
        f"Forms are not ordered by UPDATED_AT ascending correctly.\n"
        f"Expected order: {expected_ids}\nGot: {actual_ids}"
    )

    assert (
        str(jsb_unlinked.id) not in actual_ids
    ), f"Unlinked JSB (id={jsb_unlinked.id}) unexpectedly appeared in results."


@pytest.mark.asyncio
@pytest.mark.integration
async def test_forms_list_count_with_updated_at_desc_order_and_manager_id_filter(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    user = await UserFactory.persist(db_session, tenant_id=tenant.id)
    manager_id = str(uuid4())

    now = datetime.now(timezone.utc)

    jsb_linked_1 = await JobSafetyBriefingFactory.persist(
        db_session,
        project_location_id=location.id,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=3),
        updated_at=now - timedelta(days=3),
        date_for=now,
    )
    jsb_linked_2 = await JobSafetyBriefingFactory.persist(
        db_session,
        project_location_id=location.id,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=2),
        updated_at=now - timedelta(days=2),
        date_for=now,
    )
    await JobSafetyBriefingFactory.persist(
        db_session,
        project_location_id=location.id,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=1),
        updated_at=now - timedelta(days=1),
        date_for=now + timedelta(days=1),
    )

    await JSBSupervisorLinkFactory.persist(
        db_session,
        jsb_id=jsb_linked_1.id,
        manager_id=manager_id,
        tenant_id=tenant.id,
    )
    await JSBSupervisorLinkFactory.persist(
        db_session,
        jsb_id=jsb_linked_2.id,
        manager_id=manager_id,
        tenant_id=tenant.id,
    )

    await DailyReportFactory.persist(
        db_session,
        project_location_id=location.id,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=1, hours=5),
        updated_at=now - timedelta(days=1, hours=5),
        date_for=now,
    )
    await EnergyBasedObservationFactory.persist(
        db_session,
        tenant_id=tenant.id,
        created_by_id=user.id,
        created_at=now - timedelta(days=1, hours=6),
        updated_at=now - timedelta(days=1, hours=6),
        date_for=now,
    )

    await db_session.commit()

    forms_count = await call_forms_list_count_query_with_manager_ids(
        execute_gql,
        managerIds=[manager_id],
        orderBy=[{"direction": "DESC", "field": "UPDATED_AT"}],
        user=admin,
    )

    expected_count = 4

    assert (
        forms_count == expected_count
    ), f"Wrong forms count. Expected {expected_count}, got {forms_count}."


@pytest.mark.asyncio
@pytest.mark.integration
async def test_forms_list_search_by_updated_and_created_by(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)

    user = await SupervisorUserFactory.persist(db_session)

    test_user1 = await SupervisorUserFactory.persist(
        db_session,
        first_name="test",
        last_name="user1",
    )

    date = datetime.now(timezone.utc)

    await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=3,
        date_for=date,
        created_by_id=test_user1.id,
        status=models.FormStatus.IN_PROGRESS,
    )

    # Persist new JSB
    jsb_request, *_ = await build_jsb_data(db_session)
    jsb_response = await execute_save_jsb(execute_gql, jsb_request, user=test_user1)

    forms = await call_forms_list_query(execute_gql, search="user1", user=user)
    # Created 4 JSB by test_user1
    # Shows search is working on created by
    assert len(forms) == 4

    test_user2 = await SupervisorUserFactory.persist(
        db_session,
        first_name="test",
        last_name="user2",
    )

    # Change status to Complete
    jsb_request["jsbId"] = jsb_response["id"]
    jsb_response = await execute_complete_jsb(execute_gql, jsb_request, user=test_user2)

    forms = await call_forms_list_query(execute_gql, search="user2", user=user)
    # Save 1 Complete JSB by test_user2
    # Shows search is working on updated by
    assert len(forms) == 1

    test_user3 = await SupervisorUserFactory.persist(
        db_session,
        first_name="test",
        last_name="user3",
    )

    # Change status to In Progress
    jsb_id = jsb_response["id"]
    await execute_reopen_jsb(execute_gql, jsb_id)

    # Change status to Complete
    jsb_request["jsbId"] = jsb_response["id"]
    jsb_response = await execute_complete_jsb(execute_gql, jsb_request, user=test_user3)

    forms = await call_forms_list_query(execute_gql, search="user3", user=user)
    # Reopen and Save 1 Complete JSB by test_user3
    # Shows updated by changes to test_user3 and search is working on it
    assert len(forms) == 1

    forms = await call_forms_list_query(execute_gql, search="user2", user=user)
    # Updated by is changed from test_user2 to test_user3
    # Save 0 Complete JSB by test_user2
    assert len(forms) == 0
