import uuid
from typing import Any

from sqlmodel.sql.expression import col
from sqlmodel.sql.sqltypes import GUID

from worker_safety_service.clustering import ClusteringBase
from worker_safety_service.models import Location, LocationClusteringModel, WorkPackage


class LocationClustering(ClusteringBase):
    cluster_model = LocationClusteringModel
    model = Location
    model_id_db_type = GUID

    def set_valid_statement(self, statement: Any, tenant_id: uuid.UUID | None) -> Any:
        # TODO Fix bug in manually recreating clusters for tenant
        if tenant_id:
            statement = statement.join_from(
                Location, WorkPackage, onclause=Location.project_id == WorkPackage.id
            ).where(WorkPackage.tenant_id == tenant_id)

        return statement.where(col(Location.archived_at).is_(None))
