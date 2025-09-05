import json
from datetime import date
from typing import Callable
from uuid import UUID, uuid4

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlmodel import col, select

from tests.factories import (
    ContractorFactory,
    LibraryDivisionFactory,
    LibraryProjectTypeFactory,
    LibraryRegionFactory,
    LocationFactory,
    ManagerUserFactory,
    SupervisorUserFactory,
    TenantFactory,
    WorkPackageFactory,
    WorkTypeFactory,
)
from tests.integration.rest import verify_pagination
from worker_safety_service.models import AsyncSession, ProjectStatus
from worker_safety_service.models.work_packages import WorkPackage as WP_Model
from worker_safety_service.rest.routers.work_packages import (
    WorkPackage,
    WorkPackageBulkRequest,
    WorkPackageRequest,
)

LOCATIONS_ROUTE = "http://127.0.0.1:8000/rest/locations"
WORK_PACKAGES_ROUTE = "http://127.0.0.1:8000/rest/work-packages"


def make_work_package(
    contractor_id: UUID,
    division_id: UUID,
    region_id: UUID,
    manager_id: UUID,
    primary_assigned_user_id: UUID,
    external_key: UUID,
    work_type_ids: list[UUID],
    work_type_id: UUID,
) -> WorkPackage:
    return WorkPackage(
        name="Digging project",
        status=ProjectStatus.ACTIVE,
        start_date=date.today(),
        end_date=date.today(),
        external_key=str(external_key),
        meta_attributes={"penguins": "four", "geraniums": "two"},
        work_type_id=work_type_id,
        work_type_ids=work_type_ids,
        contractor_id=contractor_id,
        division_id=division_id,
        region_id=region_id,
        manager_id=manager_id,
        primary_assigned_user_id=primary_assigned_user_id,
        description="description",
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_work_package_201_ok_without_work_types(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant, work_type = await TenantFactory.with_work_type_link(db_session)
    client = rest_client(custom_tenant=tenant)
    contractor = await ContractorFactory.persist(
        session=db_session, tenant_id=tenant.id
    )
    library_division = await LibraryDivisionFactory.persist(
        session=db_session, tenant_id=tenant.id
    )
    library_region = await LibraryRegionFactory.persist(
        session=db_session, tenant_id=tenant.id
    )
    manager = await ManagerUserFactory.persist(session=db_session, tenant_id=tenant.id)

    primary_assigned_user = await SupervisorUserFactory.persist(
        session=db_session, tenant_id=tenant.id, external_key="Dr. Hendrickson"
    )
    project_type = await LibraryProjectTypeFactory.persist(session=db_session)

    work_package_request = WorkPackageRequest.pack(
        attributes=make_work_package(
            work_type_id=project_type.id,
            work_type_ids=[],
            contractor_id=contractor.id,
            division_id=library_division.id,
            region_id=library_region.id,
            manager_id=manager.id,
            primary_assigned_user_id=primary_assigned_user.id,
            external_key=uuid4(),
        )
    )

    response = await client.post(
        WORK_PACKAGES_ROUTE, json=json.loads(work_package_request.json())
    )
    assert response.status_code == 201
    work_package_id = response.json()["data"]["id"]
    work_package = await client.get(f"{WORK_PACKAGES_ROUTE}/{work_package_id}")

    data = work_package.json()["data"]
    assert data["id"] == work_package_id
    assert data["type"] == "work-package"

    attributes = data["attributes"]
    wpr_attributes = work_package_request.data.attributes

    assert attributes["name"] == wpr_attributes.name
    assert attributes["status"] == wpr_attributes.status
    assert attributes["start_date"] == str(wpr_attributes.start_date)
    assert attributes["end_date"] == str(wpr_attributes.end_date)
    assert attributes["external_key"] == wpr_attributes.external_key
    assert attributes["meta_attributes"] == wpr_attributes.meta_attributes
    assert attributes["work_type_ids"] == [str(work_type.id)]
    assert attributes["contractor_id"] == str(wpr_attributes.contractor_id)
    assert attributes["division_id"] == str(wpr_attributes.division_id)
    assert attributes["region_id"] == str(wpr_attributes.region_id)
    assert attributes["manager_id"] == str(wpr_attributes.manager_id)
    assert attributes["description"] == "description"
    assert attributes["primary_assigned_user_id"] == str(
        wpr_attributes.primary_assigned_user_id
    )

    relationships = response.json()["data"]["relationships"]
    locations = relationships["locations"]
    assert (
        locations["links"]["related"]
        == f"{LOCATIONS_ROUTE}?filter[work-package]={work_package_id}"
    )

    links = work_package.json()["data"]["links"]
    assert links["self"] == f"{WORK_PACKAGES_ROUTE}/{work_package_id}"
    await WorkTypeFactory.delete_many(db_session, [work_type])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_work_packages_201_without_work_types(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant, work_type = await TenantFactory.with_work_type_link(db_session)
    client = rest_client(custom_tenant=tenant)
    contractor = await ContractorFactory.persist(
        session=db_session, tenant_id=tenant.id
    )
    library_division = await LibraryDivisionFactory.persist(
        session=db_session, tenant_id=tenant.id
    )
    library_region = await LibraryRegionFactory.persist(
        session=db_session, tenant_id=tenant.id
    )
    manager = await ManagerUserFactory.persist(session=db_session, tenant_id=tenant.id)
    primary_assigned_user = await SupervisorUserFactory.persist(
        session=db_session, tenant_id=tenant.id, external_key="Dr. Hendrickson"
    )
    project_type = await LibraryProjectTypeFactory.persist(session=db_session)
    elements = []
    for _ in range(3):
        elements.append(
            make_work_package(
                work_type_id=project_type.id,
                work_type_ids=[],
                contractor_id=contractor.id,
                division_id=library_division.id,
                region_id=library_region.id,
                manager_id=manager.id,
                primary_assigned_user_id=primary_assigned_user.id,
                external_key=uuid4(),
            )
        )
    request = WorkPackageBulkRequest.pack_many(elements=elements)
    response = await client.post(
        f"{WORK_PACKAGES_ROUTE}/bulk", json=jsonable_encoder(request.dict())
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert len(data) == 3
    ids = []
    for attributes in data:
        assert attributes["attributes"]["work_type_ids"] == [str(work_type.id)]
        ids.append(attributes["id"])

    db_work_packages: list[WP_Model] = (
        await db_session.exec(select(WP_Model).where(col(WP_Model.id).in_(ids)))
    ).all()

    assert len(db_work_packages) == 3
    await WorkTypeFactory.delete_many(db_session, [work_type])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_work_package_201_ok_with_work_types(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant, _ = await TenantFactory.with_work_type_link(db_session)
    client = rest_client(custom_tenant=tenant)
    contractor = await ContractorFactory.persist(
        session=db_session, tenant_id=tenant.id
    )
    library_division = await LibraryDivisionFactory.persist(
        session=db_session, tenant_id=tenant.id
    )
    library_region = await LibraryRegionFactory.persist(
        session=db_session, tenant_id=tenant.id
    )
    manager = await ManagerUserFactory.persist(session=db_session, tenant_id=tenant.id)
    work_type = await WorkTypeFactory.tenant_work_type(
        session=db_session, tenant_id=tenant.id
    )
    primary_assigned_user = await SupervisorUserFactory.persist(
        session=db_session, tenant_id=tenant.id, external_key="Dr. Hendrickson"
    )
    project_type = await LibraryProjectTypeFactory.persist(session=db_session)

    work_package_request = WorkPackageRequest.pack(
        attributes=make_work_package(
            work_type_id=project_type.id,
            work_type_ids=[work_type.id],
            contractor_id=contractor.id,
            division_id=library_division.id,
            region_id=library_region.id,
            manager_id=manager.id,
            primary_assigned_user_id=primary_assigned_user.id,
            external_key=uuid4(),
        )
    )

    response = await client.post(
        WORK_PACKAGES_ROUTE, json=json.loads(work_package_request.json())
    )
    assert response.status_code == 201
    work_package_id = response.json()["data"]["id"]
    work_package = await client.get(f"{WORK_PACKAGES_ROUTE}/{work_package_id}")

    data = work_package.json()["data"]
    assert data["id"] == work_package_id
    assert data["type"] == "work-package"

    attributes = data["attributes"]
    wpr_attributes = work_package_request.data.attributes

    assert attributes["name"] == wpr_attributes.name
    assert attributes["status"] == wpr_attributes.status
    assert attributes["start_date"] == str(wpr_attributes.start_date)
    assert attributes["end_date"] == str(wpr_attributes.end_date)
    assert attributes["external_key"] == wpr_attributes.external_key
    assert attributes["meta_attributes"] == wpr_attributes.meta_attributes
    assert attributes["work_type_ids"] == [str(work_type.id)]
    assert attributes["contractor_id"] == str(wpr_attributes.contractor_id)
    assert attributes["division_id"] == str(wpr_attributes.division_id)
    assert attributes["region_id"] == str(wpr_attributes.region_id)
    assert attributes["manager_id"] == str(wpr_attributes.manager_id)
    assert attributes["description"] == "description"
    assert attributes["primary_assigned_user_id"] == str(
        wpr_attributes.primary_assigned_user_id
    )

    relationships = response.json()["data"]["relationships"]
    locations = relationships["locations"]
    assert (
        locations["links"]["related"]
        == f"{LOCATIONS_ROUTE}?filter[work-package]={work_package_id}"
    )

    links = work_package.json()["data"]["links"]
    assert links["self"] == f"{WORK_PACKAGES_ROUTE}/{work_package_id}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_work_packages_201_with_work_types(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant, _ = await TenantFactory.with_work_type_link(db_session)
    client = rest_client(custom_tenant=tenant)
    contractor = await ContractorFactory.persist(
        session=db_session, tenant_id=tenant.id
    )
    library_division = await LibraryDivisionFactory.persist(
        session=db_session, tenant_id=tenant.id
    )
    library_region = await LibraryRegionFactory.persist(
        session=db_session, tenant_id=tenant.id
    )
    manager = await ManagerUserFactory.persist(session=db_session, tenant_id=tenant.id)
    work_type = await WorkTypeFactory.tenant_work_type(
        session=db_session, tenant_id=tenant.id
    )
    primary_assigned_user = await SupervisorUserFactory.persist(
        session=db_session, tenant_id=tenant.id, external_key="Dr. Hendrickson"
    )
    project_type = await LibraryProjectTypeFactory.persist(session=db_session)
    elements = []
    for _ in range(3):
        elements.append(
            make_work_package(
                work_type_id=project_type.id,
                work_type_ids=[work_type.id],
                contractor_id=contractor.id,
                division_id=library_division.id,
                region_id=library_region.id,
                manager_id=manager.id,
                primary_assigned_user_id=primary_assigned_user.id,
                external_key=uuid4(),
            )
        )
    request = WorkPackageBulkRequest.pack_many(elements=elements)
    response = await client.post(
        f"{WORK_PACKAGES_ROUTE}/bulk", json=jsonable_encoder(request.dict())
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert len(data) == 3
    ids = []
    for attributes in data:
        assert attributes["attributes"]["work_type_ids"] == [str(work_type.id)]
        ids.append(attributes["id"])

    db_work_packages: list[WP_Model] = (
        await db_session.exec(select(WP_Model).where(col(WP_Model.id).in_(ids)))
    ).all()

    assert len(db_work_packages) == 3


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_work_package_200_ok(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    work_package = await WorkPackageFactory.persist(
        db_session,
        name="Electric Disco",
        status="pending",
        start_date=date.today(),
        end_date=date.today(),
        external_key="123",
        description="description",
    )
    _ = await LocationFactory.persist(db_session, project_id=work_package.id)
    response = await rest_api_test_client.get(
        f"{WORK_PACKAGES_ROUTE}/{work_package.id}"
    )

    assert response.status_code == 200

    links = response.json()["data"]["links"]
    assert links["self"] == WORK_PACKAGES_ROUTE + "/" + str(work_package.id)

    data = response.json()["data"]
    assert data["id"] == str(work_package.id)
    assert data["type"] == "work-package"

    attributes = data["attributes"]

    assert attributes["name"] == work_package.name
    assert attributes["status"] == work_package.status
    assert attributes["start_date"] == str(work_package.start_date)
    assert attributes["end_date"] == str(work_package.end_date)
    assert attributes["external_key"] == work_package.external_key
    assert attributes["description"] == work_package.description

    relationships = response.json()["data"]["relationships"]
    locations = relationships["locations"]
    assert (
        locations["links"]["related"]
        == f"{LOCATIONS_ROUTE}?filter[work-package]={work_package.id}"
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_work_package_404_not_found(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    response = await rest_api_test_client.get(f"{WORK_PACKAGES_ROUTE}/{str(uuid4())}")

    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_work_packages_200(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    wps = await WorkPackageFactory.persist_many(db_session, tenant_id=tenant.id, size=5)

    client = rest_client(custom_tenant=tenant)

    response = await client.get(WORK_PACKAGES_ROUTE)
    assert response.status_code == 200

    work_packages = response.json()["data"]
    assert len(work_packages) == 5

    assert {str(wp.id) for wp in wps} == {
        work_package["id"] for work_package in work_packages
    }

    wp_ids = sorted(str(wp.id) for wp in wps)
    page2_url = await verify_pagination(
        client.get(f"{WORK_PACKAGES_ROUTE}?page[limit]=2"), wp_ids[:2]
    )
    assert page2_url is not None
    page3_url = await verify_pagination(client.get(page2_url), wp_ids[2:4])
    assert page3_url is not None
    end_page = await verify_pagination(client.get(page3_url), wp_ids[4:])
    assert end_page is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_work_packages_200_empty_set(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    empty = await client.get(WORK_PACKAGES_ROUTE)
    assert empty.status_code == 200
    data = empty.json()["data"]
    assert len(data) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_work_packages_by_external_keys_200(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    external_key1 = str(uuid4())
    external_key2 = str(uuid4())
    wp1 = await WorkPackageFactory.persist(
        db_session, external_key=external_key1, tenant_id=tenant.id
    )
    wp2 = await WorkPackageFactory.persist(
        db_session, external_key=external_key2, tenant_id=tenant.id
    )
    wp3 = await WorkPackageFactory.persist(
        db_session, external_key=str(uuid4()), tenant_id=tenant.id
    )

    wps = [wp1, wp2]
    external_key_qps = "&".join(f"filter[externalKey]={wp.external_key}" for wp in wps)
    results = await client.get(f"{WORK_PACKAGES_ROUTE}?{external_key_qps}")
    assert results.status_code == 200
    work_packages = results.json()["data"]
    assert len(work_packages) == 2

    work_package_ids = {work_package["id"] for work_package in work_packages}
    assert str(wp1.id) in work_package_ids
    assert str(wp2.id) in work_package_ids
    assert str(wp3.id) not in work_package_ids


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_work_package_200(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    external_key = uuid4()
    contractor1 = await ContractorFactory.persist(
        session=db_session, tenant_id=tenant.id
    )
    library_division = await LibraryDivisionFactory.persist(
        session=db_session, tenant_id=tenant.id
    )
    library_region1 = await LibraryRegionFactory.persist(
        session=db_session, tenant_id=tenant.id
    )
    manager1 = await ManagerUserFactory.persist(session=db_session, tenant_id=tenant.id)
    work_type1 = await WorkTypeFactory.persist(session=db_session)
    primary_assigned_user1 = await SupervisorUserFactory.persist(
        session=db_session, tenant_id=tenant.id, external_key="Dr. Hendrickson"
    )

    wp = await WorkPackageFactory.persist(
        db_session,
        name="Digging project",
        start_date=date.today(),
        end_date=date.today(),
        contractor_id=str(contractor1.id),
        division_id=str(library_division.id),
        region_id=str(library_region1.id),
        manage_id=str(manager1.id),
        work_type_ids=[str(work_type1.id)],
        primary_assigned_user_id=str(primary_assigned_user1.id),
        external_key=str(external_key),
        tenant_id=str(tenant.id),
        description="description",
    )

    contractor2 = await ContractorFactory.persist(
        session=db_session, tenant_id=tenant.id
    )
    library_region2 = await LibraryRegionFactory.persist(
        session=db_session, tenant_id=tenant.id
    )
    manager2 = await ManagerUserFactory.persist(session=db_session, tenant_id=tenant.id)
    work_type2 = await WorkTypeFactory.persist(session=db_session)
    primary_assigned_user2 = await SupervisorUserFactory.persist(
        session=db_session, tenant_id=tenant.id, external_key="Dr. Hendrickson"
    )
    project_type = await LibraryProjectTypeFactory.persist(session=db_session)

    wp_edit = WorkPackageRequest.pack(
        attributes=make_work_package(
            work_type_id=project_type.id,
            work_type_ids=[work_type2.id],
            contractor_id=contractor2.id,
            division_id=library_division.id,
            region_id=library_region2.id,
            manager_id=manager2.id,
            primary_assigned_user_id=primary_assigned_user2.id,
            external_key=external_key,
        )
    )

    results = await client.put(
        f"{WORK_PACKAGES_ROUTE}/{str(wp.id)}", json=jsonable_encoder(wp_edit.dict())
    )
    assert results.status_code == 200

    links = results.json()["data"]["links"]
    assert links["self"] == WORK_PACKAGES_ROUTE + "/" + str(wp.id)

    data = results.json()["data"]
    assert data["id"] == str(wp.id)
    assert data["type"] == "work-package"

    updated_attributes = data["attributes"]
    edited_attributes = wp_edit.data.attributes

    assert wp.name == edited_attributes.name
    assert wp.division_id == edited_attributes.division_id
    assert str(wp.start_date) == str(edited_attributes.start_date)
    assert str(wp.end_date) == str(edited_attributes.end_date)
    assert wp.external_key == edited_attributes.external_key
    assert wp.description == edited_attributes.description

    assert updated_attributes["work_type_ids"] == [
        str(edited_attributes.work_type_ids[0])
    ]
    assert updated_attributes["contractor_id"] == str(edited_attributes.contractor_id)
    assert updated_attributes["division_id"] == str(edited_attributes.division_id)
    assert updated_attributes["region_id"] == str(edited_attributes.region_id)
    assert updated_attributes["manager_id"] == str(edited_attributes.manager_id)
    assert updated_attributes["primary_assigned_user_id"] == str(
        edited_attributes.primary_assigned_user_id
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_work_packages_204(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    work_package = await WorkPackageFactory.persist(
        db_session,
        tenant_id=tenant.id,
    )
    assert work_package.archived_at is None
    response = await client.delete(f"{WORK_PACKAGES_ROUTE}/{work_package.id}")

    assert response.status_code == 204

    empty = await client.get(f"{WORK_PACKAGES_ROUTE}/{work_package.id}")
    assert empty.status_code == 404
