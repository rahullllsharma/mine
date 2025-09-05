from datetime import timedelta
from typing import Any, Callable, Coroutine
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import text

from tests.factories import EnergyBasedObservationFactory, TenantFactory
from worker_safety_service.gcloud.storage import FileStorage
from worker_safety_service.models import AsyncSession, EnergyBasedObservationLayout
from worker_safety_service.models.concepts import File

DOWN_REVISION = "a3ee7f1cadbb"
CURRENT_REVISION = "8f800c7f8aab"


@pytest.mark.skip(reason="not working; to be addressed later")
async def test_8f800c7f8aab_migration_updates_photo_urls(
    migrate_upto: Callable[..., Coroutine[Any, Any, None]],
    db_session: AsyncSession,
) -> None:
    """Test that migration 8f800c7f8aab updates signed URLs for EBO photos correctly"""
    # Setup test data
    await migrate_upto(DOWN_REVISION)
    tenant = await TenantFactory.persist(db_session)
    photo1 = File(
        id="test1.jpg",
        name="test1.jpg",
        display_name="test1.jpg",
        signed_url=None,
    )
    photo2 = File(
        id="test2.jpg",
        name="test2.jpg",
        display_name="test2.jpg",
        signed_url=None,
    )

    ebo = await EnergyBasedObservationFactory.persist(
        db_session,
        tenant_id=tenant.id,
        contents={"photos": [photo1.dict(), photo2.dict()]},
    )

    # Mock FileStorage
    mock_storage = MagicMock(spec=FileStorage)
    mock_storage._url.side_effect = (
        lambda file_id, expiration: f"https://storage.googleapis.com/{file_id}?signed=true"
    )

    # Run specific migration
    with patch(
        "worker_safety_service.gcloud.storage.FileStorage", return_value=mock_storage
    ):
        await migrate_upto(CURRENT_REVISION)

    # Verify results
    query = text("SELECT contents FROM energy_based_observations WHERE id = :id")
    result = await db_session.execute(query, {"id": ebo.id})
    updated_contents = result.scalar_one()

    # Parse updated contents
    updated_ebo = EnergyBasedObservationLayout.parse_obj(updated_contents)

    # Assertions
    assert updated_ebo.photos
    assert len(updated_ebo.photos) == 2
    for photo in updated_ebo.photos:
        assert photo.id
        assert photo.signed_url is not None
        # FIXME: @mainak-urbint
        assert "signed=true" in photo.signed_url
        assert photo.id in photo.signed_url

    # Verify FileStorage was called correctly
    mock_storage._url.assert_any_call("test1.jpg", expiration=timedelta(days=356))
    mock_storage._url.assert_any_call("test2.jpg", expiration=timedelta(days=356))
    assert mock_storage._url.call_count == 2


@pytest.mark.skip(reason="not working; to be addressed later")
async def test_8f800c7f8aab_handles_empty_photos(
    migrate_upto: Callable[..., Coroutine[Any, Any, None]],
    db_session: AsyncSession,
) -> None:
    """Test that migration 8f800c7f8aab handles EBOs without photos gracefully"""
    await migrate_upto(DOWN_REVISION)
    # Setup EBO without photos
    tenant = await TenantFactory.persist(db_session)
    ebo = await EnergyBasedObservationFactory.persist(
        db_session, tenant_id=tenant.id, contents={"other_field": "value"}
    )
    await db_session.commit()

    # Run specific migration
    mock_storage = MagicMock(spec=FileStorage)
    with patch(
        "worker_safety_service.gcloud.storage.FileStorage", return_value=mock_storage
    ):
        await migrate_upto(CURRENT_REVISION)

    # Verify no changes were made
    query = text("SELECT contents FROM energy_based_observations WHERE id = :id")
    result = await db_session.execute(query, {"id": ebo.id})
    updated_contents = result.scalar_one()

    assert updated_contents == {"other_field": "value"}
    assert mock_storage._url.call_count == 0
