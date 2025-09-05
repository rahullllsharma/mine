import uuid
from typing import Callable

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlmodel import select

from tests.factories import (
    LibraryControlFactory,
    LibraryHazardFactory,
    LibrarySiteConditionFactory,
    LibrarySiteConditionRecommendationsFactory,
    TenantFactory,
)
from worker_safety_service.models import AsyncSession, TenantLibraryHazardSettings
from worker_safety_service.rest.routers.library_site_conditions_recommendations import (
    SiteConditionHazardAndControlRecommendation,
    SiteConditionHazardAndControlRecommendationRequest,
)

LIBRARY_SITE_CONDITION_RECOMMENDATIONS_ROUTE = (
    "http://127.0.0.1:8000/rest/library-site-condition-hazards-recommendations"
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_library_site_conditions(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    response = await client.get(LIBRARY_SITE_CONDITION_RECOMMENDATIONS_ROUTE)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 20


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_site_condition_recommendation_create(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    links = (
        (
            await db_session.execute(
                select(TenantLibraryHazardSettings).where(
                    TenantLibraryHazardSettings.tenant_id == tenant.id
                )
            )
        )
        .scalars()
        .all()
    )
    assert not links

    lsc = await LibrarySiteConditionFactory.persist(db_session)
    lc = await LibraryControlFactory.persist(db_session)
    lh = await LibraryHazardFactory.persist(db_session)

    library_site_condition_body = (
        SiteConditionHazardAndControlRecommendationRequest.pack(
            attributes=SiteConditionHazardAndControlRecommendation(
                library_site_condition_id=lsc.id,
                library_control_id=lc.id,
                library_hazard_id=lh.id,
            )
        )
    )

    response = await client.post(
        url=f"{LIBRARY_SITE_CONDITION_RECOMMENDATIONS_ROUTE}",
        json=jsonable_encoder(library_site_condition_body.dict()),
    )
    assert response.status_code == 201
    data = response.json()["data"]

    assert data["relationships"]["library-site-condition"]["data"]["id"] == str(lsc.id)
    assert data["relationships"]["library-control"]["data"]["id"] == str(lc.id)
    assert data["relationships"]["library-hazard"]["data"]["id"] == str(lh.id)

    links = (
        (
            await db_session.execute(
                select(TenantLibraryHazardSettings).where(
                    TenantLibraryHazardSettings.tenant_id == tenant.id,
                    TenantLibraryHazardSettings.library_hazard_id == lh.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_site_condition_recommendation_delete(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    lsc = await LibrarySiteConditionFactory.persist(db_session)
    lc = await LibraryControlFactory.persist(db_session)
    lh = await LibraryHazardFactory.persist(db_session)

    await LibrarySiteConditionRecommendationsFactory.persist(
        db_session,
        library_site_condition_id=lsc.id,
        library_control_id=lc.id,
        library_hazard_id=lh.id,
    )

    response = await client.delete(
        url=f"{LIBRARY_SITE_CONDITION_RECOMMENDATIONS_ROUTE}?filter[library_site_condition_id]={lsc.id}&filter[library_control_id]={lc.id}&filter[library_hazard_id]={lh.id}"
    )

    assert response.status_code == 204


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_site_condition_recommendation_delete_not_found(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    response = await client.delete(
        url=f"{LIBRARY_SITE_CONDITION_RECOMMENDATIONS_ROUTE}?filter[library_site_condition_id]={uuid.uuid4()}&filter[library_control_id]={uuid.uuid4()}&filter[library_hazard_id]={uuid.uuid4()}"
    )

    assert response.status_code == 404
    title = response.json()["title"]
    assert title == "Not Found"
