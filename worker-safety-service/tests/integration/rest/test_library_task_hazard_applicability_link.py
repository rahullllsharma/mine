import uuid
from typing import Callable

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient

from tests.factories import (
    LibraryHazardFactory,
    LibraryTaskFactory,
    LibraryTaskHazardApplicabilityFactory,
    TenantFactory,
)
from worker_safety_service.models import AsyncSession
from worker_safety_service.models.base import ApplicabilityLevel
from worker_safety_service.rest.routers.library_task_hazard_applicability_link import (
    TaskAndHazardApplicabilityRequest,
    TaskHazardApplicabilityLink,
)

LIBRARY_TASK_HAZARD_APPLICABILITY_LINKS_ROUTE = (
    "http://127.0.0.1:8000/rest/library-task-hazard-applicability"
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_library_task_hazard_applicability_link(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    await LibraryTaskHazardApplicabilityFactory.persist_many(db_session, size=20)
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    response = await client.get(LIBRARY_TASK_HAZARD_APPLICABILITY_LINKS_ROUTE)

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 20


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_task_hazard_applicability_link_create(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    lt = await LibraryTaskFactory.persist(db_session)
    lh = await LibraryHazardFactory.persist(db_session)
    applicability_level: ApplicabilityLevel = ApplicabilityLevel("rarely")

    task_hazard_applicability_req_body = TaskAndHazardApplicabilityRequest.pack(
        attributes=TaskHazardApplicabilityLink(
            applicability_level=applicability_level,
            library_task_id=lt.id,
            library_hazard_id=lh.id,
        )
    )

    response = await client.post(
        url=f"{LIBRARY_TASK_HAZARD_APPLICABILITY_LINKS_ROUTE}",
        json=jsonable_encoder(task_hazard_applicability_req_body.dict()),
    )

    assert response.status_code == 201
    data = response.json()["data"]

    assert data["relationships"]["library-task"]["data"]["id"] == str(lt.id)
    assert data["relationships"]["library-hazard"]["data"]["id"] == str(lh.id)
    assert data["attributes"]["applicability_level"] == applicability_level


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_task_hazard_applicability_link_create_duplicate(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    lt = await LibraryTaskFactory.persist(db_session)
    lh = await LibraryHazardFactory.persist(db_session)
    applicability_level = ApplicabilityLevel("always")

    await LibraryTaskHazardApplicabilityFactory.persist(
        db_session,
        library_task_id=lt.id,
        library_hazard_id=lh.id,
        applicability=applicability_level,
    )

    task_hazard_applicability_req_body = TaskAndHazardApplicabilityRequest.pack(
        attributes=TaskHazardApplicabilityLink(
            applicability_level=applicability_level,
            library_task_id=lt.id,
            library_hazard_id=lh.id,
        )
    )

    response = await client.post(
        url=f"{LIBRARY_TASK_HAZARD_APPLICABILITY_LINKS_ROUTE}",
        json=jsonable_encoder(task_hazard_applicability_req_body.dict()),
    )

    assert response.status_code == 400
    title = response.json()["title"]
    assert title == "EntityAlreadyExists"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_task_hazard_applicability_update(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    lt = await LibraryTaskFactory.persist(db_session)
    lh = await LibraryHazardFactory.persist(db_session)
    applicability_level = ApplicabilityLevel("always")

    await LibraryTaskHazardApplicabilityFactory.persist(
        db_session,
        library_task_id=lt.id,
        library_hazard_id=lh.id,
        applicability=applicability_level,
    )

    response = await client.put(
        url=f"{LIBRARY_TASK_HAZARD_APPLICABILITY_LINKS_ROUTE}?filter[library_task_id]={lt.id}&filter[library_hazard_id]={lh.id}&filter[applicability_leve]=never"
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["relationships"]["library-task"]["data"]["id"] == str(lt.id)
    assert data["relationships"]["library-hazard"]["data"]["id"] == str(lh.id)
    assert data["attributes"]["applicability_level"] == "never"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_task_hazard_update_data_not_found(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    response = await client.put(
        url=f"{LIBRARY_TASK_HAZARD_APPLICABILITY_LINKS_ROUTE}?filter[library_task_id]={uuid.uuid4()}&filter[library_hazard_id]={uuid.uuid4()}&filter[applicability_leve]=never"
    )

    assert response.status_code == 400
    title = response.json()["title"]
    assert title == "DataNotFound"
