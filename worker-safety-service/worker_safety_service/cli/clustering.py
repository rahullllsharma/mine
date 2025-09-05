import typer
from sqlmodel import select

from worker_safety_service.cli.utils import (
    TyperContext,
    run_async,
    with_redis,
    with_session,
)
from worker_safety_service.dal.work_packages import LocationClustering
from worker_safety_service.models import Tenant
from worker_safety_service.urbint_logging import get_logger

app = typer.Typer()
logger = get_logger(__name__)


@app.command(name="recreate")
@run_async
@with_session
@with_redis
async def recreate_clustering(ctx: TyperContext, tenant_name: str) -> None:
    tenant_id = (await ctx.session.exec(select(Tenant.id))).first()
    if not tenant_id:
        raise ValueError(f"Invalid tenant {tenant_name}")
    await LocationClustering(ctx.session).recreate(tenant_id)


@app.command(name="check-clusters")
@run_async
@with_session
@with_redis
async def check_invalid_clusters(ctx: TyperContext) -> None:
    clustering = LocationClustering(ctx.session)
    tenant_ids = (await ctx.session.exec(select(Tenant.id))).all()
    for tenant_id in tenant_ids:
        await clustering.check_all_clusters(tenant_id)
        await ctx.session.commit()


@app.command(name="check-empty")
@run_async
@with_session
@with_redis
async def check_empty_clusters(
    ctx: TyperContext, up_to_zoom: int = int(LocationClustering.max_zoom / 3)
) -> None:
    clustering = LocationClustering(ctx.session)
    tenant_ids = (await ctx.session.exec(select(Tenant.id))).all()
    for tenant_id in tenant_ids:
        await clustering.check_empty_clusters(tenant_id, up_to_zoom=up_to_zoom)


@app.command(name="update-registered-clusters-centroid")
@run_async
@with_session
@with_redis
async def update_registered_clusters_centroid(ctx: TyperContext) -> None:
    clustering = LocationClustering(ctx.session)
    await clustering.update_registered_clusters_centroid()


@app.command(name="update-all-clusters-centroid")
@run_async
@with_session
@with_redis
async def update_all_clusters_centroid(ctx: TyperContext) -> None:
    clustering = LocationClustering(ctx.session)
    tenant_ids = (await ctx.session.exec(select(Tenant.id))).all()
    for tenant_id in tenant_ids:
        await clustering.update_tenant_clusters_centroid(tenant_id)
        await ctx.session.commit()
