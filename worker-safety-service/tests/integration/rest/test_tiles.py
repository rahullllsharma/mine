import datetime

import pytest

from tests.factories import LocationFactory
from tests.integration.conftest import ExecuteRest
from tests.vector_tile import decode_tile
from worker_safety_service.models import AsyncSession
from worker_safety_service.types import Point

TILE_ROUTE = "/locations/tile/{}/{}/{}"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_locations_tile(
    execute_rest: ExecuteRest,
    db_session: AsyncSession,
) -> None:
    locations = {
        str(i.id): i.geom
        for i in await LocationFactory.persist_many(db_session, size=50)
    }
    # Ignore archived
    await LocationFactory.persist(db_session, archived_at=datetime.datetime.utcnow())

    response = await execute_rest(TILE_ROUTE.format(0, 0, 0))
    tile = decode_tile(response.read())
    response_ids = {
        i["properties"]["locationId"] for i in tile["locations"]["features"]
    }
    assert set(locations.keys()) == response_ids

    # On a small tile
    location_id, geom = list(locations.items())[0]
    response = await execute_rest(TILE_ROUTE.format(*geom.to_tile_bbox(24)))
    tile = decode_tile(response.read())
    response_ids = {
        i["properties"]["locationId"] for i in tile["locations"]["features"]
    }
    assert response_ids == {location_id}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_locations_tile_raises_on_invalid_zoom(execute_rest: ExecuteRest) -> None:
    await execute_rest(TILE_ROUTE.format(-1, 0, 0), expected_status_code=404)
    await execute_rest(TILE_ROUTE.format(29, 0, 0), expected_status_code=404)
    await execute_rest(TILE_ROUTE.format(0, -1, 0), expected_status_code=404)
    await execute_rest(TILE_ROUTE.format(0, 1, 0), expected_status_code=404)
    await execute_rest(TILE_ROUTE.format(0, 0, -1), expected_status_code=404)
    await execute_rest(TILE_ROUTE.format(0, 0, 1), expected_status_code=404)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_locations_tile_edges(
    execute_rest: ExecuteRest,
    db_session: AsyncSession,
) -> None:
    # TileBBox don't catch map edges, probably not an issue
    # but it's how mapbox TileBBox works https://github.com/mapbox/postgis-vt-util
    await LocationFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {"geom": Point(-180, 90)},
            {"geom": Point(-180, 87)},
            {"geom": Point(180, 90)},
            {"geom": Point(180, -90)},
            {"geom": Point(-180, -90)},
            {"geom": Point(-180, -90)},
        ],
    )

    response = await execute_rest(TILE_ROUTE.format(0, 0, 0))
    binary = response.read()
    assert not binary
