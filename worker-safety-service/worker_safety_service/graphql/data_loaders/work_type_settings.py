import uuid
from typing import List, Optional, Tuple

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.activity_work_type_settings import (
    ActivityWorkTypeSettingsManager,
)
from worker_safety_service.models import WorkType


class ActivityWorkTypesSettingsLoader:
    def __init__(
        self,
        manager: ActivityWorkTypeSettingsManager,
    ):
        self.__manager = manager
        self.get_activity_aliases = DataLoader(load_fn=self.load_activity_aliases)
        self.get_work_types_and_aliases_by_work_types = DataLoader(
            load_fn=self.load_work_types_and_aliases_by_work_types
        )

    async def load_activity_aliases(
        self, keys: List[Tuple[uuid.UUID, tuple]]
    ) -> List[List[Optional[str]]]:
        results = []
        for key in keys:
            activity_id, work_type_ids_tuple = key
            work_type_ids = list(work_type_ids_tuple)
            alias = await self.__manager.get_activity_aliases(
                activity_id, work_type_ids
            )
            results.append(alias)
        return results

    async def load_work_types_and_aliases_by_work_types(
        self, keys: List[Tuple[uuid.UUID, uuid.UUID, Optional[uuid.UUID]]]
    ) -> List[dict[uuid.UUID, list[tuple["WorkType", Optional[str]]]]]:
        """
        keys: List of (work_type_id, library_activity_group_id, tenant_id)
        Returns: List of dicts mapping work_type_id to list of (WorkType, alias) tuples
        """
        results = []
        for (
            work_type_id,
            library_activity_group_id,
            tenant_id,
        ) in keys:  # Renamed variable
            data = await self.__manager.get_work_types_and_aliases_by_work_types(  # Call new manager method
                [work_type_id],  # Pass as a list, as the manager expects a list
                library_activity_group_id,
                tenant_id,
            )
            results.append(data)
        return results
