from logging import getLogger
from typing import Callable

import pytest
from httpx import AsyncClient
from sqlmodel import select

from tests.factories import LibraryTaskFactory, TenantFactory, unique_id_factory
from worker_safety_service.models import AsyncSession
from worker_safety_service.models.standard_operating_procedures import (
    LibraryTaskStandardOperatingProcedure,
    StandardOperatingProcedure,
)
from worker_safety_service.rest.routers.standard_operating_procedures import (
    StandardOperatingProcedureAttributes,
    StandardOperatingProcedureRequest,
)

logger = getLogger(__name__)
ROUTE = "http://127.0.0.1:8000/rest/standard-operating-procedures"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_create_201_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    request = StandardOperatingProcedureRequest.pack(
        attributes=StandardOperatingProcedureAttributes(
            name="sop name", link="https://..."
        )
    )

    # Act
    response = await client.post(
        f"{ROUTE}",
        json=request.dict(),
    )

    # Assert
    assert response.status_code == 201
    response_data = response.json()["data"]
    id = response.json()["data"]["id"]

    assert response_data["attributes"] == {"name": "sop name", "link": "https://..."}

    standard_operating_procedure = (
        await db_session.execute(
            select(StandardOperatingProcedure).where(
                StandardOperatingProcedure.id == id
            )
        )
    ).scalar()
    assert standard_operating_procedure
    assert standard_operating_procedure.name == "sop name"
    assert standard_operating_procedure.link == "https://..."
    assert standard_operating_procedure.tenant_id == tenant.id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_get_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    attributes = StandardOperatingProcedureAttributes(
        name="sop name", link="https://..."
    )
    request = StandardOperatingProcedureRequest.pack(attributes=attributes)
    response1 = await client.post(
        f"{ROUTE}",
        json=request.dict(),
    )
    response2 = await client.post(
        f"{ROUTE}",
        json=request.dict(),
    )
    ids = [response1.json()["data"]["id"], response2.json()["data"]["id"]]
    ids.sort()

    # Act
    response = await client.get(
        f"{ROUTE}",
    )

    # Assert
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2
    assert response.json()["data"][0]["id"] == ids[0]
    assert response.json()["data"][1]["id"] == ids[1]
    assert response.json()["data"][0]["attributes"]["name"] == attributes.name
    assert response.json()["data"][0]["attributes"]["link"] == attributes.link
    assert response.json()["data"][1]["attributes"]["name"] == attributes.name
    assert response.json()["data"][1]["attributes"]["link"] == attributes.link


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_get_after_limit_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    attributes = StandardOperatingProcedureAttributes(
        name="sop name", link="https://..."
    )
    request = StandardOperatingProcedureRequest.pack(attributes=attributes)
    response1 = await client.post(
        f"{ROUTE}",
        json=request.dict(),
    )
    response2 = await client.post(
        f"{ROUTE}",
        json=request.dict(),
    )
    response3 = await client.post(
        f"{ROUTE}",
        json=request.dict(),
    )
    ids = [
        response1.json()["data"]["id"],
        response2.json()["data"]["id"],
        response3.json()["data"]["id"],
    ]
    ids.sort()

    # Act
    response = await client.get(
        f"{ROUTE}", params={"page[limit]": 1, "page[after]": ids[1]}
    )

    # Assert
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["id"] == ids[2]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_get_by_id_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    attributes = StandardOperatingProcedureAttributes(
        name="sop name", link="https://..."
    )
    request = StandardOperatingProcedureRequest.pack(attributes=attributes)
    post_response = await client.post(
        f"{ROUTE}",
        json=request.dict(),
    )
    id = post_response.json()["data"]["id"]

    # Act
    get_response = await client.get(
        f"{ROUTE}/{id}",
    )

    # Assert
    assert get_response.status_code == 200
    assert post_response.json() == get_response.json()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_get_by_id_404_not_found(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    id = unique_id_factory()

    # Act
    get_response = await client.get(
        f"{ROUTE}/{id}",
    )

    # Assert
    assert get_response.status_code == 404, get_response.json()
    assert get_response.json() == {
        "title": "Not Found",
        "detail": f"The StandardOperatingProcedure with {id} could not be found.",
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_put_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    attributes = StandardOperatingProcedureAttributes(
        name="sop name", link="https://..."
    )
    request = StandardOperatingProcedureRequest.pack(attributes=attributes)
    post_response = await client.post(
        f"{ROUTE}",
        json=request.dict(),
    )
    id = post_response.json()["data"]["id"]
    attributes = StandardOperatingProcedureAttributes(
        name="sop updated name", link="dummy link"
    )
    request = StandardOperatingProcedureRequest.pack(attributes=attributes)

    # Act
    put_response = await client.put(
        f"{ROUTE}/{id}",
        json=request.dict(),
    )

    # Assert
    assert put_response.status_code == 200
    assert put_response.json()["data"]["attributes"]["name"] == "sop updated name"
    assert put_response.json()["data"]["attributes"]["link"] == "dummy link"
    standard_operating_procedure = (
        await db_session.execute(
            select(StandardOperatingProcedure).where(
                StandardOperatingProcedure.id == id
            )
        )
    ).scalar()
    assert standard_operating_procedure
    assert standard_operating_procedure.name == "sop updated name"
    assert standard_operating_procedure.link == "dummy link"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_put_404_not_found(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    id = unique_id_factory()
    attributes = StandardOperatingProcedureAttributes(
        name="sop updated name", link="dummy link"
    )
    request = StandardOperatingProcedureRequest.pack(attributes=attributes)

    # Act
    put_response = await client.put(
        f"{ROUTE}/{id}",
        json=request.dict(),
    )

    # Assert
    assert put_response.status_code == 404
    assert put_response.json() == {
        "title": "Not Found",
        "detail": f"The StandardOperatingProcedure with {id} could not be found.",
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_delete_204_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    attributes = StandardOperatingProcedureAttributes(
        name="sop name", link="https://..."
    )
    request = StandardOperatingProcedureRequest.pack(attributes=attributes)
    post_response = await client.post(
        f"{ROUTE}",
        json=request.dict(),
    )
    id = post_response.json()["data"]["id"]

    # Act
    delete_response = await client.delete(
        f"{ROUTE}/{id}",
    )

    # Assert
    assert delete_response.status_code == 204
    assert delete_response.text == ""
    standard_operating_procedure = (
        await db_session.execute(
            select(StandardOperatingProcedure).where(
                StandardOperatingProcedure.id == id
            )
        )
    ).scalar()
    assert standard_operating_procedure is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_delete_404_not_found(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    id = unique_id_factory()

    # Act
    delete_response = await client.delete(f"{ROUTE}/{id}")

    # Assert
    assert delete_response.status_code == 404
    assert delete_response.json() == {
        "title": "Not Found",
        "detail": f"The StandardOperatingProcedure with {id} could not be found.",
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_link_put_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    tenant = await TenantFactory.persist(db_session)
    library_task = await LibraryTaskFactory.persist(
        db_session, name="test_task", archived_at=None
    )
    client = rest_client(custom_tenant=tenant)
    attributes = StandardOperatingProcedureAttributes(
        name="sop name", link="https://..."
    )
    request = StandardOperatingProcedureRequest.pack(attributes=attributes)
    post_response = await client.post(
        f"{ROUTE}",
        json=request.dict(),
    )
    standard_operating_procedure_id = post_response.json()["data"]["id"]

    # Act
    put_response = await client.put(
        f"{ROUTE}/{standard_operating_procedure_id}/relationships/library-tasks/{library_task.id}"
    )

    # Assert
    assert put_response.status_code == 204
    assert put_response.text == ""
    link = (
        await db_session.execute(
            select(LibraryTaskStandardOperatingProcedure)
            .where(
                LibraryTaskStandardOperatingProcedure.library_task_id == library_task.id
            )
            .where(
                LibraryTaskStandardOperatingProcedure.standard_operating_procedure_id
                == standard_operating_procedure_id
            )
        )
    ).scalar()
    assert link

    # Act
    put_response = await client.put(
        f"{ROUTE}/{standard_operating_procedure_id}/relationships/library-tasks/{library_task.id}"
    )
    assert put_response.status_code == 204


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_link_put_404_task_not_found(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    tenant = await TenantFactory.persist(db_session)
    library_task_id = unique_id_factory()
    client = rest_client(custom_tenant=tenant)
    attributes = StandardOperatingProcedureAttributes(
        name="sop name", link="https://..."
    )
    request = StandardOperatingProcedureRequest.pack(attributes=attributes)
    post_response = await client.post(
        f"{ROUTE}",
        json=request.dict(),
    )
    standard_operating_procedure_id = post_response.json()["data"]["id"]

    # Act
    put_response = await client.put(
        f"{ROUTE}/{standard_operating_procedure_id}/relationships/library-tasks/{library_task_id}"
    )

    # Assert
    assert put_response.status_code == 404
    assert put_response.json() == {
        "title": "Not Found",
        "detail": f"The LibraryTask with {library_task_id} could not be found.",
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_link_put_404_not_found(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    tenant = await TenantFactory.persist(db_session)
    library_task = await LibraryTaskFactory.persist(
        db_session, name="test_task", archived_at=None
    )
    client = rest_client(custom_tenant=tenant)
    standard_operating_procedure_id = unique_id_factory()

    # Act
    put_response = await client.put(
        f"{ROUTE}/{standard_operating_procedure_id}/relationships/library-tasks/{library_task.id}"
    )

    # Assert
    assert put_response.status_code == 404
    assert put_response.json() == {
        "title": "Not Found",
        "detail": f"The StandardOperatingProcedure with {standard_operating_procedure_id} could not be found.",
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_link_delete_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    tenant = await TenantFactory.persist(db_session)
    library_task = await LibraryTaskFactory.persist(
        db_session, name="test_task", archived_at=None
    )
    client = rest_client(custom_tenant=tenant)
    attributes = StandardOperatingProcedureAttributes(
        name="sop name", link="https://..."
    )
    request = StandardOperatingProcedureRequest.pack(attributes=attributes)
    post_response = await client.post(
        f"{ROUTE}",
        json=request.dict(),
    )
    standard_operating_procedure_id = post_response.json()["data"]["id"]
    await client.put(
        f"{ROUTE}/{standard_operating_procedure_id}/relationships/library-tasks/{library_task.id}"
    )

    # Act
    delete_response = await client.delete(
        f"{ROUTE}/{standard_operating_procedure_id}/relationships/library-tasks/{library_task.id}"
    )

    # Assert
    assert delete_response.status_code == 204
    assert delete_response.text == ""
    link = (
        await db_session.execute(
            select(LibraryTaskStandardOperatingProcedure)
            .where(
                LibraryTaskStandardOperatingProcedure.library_task_id == library_task.id
            )
            .where(
                LibraryTaskStandardOperatingProcedure.standard_operating_procedure_id
                == standard_operating_procedure_id
            )
        )
    ).scalar()
    assert link is None

    # Act
    delete_response = await client.delete(
        f"{ROUTE}/{standard_operating_procedure_id}/relationships/library-tasks/{library_task.id}"
    )
    assert delete_response.status_code == 204


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_link_delete_404_task_not_found(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    tenant = await TenantFactory.persist(db_session)
    library_task_id = unique_id_factory()
    client = rest_client(custom_tenant=tenant)
    attributes = StandardOperatingProcedureAttributes(
        name="sop name", link="https://..."
    )
    request = StandardOperatingProcedureRequest.pack(attributes=attributes)
    post_response = await client.post(
        f"{ROUTE}",
        json=request.dict(),
    )
    standard_operating_procedure_id = post_response.json()["data"]["id"]

    # Act
    delete_response = await client.delete(
        f"{ROUTE}/{standard_operating_procedure_id}/relationships/library-tasks/{library_task_id}"
    )

    # Assert
    assert delete_response.status_code == 404
    assert delete_response.json() == {
        "title": "Not Found",
        "detail": f"The LibraryTask with {library_task_id} could not be found.",
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_link_delete_404_not_found(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    tenant = await TenantFactory.persist(db_session)
    library_task = await LibraryTaskFactory.persist(
        db_session, name="test_task", archived_at=None
    )
    client = rest_client(custom_tenant=tenant)
    standard_operating_procedure_id = unique_id_factory()

    # Act
    delete_response = await client.delete(
        f"{ROUTE}/{standard_operating_procedure_id}/relationships/library-tasks/{library_task.id}"
    )

    # Assert
    assert delete_response.status_code == 404
    assert delete_response.json() == {
        "title": "Not Found",
        "detail": f"The StandardOperatingProcedure with {standard_operating_procedure_id} could not be found.",
    }
