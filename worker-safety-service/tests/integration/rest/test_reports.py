import datetime
from logging import getLogger
from typing import Callable
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient

from tests.factories import (
    DailyReportFactory,
    EnergyBasedObservationFactory,
    JobSafetyBriefingFactory,
    LocationFactory,
    TenantFactory,
    UserFactory,
    WorkPackageFactory,
)
from worker_safety_service.models import AsyncSession

logger = getLogger(__name__)
REPORTS_ROUTE = "http://127.0.0.1:8000/rest/reports"
REPORTS_TOKEN_ROUTE = "http://127.0.0.1:8000/rest/reports_token"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_get_daily_reports(
    db_session: AsyncSession,
    rest_client: Callable[..., AsyncClient],
) -> None:
    tenant = await TenantFactory.persist(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    locations = await LocationFactory.persist_many(
        db_session, size=2, project_id=work_package.id
    )
    _ = await DailyReportFactory.persist_many(
        db_session,
        size=5,
        per_item_kwargs=[
            {
                "updated_at": "2024-01-01T00:00:00",
                "project_location_id": locations[0].id,
                "sections": {},
            },
            {
                "updated_at": "2024-01-02T00:00:00",
                "project_location_id": locations[1].id,
                "sections": {},
            },
            {
                "updated_at": "2024-01-03T00:00:00",
                "project_location_id": locations[0].id,
                "sections": {},
            },
            {
                "updated_at": "2023-05-13T00:00:00",
                "project_location_id": locations[1].id,
                "sections": {},
            },
            {
                "updated_at": "2023-10-23T00:00:00",
                "project_location_id": locations[0].id,
                "sections": {},
            },
            {"updated_at": "2023-05-13T00:00:00", "sections": {}},
            {"updated_at": "2023-10-23T00:00:00", "sections": {}},
        ],
    )
    client = rest_client(custom_tenant=tenant)

    response = await client.get(
        f"{REPORTS_ROUTE}/dir?filter[start-date]=2023-01-02T00:00:00&filter[end-date]=2025-01-03T00:00:00"
    )

    # check for tenant based results

    assert len(response.json()) == 5

    # test filters for start date and end date

    response = await client.get(
        f"{REPORTS_ROUTE}/dir?filter[start-date]=2024-01-02T00:00:00&filter[end-date]=2024-01-03T00:00:00"
    )

    reports = response.json()
    assert len(reports) == 2
    for report in reports:
        assert report["created_by"] is not None
        assert (
            report["created_by"]["first_name"] is not None
            or report["created_by"]["last_name"] is not None
        )
        assert report["date_for"] is not None
        assert report["sections"] is not None


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_get_ebos(
    db_session: AsyncSession,
    rest_client: Callable[..., AsyncClient],
) -> None:
    tenant = await TenantFactory.persist(db_session)
    _ = await EnergyBasedObservationFactory.persist_many(
        db_session,
        size=7,
        per_item_kwargs=[
            {
                "updated_at": "2024-01-01T00:00:00",
                "tenant_id": tenant.id,
                "contents": {},
            },
            {
                "updated_at": "2024-01-02T00:00:00",
                "tenant_id": tenant.id,
                "contents": {},
            },
            {
                "updated_at": "2024-01-03T00:00:00",
                "tenant_id": tenant.id,
                "contents": {},
            },
            {
                "updated_at": "2023-05-13T00:00:00",
                "tenant_id": tenant.id,
                "contents": {},
            },
            {
                "updated_at": "2023-10-23T00:00:00",
                "tenant_id": tenant.id,
                "contents": {},
            },
            {"updated_at": "2023-05-13T00:00:00", "contents": {}},
            {"updated_at": "2023-10-23T00:00:00", "contents": {}},
        ],
    )
    client = rest_client(custom_tenant=tenant)

    response = await client.get(
        f"{REPORTS_ROUTE}/ebo?filter[start-date]=2023-01-02T00:00:00&filter[end-date]=2025-01-03T00:00:00"
    )

    # check for tenant based results

    assert len(response.json()) == 5

    # test filters for start date and end date

    response = await client.get(
        f"{REPORTS_ROUTE}/ebo?filter[start-date]=2024-01-02T00:00:00&filter[end-date]=2024-01-03T00:00:00"
    )

    reports = response.json()
    assert len(reports) == 2
    for report in reports:
        assert report["created_by"] is not None
        assert (
            report["created_by"]["first_name"] is not None
            or report["created_by"]["last_name"] is not None
        )
        assert report["date_for"] is not None
        assert report["contents"] is not None
        assert report["form_id"] is not None


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_get_jsbs(
    db_session: AsyncSession,
    rest_client: Callable[..., AsyncClient],
) -> None:
    tenant = await TenantFactory.persist(db_session)
    _ = await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=7,
        per_item_kwargs=[
            {
                "updated_at": "2024-01-01T00:00:00",
                "tenant_id": tenant.id,
                "contents": {},
            },
            {
                "updated_at": "2024-01-02T00:00:00",
                "tenant_id": tenant.id,
                "contents": {},
            },
            {
                "updated_at": "2024-01-03T00:00:00",
                "tenant_id": tenant.id,
                "contents": {},
            },
            {
                "updated_at": "2023-05-13T00:00:00",
                "tenant_id": tenant.id,
                "contents": {},
            },
            {
                "updated_at": "2023-10-23T00:00:00",
                "tenant_id": tenant.id,
                "contents": {},
            },
            {"updated_at": "2023-05-13T00:00:00", "contents": {}},
            {"updated_at": "2023-10-23T00:00:00", "contents": {}},
        ],
    )
    client = rest_client(custom_tenant=tenant)

    response = await client.get(
        f"{REPORTS_ROUTE}/jsb?filter[start-date]=2023-01-02T00:00:00&filter[end-date]=2025-01-03T00:00:00"
    )

    # check for tenant based results

    assert len(response.json()) == 5

    # test filters for start date and end date

    response = await client.get(
        f"{REPORTS_ROUTE}/jsb?filter[start-date]=2024-01-02T00:00:00&filter[end-date]=2024-01-03T00:00:00"
    )

    reports = response.json()
    assert len(reports) == 2
    for report in reports:
        assert report["created_by"] is not None
        assert (
            report["created_by"]["first_name"] is not None
            or report["created_by"]["last_name"] is not None
        )
        assert report["date_for"] is not None
        assert report["contents"] is not None


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_generate_token_for_reports(
    db_session: AsyncSession,
    rest_client: Callable[..., AsyncClient],
) -> None:
    tenant = await TenantFactory.persist(db_session)
    user = await UserFactory.persist(
        db_session, tenant_id=tenant.id, email="test@email.com"
    )
    client = rest_client(custom_tenant=tenant)
    data = {"user_name": user.email}
    response = await client.post(
        f"{REPORTS_TOKEN_ROUTE}",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    print(response)

    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None
    assert response.json()["expires_at"] is not None


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_get_ebos_with_refreshed_signed_urls(
    mocked_file_storage: MagicMock,
    mocked_cache: MagicMock,
    db_session: AsyncSession,
    rest_client: Callable[..., AsyncClient],
) -> None:
    tenant = await TenantFactory.persist(db_session)
    _photo_file = {
        "id": "beefa9d8-2a7d-4b37-9fec-3f2a433e7050/2025-05-14-f441adfd-aa32-467f-9d73-1610e3af7b5e",
        "md5": None,
        "url": "https://storage.googleapis.com/worker-safety-local-dev/beefa9d8-2a7d-4b37-9fec-3f2a433e7050/2025-05-14-f441adfd-aa32-467f-9d73-1610e3af7b5e",
        "date": None,
        "name": "1413823428-amazingly-free-stock-websites",
        "size": "129.063 KB",
        "time": None,
        "crc32c": None,
        "category": None,
        "mimetype": None,
        "signed_url": "https://storage.googleapis.com/worker-safety-local-dev/beefa9d8-2a7d-4b37-9fec-3f2a433e7050/2025-05-14-f441adfd-aa32-467f-9d73-1610e3af7b5e?Expires=1781948286&GoogleAccessId=worker-safety-local-dev%40urbint-1259.iam.gserviceaccount.com&Signature=NUyKz8PNw0jHxyxFPPqYRHLSxE%2Bff%2BJE9ZO4qrQ0Z8Oz3uEqX8NBfh92sn6lGaGMG4DSNcNH62b3Kw%2FvjNc6sqmjrbLkSrMD7Bqpe0V30XxsaiekXI4Uh9sjjjPayq3VNXTwOcWN%2BMTuqjj15hruU8mSVkYw0cNC7bRjHgc4pTLXcVi3i6Og7RLvErCzHolEBsQe8bFUBm46%2FgqrTTYj4ZNg%2B0KVkN%2B85%2FFeS5ch8T4NaGuH8R5aFUMhREhanPScos4ag8vRSjpTV3JOegOaz8KlhXMdCZSTSIzyUXSbRDIieGnZvNmCIFiTeolm1TAtB92tOInPdRPLjNMO%2FWCvew%3D%3D",
        "description": None,
        "display_name": "1413823428-amazingly-free-stock-websites",
    }
    _ = await EnergyBasedObservationFactory.persist_many(
        db_session,
        size=3,
        per_item_kwargs=[
            {
                "updated_at": "2024-01-01T00:00:00",
                "tenant_id": tenant.id,
                "contents": {
                    "photos": [_photo_file],
                },
            },
            {
                "updated_at": "2024-01-02T00:00:00",
                "tenant_id": tenant.id,
                "contents": {},
            },
            {"updated_at": "2024-01-03T00:00:00", "contents": {}},
        ],
    )
    client = rest_client(custom_tenant=tenant)

    # Simulate no value present in cache, then hit endpoint
    mocked_cache.get.return_value = None
    response = await client.get(
        f"{REPORTS_ROUTE}/ebo?filter[start-date]=2023-01-02T00:00:00&filter[end-date]=2025-01-03T00:00:00"
    )

    # check for tenant based results
    assert len(response.json()) == 2

    # test signed_url is not the same as db; generated using FileStorage._url()
    reports = response.json()
    for report in reports:
        assert report["contents"] is not None
        if "photos" in report["contents"].keys():
            assert (
                report["contents"]["photos"][0]["signed_url"]
                is not _photo_file["signed_url"]
            )

    # check if _url was callled with correct params
    mocked_file_storage._url.assert_called_once_with(
        _photo_file["id"], datetime.timedelta(days=7)
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_get_ebos_with_cached_signed_urls(
    mocked_file_storage: MagicMock,
    mocked_cache: MagicMock,
    db_session: AsyncSession,
    rest_client: Callable[..., AsyncClient],
) -> None:
    tenant = await TenantFactory.persist(db_session)
    _photo_file = {
        "id": "beefa9d8-2a7d-4b37-9fec-3f2a433e7050/2025-05-14-f441adfd-aa32-467f-9d73-1610e3af7b5e",
        "md5": None,
        "url": "https://storage.googleapis.com/worker-safety-local-dev/beefa9d8-2a7d-4b37-9fec-3f2a433e7050/2025-05-14-f441adfd-aa32-467f-9d73-1610e3af7b5e",
        "date": None,
        "name": "1413823428-amazingly-free-stock-websites",
        "size": "129.063 KB",
        "time": None,
        "crc32c": None,
        "category": None,
        "mimetype": None,
        "signed_url": "https://storage.googleapis.com/worker-safety-local-dev/beefa9d8-2a7d-4b37-9fec-3f2a433e7050/2025-05-14-f441adfd-aa32-467f-9d73-1610e3af7b5e?Expires=1781948286&GoogleAccessId=worker-safety-local-dev%40urbint-1259.iam.gserviceaccount.com&Signature=NUyKz8PNw0jHxyxFPPqYRHLSxE%2Bff%2BJE9ZO4qrQ0Z8Oz3uEqX8NBfh92sn6lGaGMG4DSNcNH62b3Kw%2FvjNc6sqmjrbLkSrMD7Bqpe0V30XxsaiekXI4Uh9sjjjPayq3VNXTwOcWN%2BMTuqjj15hruU8mSVkYw0cNC7bRjHgc4pTLXcVi3i6Og7RLvErCzHolEBsQe8bFUBm46%2FgqrTTYj4ZNg%2B0KVkN%2B85%2FFeS5ch8T4NaGuH8R5aFUMhREhanPScos4ag8vRSjpTV3JOegOaz8KlhXMdCZSTSIzyUXSbRDIieGnZvNmCIFiTeolm1TAtB92tOInPdRPLjNMO%2FWCvew%3D%3D",
        "description": None,
        "display_name": "1413823428-amazingly-free-stock-websites",
    }
    _ = await EnergyBasedObservationFactory.persist_many(
        db_session,
        size=3,
        per_item_kwargs=[
            {
                "updated_at": "2024-01-01T00:00:00",
                "tenant_id": tenant.id,
                "contents": {
                    "photos": [_photo_file],
                },
            },
            {
                "updated_at": "2024-01-02T00:00:00",
                "tenant_id": tenant.id,
                "contents": {},
            },
            {"updated_at": "2024-01-03T00:00:00", "contents": {}},
        ],
    )
    client = rest_client(custom_tenant=tenant)

    # call endpoint, when signed_url does not exist in cache
    mocked_cache.get.return_value = None
    _ = await client.get(
        f"{REPORTS_ROUTE}/ebo?filter[start-date]=2023-01-02T00:00:00&filter[end-date]=2025-01-03T00:00:00"
    )

    # check if _url was callled with correct params
    mocked_file_storage._url.assert_called_once_with(
        _photo_file["id"], datetime.timedelta(days=7)
    )
    mocked_cache.set.assert_called_once()

    # Resets
    mocked_cache.reset_mock()
    mocked_file_storage.reset_mock()

    # call the api again, when signed_url present in cache
    mocked_cache.get.return_value = (
        f"https://storage.googleapis.com/{_photo_file['id']}?signed=true"
    )
    _ = await client.get(
        f"{REPORTS_ROUTE}/ebo?filter[start-date]=2023-01-02T00:00:00&filter[end-date]=2025-01-03T00:00:00"
    )

    # check if _url was callled with correct params
    mocked_file_storage._url.assert_not_called()
