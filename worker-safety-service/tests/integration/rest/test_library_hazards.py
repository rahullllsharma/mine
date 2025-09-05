import uuid
from typing import Callable

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlmodel import col, select

from tests.factories import (
    LibraryHazardFactory,
    LibrarySiteConditionFactory,
    LibrarySiteConditionRecommendationsFactory,
    LibraryTaskFactory,
    LibraryTaskRecommendationsFactory,
    TenantFactory,
)
from worker_safety_service.models import AsyncSession, TenantLibraryHazardSettings
from worker_safety_service.rest.routers.library_hazards import (
    EnergyLevel,
    EnergyType,
    LibraryHazard,
    LibraryHazardRequest,
)

LIBRARY_HAZARDS_ROUTE = "http://127.0.0.1:8000/rest/library-hazards"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_library_hazards(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    response = await client.get(f"{LIBRARY_HAZARDS_ROUTE}?page[limit]=10")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 10


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_hazard_get(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_hazard = await LibraryHazardFactory.persist(
        db_session, name="test_hazard", archived_at=None
    )
    client = rest_client(custom_tenant=tenant)

    response = await client.get(f"{LIBRARY_HAZARDS_ROUTE}/{library_hazard.id}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["attributes"]["id"] == str(library_hazard.id)
    assert data["attributes"]["name"] == "test_hazard"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_hazard_get_filtered(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)

    library_hazard = await LibraryHazardFactory.persist(
        db_session, name="test_hazard", archived_at=None
    )

    site_condition = await LibrarySiteConditionFactory.persist(
        db_session, name="test_site_condition", archived_at=None
    )

    task = await LibraryTaskFactory.persist(
        db_session, name="test_task", archived_at=None
    )

    await LibrarySiteConditionRecommendationsFactory.persist(
        db_session,
        library_hazard_id=library_hazard.id,
        library_site_condition_id=site_condition.id,
    )

    await LibraryTaskRecommendationsFactory.persist(
        db_session, library_hazard_id=library_hazard.id, library_task_id=task.id
    )

    client = rest_client(custom_tenant=tenant)

    response = await client.get(
        f"{LIBRARY_HAZARDS_ROUTE}?filter[library-site-condition]={site_condition.id}&filter[library-task]={task.id}"
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["attributes"]["id"] == str(library_hazard.id)
    assert data[0]["attributes"]["name"] == "test_hazard"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_hazard_get_not_found(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    response = await client.get(f"{LIBRARY_HAZARDS_ROUTE}/{uuid.uuid4()}")
    assert response.status_code == 404
    title = response.json()["title"]
    assert title == "Not Found"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_hazard_create(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    links = (
        (
            await db_session.execute(
                select(TenantLibraryHazardSettings).where(
                    col(TenantLibraryHazardSettings.tenant_id) == tenant.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert not links

    test_library_hazard_id = uuid.UUID("3ea2a9a1-92aa-48b6-8f25-867e5206aed4")
    library_hazard_body = LibraryHazardRequest.pack(
        attributes=LibraryHazard(
            id=test_library_hazard_id,
            name="New Hazard",
            for_tasks=True,
            for_site_conditions=False,
            energy_type=EnergyType.BIOLOGICAL,
            energy_level=EnergyLevel.HIGH_ENERGY,
        )
    )

    response = await client.post(
        url=f"{LIBRARY_HAZARDS_ROUTE}/{str(test_library_hazard_id)}",
        json=jsonable_encoder(library_hazard_body.dict()),
    )
    assert response.status_code == 201
    data = response.json()["data"]

    assert data["attributes"]["id"] == str(test_library_hazard_id)
    assert data["attributes"]["name"] == "New Hazard"
    assert data["attributes"]["for_tasks"] is True
    assert data["attributes"]["for_site_conditions"] is False
    assert data["attributes"]["energy_type"] == EnergyType.BIOLOGICAL
    assert data["attributes"]["energy_level"] == EnergyLevel.HIGH_ENERGY

    new_links = (
        (
            await db_session.execute(
                select(TenantLibraryHazardSettings).where(
                    col(TenantLibraryHazardSettings.tenant_id) == tenant.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert new_links
    assert len(new_links) == len(links) + 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_hazard_put(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_hazard = await LibraryHazardFactory.persist(
        db_session, name="Hazard", for_tasks=True, archived_at=None
    )
    client = rest_client(custom_tenant=tenant)

    library_hazard_body = LibraryHazardRequest.pack(
        attributes=LibraryHazard(
            id=library_hazard.id,
            name="Another Hazard",
            for_tasks=False,
            for_site_conditions=False,
            energy_type=EnergyType.ELECTRICAL,
            energy_level=EnergyLevel.LOW_ENERGY,
        )
    )

    response = await client.put(
        url=f"{LIBRARY_HAZARDS_ROUTE}/{library_hazard.id}",
        json=jsonable_encoder(library_hazard_body.dict()),
    )
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["attributes"]["id"] == str(library_hazard.id)
    assert data["attributes"]["name"] == "Another Hazard"
    assert data["attributes"]["for_tasks"] is False
    assert data["attributes"]["for_site_conditions"] is False
    assert data["attributes"]["energy_type"] == EnergyType.ELECTRICAL
    assert data["attributes"]["energy_level"] == EnergyLevel.LOW_ENERGY


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_hazard_delete(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_hazard = await LibraryHazardFactory.persist(
        db_session, name="Test", archived_at=None
    )
    client = rest_client(custom_tenant=tenant)

    response = await client.delete(url=f"{LIBRARY_HAZARDS_ROUTE}/{library_hazard.id}")
    assert response.status_code == 204

    response = await client.get(f"{LIBRARY_HAZARDS_ROUTE}/{library_hazard.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_hazard_delete_not_found(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    response = await client.delete(url=f"{LIBRARY_HAZARDS_ROUTE}/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_hazard_create_without_image_url(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    test_library_hazard_id = uuid.uuid4()
    library_hazard_body = LibraryHazardRequest.pack(
        attributes=LibraryHazard(
            id=test_library_hazard_id,
            name="New Hazard",
            for_tasks=True,
            for_site_conditions=False,
            energy_type=EnergyType.BIOLOGICAL,
            energy_level=EnergyLevel.HIGH_ENERGY,
            # No image_url provided
        )
    )

    response = await client.post(
        url=f"{LIBRARY_HAZARDS_ROUTE}/{str(test_library_hazard_id)}",
        json=jsonable_encoder(library_hazard_body.dict()),
    )
    assert response.status_code == 201
    data = response.json()["data"]

    assert data["attributes"]["id"] == str(test_library_hazard_id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_hazard_update_without_image_url(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_hazard = await LibraryHazardFactory.persist(
        db_session,
        name="Hazard",
        for_tasks=True,
        archived_at=None,
        image_url="some_image_url",
    )
    client = rest_client(custom_tenant=tenant)

    library_hazard_body = LibraryHazardRequest.pack(
        attributes=LibraryHazard(
            id=library_hazard.id,
            name="Updated Hazard",
            for_tasks=False,
            for_site_conditions=False,
            energy_type=EnergyType.ELECTRICAL,
            energy_level=EnergyLevel.LOW_ENERGY,
            # No image_url provided
        )
    )

    response = await client.put(
        url=f"{LIBRARY_HAZARDS_ROUTE}/{library_hazard.id}",
        json=jsonable_encoder(library_hazard_body.dict()),
    )
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["attributes"]["id"] == str(library_hazard.id)
    assert data["attributes"]["name"] == "Updated Hazard"
    assert (
        data["attributes"]["image_url"] == "some_image_url"
    )  # image_url is not changed


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_hazard_create_with_image_url(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    test_library_hazard_id = uuid.uuid4()
    library_hazard_body = LibraryHazardRequest.pack(
        attributes=LibraryHazard(
            id=test_library_hazard_id,
            name="New Hazard",
            for_tasks=True,
            for_site_conditions=False,
            energy_type=EnergyType.BIOLOGICAL,
            energy_level=EnergyLevel.HIGH_ENERGY,
            image_url="http://example.com/image.jpg",
        )
    )

    response = await client.post(
        url=f"{LIBRARY_HAZARDS_ROUTE}/{str(test_library_hazard_id)}",
        json=jsonable_encoder(library_hazard_body.dict()),
    )
    assert response.status_code == 201
    data = response.json()["data"]

    assert data["attributes"]["id"] == str(test_library_hazard_id)
    assert data["attributes"]["image_url"] == "http://example.com/image.jpg"
