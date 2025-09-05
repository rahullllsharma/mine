import uuid

import pytest

from tests.factories import (
    AdminUserFactory,
    DailyReportFactory,
    ManagerUserFactory,
    SupervisorUserFactory,
    ViewerUserFactory,
)
from tests.integration.conftest import DBData, ExecuteGQL
from tests.integration.daily_report.helpers import (
    build_report_data,
    build_report_update_data,
    create_report,
    save_daily_report_mutation,
)
from worker_safety_service.models import AsyncSession, User


@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_daily_report_on_create_supervisor(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    The following roles can create a report:
      - Supervisor
      - Manager
      - Administrator
    """
    supervisor = await SupervisorUserFactory.persist(db_session)
    _, report = await create_report(execute_gql, db_session, user=supervisor)
    db_report = await db_data.daily_report(report["id"])
    assert db_report.id == uuid.UUID(report["id"])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_daily_report_on_create_manager(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    The following roles can create a report:
      - Supervisor
      - Manager
      - Administrator
    """
    manager = await ManagerUserFactory.persist(db_session)
    _, report = await create_report(execute_gql, db_session, user=manager)
    db_report = await db_data.daily_report(report["id"])
    assert db_report.id == uuid.UUID(report["id"])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_daily_report_on_create_administrator(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    The following roles can create a report:
      - Supervisor
      - Manager
      - Administrator
    """
    admin = await AdminUserFactory.persist(db_session)
    _, report = await create_report(execute_gql, db_session, user=admin)
    db_report = await db_data.daily_report(report["id"])
    assert db_report.id == uuid.UUID(report["id"])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_daily_report_on_create_no_permission(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    A Viewer cannot create a report
    """
    viewer = await ViewerUserFactory.persist(db_session)
    report_data, *_ = await build_report_data(db_session)

    rsp = (
        await execute_gql(
            **save_daily_report_mutation,
            variables={"dailyReportInput": report_data},
            raw=True,
            user=viewer,
        )
    ).json()

    assert rsp["data"] is None
    assert len(rsp["errors"]) == 1
    assert rsp["errors"][0]["message"] == "User is not authorized to create reports"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_daily_report_on_update_own_permission(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    The following roles can update their own report:
      - Supervisor
      - Manager
      - Administrator
    """
    supervisor = await SupervisorUserFactory.persist(db_session)
    manager = await ManagerUserFactory.persist(db_session)
    administrator = await AdminUserFactory.persist(db_session)

    for user in [supervisor, manager, administrator]:
        report_data, report = await build_report_update_data(db_session, user)
        rsp = await execute_gql(
            **save_daily_report_mutation,
            variables={"dailyReportInput": report_data},
            user=user,
        )
        await db_session.refresh(report)
        assert str(report.id) == rsp["saveDailyReport"]["id"]
        assert (
            str(report.created_by_id)
            == str(user.id)
            == rsp["saveDailyReport"]["createdBy"]["id"]
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_daily_report_on_update_own_no_permission(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    A Viewer cannot update own report
    (This situation should never happen because the viewer cannot also create)
    """
    viewer: User = await ViewerUserFactory.persist(db_session)

    report_data, report = await build_report_update_data(db_session)
    rsp = (
        await execute_gql(
            **save_daily_report_mutation,
            variables={"dailyReportInput": report_data},
            user=viewer,
            raw=True,
        )
    ).json()
    await db_session.refresh(report)
    assert rsp["data"] is None
    assert len(rsp["errors"]) == 1
    assert rsp["errors"][0]["message"] == "User is not authorized to edit this report"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_daily_report_on_update_any_permission(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    The following roles can update any report:
      - Manager
      - Administrator
    """
    manager = await ManagerUserFactory.persist(db_session)
    administrator = await AdminUserFactory.persist(db_session)

    report_data, report = await build_report_update_data(db_session)

    for user in [manager, administrator]:
        rsp = (
            await execute_gql(
                **save_daily_report_mutation,
                variables={"dailyReportInput": report_data},
                raw=True,
                user=user,
            )
        ).json()
        await db_session.refresh(report)
        assert str(report.id) == rsp["data"]["saveDailyReport"]["id"]
        assert report.created_by.id != user.id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_daily_report_on_update_any_no_permission(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    The following roles cannot update others report:
      - Supervisor
      - Viewer
    """
    supervisor = await SupervisorUserFactory.persist(db_session)
    viewer = await ViewerUserFactory.persist(db_session)

    report_data, report = await build_report_update_data(db_session)

    for user in [supervisor, viewer]:
        rsp = (
            await execute_gql(
                **save_daily_report_mutation,
                variables={"dailyReportInput": report_data},
                user=user,
                raw=True,
            )
        ).json()
        await db_session.refresh(report)
        assert rsp["data"] is None
        assert len(rsp["errors"]) == 1
        assert (
            rsp["errors"][0]["message"] == "User is not authorized to edit this report"
        )


delete_daily_report_mutation = {
    "operation_name": "DeleteDailyReport",
    "query": """
mutation DeleteDailyReport($id: UUID!) {
    deleteDailyReport(id: $id)
}
""",
}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_own_daily_report_permission(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    The following roles can delete their own report:
      - Supervisor
      - Manager
      - Administrator
    """
    supervisor = await SupervisorUserFactory.persist(db_session)
    manager = await ManagerUserFactory.persist(db_session)
    administrator = await AdminUserFactory.persist(db_session)

    users = [supervisor, manager, administrator]
    reports = await DailyReportFactory.persist_many(
        db_session, per_item_kwargs=[{"created_by_id": i.id} for i in users]
    )
    for idx, user in enumerate(users):
        report = reports[idx]
        rsp = await execute_gql(
            **delete_daily_report_mutation, variables={"id": report.id}, user=user
        )
        await db_session.refresh(report)
        assert rsp["deleteDailyReport"] is True
        assert report.archived_at is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_own_daily_report_no_permissions(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    A Viewer cannot delete it's own report
    (This situation should never happen because the viewer cannot also create)
    """
    viewer = await ViewerUserFactory.persist(db_session)
    report = await DailyReportFactory.persist(db_session, created_by_id=viewer.id)
    rsp = (
        await execute_gql(
            **delete_daily_report_mutation,
            variables={"id": report.id},
            user=viewer,
            raw=True,
        )
    ).json()
    await db_session.refresh(report)
    assert report.archived_at is None
    assert rsp["data"] is None
    assert len(rsp["errors"]) == 1
    assert rsp["errors"][0]["message"] == "User is not authorized to delete report"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_any_daily_report_permission(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    The following roles can delete their other users report:
      - Manager
      - Administrator
    """
    manager = await ManagerUserFactory.persist(db_session)
    report = await DailyReportFactory.persist(db_session)
    rsp = await execute_gql(
        **delete_daily_report_mutation, variables={"id": report.id}, user=manager
    )
    await db_session.refresh(report)
    assert rsp["deleteDailyReport"] is True
    assert report.archived_at is not None

    admin = await AdminUserFactory.persist(db_session)
    report = await DailyReportFactory.persist(db_session)
    rsp = await execute_gql(
        **delete_daily_report_mutation, variables={"id": report.id}, user=admin
    )
    await db_session.refresh(report)
    assert rsp["deleteDailyReport"] is True
    assert report.archived_at is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_any_daily_report_no_permission(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    The following roles cannot delete their other users report:
      - Viewer
      - Supervisor
    """
    viewer = await ViewerUserFactory.persist(db_session)
    report = await DailyReportFactory.persist(db_session)
    rsp = (
        await execute_gql(
            **delete_daily_report_mutation,
            variables={"id": report.id},
            raw=True,
            user=viewer,
        )
    ).json()
    await db_session.refresh(report)
    assert report.archived_at is None
    assert rsp["data"] is None
    assert len(rsp["errors"]) == 1
    assert rsp["errors"][0]["message"] == "User is not authorized to delete report"

    supervisor = await SupervisorUserFactory.persist(db_session)
    report = await DailyReportFactory.persist(db_session)
    rsp = (
        await execute_gql(
            **delete_daily_report_mutation,
            variables={"id": report.id},
            raw=True,
            user=supervisor,
        )
    ).json()
    await db_session.refresh(report)
    assert report.archived_at is None
    assert rsp["data"] is None
    assert len(rsp["errors"]) == 1
    assert rsp["errors"][0]["message"] == "User is not authorized to delete report"
