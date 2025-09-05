import pytest

from tests.factories import (
    AdminUserFactory,
    EnergyBasedObservationFactory,
    ManagerUserFactory,
    SupervisorUserFactory,
    ViewerUserFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.energy_based_observations.helpers import (
    build_ebo_data,
    execute_complete_ebo,
    execute_reopen_ebo,
)
from worker_safety_service.models import AsyncSession

delete_ebo_report_mutation = {
    "operation_name": "DeleteEbo",
    "query": """
mutation DeleteEbo($id: UUID!) {
    deleteEnergyBasedObservation(id: $id)
}
""",
}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_own_ebo_report_permission(
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
    reports = await EnergyBasedObservationFactory.persist_many(
        db_session, per_item_kwargs=[{"created_by_id": i.id} for i in users]
    )

    for idx, user in enumerate(users):
        report = reports[idx]
        rsp = await execute_gql(
            **delete_ebo_report_mutation, variables={"id": report.id}, user=user
        )
        await db_session.refresh(report)
        assert rsp["deleteEnergyBasedObservation"] is True
        assert report.archived_at is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_own_ebo_report_no_permissions(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    A Viewer cannot delete it's own report
    (This situation should never happen because the viewer cannot also create)
    """
    viewer = await ViewerUserFactory.persist(db_session)
    report = await EnergyBasedObservationFactory.persist(
        db_session, created_by_id=viewer.id
    )
    rsp = (
        await execute_gql(
            **delete_ebo_report_mutation,
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
async def test_delete_any_ebo_report_permission(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    The following roles can delete their other users report:
      - Manager
      - Administrator
    """
    manager = await ManagerUserFactory.persist(db_session)
    report = await EnergyBasedObservationFactory.persist(db_session)
    rsp = await execute_gql(
        **delete_ebo_report_mutation, variables={"id": report.id}, user=manager
    )
    await db_session.refresh(report)
    assert rsp["deleteEnergyBasedObservation"] is True
    assert report.archived_at is not None

    admin = await AdminUserFactory.persist(db_session)
    report = await EnergyBasedObservationFactory.persist(db_session)
    rsp = await execute_gql(
        **delete_ebo_report_mutation, variables={"id": report.id}, user=admin
    )
    await db_session.refresh(report)
    assert rsp["deleteEnergyBasedObservation"] is True
    assert report.archived_at is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_any_ebo_report_no_permission(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    The following roles cannot delete their other users report:
      - Viewer
      - Supervisor
    """
    viewer = await ViewerUserFactory.persist(db_session)
    report = await EnergyBasedObservationFactory.persist(db_session)
    rsp = (
        await execute_gql(
            **delete_ebo_report_mutation,
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
    report = await EnergyBasedObservationFactory.persist(db_session)
    rsp = (
        await execute_gql(
            **delete_ebo_report_mutation,
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


@pytest.mark.asyncio
@pytest.mark.integration
async def test_reopen_ebo_permission(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    The following roles can reopen EBO:
      - Manager
      - Administrator
    """
    manager = await ManagerUserFactory.persist(db_session)
    administrator = await AdminUserFactory.persist(db_session)
    users = [manager, administrator]
    ebos = await EnergyBasedObservationFactory.persist_many(
        db_session, per_item_kwargs=[{"created_by_id": i.id} for i in users]
    )

    for ebo in ebos:
        ebo_contents = await build_ebo_data(db_session)
        ebo_request = {"id": ebo.id, "energyBasedObservationInput": ebo_contents}
        await execute_complete_ebo(execute_gql, ebo_request)

    for idx, user in enumerate(users):
        reopened_ebo = await execute_reopen_ebo(execute_gql, ebos[idx].id, user=user)
        assert reopened_ebo["status"] == "IN_PROGRESS"
        assert reopened_ebo["completedAt"] is not None
        assert reopened_ebo["completedBy"] is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_reopen_ebo_no_permission(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    The following roles can't reopen EBO:
      - Viewer
    """
    viewer = await ViewerUserFactory.persist(db_session)

    users = [viewer]
    ebos = await EnergyBasedObservationFactory.persist_many(
        db_session, per_item_kwargs=[{"created_by_id": i.id} for i in users]
    )

    for ebo in ebos:
        ebo_contents = await build_ebo_data(db_session)
        ebo_request = {"id": ebo.id, "energyBasedObservationInput": ebo_contents}
        await execute_complete_ebo(execute_gql, ebo_request)

    for idx, user in enumerate(users):
        with pytest.raises(Exception):
            await execute_reopen_ebo(execute_gql, (ebos[idx]).id, user=user)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_supervisor_reopen_own_closed_ebo_permission(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    The following roles can reopen only their own closed EBO:
      - Supervisor
    """
    supervisor = await SupervisorUserFactory.persist(db_session)
    admin = await AdminUserFactory.persist(db_session)

    users = [supervisor, admin]
    ebos = await EnergyBasedObservationFactory.persist_many(
        db_session, per_item_kwargs=[{"created_by_id": i.id} for i in users]
    )

    for ebo in ebos:
        ebo_contents = await build_ebo_data(db_session)
        ebo_request = {"id": ebo.id, "energyBasedObservationInput": ebo_contents}
        await execute_complete_ebo(execute_gql, ebo_request)

    # Supervisor should be able to reopen their own EBO
    supervisor_ebo = next(ebo for ebo in ebos if ebo.created_by_id == supervisor.id)
    reopened_supervisor_ebo = await execute_reopen_ebo(
        execute_gql, supervisor_ebo.id, user=supervisor
    )
    assert reopened_supervisor_ebo["createdBy"]["id"] == str(supervisor.id)

    # Supervisor should not be able to reopen EBO
    admin_ebo = next(ebo for ebo in ebos if ebo.created_by_id == admin.id)
    with pytest.raises(Exception):
        await execute_reopen_ebo(execute_gql, admin_ebo.id, user=supervisor)
