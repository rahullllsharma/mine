from datetime import datetime, timezone

import pytest

from tests.factories import DailyReportFactory, LocationFactory, TenantFactory
from worker_safety_service.dal.locations import LocationsManager
from worker_safety_service.models import AsyncSession, FormStatus


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_location(
    db_session: AsyncSession, locations_manager: LocationsManager
) -> None:
    location = await LocationFactory.persist(db_session)
    location_id = location.id
    geom = location.geom
    name = location.name
    tenant_id = (await TenantFactory.default_tenant(db_session)).id

    result = await locations_manager.get_location(location_id, tenant_id)

    assert result
    assert result.id == location_id
    assert result.geom == geom
    assert result.name == name


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_locations_by_id(
    db_session: AsyncSession, locations_manager: LocationsManager
) -> None:
    locations = await LocationFactory.persist_many(db_session, size=3)
    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    location_ids = [location.id for location in locations]
    results = await locations_manager.get_locations_by_id(
        ids=location_ids, tenant_id=tenant_id
    )

    assert len(results) == 3
    assert all(location_id in location_ids for location_id in results.keys())


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_locations(
    db_session: AsyncSession, locations_manager: LocationsManager
) -> None:
    locations = await LocationFactory.persist_many(db_session, size=3)
    project_id = locations[0].project_id
    assert project_id

    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    location_ids = [location.id for location in locations]
    result = await locations_manager.get_locations(
        ids=location_ids, tenant_id=tenant_id, project_ids=[project_id]
    )

    assert len(result) == 1
    assert locations[0].id == result[0].id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_validate_location_archive_raises_on_daily_report_in_progress(
    db_session: AsyncSession,
    locations_manager: LocationsManager,
) -> None:
    """
    Locations cannot be deleted if a daily inspection report is in progress
    """
    location = await LocationFactory.persist(db_session)

    await DailyReportFactory.persist(
        db_session,
        project_location_id=location.id,
        status=FormStatus.IN_PROGRESS,
    )

    with pytest.raises(ValueError) as e:
        await locations_manager.validate_location_archive([location.id])
    assert e.match(f"Project location {location.id} has 1 active daily reports.")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_validate_location_archive_raises_on_daily_report_completed(
    db_session: AsyncSession,
    locations_manager: LocationsManager,
) -> None:
    """
    Locations cannot be deleted if a daily inspection report is completed
    """
    location = await LocationFactory.persist(db_session)

    await DailyReportFactory.persist(
        db_session, project_location_id=location.id, status=FormStatus.COMPLETE
    )

    with pytest.raises(ValueError) as e:
        await locations_manager.validate_location_archive([location.id])
    assert e.match(f"Project location {location.id} has 1 active daily reports.")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_validate_location_archive_accepts_on_no_daily_reports(
    db_session: AsyncSession,
    locations_manager: LocationsManager,
) -> None:
    """
    Locations can be deleted if no daily inspection report is associated
    """

    location = await LocationFactory.persist(db_session)

    result = await locations_manager.validate_location_archive([location.id])
    assert result is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_validate_location_archive_accepts_on_archived_reports(
    db_session: AsyncSession,
    locations_manager: LocationsManager,
) -> None:
    """
    Locations can be deleted if a daily inspection report is associated but archived
    """
    location = await LocationFactory.persist(db_session)

    await DailyReportFactory.persist(
        db_session,
        project_location_id=location.id,
        status=FormStatus.COMPLETE,
        archived_at=datetime.now(timezone.utc),
    )

    result = await locations_manager.validate_location_archive([location.id])
    assert result is True
