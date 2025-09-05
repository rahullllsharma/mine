import functools
import uuid
from typing import List, Tuple

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.library import LibraryFilterType, LibraryManager
from worker_safety_service.dal.library_tasks import LibraryTasksManager
from worker_safety_service.dal.work_types import WorkTypeManager
from worker_safety_service.graphql.data_loaders.utils import create_order_by_hash
from worker_safety_service.models import (
    LibraryControl,
    LibraryHazard,
    LibraryTaskLibraryHazardLink,
)
from worker_safety_service.models.library import (  # LibrarySiteCondition,
    LibraryActivityGroup,
    LibraryActivityType,
    LibraryAssetType,
    LibraryDivision,
    LibraryProjectType,
    LibraryRegion,
    LibraryTask,
    LocationHazardControlSettings,
    LocationHazardControlSettingsCreate,
    WorkType,
)
from worker_safety_service.types import OrderBy


class LibraryLoader:
    """
    Data loaders for library objects
    """

    def __init__(
        self,
        manager: LibraryManager,
        library_tasks_manager: LibraryTasksManager,
        work_type_manager: WorkTypeManager,
        tenant_id: uuid.UUID,
    ):
        self.__manager = manager
        self.__library_tasks_manager = library_tasks_manager
        self.__work_types_manager = work_type_manager
        self.__task_hazards_map: dict[int | None, DataLoader] = {}
        self.__site_conditions_hazards_map: dict[int | None, DataLoader] = {}
        self.__task_controls_map: dict[int | None, DataLoader] = {}
        self.__site_condition_controls_map: dict[int | None, DataLoader] = {}
        self.__tasks_by_activity_group_map: dict[int | None, DataLoader] = {}
        self.regions = DataLoader(load_fn=self.load_regions)
        self.divisions = DataLoader(load_fn=self.load_divisions)
        self.project_types = DataLoader(load_fn=self.load_project_types)
        self.asset_types = DataLoader(load_fn=self.load_asset_types)
        self.activity_types = DataLoader(load_fn=self.load_activity_types)
        self.tenant_id = tenant_id
        self.activity_groups_by_library_task = DataLoader(
            load_fn=self.load_activity_groups_by_library_task
        )
        self.work_type_linked_activity_groups_by_library_task = DataLoader(
            load_fn=self.load_work_type_linked_activity_groups_by_library_task
        )
        self.work_types_by_library_task = DataLoader(
            load_fn=self.load_work_types_by_library_task
        )
        self.work_types_by_library_site_condition = DataLoader(
            load_fn=self.load_work_types_by_library_site_condition
        )
        self.work_types = DataLoader(load_fn=self.load_work_types)
        self.task_applicability_levels = DataLoader(
            load_fn=self.load_task_applicability_levels
        )

    def task_hazards(self, order_by: list[OrderBy] | None = None) -> DataLoader:
        key = create_order_by_hash(order_by)
        dataloader = self.__task_hazards_map.get(key)
        if not dataloader:
            dataloader = self.__task_hazards_map[key] = DataLoader(
                load_fn=functools.partial(
                    self.load_hazards, LibraryFilterType.TASK, order_by=order_by
                )
            )
        return dataloader

    def task_hazards_v2(self, order_by: list[OrderBy] | None = None) -> DataLoader:
        key = create_order_by_hash(order_by)
        dataloader = self.__task_hazards_map.get(key)
        if not dataloader:
            dataloader = self.__task_hazards_map[key] = DataLoader(
                load_fn=functools.partial(
                    self.load_hazards_v2, LibraryFilterType.TASK, order_by=order_by
                )
            )
        return dataloader

    def site_conditions_hazards(
        self, order_by: list[OrderBy] | None = None
    ) -> DataLoader:
        key = create_order_by_hash(order_by)
        dataloader = self.__site_conditions_hazards_map.get(key)
        if not dataloader:
            dataloader = self.__site_conditions_hazards_map[key] = DataLoader(
                load_fn=functools.partial(
                    self.load_hazards,
                    LibraryFilterType.SITE_CONDITION,
                    order_by=order_by,
                )
            )
        return dataloader

    def site_conditions_hazards_v2(
        self, order_by: list[OrderBy] | None = None
    ) -> DataLoader:
        key = create_order_by_hash(order_by)
        dataloader = self.__site_conditions_hazards_map.get(key)
        if not dataloader:
            dataloader = self.__site_conditions_hazards_map[key] = DataLoader(
                load_fn=functools.partial(
                    self.load_hazards_v2,
                    LibraryFilterType.SITE_CONDITION,
                    order_by=order_by,
                )
            )
        return dataloader

    async def load_hazards(
        self,
        type_key: LibraryFilterType,
        library_type_ids: list[uuid.UUID],
        order_by: list[OrderBy] | None = None,
    ) -> list[list[LibraryHazard]]:
        return await self.__manager.load_hazards(
            type_key=type_key,
            library_type_ids=library_type_ids,
            order_by=order_by,
        )

    async def load_hazards_v2(
        self,
        type_key: LibraryFilterType,
        library_type_ids: list[uuid.UUID],
        order_by: list[OrderBy] | None = None,
    ) -> list[list[LibraryHazard]]:
        return await self.__manager.load_hazards_v2(
            type_key=type_key,
            library_type_ids=library_type_ids,
            order_by=order_by,
            tenant_id=self.tenant_id,
        )

    def task_controls(self, order_by: list[OrderBy] | None = None) -> DataLoader:
        key = create_order_by_hash(order_by)
        dataloader = self.__task_controls_map.get(key)
        if not dataloader:
            dataloader = self.__task_controls_map[key] = DataLoader(
                load_fn=functools.partial(
                    self.load_controls, LibraryFilterType.TASK, order_by=order_by
                )
            )
        return dataloader

    def task_controls_v2(self, order_by: list[OrderBy] | None = None) -> DataLoader:
        key = create_order_by_hash(order_by)
        dataloader = self.__task_controls_map.get(key)
        if not dataloader:
            dataloader = self.__task_controls_map[key] = DataLoader(
                load_fn=functools.partial(
                    self.load_controls_v2, LibraryFilterType.TASK, order_by=order_by
                )
            )
        return dataloader

    def site_condition_controls(
        self, order_by: list[OrderBy] | None = None
    ) -> DataLoader:
        key = create_order_by_hash(order_by)
        dataloader = self.__site_condition_controls_map.get(key)
        if not dataloader:
            dataloader = self.__site_condition_controls_map[key] = DataLoader(
                load_fn=functools.partial(
                    self.load_controls,
                    LibraryFilterType.SITE_CONDITION,
                    order_by=order_by,
                )
            )
        return dataloader

    def site_condition_controls_v2(
        self, order_by: list[OrderBy] | None = None
    ) -> DataLoader:
        key = create_order_by_hash(order_by)
        dataloader = self.__site_condition_controls_map.get(key)
        if not dataloader:
            dataloader = self.__site_condition_controls_map[key] = DataLoader(
                load_fn=functools.partial(
                    self.load_controls_v2,
                    LibraryFilterType.SITE_CONDITION,
                    order_by=order_by,
                )
            )
        return dataloader

    async def load_controls(
        self,
        type_key: LibraryFilterType,
        library_hazard_ids: list[tuple[uuid.UUID | None, uuid.UUID]],
        order_by: list[OrderBy] | None = None,
    ) -> list[list[LibraryControl]]:
        """`library_hazard_ids` with `(library_parent_id, library_hazard_id)`"""
        return await self.__manager.load_controls(
            type_key=type_key,
            library_hazard_ids=library_hazard_ids,
            order_by=order_by,
        )

    async def load_controls_v2(
        self,
        type_key: LibraryFilterType,
        library_hazard_ids: list[tuple[uuid.UUID | None, uuid.UUID]],
        order_by: list[OrderBy] | None = None,
    ) -> list[list[LibraryControl]]:
        """`library_hazard_ids` with `(library_parent_id, library_hazard_id)`"""
        return await self.__manager.load_controls_v2(
            tenant_id=self.tenant_id,
            type_key=type_key,
            library_hazard_ids=library_hazard_ids,
            order_by=order_by,
        )

    async def load_activity_groups_by_library_task(
        self, library_task_ids: list[uuid.UUID]
    ) -> list[list[LibraryActivityGroup | None] | None]:
        activity_groups = await self.__manager.get_activity_groups_by_library_task(
            library_task_ids
        )
        return [activity_groups.get(i) for i in library_task_ids]

    async def load_work_type_linked_activity_groups_by_library_task(
        self, keys: List[Tuple[uuid.UUID, tuple]]
    ) -> list[list[LibraryActivityGroup | None] | None]:
        library_task_ids = []
        work_type_ids = []
        # TODO: Needs to be optimized
        for key in keys:
            library_task_id, work_type_ids_tuple = key
            work_type_ids = list(work_type_ids_tuple)
            library_task_ids.append(library_task_id)
        activity_groups = await self.__manager.get_activity_groups_by_library_task(
            library_task_ids, work_type_ids
        )
        return [activity_groups.get(i) for i in library_task_ids]

    async def load_work_types_by_library_task(
        self, library_task_ids: list[uuid.UUID]
    ) -> list[list[WorkType | None] | None]:
        worktypes = await self.__manager.get_work_types_by_library_task(
            library_task_ids, self.tenant_id
        )
        return [worktypes.get(i) for i in library_task_ids]

    async def load_work_types_by_library_site_condition(
        self, library_site_condition_ids: list[uuid.UUID]
    ) -> list[list[WorkType | None] | None]:
        worktypes = await self.__manager.get_work_types_by_library_site_condition(
            library_site_condition_ids, self.tenant_id
        )
        return [worktypes.get(i) for i in library_site_condition_ids]

    async def load_work_types(
        self, work_type_ids: list[uuid.UUID]
    ) -> list[WorkType | None]:
        # TODO: I'm not really sure why this is not guarded by tenant id but I'll kee it that way for now.
        inv_idx = {_id: pos for pos, _id in enumerate(work_type_ids)}
        ret: list[WorkType | None] = [None] * len(work_type_ids)
        res = await self.__work_types_manager.get_work_types(ids=work_type_ids)
        for work_type in res:
            ret[inv_idx[work_type.id]] = work_type

        return ret

    def tasks_by_activity_group(
        self, order_by: list[OrderBy] | None = None
    ) -> DataLoader:
        key = create_order_by_hash(order_by)
        dataloader = self.__tasks_by_activity_group_map.get(key)
        if not dataloader:
            dataloader = self.__tasks_by_activity_group_map[key] = DataLoader(
                load_fn=functools.partial(
                    self.load_tasks_by_activity_group,
                    order_by=order_by,
                )
            )
        return dataloader

    async def load_tasks_by_activity_group(
        self,
        activity_groups_ids: list[uuid.UUID],
        order_by: list[OrderBy] | None = None,
    ) -> list[list[LibraryTask]]:
        items = (
            await self.__library_tasks_manager.get_library_tasks_by_activity_group_id(
                activity_groups_ids, order_by=order_by, tenant_id=self.tenant_id
            )
        )
        return [items.get(i) or [] for i in activity_groups_ids]

    async def get_hazards(
        self,
        type_key: LibraryFilterType,
        id: uuid.UUID | None = None,
        library_task_id: uuid.UUID | None = None,
        library_site_condition_id: uuid.UUID | None = None,
        order_by: list[OrderBy] | None = None,
    ) -> list[LibraryHazard]:
        return await self.__manager.get_hazards(
            type_key=type_key,
            id=id,
            library_task_id=library_task_id,
            library_site_condition_id=library_site_condition_id,
            order_by=order_by,
        )

    async def get_hazards_v2(
        self,
        type_key: LibraryFilterType | None = None,
        id: uuid.UUID | None = None,
        library_task_id: uuid.UUID | None = None,
        library_site_condition_id: uuid.UUID | None = None,
        order_by: list[OrderBy] | None = None,
        allow_archived: bool = False,
    ) -> list[LibraryHazard]:
        return await self.__manager.get_hazards_v2(
            type_key=type_key,
            id=id,
            library_task_id=library_task_id,
            library_site_condition_id=library_site_condition_id,
            order_by=order_by,
            tenant_id=self.tenant_id,
            allow_archived=allow_archived,
        )

    async def get_controls(
        self,
        type_key: LibraryFilterType | None,
        id: uuid.UUID | None = None,
        library_hazard_id: uuid.UUID | None = None,
        library_task_id: uuid.UUID | None = None,
        library_site_condition_id: uuid.UUID | None = None,
        order_by: list[OrderBy] | None = None,
        allow_archived: bool = False,
    ) -> list[LibraryControl]:
        return await self.__manager.get_controls(
            type_key=type_key,
            id=id,
            library_hazard_id=library_hazard_id,
            library_task_id=library_task_id,
            library_site_condition_id=library_site_condition_id,
            order_by=order_by,
        )

    async def get_controls_v2(
        self,
        type_key: LibraryFilterType | None,
        id: uuid.UUID | None = None,
        library_hazard_id: uuid.UUID | None = None,
        library_task_id: uuid.UUID | None = None,
        library_site_condition_id: uuid.UUID | None = None,
        order_by: list[OrderBy] | None = None,
        allow_archived: bool = False,
    ) -> list[LibraryControl]:
        return await self.__manager.get_controls_v2(
            type_key=type_key,
            tenant_id=self.tenant_id,
            id=id,
            library_hazard_id=library_hazard_id,
            library_task_id=library_task_id,
            library_site_condition_id=library_site_condition_id,
            order_by=order_by,
            allow_archived=allow_archived,
        )

    async def get_regions(
        self, order_by: list[OrderBy] | None = None
    ) -> list[LibraryRegion]:
        return await self.__manager.get_regions(
            order_by=order_by, tenant_id=self.tenant_id
        )

    async def load_regions(
        self, library_region_ids: list[uuid.UUID]
    ) -> list[LibraryRegion | None]:
        items = await self.__manager.get_regions_by_id(library_region_ids)
        return [items.get(i) for i in library_region_ids]

    async def get_divisions(
        self, order_by: list[OrderBy] | None = None
    ) -> list[LibraryDivision]:
        return await self.__manager.get_divisions(
            order_by=order_by, tenant_id=self.tenant_id
        )

    async def load_divisions(
        self, library_division_ids: list[uuid.UUID]
    ) -> list[LibraryDivision | None]:
        items = await self.__manager.get_divisions_by_id(library_division_ids)
        return [items.get(i) for i in library_division_ids]

    async def get_project_types(
        self, order_by: list[OrderBy] | None = None
    ) -> list[LibraryProjectType]:
        return await self.__manager.get_project_types(order_by=order_by)

    async def load_project_types(
        self, library_project_type_ids: list[uuid.UUID]
    ) -> list[LibraryProjectType | None]:
        items = await self.__manager.get_project_types_by_id(library_project_type_ids)
        return [items.get(i) for i in library_project_type_ids]

    async def get_asset_types(
        self, order_by: list[OrderBy] | None = None
    ) -> list[LibraryAssetType]:
        return await self.__manager.get_asset_types(order_by=order_by)

    async def load_asset_types(
        self, library_asset_type_ids: list[uuid.UUID]
    ) -> list[LibraryAssetType | None]:
        items = await self.__manager.get_asset_types_by_id(library_asset_type_ids)
        return [items.get(i) for i in library_asset_type_ids]

    async def get_activity_types(
        self, order_by: list[OrderBy] | None = None
    ) -> list[LibraryActivityType]:
        return await self.__manager.get_activity_types(
            order_by=order_by, tenant_id=self.tenant_id
        )

    async def load_activity_types(
        self, ids: list[uuid.UUID]
    ) -> list[LibraryActivityType | None]:
        items = await self.__manager.get_activity_types_by_id(ids)
        return [items.get(i) for i in ids]

    async def get_activity_groups(
        self, order_by: list[OrderBy] | None = None
    ) -> list[LibraryActivityGroup]:
        return await self.__manager.get_activity_groups(
            order_by=order_by, tenant_id=self.tenant_id
        )

    async def add_location_hazard_control_settings(
        self,
        location_hazard_control_settings: list[LocationHazardControlSettingsCreate],
        user_id: uuid.UUID,
    ) -> None:
        return await self.__manager.create_location_hazard_control_setting(
            location_hazard_control_settings, self.tenant_id, user_id
        )

    async def remove_location_hazard_control_settings(
        self, location_hazard_control_setting_ids: list[uuid.UUID]
    ) -> None:
        return await self.__manager.delete_location_hazard_control_setting(
            self.tenant_id, location_hazard_control_setting_ids
        )

    async def get_location_hazard_control_settings(
        self, location_id: uuid.UUID
    ) -> list[LocationHazardControlSettings]:
        return await self.__manager.get_location_hazard_control_settings(location_id)

    async def load_task_applicability_levels(
        self,
        library_hazard_task_tuples: list[tuple[uuid.UUID, uuid.UUID | None]],
    ) -> list[list[LibraryTaskLibraryHazardLink]]:
        all_results = await self.__manager.get_task_applicability_levels(
            library_hazard_task_tuples
        )

        results_map: dict[tuple[uuid.UUID, uuid.UUID | None], list] = {
            (hazard_id, task_id if task_id else None): []
            for hazard_id, task_id in library_hazard_task_tuples
        }

        for item in all_results:
            key = (item.library_hazard_id, item.library_task_id)

            if key in results_map:
                results_map[key].append(item)
            elif item.library_task_id is not None:
                # If the exact key doesn't exist but the task ID is not None,
                # this means it's a result for the original tuple (hazard_id, None).
                hazard_only_key = (item.library_hazard_id, None)
                if hazard_only_key in results_map:
                    results_map[hazard_only_key].append(item)

        return [results_map[item] for item in library_hazard_task_tuples]
