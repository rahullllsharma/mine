import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, Response

from worker_safety_service.context import Context, get_context
from worker_safety_service.models import ProjectStatus, RiskLevel
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.utils import validate_tile_bbox

router = APIRouter()


@router.get("/locations/tile/{zoom}/{x}/{y}", tags=["tiles"])
async def locations_tile_view(
    zoom: int,
    x: int,
    y: int,
    search: str | None = Query(None),
    library_region_ids: list[uuid.UUID] | None = Query(None),
    library_division_ids: list[uuid.UUID] | None = Query(None),
    library_project_type_ids: list[uuid.UUID] | None = Query(None),
    work_type_ids: list[uuid.UUID] | None = Query(None),
    project_ids: list[uuid.UUID] | None = Query(None),
    project_status: list[ProjectStatus] | None = Query(None),
    contractor_ids: list[uuid.UUID] | None = Query(None),
    supervisor_ids: list[uuid.UUID] | None = Query(None),
    risk_levels: list[RiskLevel] | None = Query(None),
    risk_level_date: date | None = Query(None),
    context: Context = Depends(get_context),
) -> Response:
    """Get a tile for a given zoom level, latitude, and longitude"""
    try:
        validate_tile_bbox(zoom, x, y)
    except Exception as error:
        return ErrorResponse(404, "Not found", error.args[0])

    tile = await context.project_locations.get_tile(
        tile_box=(zoom, x, y),
        library_region_ids=library_region_ids,
        library_division_ids=library_division_ids,
        library_project_type_ids=library_project_type_ids,
        work_type_ids=work_type_ids,
        project_ids=project_ids,
        project_status=project_status,
        contractor_ids=contractor_ids,
        all_supervisor_ids=supervisor_ids,
        search=search,
        risk_level_date=risk_level_date,
        risk_levels=risk_levels,
    )
    return Response(content=tile, media_type="application/x-protobuf")
