import uuid
from collections import defaultdict
from collections.abc import Iterable
from time import time
from typing import Any, AsyncGenerator, NamedTuple

from redis.asyncio.lock import Lock
from redis.exceptions import LockError
from sqlalchemy.sql import Values
from sqlalchemy.sql.expression import union_all
from sqlmodel import (
    Integer,
    col,
    column,
    delete,
    func,
    literal,
    or_,
    select,
    text,
    update,
)

from worker_safety_service.clustering.utils import (
    BuildTile,
    Coordinates,
    NewClustering,
    PostponeClustering,
    ignore_errors,
    point_hex_to_tile,
)
from worker_safety_service.config import settings
from worker_safety_service.models.utils import (
    AsyncSession,
    ClusteringModelBase,
    ClusteringObjectModelBase,
    PointColumn,
    PolygonColumn,
)
from worker_safety_service.redis_client import get_redis_client
from worker_safety_service.types import Point, Polygon
from worker_safety_service.urbint_logging import get_logger
from worker_safety_service.urbint_logging.fastapi_utils import Stats
from worker_safety_service.utils import iter_by_step

logger = get_logger(__name__)
MAX_POSTGRES_PARAMS = 32000  # real 32767


class ClusteringBase:
    # !WARN! To update the following settings:
    # - "clustering recreate" cli needs to be called
    # - add new clustering_* db functions
    # - add models table indexes on clustering column
    max_zoom = 12
    radius = 60

    cluster_model: type[ClusteringModelBase]
    model: type[ClusteringObjectModelBase]
    model_id_db_type: Any

    default_lock_timeout: int = 60 * 60
    default_blocking_timeout: int = 5

    # Max number of models to calculate at same time
    batch_size = 500

    # Number of cluster centroid to do at same time
    batch_centroid_size = 100

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.redis_client = get_redis_client()

    def set_valid_statement(self, statement: Any, tenant_id: uuid.UUID | None) -> Any:
        """Apply required relations and filter to fetch valid models"""
        raise NotImplementedError()

    @ignore_errors
    async def update(
        self,
        tenant_id: uuid.UUID,
        *models_items: Iterable[ClusteringObjectModelBase],
    ) -> None:
        # !WARN! Must be called with model lock

        with Stats("clustering"):
            cluster_ids = self._extract_clustering_ids(*models_items)
            await self._add_with_lock(tenant_id, *models_items)
            if cluster_ids:
                await self.session.flush()
                await self.check_clusters(tenant_id, cluster_ids)

            self._extract_clustering_ids(*models_items, ref=cluster_ids)
            if cluster_ids:
                await self._register_update_of_clusters_centroid(tenant_id, cluster_ids)

    @ignore_errors
    async def delete(
        self,
        tenant_id: uuid.UUID,
        *models_items: Iterable[ClusteringObjectModelBase],
    ) -> None:
        # !WARN! Must be called with model lock

        with Stats("clustering"):
            cluster_ids = self._extract_clustering_ids(*models_items)
            self._clear_models(*models_items)
            if cluster_ids:
                await self.session.flush()
                await self.check_clusters(tenant_id, cluster_ids)
                await self._register_update_of_clusters_centroid(tenant_id, cluster_ids)

    @ignore_errors
    async def batch(
        self,
        tenant_id: uuid.UUID,
        *,
        added: Iterable[ClusteringObjectModelBase] | None = None,
        updated: Iterable[ClusteringObjectModelBase] | None = None,
        deleted: Iterable[ClusteringObjectModelBase] | None = None,
    ) -> None:
        # !WARN! Must be called with model lock

        with Stats("clustering"):
            cluster_ids: defaultdict[int, set[uuid.UUID]] = defaultdict(set)
            models_items: list[Iterable[ClusteringObjectModelBase]] = []
            if added:
                models_items.append(added)
            if updated:
                self._extract_clustering_ids(updated, ref=cluster_ids)
                models_items.append(updated)
            if deleted:
                self._extract_clustering_ids(deleted, ref=cluster_ids)
                self._clear_models(deleted)

            if models_items:
                await self._add_with_lock(tenant_id, *models_items)
            if cluster_ids:
                await self.session.flush()
                await self.check_clusters(tenant_id, cluster_ids)

            if added:
                self._extract_clustering_ids(added, ref=cluster_ids)
            if updated:
                self._extract_clustering_ids(updated, ref=cluster_ids)
            if cluster_ids:
                await self._register_update_of_clusters_centroid(tenant_id, cluster_ids)

    async def recreate(self, tenant_id: uuid.UUID) -> None:
        # Let's clear everything first
        async with self._with_lock(tenant_id):
            update_stmt = update(self.model).where(self.model.clustering != [])
            await self.session.execute(
                self.set_valid_statement(update_stmt, tenant_id).values(
                    {"clustering": []}
                )
            )
            await self.session.execute(
                delete(self.cluster_model).where(
                    self.cluster_model.tenant_id == tenant_id
                )
            )
            await self.session.commit()

        # Now update it
        async for models in self._iter_and_lock_all_db_models(
            tenant_id, self.batch_size
        ):
            await self.update(tenant_id, models)
            await self.session.commit()  # Commit to release the model lock

    async def check_all_clusters(self, tenant_id: uuid.UUID) -> None:
        cluster_ids = defaultdict(set)
        for zoom, cluster_id in (
            await self.session.execute(
                select(self.cluster_model.zoom, self.cluster_model.id)
            )
        ).all():
            cluster_ids[zoom].add(cluster_id)

        await self.check_clusters(tenant_id, cluster_ids)

    async def check_clusters(
        self,
        tenant_id: uuid.UUID,
        cluster_ids: defaultdict[int, set[uuid.UUID]],
    ) -> None:
        start = time()
        try:
            async with self._with_lock(tenant_id):
                await self._check_clusters(cluster_ids)
        except LockError:
            logger.critical(
                "Failed to lock clustering, failed to check clusters, please run 'clustering check-clusters' CLI",
                lock_name=self._build_lock_name(tenant_id),
                waited_for=round(time() - start, 4),
                tenant_id=str(tenant_id),
                cluster_ids=str(cluster_ids),
            )

    async def check_empty_clusters(
        self, tenant_id: uuid.UUID, up_to_zoom: int | None = None
    ) -> None:
        or_queries = [self.model.clustering == []]
        if up_to_zoom is not None:
            up_to_zoom = max(0, min(up_to_zoom, self.max_zoom))
            for zoom in range(up_to_zoom + 1):
                or_queries.append(self.clustering_id_column(zoom).is_(None))

        stmt = select(self.model.id).where(or_(*or_queries))
        stmt = self.set_valid_statement(stmt, tenant_id)
        model_ids = (await self.session.exec(stmt)).all()
        if model_ids:
            logger.info(
                "Found models with empty clustering",
                length=len(model_ids),
                model_ids=list(map(str, model_ids)),
                up_to_zoom=up_to_zoom,
            )
            for block_ids in iter_by_step(self.batch_size, model_ids):
                models = await self._lock_db_models(block_ids)
                await self.update(tenant_id, models)
                await self.session.commit()  # Commit to release the model lock

    def _build_centroid_queue_name(self) -> str:
        return f"clusteringCentroid:{self.cluster_model.__tablename__}"

    async def _register_update_of_clusters_centroid(
        self, tenant_id: uuid.UUID, cluster_ids: dict[int, set[uuid.UUID]]
    ) -> None:
        await self.redis_client.sadd(
            self._build_centroid_queue_name(),
            *(
                f"{tenant_id.hex}:{zoom}:{cluster_id.hex}"
                for zoom, ids in cluster_ids.items()
                for cluster_id in ids
            ),
        )

    async def update_registered_clusters_centroid(self) -> None:
        cluster_str: str
        while True:
            clusters: dict[uuid.UUID, dict[int, set[uuid.UUID]]] = defaultdict(
                lambda: defaultdict(set)
            )
            for cluster_data in await self.redis_client.spop(
                self._build_centroid_queue_name(), self.batch_centroid_size
            ):
                try:
                    if isinstance(cluster_data, bytes):
                        cluster_str = cluster_data.decode()
                    else:
                        cluster_str = str(cluster_data)
                    tenant_id_str, zoom_str, cluster_id_str = cluster_str.split(":")
                    clusters[uuid.UUID(tenant_id_str)][int(zoom_str)].add(
                        uuid.UUID(cluster_id_str)
                    )
                except:  # noqa: E722
                    logger.exception(
                        "Invalid cluster reference", cluster_str=cluster_str
                    )
            if not clusters:
                break

            for tenant_id, cluster_ids in clusters.items():
                try:
                    await self.update_tenant_clusters_centroid(tenant_id, cluster_ids)
                except:  # noqa: E722
                    logger.exception(
                        "Failed to define tenant clusters centroid",
                        tenant_id=str(tenant_id),
                        cluster_ids=str(cluster_ids),
                    )
                    await self._register_update_of_clusters_centroid(
                        tenant_id, cluster_ids
                    )

    async def update_tenant_clusters_centroid(
        self, tenant_id: uuid.UUID, cluster_ids: dict[int, set[uuid.UUID]] | None = None
    ) -> None:
        # No need to lock clustering, this don't need to be precise centroid information
        queries = []
        if cluster_ids:
            for zoom, ids in cluster_ids.items():
                stmt = (
                    select(  # type: ignore
                        self.cluster_model.id,
                        func.ST_Centroid(
                            func.ST_Multi(func.ST_Union(self.model.geom))
                        ).label("centroid"),
                    )
                    .join_from(
                        self.cluster_model,
                        self.model,
                        onclause=self.clustering_id_column(zoom)
                        == self.cluster_model.id,
                    )
                    .where(self.cluster_model.zoom == zoom)
                    .where(col(self.cluster_model.id).in_(ids))
                    .group_by(self.cluster_model.id)
                )
                queries.append(self.set_valid_statement(stmt, tenant_id))
        else:
            for zoom in range(self.max_zoom + 1):
                stmt = (
                    select(  # type: ignore
                        self.cluster_model.id,
                        func.ST_Centroid(
                            func.ST_Multi(func.ST_Union(self.model.geom))
                        ).label("centroid"),
                    )
                    .join_from(
                        self.cluster_model,
                        self.model,
                        onclause=self.clustering_id_column(zoom)
                        == self.cluster_model.id,
                    )
                    .where(self.cluster_model.zoom == zoom)
                    .group_by(self.cluster_model.id)
                )
                queries.append(self.set_valid_statement(stmt, tenant_id))

        zoom_stmt = union_all(*queries).alias()
        update_stmt = (
            update(self.cluster_model)
            .where(self.cluster_model.id == zoom_stmt.c.id)
            .values({"geom_centroid": zoom_stmt.c.centroid})
        )
        await self.session.execute(
            update_stmt, execution_options={"synchronize_session": False}
        )

    def with_clustering(self, tile_box: tuple[int, int, int]) -> bool:
        return tile_box[0] <= self.max_zoom

    def tile_geom_column(self, tile_box: tuple[int, int, int], geom_column: Any) -> Any:
        return func.ST_AsMVTGeom(
            func.ST_Transform(geom_column, settings.MAPBOX_SRID),
            func.TileBBox(*tile_box, settings.MAPBOX_SRID),
        ).label("geom")

    def clustering_id_column(self, zoom: int) -> Any:
        return getattr(func, f"clustering_{zoom}")(self.model.clustering)

    async def get_clusters(
        self,
        tile_box: tuple[int, int, int],
        tenant_id: uuid.UUID | None = None,
    ) -> dict[uuid.UUID, Coordinates]:
        if not self.with_clustering(tile_box):
            return {}

        cluster_statement = select(
            self.cluster_model.id,
            self.tile_geom_column(tile_box, self.cluster_model.geom_centroid),
        ).where(
            self.cluster_model.zoom == tile_box[0],
            func.ST_Intersects(
                func.TileBBox(*tile_box, settings.DEFAULT_SRID),
                self.cluster_model.geom_centroid,
            ),
        )
        if tenant_id:
            cluster_statement = cluster_statement.where(
                self.cluster_model.tenant_id == tenant_id
            )

        return {
            cluster_id: point_hex_to_tile(geom_hex)
            for cluster_id, geom_hex in (
                await self.session.exec(cluster_statement)
            ).all()
        }

    def build_tile(self, name: str) -> BuildTile:
        return BuildTile(name)

    async def _find_db_clusters(
        self,
        tenant_id: uuid.UUID,
        *models_items: Iterable[ClusteringObjectModelBase],
    ) -> AsyncGenerator[tuple[ClusteringModelBase, list[Any]], None]:
        """Check if model intersect any existing cluster"""

        data = [(i.id, i.geom) for models in models_items for i in models]
        if data:
            for block_data in iter_by_step(MAX_POSTGRES_PARAMS, data):
                values = Values(
                    column("id", self.model_id_db_type),
                    column("geom", PointColumn),
                    name="points",
                )
                values_stmt = select(values.data(block_data)).cte("points")  # type: ignore
                cluster_stmt = (
                    select(self.cluster_model.id, values_stmt.c.id.label("model_id"))
                    .distinct(values_stmt.c.id, self.cluster_model.zoom)
                    .join_from(
                        self.cluster_model,
                        values_stmt,
                        onclause=func.ST_Intersects(
                            self.cluster_model.geom,
                            func.cast(values_stmt.c.geom, PointColumn),
                        ),
                    )
                    .where(self.cluster_model.tenant_id == tenant_id)
                    .order_by(
                        values_stmt.c.id,
                        self.cluster_model.zoom,
                        func.ST_Distance(
                            func.ST_Centroid(self.cluster_model.geom),
                            func.cast(values_stmt.c.geom, PointColumn),
                        ),
                    )
                ).alias()

                stmt = (
                    select(  # type: ignore
                        self.cluster_model,
                        func.array_agg(cluster_stmt.c.model_id).label("model_ids"),
                    )
                    .where(self.cluster_model.id == cluster_stmt.c.id)
                    .group_by(self.cluster_model.id)
                )
                # TODO
                # this is a slow query as is taking half of clustering calculation time
                # check if is slow on stage/prod db (more power?), if not, try to improve it
                for cluster, model_ids in (await self.session.execute(stmt)).all():
                    yield cluster, model_ids

    async def _add_with_lock(
        self,
        tenant_id: uuid.UUID,
        *models_items: Iterable[ClusteringObjectModelBase],
    ) -> None:
        start = time()
        postpone: PostponeClustering | None = None
        for block_models in iter_by_step(self.batch_size, *models_items):
            try:
                async with self._with_lock(tenant_id):
                    postpone = await self._add(
                        tenant_id, block_models, postpone=postpone
                    )
            except LockError:
                logger.critical(
                    "Failed to lock clustering, failed to update clustering, please run 'clustering check-empty' CLI",
                    lock_name=self._build_lock_name(tenant_id),
                    waited_for=round(time() - start, 4),
                    tenant_id=str(tenant_id),
                    model_ids=str([i.id for i in block_models]),
                )
                # Let clear all clustering so it can be fixed on check-empty CLI
                self._clear_models(block_models)

        if postpone:
            await self._run_postpone(tenant_id, postpone)

    async def _add(
        self,
        tenant_id: uuid.UUID,
        models: Iterable[ClusteringObjectModelBase],
        postpone: PostponeClustering | None = None,
    ) -> PostponeClustering:
        new_clustering = NewClustering(self.max_zoom)
        new_clustering.add_models(models)

        # We need to postpone some models clustering build because we are working with locked models.
        # Lock works as, first lock models using DB, then lock tenant clustering using redis, and to avoid deadlocks,
        # we need to finish current calculations (unlock tenant clustering lock)
        # then lock models and then lock tenant clustering to finaly calculate clustering on missing models
        postpone = postpone or PostponeClustering()

        if not new_clustering.with_items():
            return postpone

        # Check db for existing clusters
        async for db_cluster, model_ids in self._find_db_clusters(tenant_id, models):
            new_clustering.set_cluster(db_cluster, model_ids)

        # Do in memory calculation of clusters
        # Start on max zoom and go one by one until zoom 0
        for zoom in range(self.max_zoom, -1, -1):
            missing_model_ids = new_clustering.all_ids()
            while missing_model_ids:
                model_id = missing_model_ids.pop()
                cluster_model_ids: list[Any] = [model_id]

                # We could have a cluster already defined (from _find_db_clusters)
                # if yes, no need to check, just merge into the same reference
                cluster = new_clustering.find(zoom, model_id)
                if cluster:
                    # Try to find more models in same cluster already defined by _find_db_clusters
                    to_merge = new_clustering.matching(cluster, missing_model_ids)
                    if to_merge:
                        cluster_model_ids.extend(to_merge)
                        missing_model_ids.difference_update(to_merge)

                # Find clusters on local/memory points
                geom_centroid, geom_buffer = new_clustering.get_buffer(
                    self.radius, zoom, model_id, cluster
                )
                to_merge = new_clustering.intersects(
                    zoom, geom_buffer, missing_model_ids
                )
                if to_merge:
                    cluster_model_ids.extend(to_merge)
                    missing_model_ids.difference_update(to_merge)

                # Create cluster if new
                if not cluster and len(cluster_model_ids) > 1:
                    cluster = self.cluster_model(
                        zoom=zoom,
                        geom=geom_buffer,
                        geom_centroid=geom_centroid,
                        tenant_id=tenant_id,
                    )
                    self.session.add(cluster)
                    postpone.add_cluster(cluster)

                if cluster:
                    # Make sure all have same cluster
                    new_clustering.set_cluster(cluster, cluster_model_ids)
                else:
                    # Check later if we have other db models that could create a cluster
                    postpone.add_model_without_cluster(
                        zoom, model_id, new_clustering.get_geom(model_id)
                    )

        # Define new clustering on sqlalchemy models to be updated
        for model in models:
            new_model_clustering = new_clustering.get(model.id)
            if new_model_clustering != model.clustering:
                model.clustering = new_model_clustering
                self.session.add(model)

        return postpone

    async def _fetch_postpone(
        self,
        tenant_id: uuid.UUID,
        postpone: PostponeClustering,
    ) -> tuple[
        set[Any], list["ModelOnCluster"], defaultdict[tuple[int, Any], dict[Any, Point]]
    ]:
        lock_model_ids: set[Any] = set()
        cluster_models: list[ModelOnCluster] = []
        model_models: list[ModelOnModel] = []

        # Find loose models on db for new clusters
        if postpone.clusters:
            cluster_models = await self._find_db_models_for_clusters(
                tenant_id, postpone.clusters
            )
            for cluster_model in cluster_models:
                lock_model_ids.add(cluster_model.model_id)

        # Find loose models on db for new models
        values = postpone.build_values(self.radius)
        model_clusters: defaultdict[tuple[int, Any], dict[Any, Point]] = defaultdict(
            dict
        )
        if values:
            model_models = await self._find_db_models_for_models(tenant_id, values)
            for model_model in model_models:
                lock_model_ids.add(model_model.id)
                lock_model_ids.add(model_model.model_id)
                model_clusters[(model_model.zoom, model_model.id)][
                    model_model.model_id
                ] = model_model.model_geom

        return lock_model_ids, cluster_models, model_clusters

    async def _do_postpone(
        self,
        tenant_id: uuid.UUID,
        models: dict[Any, ClusteringObjectModelBase],
        cluster_models: list["ModelOnCluster"],
        model_clusters: dict[tuple[int, Any], dict[Any, Point]],
    ) -> None:
        new_clustering: dict[Any, list[uuid.UUID | None]] = {}

        for cluster_model in cluster_models:
            # If geom changed on model, ignore clustering update
            # probably, it was already updated in another action, just ignore here
            model = models.get(cluster_model.model_id)
            if model and model.geom == cluster_model.model_geom:
                if model.id not in new_clustering:
                    # needs to be copied to be catch on sqlalchemy update
                    new_clustering[model.id] = self._copy_and_set_clustering(
                        model.clustering
                    )
                new_clustering[model.id][cluster_model.zoom] = cluster_model.id

        for (zoom, local_model_id), models_data in model_clusters.items():
            zoom_clustering = [
                model_id
                for model_id, model_geom in models_data.items()
                if (
                    # If geom changed on model, ignore clustering update
                    # probably, it was already updated in another action, just ignore here
                    models.get(model_id)
                    and models[model_id].geom == model_geom
                    # Ignore if was added on cluster_models
                    and zoom not in new_clustering.get(model_id, [])
                )
            ]
            if zoom_clustering:
                zoom_clustering.append(local_model_id)
                local_model = models[local_model_id]
                new_cluster = self.cluster_model(
                    zoom=zoom,
                    tenant_id=tenant_id,
                    geom=NewClustering.build_buffer(
                        zoom, local_model.geom, self.radius
                    ),
                    geom_centroid=local_model.geom,
                )
                self.session.add(new_cluster)
                for model_id in zoom_clustering:
                    if model_id not in new_clustering:
                        # needs to be copied to be catch on sqlalchemy update
                        new_clustering[model_id] = self._copy_and_set_clustering(
                            models[model_id].clustering
                        )
                    new_clustering[model_id][new_cluster.zoom] = new_cluster.id

        for model_id, clustering in new_clustering.items():
            model = models[model_id]
            model.clustering = clustering
            self.session.add(model)

    async def _run_postpone(
        self,
        tenant_id: uuid.UUID,
        postpone: PostponeClustering,
    ) -> None:
        # Flush any sqlalchemy change to make sure new clustering is updated for models
        await self.session.flush()

        lock_model_ids, cluster_models, model_clusters = await self._fetch_postpone(
            tenant_id, postpone
        )
        if lock_model_ids:
            # Lock models
            models = {i.id: i for i in await self._lock_db_models(lock_model_ids)}

            async with self._with_lock(tenant_id):
                await self._do_postpone(
                    tenant_id, models, cluster_models, model_clusters
                )

    def _copy_and_set_clustering(
        self, clustering: list[uuid.UUID | None]
    ) -> list[uuid.UUID | None]:
        size = self.max_zoom + 1
        if not clustering:
            return [None] * size

        clustering = list(clustering)
        if len(clustering) < size:
            clustering.extend(None for _ in range(size - len(clustering)))
        return clustering

    def _clear_models(
        self,
        *models_items: Iterable[ClusteringObjectModelBase],
    ) -> None:
        for models in models_items:
            for model in models:
                model.clustering = []
                self.session.add(model)

    async def _check_clusters(
        self,
        cluster_ids: defaultdict[int, set[uuid.UUID]],
    ) -> None:
        if not cluster_ids:
            return None

        # Remove clusters with single entry or without entries
        delete_cluster_ids: set[uuid.UUID] = set()
        clear_zoom: defaultdict[int, list[uuid.UUID]] = defaultdict(list)

        queries = []
        current_params = 0
        cluster_ids = cluster_ids.copy()
        while cluster_ids:
            zoom, ids = cluster_ids.popitem()

            if (len(ids) + current_params) > MAX_POSTGRES_PARAMS:
                position = MAX_POSTGRES_PARAMS - current_params
                ids_list = list(ids)
                ids = set(ids_list[:position])
                cluster_ids[zoom] = set(ids_list[position:])

            current_params += len(ids)
            delete_cluster_ids.update(ids)
            clustering_column = self.clustering_id_column(zoom)
            queries.append(
                select(  # type: ignore
                    literal(zoom).label("zoom"),
                    clustering_column.label("cluster_id"),
                    func.count(self.model.id).label("length"),
                )
                .where(clustering_column.in_(ids))
                .group_by(clustering_column)
            )

            if queries and (not cluster_ids or current_params >= MAX_POSTGRES_PARAMS):
                for zoom, cluster_id, length in (
                    await self.session.execute(union_all(*queries))
                ).all():
                    if length == 1:
                        clear_zoom[zoom].append(cluster_id)
                    else:
                        delete_cluster_ids.discard(cluster_id)

                current_params = 0
                queries.clear()

        if clear_zoom:
            for zoom, zoom_cluster_ids in clear_zoom.items():
                update_stmt = text(
                    f"UPDATE {self.model.__tablename__} SET clustering[{zoom + 1}] = NULL WHERE array[clustering_{zoom}(clustering)] && :ids"
                )
                connection = await self.session.connection()
                await connection.execute(
                    update_stmt, parameters={"ids": zoom_cluster_ids}
                )
            logger.info("Removed single entry clusters", cluster_ids=dict(clear_zoom))
        if delete_cluster_ids:
            await self.session.execute(
                delete(self.cluster_model).where(
                    col(self.cluster_model.id).in_(delete_cluster_ids)
                )
            )
            logger.info("Deleted empty clusters", cluster_ids=list(clear_zoom))

    async def _find_db_models_for_clusters(
        self,
        tenant_id: uuid.UUID,
        clusters: dict[int, list[uuid.UUID]],
    ) -> list["ModelOnCluster"]:
        """Check if cluster intersect any existing model (without cluster)"""

        result: list["ModelOnCluster"] = []

        queries = []
        current_params = 0
        clusters = clusters.copy()
        while clusters:
            zoom, ids = clusters.popitem()

            if (len(ids) + current_params) > MAX_POSTGRES_PARAMS:
                position = MAX_POSTGRES_PARAMS - current_params
                ids_list = list(ids)
                ids = ids_list[:position]
                clusters[zoom] = ids_list[position:]

            stmt = (
                select(  # type: ignore
                    self.cluster_model.id,
                    self.cluster_model.zoom,
                    col(self.model.id).label("model_id"),
                    col(self.model.geom).label("model_geom"),
                )
                .join_from(
                    self.cluster_model,
                    self.model,
                    onclause=func.ST_Intersects(
                        self.cluster_model.geom, self.model.geom
                    ),
                )
                .where(col(self.cluster_model.id).in_(ids))
                .where(self.clustering_id_column(zoom).is_(None))
            )
            queries.append(self.set_valid_statement(stmt, tenant_id))

            if queries and (not clusters or current_params >= MAX_POSTGRES_PARAMS):
                result.extend((await self.session.execute(union_all(*queries))).all())  # type: ignore
                current_params = 0
                queries.clear()

        return result

    async def _find_db_models_for_models(
        self,
        tenant_id: uuid.UUID,
        data: list[tuple[int, Any, Polygon]],
    ) -> list["ModelOnModel"]:
        """Check if model intersect any existing model (without cluster)"""

        result: list[ModelOnModel] = []
        for block_data in iter_by_step(MAX_POSTGRES_PARAMS, data):
            sql_values = Values(
                column("zoom", Integer),
                column("id", self.model_id_db_type),
                column("geom", PolygonColumn),
                name="points",
            )
            values = select(sql_values.data(block_data)).cte("points")  # type: ignore

            queries = []
            for zoom in {i[0] for i in block_data}:
                stmt = (
                    select(  # type: ignore
                        values.c.zoom,
                        values.c.id,
                        col(self.model.id).label("model_id"),
                        col(self.model.geom).label("model_geom"),
                    )
                    .join_from(
                        self.model,
                        values,
                        onclause=func.ST_Intersects(
                            self.model.geom, func.cast(values.c.geom, PolygonColumn)
                        ),
                    )
                    .where(self.clustering_id_column(zoom).is_(None))
                    .where(self.model.id != values.c.id)
                    .where(values.c.zoom == zoom)
                )
                queries.append(self.set_valid_statement(stmt, tenant_id))

            result.extend((await self.session.execute(union_all(*queries))).all())  # type: ignore

        return result

    async def _lock_db_models(
        self, ids: Iterable[Any]
    ) -> list[ClusteringObjectModelBase]:
        result: list[ClusteringObjectModelBase] = []
        for block_ids in iter_by_step(MAX_POSTGRES_PARAMS, ids):
            stmt = (
                select(self.model)
                .where(col(self.model.id).in_(block_ids))
                .with_for_update()
            )
            stmt = self.set_valid_statement(stmt, None)
            result.extend((await self.session.exec(stmt)).all())
        return result

    async def _iter_and_lock_all_db_models(
        self, tenant_id: uuid.UUID, step: int
    ) -> AsyncGenerator[list[ClusteringObjectModelBase], None]:
        stmt = self.set_valid_statement(select(self.model.id), tenant_id)
        model_ids = (await self.session.exec(stmt)).all()
        for block_ids in iter_by_step(self.batch_size, model_ids):
            yield await self._lock_db_models(block_ids)

        # Check if new models was been added
        new_model_ids = set((await self.session.exec(stmt)).all())
        new_model_ids.difference_update(model_ids)
        if new_model_ids:
            for block_ids in iter_by_step(step, model_ids):
                yield await self._lock_db_models(block_ids)

    def _extract_clustering_ids(
        self,
        *models_items: Iterable[ClusteringObjectModelBase],
        ref: defaultdict[int, set[uuid.UUID]] | None = None,
    ) -> defaultdict[int, set[uuid.UUID]]:
        if ref is None:
            ref = defaultdict(set)

        for models in models_items:
            for model in models:
                for zoom, cluster_id in enumerate(model.clustering):
                    if cluster_id:
                        ref[zoom].add(cluster_id)

        return ref

    def _build_lock_name(self, tenant_id: uuid.UUID) -> str:
        return f"clustering:{self.cluster_model.__tablename__}:{tenant_id}"

    def _with_lock(self, tenant_id: uuid.UUID) -> Lock:
        name = self._build_lock_name(tenant_id)
        # Always create a new LockWithStats because of lock_started_at
        return LockWithStats(
            self.redis_client,
            name=name,
            timeout=self.default_lock_timeout,
            blocking_timeout=self.default_blocking_timeout,
        )


class ModelOnCluster(NamedTuple):
    id: uuid.UUID
    zoom: int
    model_id: Any
    model_geom: Point


class ModelOnModel(NamedTuple):
    zoom: int
    id: Any
    model_id: Any
    model_geom: Point


class LockWithStats(Lock):
    lock_started_at: float | None = None

    async def acquire(self, *args: Any, **kwargs: Any) -> Any:
        with Stats("clustering_lock_acquire"):
            result = await super().acquire(*args, **kwargs)

        self.lock_started_at = time()
        return result

    async def do_release(self, *args: Any, **kwargs: Any) -> None:
        await super().do_release(*args, **kwargs)
        if self.lock_started_at:
            Stats.inc("clustering_locked", time() - self.lock_started_at)
