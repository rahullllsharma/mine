import json
import uuid
from logging import getLogger
from typing import Callable

import pytest
from httpx import AsyncClient
from sqlmodel import col, select

from tests.factories import (
    LibrarySiteConditionFactory,
    TenantFactory,
    WorkTypeFactory,
    WorkTypeLibrarySiteConditionLinkFactory,
    WorkTypeTaskLinkFactory,
)
from worker_safety_service.models import (
    AsyncSession,
    WorkType,
    WorkTypeLibrarySiteConditionLink,
    WorkTypeTaskLink,
)
from worker_safety_service.rest.routers.work_types import (
    WorkTypeAttributes,
    WorkTypeRequest,
)

logger = getLogger(__name__)
WORK_TYPE_ROUTE = "http://127.0.0.1:8000/rest/work-types"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_core_work_type_201_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    wt_id = uuid.uuid4()
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(name="test_343")
    )
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{wt_id}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    work_type = (
        await db_session.execute(select(WorkType).where(WorkType.id == wt_id))
    ).scalar()
    assert work_type
    assert work_type.name == "test_343"
    assert work_type.core_work_type_ids is None
    assert work_type.tenant_id is None

    await TenantFactory.delete_many(db_session, [tenant])
    await WorkTypeFactory.delete_many(db_session, [work_type])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_tenant_work_type_201_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    wt_1, _, _ = await WorkTypeFactory.core_work_type_with_task_and_sc_link(
        session=db_session, name="test_1"
    )
    wt_2, _, _ = await WorkTypeFactory.core_work_type_with_task_and_sc_link(
        session=db_session, name="test_2"
    )
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(
            name="tenant_test_343", core_work_type_ids=[wt_1.id, wt_2.id]
        )
    )
    twt_id = uuid.uuid4()
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{twt_id}?tenant_id={tenant.id}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    tenant_work_type = (
        await db_session.execute(select(WorkType).where(WorkType.id == twt_id))
    ).scalar()
    assert tenant_work_type
    assert tenant_work_type.name == "tenant_test_343"
    assert set(tenant_work_type.core_work_type_ids) == set([wt_1.id, wt_2.id])
    assert tenant_work_type.tenant_id == tenant.id
    wt_t_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_([wt_1.id, wt_2.id, twt_id]),
            )
        )
    ).all()
    assert wt_t_link
    assert len(wt_t_link) == 4
    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [wt_1.id, wt_2.id, twt_id]
                ),
            )
        )
    ).all()
    assert wt_sc_link
    assert len(wt_sc_link) == 4

    await WorkTypeTaskLinkFactory.delete_many(db_session, wt_t_link)
    await WorkTypeLibrarySiteConditionLinkFactory.delete_many(db_session, wt_sc_link)
    await TenantFactory.delete_many(db_session, [tenant])
    await WorkTypeFactory.delete_many(db_session, [wt_1, wt_2, tenant_work_type])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_core_work_type_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    db_work_type = await WorkTypeFactory.persist(db_session)

    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(
            name="test_3_2", core_work_type_ids=[str(uuid.uuid4())]
        )
    )
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(db_work_type.id)}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 200
    work_type = response.json()["data"]["attributes"]

    assert work_type["name"] == "test_3_2"

    await db_session.refresh(db_work_type)
    assert db_work_type.name == "test_3_2"

    await TenantFactory.delete_many(db_session, [tenant])
    await WorkTypeFactory.delete_many(db_session, [db_work_type])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_tenant_work_type_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    wt_1, _, _ = await WorkTypeFactory.core_work_type_with_task_and_sc_link(
        session=db_session, name="test_1"
    )
    wt_2, _, _ = await WorkTypeFactory.core_work_type_with_task_and_sc_link(
        session=db_session, name="test_2"
    )
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(
            name="tenant_test_343", core_work_type_ids=[wt_1.id]
        )
    )
    twt_id = uuid.uuid4()
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{twt_id}?tenant_id={tenant.id}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    tenant_work_type = (
        await db_session.execute(select(WorkType).where(WorkType.id == twt_id))
    ).scalar()
    assert tenant_work_type

    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(name="tenant_test_343_1")
    )
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(tenant_work_type.id)}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 200
    work_type_resp = response.json()["data"]["attributes"]
    assert work_type_resp["name"] == "tenant_test_343_1"

    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(core_work_type_ids=[wt_2.id])
    )
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(tenant_work_type.id)}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 200
    work_type_resp = response.json()["data"]["attributes"]
    assert work_type_resp["core_work_type_ids"] == [str(wt_2.id)]

    await db_session.refresh(tenant_work_type)
    assert tenant_work_type.name == "tenant_test_343_1"
    assert tenant_work_type.core_work_type_ids == [wt_2.id]
    assert tenant_work_type.tenant_id

    wt_t_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_([wt_1.id, wt_2.id, twt_id]),
            )
        )
    ).all()
    assert wt_t_link
    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [wt_1.id, wt_2.id, twt_id]
                ),
            )
        )
    ).all()
    assert wt_sc_link

    await WorkTypeTaskLinkFactory.delete_many(db_session, wt_t_link)
    await WorkTypeLibrarySiteConditionLinkFactory.delete_many(db_session, wt_sc_link)
    await TenantFactory.delete_many(db_session, [tenant])
    await WorkTypeFactory.delete_many(db_session, [wt_1, wt_2, tenant_work_type])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_tenant_work_type_204_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    # create core work type with 1 task and sc each
    cwt, _, _ = await WorkTypeFactory.core_work_type_with_task_and_sc_link(db_session)

    # create a tenant wt using the cwt, thus linking the cwt's task and sc to this twt.
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(
            name="tenant_test_343", core_work_type_ids=[cwt.id]
        )
    )
    twt_id = uuid.uuid4()
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{twt_id}?tenant_id={tenant.id}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    tenant_work_type = (
        await db_session.execute(select(WorkType).where(WorkType.id == twt_id))
    ).scalar()
    assert tenant_work_type
    assert tenant_work_type.name == "tenant_test_343"
    assert tenant_work_type.core_work_type_ids == [cwt.id]
    assert tenant_work_type.tenant_id == tenant.id

    # validate the links
    wt_t_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_([cwt.id, twt_id]),
            )
        )
    ).all()
    assert wt_t_link
    assert len(wt_t_link) == 2
    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [cwt.id, twt_id]
                ),
            )
        )
    ).all()
    assert wt_sc_link
    assert len(wt_sc_link) == 2

    response = await client.delete(
        f"{WORK_TYPE_ROUTE}/{str(twt_id)}",
    )
    assert response.status_code == 200

    # validate the links
    wt_t_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_([cwt.id, twt_id]),
            )
        )
    ).all()
    assert wt_t_link
    assert len(wt_t_link) == 1
    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [cwt.id, twt_id]
                ),
            )
        )
    ).all()
    assert wt_sc_link
    assert len(wt_sc_link) == 1

    await WorkTypeTaskLinkFactory.delete_many(db_session, wt_t_link)
    await WorkTypeLibrarySiteConditionLinkFactory.delete_many(db_session, wt_sc_link)
    await TenantFactory.delete_many(db_session, [tenant])
    await WorkTypeFactory.delete_many(db_session, [cwt, tenant_work_type])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_core_work_type_204_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    # create core work type with 1 task and sc each
    cwt, _, _ = await WorkTypeFactory.core_work_type_with_task_and_sc_link(
        db_session, name="new_core_work_type_for_archiving"
    )

    # create a tenant wt using the cwt, thus linking the cwt's task and sc to this twt.
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(
            name="tenant_test_343", core_work_type_ids=[cwt.id]
        )
    )
    twt_id = uuid.uuid4()
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{twt_id}?tenant_id={tenant.id}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    tenant_work_type = (
        await db_session.execute(select(WorkType).where(WorkType.id == twt_id))
    ).scalar()
    assert tenant_work_type
    assert tenant_work_type.name == "tenant_test_343"
    assert tenant_work_type.core_work_type_ids == [cwt.id]
    assert tenant_work_type.tenant_id == tenant.id

    # validate the links
    wt_t_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_([cwt.id, twt_id]),
            )
        )
    ).all()
    assert wt_t_link
    assert len(wt_t_link) == 2
    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [cwt.id, twt_id]
                ),
            )
        )
    ).all()
    assert wt_sc_link
    assert len(wt_sc_link) == 2

    response = await client.delete(
        f"{WORK_TYPE_ROUTE}/{str(cwt.id)}",
    )
    assert response.status_code == 200
    await db_session.refresh(tenant_work_type)
    assert tenant_work_type.core_work_type_ids == []

    # validate the links
    wt_t_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_([cwt.id, twt_id]),
            )
        )
    ).all()
    assert not wt_t_link

    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [cwt.id, twt_id]
                ),
            )
        )
    ).all()
    assert not wt_sc_link

    await TenantFactory.delete_many(db_session, [tenant])
    await WorkTypeFactory.delete_many(db_session, [cwt, tenant_work_type])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_linking_library_site_conditions_with_tenant_work_types(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    # create core work type with 1 task and sc each
    cwt, _, _ = await WorkTypeFactory.core_work_type_with_task_and_sc_link(db_session)
    lsc = await LibrarySiteConditionFactory.persist(session=db_session)

    # create a tenant wt using the cwt, thus linking the cwt's task and sc to this twt.
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(
            name="tenant_test_343", core_work_type_ids=[cwt.id]
        )
    )
    twt_id = uuid.uuid4()
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{twt_id}?tenant_id={tenant.id}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    tenant_work_type = (
        await db_session.execute(select(WorkType).where(WorkType.id == twt_id))
    ).scalar()
    assert tenant_work_type
    assert tenant_work_type.name == "tenant_test_343"
    assert tenant_work_type.core_work_type_ids == [cwt.id]
    assert tenant_work_type.tenant_id == tenant.id

    # validate the links
    wt_t_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_([cwt.id, twt_id]),
            )
        )
    ).all()
    assert wt_t_link
    assert len(wt_t_link) == 2
    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [cwt.id, twt_id]
                ),
            )
        )
    ).all()
    assert wt_sc_link
    assert len(wt_sc_link) == 2

    # now link one more sc to the tenant wt, this should NOT link this sc to the core wt.
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(twt_id)}/relationships/library-site-conditions/{str(lsc.id)}"
    )
    assert response.status_code == 200

    # validate results
    wt_t_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_([cwt.id, twt_id]),
            )
        )
    ).all()
    assert wt_t_link
    assert len(wt_t_link) == 2
    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [cwt.id, twt_id]
                ),
            )
        )
    ).all()
    assert wt_sc_link
    assert len(wt_sc_link) == 3  # success

    await WorkTypeTaskLinkFactory.delete_many(db_session, wt_t_link)
    await WorkTypeLibrarySiteConditionLinkFactory.delete_many(db_session, wt_sc_link)
    await TenantFactory.delete_many(db_session, [tenant])
    await WorkTypeFactory.delete_many(db_session, [cwt, tenant_work_type])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_linking_library_site_conditions_with_core_work_types(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    # create core work type with 1 task and sc each
    cwt, _, _ = await WorkTypeFactory.core_work_type_with_task_and_sc_link(db_session)
    lsc = await LibrarySiteConditionFactory.persist(session=db_session)

    # create a tenant wt using the cwt, thus linking the cwt's task and sc to this twt.
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(
            name="tenant_test_343", core_work_type_ids=[cwt.id]
        )
    )
    twt_id = uuid.uuid4()
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{twt_id}?tenant_id={tenant.id}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    tenant_work_type = (
        await db_session.execute(select(WorkType).where(WorkType.id == twt_id))
    ).scalar()
    assert tenant_work_type
    assert tenant_work_type.name == "tenant_test_343"
    assert tenant_work_type.core_work_type_ids == [cwt.id]
    assert tenant_work_type.tenant_id == tenant.id

    # validate the links
    wt_t_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_([cwt.id, twt_id]),
            )
        )
    ).all()
    assert wt_t_link
    assert len(wt_t_link) == 2
    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [cwt.id, twt_id]
                ),
            )
        )
    ).all()
    assert wt_sc_link
    assert len(wt_sc_link) == 2

    # now link one more sc to the core wt, this should also link this sc to the tenant wt.
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt.id)}/relationships/library-site-conditions/{str(lsc.id)}"
    )
    assert response.status_code == 200

    # validate results
    wt_t_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_([cwt.id, twt_id]),
            )
        )
    ).all()
    assert wt_t_link
    assert len(wt_t_link) == 2
    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [cwt.id, twt_id]
                ),
            )
        )
    ).all()
    assert wt_sc_link
    assert len(wt_sc_link) == 4  # success

    await WorkTypeTaskLinkFactory.delete_many(db_session, wt_t_link)
    await WorkTypeLibrarySiteConditionLinkFactory.delete_many(db_session, wt_sc_link)
    await TenantFactory.delete_many(db_session, [tenant])
    await WorkTypeFactory.delete_many(db_session, [cwt, tenant_work_type])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_unlinking_library_site_conditions_from_tenant_work_type(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    cwt, _, _ = await WorkTypeFactory.core_work_type_with_task_and_sc_link(db_session)

    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(
            name="tenant_test_343", core_work_type_ids=[cwt.id]
        )
    )
    twt_id = uuid.uuid4()
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{twt_id}?tenant_id={tenant.id}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    tenant_work_type = (
        await db_session.execute(select(WorkType).where(WorkType.id == twt_id))
    ).scalar()
    assert tenant_work_type
    assert tenant_work_type.name == "tenant_test_343"
    assert tenant_work_type.core_work_type_ids == [cwt.id]
    assert tenant_work_type.tenant_id == tenant.id

    wt_t_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_([cwt.id, twt_id]),
            )
        )
    ).all()
    assert wt_t_link
    assert len(wt_t_link) == 2
    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [cwt.id, twt_id]
                ),
            )
        )
    ).all()
    assert wt_sc_link
    assert len(wt_sc_link) == 2

    response = await client.delete(
        f"{WORK_TYPE_ROUTE}/{str(tenant_work_type.id)}/relationships/library-site-conditions/{str(wt_sc_link[0].library_site_condition_id)}"
    )
    assert response.status_code == 204

    wt_t_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_([cwt.id, twt_id]),
            )
        )
    ).all()
    assert wt_t_link
    assert len(wt_t_link) == 2
    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [cwt.id, twt_id]
                ),
            )
        )
    ).all()
    assert wt_sc_link
    assert len(wt_sc_link) == 1

    await WorkTypeTaskLinkFactory.delete_many(db_session, wt_t_link)
    await WorkTypeLibrarySiteConditionLinkFactory.delete_many(db_session, wt_sc_link)
    await TenantFactory.delete_many(db_session, [tenant])
    await WorkTypeFactory.delete_many(db_session, [cwt, tenant_work_type])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_unlinking_library_site_conditions_from_core_work_type(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    cwt, _, _ = await WorkTypeFactory.core_work_type_with_task_and_sc_link(db_session)

    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(
            name="tenant_test_343", core_work_type_ids=[cwt.id]
        )
    )
    twt_id = uuid.uuid4()
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{twt_id}?tenant_id={tenant.id}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    tenant_work_type = (
        await db_session.execute(select(WorkType).where(WorkType.id == twt_id))
    ).scalar()
    assert tenant_work_type
    assert tenant_work_type.name == "tenant_test_343"
    assert tenant_work_type.core_work_type_ids == [cwt.id]
    assert tenant_work_type.tenant_id == tenant.id

    wt_t_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_([cwt.id, twt_id]),
            )
        )
    ).all()
    assert wt_t_link
    assert len(wt_t_link) == 2
    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [cwt.id, twt_id]
                ),
            )
        )
    ).all()
    assert wt_sc_link
    assert len(wt_sc_link) == 2

    response = await client.delete(
        f"{WORK_TYPE_ROUTE}/{str(cwt.id)}/relationships/library-site-conditions/{str(wt_sc_link[0].library_site_condition_id)}"
    )
    assert response.status_code == 204

    wt_t_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_([cwt.id, twt_id]),
            )
        )
    ).all()
    assert wt_t_link
    assert len(wt_t_link) == 2
    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [cwt.id, twt_id]
                ),
            )
        )
    ).all()
    assert not wt_sc_link

    await WorkTypeTaskLinkFactory.delete_many(db_session, wt_t_link)
    await TenantFactory.delete_many(db_session, [tenant])
    await WorkTypeFactory.delete_many(db_session, [cwt, tenant_work_type])


# test scenario where the core_work_type_ids does not exists in the DB.
@pytest.mark.asyncio
@pytest.mark.integration
async def test_core_work_type_id_does_not_exists(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(
            name="tenant_test_343", core_work_type_ids=[uuid.uuid4()]
        )
    )
    twt_id = uuid.uuid4()
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{twt_id}?tenant_id={tenant.id}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 400

    tenant_work_type = (
        await db_session.execute(select(WorkType).where(WorkType.id == twt_id))
    ).scalar()
    assert not tenant_work_type

    await TenantFactory.delete_many(db_session, [tenant])


# test scenario where the id value provided as core_work_type_ids belongs to a tenant_work_type
async def test_core_work_type_id_is_a_tenant_work_type_id(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    wt = await WorkTypeFactory.persist(session=db_session)
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(
            name="tenant_test_343", core_work_type_ids=[wt.id]
        )
    )
    twt_id = uuid.uuid4()
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{twt_id}?tenant_id={tenant.id}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    tenant_work_type = (
        await db_session.execute(select(WorkType).where(WorkType.id == twt_id))
    ).scalar()
    assert tenant_work_type
    assert tenant_work_type.name == "tenant_test_343"
    assert tenant_work_type.core_work_type_ids == [wt.id]
    assert tenant_work_type.tenant_id == tenant.id

    twt_id = uuid.uuid4()
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(
            name="tenant_test_343", core_work_type_ids=[tenant_work_type.id]
        )
    )
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{twt_id}?tenant_id={tenant.id}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 400

    await TenantFactory.delete_many(db_session, [tenant])
    await WorkTypeFactory.delete_many(db_session, [wt, tenant_work_type])
