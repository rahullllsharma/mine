import uuid
from dataclasses import dataclass

import pytest

from tests.factories import (
    ActivityFactory,
    LocationFactory,
    TenantFactory,
    WorkPackageFactory,
)
from worker_safety_service.models import Activity, AsyncSession, Location, WorkPackage


@dataclass
class SharedData:
    tenant_id: uuid.UUID
    work_package: WorkPackage
    location: Location


async def create_activity_with_tenant(
    db_session: AsyncSession,
    external_key: str | None = None,
    shared_data: SharedData | None = None,
) -> tuple[Activity, SharedData]:
    if external_key is None:
        external_key = str(uuid.uuid4())
    if shared_data is None:
        tenant = await TenantFactory.persist(db_session)
        tenant_id = tenant.id
        work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant_id)
        location = await LocationFactory.persist(
            db_session, tenant_id=tenant_id, project_id=work_package.id
        )
        shared_data = SharedData(
            tenant_id=tenant_id,
            work_package=work_package,
            location=location,
        )
    else:
        tenant_id = shared_data.tenant_id
        work_package = shared_data.work_package
        location = shared_data.location

    activity = await ActivityFactory.persist(
        db_session,
        location_id=location.id,
        external_key=external_key,
    )
    return activity, SharedData(
        tenant_id=tenant_id, work_package=work_package, location=location
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_and_edit_activities_with_different_external_keys(
    db_session: AsyncSession,
) -> None:
    same_uuid = str(uuid.uuid4())
    # We should be able to have external keys on activities
    activity1_t1, shared_data1 = await create_activity_with_tenant(db_session)
    activity2_t1, _ = await create_activity_with_tenant(
        db_session, shared_data=shared_data1
    )
    activity3_t1, _ = await create_activity_with_tenant(
        db_session,
        external_key=same_uuid,
        shared_data=shared_data1,
    )
    # and we should be able to create more external keys in other tenants
    activity1_t2, shared_data2 = await create_activity_with_tenant(db_session)
    activity2_t2, _ = await create_activity_with_tenant(
        db_session, shared_data=shared_data2
    )
    # and the external_key can be the same as in a different tenant
    activity3_t2, _ = await create_activity_with_tenant(
        db_session,
        external_key=same_uuid,
        shared_data=shared_data2,
    )

    # and we can edit them to new (unique) keys
    activity1_t1.external_key = str(uuid.uuid4())
    db_session.add(activity1_t1)
    activity1_t2.external_key = str(uuid.uuid4())
    db_session.add(activity1_t2)
    await db_session.commit()

    # but we can't duplicate a key in a tenant in an update
    with pytest.raises(Exception):
        activity1_t1.external_key = same_uuid
        db_session.add(activity1_t1)
        await db_session.commit()

    # and we can't create a duplicate key
    with pytest.raises(Exception):
        activity4_t1, _ = await create_activity_with_tenant(
            db_session,
            external_key=same_uuid,
            shared_data=shared_data1,
        )
