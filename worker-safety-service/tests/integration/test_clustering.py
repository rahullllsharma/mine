import asyncio
import uuid
from time import time
from typing import Any

import pytest
from sqlalchemy.orm import sessionmaker

from tests.factories import (
    LocationClusteringFactory,
    LocationFactory,
    TenantFactory,
    WorkPackageFactory,
)
from worker_safety_service.dal.work_packages import LocationClustering
from worker_safety_service.models import AsyncSession, Location
from worker_safety_service.types import Point


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.xfail
async def test_clustering_lock(
    db_session: AsyncSession, async_sessionmaker: sessionmaker
) -> None:
    """Make sure lock is working per tenant"""

    tenant_1, tenant_2 = await TenantFactory.persist_many(db_session, size=2, id=None)
    work_package_1 = await WorkPackageFactory.persist(db_session, tenant_id=tenant_1.id)
    locations_1 = await LocationFactory.persist_many(
        db_session, size=3, project_id=work_package_1.id
    )
    work_package_2 = await WorkPackageFactory.persist(db_session, tenant_id=tenant_2.id)
    locations_2 = await LocationFactory.persist_many(
        db_session, size=3, project_id=work_package_2.id
    )

    start_times: list[tuple[uuid.UUID, float]] = []
    times: dict[uuid.UUID, list[tuple[float, float]]] = {
        tenant_1.id: [],
        tenant_2.id: [],
    }

    async def _add(
        tenant_id: uuid.UUID,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        start = time()
        await asyncio.sleep(0.2)
        times[tenant_id].append((start, time()))

    async def test_update(tenant_id: uuid.UUID, location: Location) -> None:
        async with async_sessionmaker() as with_session:
            start_times.append((location.id, time()))
            clustering = LocationClustering(with_session)
            clustering._add = _add  # type: ignore
            await clustering.update(tenant_id, [location])

    await asyncio.gather(
        *(test_update(tenant_1.id, location) for location in locations_1),
        *(test_update(tenant_2.id, location) for location in locations_2),
    )

    # For same tenant, it should be locked
    for t_times in times.values():
        t_times.sort(key=lambda i: i[1])
        previous_end = t_times[0][1]
        for start, end in t_times[1:]:
            assert start > previous_end
            previous_end = end

    # For different tenants, it should run at same time
    start_1, end_1 = times[tenant_1.id][0]
    start_2, end_2 = times[tenant_2.id][0]
    assert start_1 < end_2
    assert start_2 < end_1


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.xfail
async def test_clustering_lock_ignored(db_session: AsyncSession) -> None:
    """Make sure lock is ignored after some time, but no calculation should be made"""

    tenant_id = (await TenantFactory.persist(db_session, id=None)).id
    work_package_1 = await WorkPackageFactory.persist(db_session, tenant_id=tenant_id)
    location = await LocationFactory.persist(db_session, project_id=work_package_1.id)
    called_times = []

    async def _add(*args: Any, **kwargs: Any) -> None:
        called_times.append(time())

    clustering = LocationClustering(db_session)
    clustering.default_blocking_timeout = 1
    clustering._add = _add  # type: ignore

    # Let's force a lock
    path = clustering._build_lock_name(tenant_id)
    try:
        await clustering.redis_client.set(path, "invalid")

        await clustering.update(tenant_id, [location])

        # On lock error, it be ignored and not raise an error
        assert not called_times
    finally:
        # In case the test fails, we don't lock it for others
        await clustering.redis_client.delete(path)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_clustering_ignored_on_error(db_session: AsyncSession) -> None:
    """Make sure all clustering calculation are ignored on error"""

    tenant_id = (await TenantFactory.persist(db_session, id=None)).id
    work_package_1 = await WorkPackageFactory.persist(db_session, tenant_id=tenant_id)
    location = await LocationFactory.persist(db_session, project_id=work_package_1.id)

    async def _raise_error(*args: Any, **kwargs: Any) -> None:
        raise ValueError("Some error")

    clustering = LocationClustering(db_session)
    clustering._add = _raise_error  # type: ignore
    clustering._clear_models = _raise_error  # type: ignore

    await clustering.update(tenant_id, [location])
    await db_session.refresh(location)
    assert location.clustering == []

    await clustering.batch(tenant_id, added=[location])
    await db_session.refresh(location)
    assert location.clustering == []

    await clustering.batch(tenant_id, updated=[location])
    await db_session.refresh(location)
    assert location.clustering == []

    await clustering.batch(tenant_id, deleted=[location])
    await db_session.refresh(location)
    assert location.clustering == []

    await clustering.delete(tenant_id, [location])
    await db_session.refresh(location)
    assert location.clustering == []


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_clustering_on_existing_cluster(
    db_session: AsyncSession,
    location_clustering: LocationClustering,
) -> None:
    """Make sure db models are merged with existing clusters"""

    geom = Point(0, 0)
    work_package_1 = await WorkPackageFactory.persist(db_session)
    location_1, location_2 = await LocationFactory.persist_many(
        db_session, size=2, project_id=work_package_1.id, geom=geom
    )
    await location_clustering.update(work_package_1.tenant_id, [location_1, location_2])
    await location_clustering.session.commit()
    await db_session.refresh(location_1)
    await db_session.refresh(location_2)
    assert all(location_1.clustering)
    assert location_1.clustering == location_2.clustering

    # Adding a new location to same point will add it to existing clusters
    location_3 = await LocationFactory.persist(
        db_session, project_id=work_package_1.id, geom=geom
    )
    await location_clustering.update(work_package_1.tenant_id, [location_3])
    await db_session.commit()

    await db_session.refresh(location_3)
    assert location_1.clustering == location_3.clustering


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_find_closest_clustering(
    db_session: AsyncSession,
    location_clustering: LocationClustering,
) -> None:
    """
    If model intersect multiple clusters, should go to the closest one,
    even if in a lower zoom they exist in same cluster
    """

    work_package_1 = await WorkPackageFactory.persist(db_session)

    # center at lon 1.5
    cluster_1 = await LocationClusteringFactory.persist_box(
        db_session, zoom=0, box=((0, 1), (3, 0))
    )
    # center at lon 3
    cluster_2 = await LocationClusteringFactory.persist_box(
        db_session, zoom=0, box=((2, 1), (4, 0))
    )

    # we have overlap between lon 2 and lon 3
    # adding point to 2.1 should be closer to cluster_1
    location_1 = await LocationFactory.persist(
        db_session, project_id=work_package_1.id, geom=Point(2.1, 0.5)
    )
    # adding point to 2.9 should be closer to cluster_2
    location_2 = await LocationFactory.persist(
        db_session, project_id=work_package_1.id, geom=Point(2.9, 0.5)
    )

    await location_clustering.update(work_package_1.tenant_id, [location_1, location_2])
    await location_clustering.session.commit()
    await db_session.refresh(location_1)
    await db_session.refresh(location_2)
    assert location_1.clustering[0] == cluster_1.id
    assert location_2.clustering[0] == cluster_2.id


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_postpone_clustering_on_models(
    db_session: AsyncSession,
    location_clustering: LocationClustering,
) -> None:
    """Make sure db models are merged with new models"""

    geom = Point(0, 0)
    work_package_1 = await WorkPackageFactory.persist(db_session)
    location_1 = await LocationFactory.persist(
        db_session, project_id=work_package_1.id, geom=geom
    )
    assert location_1.clustering == []
    await location_clustering.update(work_package_1.tenant_id, [location_1])
    await location_clustering.session.commit()
    await db_session.refresh(location_1)
    assert not any(location_1.clustering)

    # Adding a new location to same point will trigger postpone clustering, because it can't find any clustering created
    location_2 = await LocationFactory.persist(
        db_session, project_id=work_package_1.id, geom=geom
    )
    await location_clustering.update(work_package_1.tenant_id, [location_2])
    await db_session.commit()

    await db_session.refresh(location_1)
    await db_session.refresh(location_2)
    assert location_1.clustering == location_2.clustering


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_postpone_clustering_on_clusters(
    db_session: AsyncSession,
    location_clustering: LocationClustering,
) -> None:
    """Make sure db models are merged with new clusters"""

    geom = Point(0, 0)
    work_package_1 = await WorkPackageFactory.persist(db_session)
    location_1 = await LocationFactory.persist(
        db_session, project_id=work_package_1.id, geom=geom
    )
    assert location_1.clustering == []
    await location_clustering.update(work_package_1.tenant_id, [location_1])
    await location_clustering.session.commit()
    await location_clustering.session.refresh(location_1)
    assert location_1.clustering == [None] * (location_clustering.max_zoom + 1)

    # Adding new locations to same point will trigger postpone clustering, because it can't find any clustering created
    location_2, location_3 = await LocationFactory.persist_many(
        db_session, size=2, project_id=work_package_1.id, geom=geom
    )
    location_4 = await LocationFactory.persist(
        db_session, project_id=work_package_1.id, geom=Point(-90, -180)
    )
    await location_clustering.update(
        work_package_1.tenant_id, [location_2, location_3, location_4]
    )
    await location_clustering.session.commit()

    await db_session.refresh(location_1)
    await db_session.refresh(location_2)
    await db_session.refresh(location_3)
    await db_session.refresh(location_4)
    assert all(location_1.clustering)
    assert location_1.clustering == location_2.clustering
    assert location_2.clustering == location_3.clustering
    assert not any(location_4.clustering)
