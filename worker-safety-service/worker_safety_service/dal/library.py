import enum
import re
import uuid
from collections import defaultdict
from collections.abc import Collection
from typing import Any, List, Optional, Type, TypeVar, Union

from sqlmodel import and_, col, delete, or_, select, update
from sqlmodel.sql.expression import SelectOfScalar

from worker_safety_service.dal.exceptions.data_not_found import DataNotFoundException
from worker_safety_service.dal.exceptions.entity_already_exists import (
    EntityAlreadyExistsException,
)
from worker_safety_service.models import (
    AsyncSession,
    LibraryActivityGroup,
    LibraryActivityType,
    LibraryActivityTypeTenantLink,
    LibraryAssetType,
    LibraryControl,
    LibraryDivision,
    LibraryDivisionTenantLink,
    LibraryHazard,
    LibraryProjectType,
    LibraryRegion,
    LibraryRegionTenantLink,
    LibrarySiteConditionRecommendations,
    LibraryTask,
    LibraryTaskActivityGroup,
    LibraryTaskLibraryHazardLink,
    LibraryTaskRecommendations,
    LocationHazardControlSettings,
    LocationHazardControlSettingsCreate,
    WorkType,
    WorkTypeLibrarySiteConditionLink,
    WorkTypeTaskLink,
    set_order_by,
)
from worker_safety_service.models.tenant_library_settings import (
    TenantLibraryControlSettings,
    TenantLibraryHazardSettings,
)
from worker_safety_service.models.work_type_settings import ActivityWorkTypeSettings
from worker_safety_service.types import OrderBy
from worker_safety_service.urbint_logging import get_logger

ERROR_MSG_PATTERN = r"duplicate key value violates unique constraint \"(\S+)\""
logger = get_logger(__name__)


@enum.unique
class LibraryFilterType(enum.Enum):
    TASK = "task"
    SITE_CONDITION = "site_condition"


T = TypeVar("T", bound=Union[LibraryHazard, LibraryControl])


class LibraryManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_task_recommendations(
        self, library_task_id: uuid.UUID, tenant_id: uuid.UUID | None = None
    ) -> list[LibraryTaskRecommendations]:
        statement = select(LibraryTaskRecommendations).where(
            LibraryTaskRecommendations.library_task_id == library_task_id
        )
        # NOTE: Below condition is part of CTL phase 1 changes. Adding note for reference.
        if tenant_id:
            statement = statement.join(
                TenantLibraryHazardSettings,
                onclause=TenantLibraryHazardSettings.library_hazard_id
                == LibraryTaskRecommendations.library_hazard_id,
            ).where(TenantLibraryHazardSettings.tenant_id == tenant_id)
        return (await self.session.exec(statement)).all()

    async def get_site_condition_recommendations(
        self,
        library_site_condition_ids: Collection[uuid.UUID],
        tenant_id: uuid.UUID | None = None,
    ) -> defaultdict[uuid.UUID, defaultdict[uuid.UUID, set[uuid.UUID]]]:
        statement = select(LibrarySiteConditionRecommendations).where(
            col(LibrarySiteConditionRecommendations.library_site_condition_id).in_(
                library_site_condition_ids
            )
        )
        # NOTE: Below condition is part of CTL phase 1 changes. Adding note for reference.
        if tenant_id:
            statement = statement.join(
                TenantLibraryHazardSettings,
                onclause=TenantLibraryHazardSettings.library_hazard_id
                == LibrarySiteConditionRecommendations.library_hazard_id,
            ).where(TenantLibraryHazardSettings.tenant_id == tenant_id)

        items: defaultdict[
            uuid.UUID, defaultdict[uuid.UUID, set[uuid.UUID]]
        ] = defaultdict(lambda: defaultdict(set))
        for item in (await self.session.exec(statement)).all():
            items[item.library_site_condition_id][item.library_hazard_id].add(
                item.library_control_id
            )
        return items

    async def get_hazards(
        self,
        type_key: LibraryFilterType | None = None,
        id: uuid.UUID | None = None,
        library_task_id: uuid.UUID | None = None,
        library_site_condition_id: uuid.UUID | None = None,
        order_by: list[OrderBy] | None = None,
    ) -> list[LibraryHazard]:
        """
        Retrieve library hazards
        """
        statement = select(LibraryHazard)

        if id:
            statement = statement.where(LibraryHazard.id == id)

        if type_key == LibraryFilterType.TASK:
            if library_task_id:
                statement = statement.where(
                    LibraryHazard.id == LibraryTaskRecommendations.library_hazard_id
                ).where(LibraryTaskRecommendations.library_task_id == library_task_id)
            else:
                statement = statement.where(col(LibraryHazard.for_tasks).is_(True))
        elif type_key == LibraryFilterType.SITE_CONDITION:
            statement = statement
            if library_site_condition_id:
                statement = statement.where(
                    LibraryHazard.id
                    == LibrarySiteConditionRecommendations.library_hazard_id
                ).where(
                    LibrarySiteConditionRecommendations.library_site_condition_id
                    == library_site_condition_id
                )
            else:
                statement = statement.where(
                    col(LibraryHazard.for_site_conditions).is_(True)
                )
        else:
            raise NotImplementedError(f"hazard type {type_key} not implemented")

        statement = statement.group_by(LibraryHazard.id)
        statement = set_order_by(LibraryHazard, statement, order_by=order_by)
        return (await self.session.exec(statement)).all()

    async def get_hazards_v2(
        self,
        type_key: LibraryFilterType | None = None,
        tenant_id: uuid.UUID | None = None,
        id: uuid.UUID | None = None,
        library_task_id: uuid.UUID | None = None,
        library_site_condition_id: uuid.UUID | None = None,
        order_by: list[OrderBy] | None = None,
        allow_archived: bool = False,
    ) -> list[LibraryHazard]:
        """
        Retrieve library hazards
        """
        statement = select(LibraryHazard)

        if id:
            return await self._execute_statement(
                statement=statement.where(LibraryHazard.id == id),
                order_by=order_by,
                model=LibraryHazard,
                allow_archived=allow_archived,
            )
        if not tenant_id:
            return []

        statement = self._apply_tenant_filter(
            statement=statement,
            tenant_id=tenant_id,
            model=LibraryHazard,
        )

        if type_key == LibraryFilterType.TASK:
            statement = self._apply_hazard_task_filter(
                statement=statement, library_task_id=library_task_id
            )
        elif type_key == LibraryFilterType.SITE_CONDITION:
            statement = self._apply_hazard_site_condition_filter(
                statement=statement, library_site_condition_id=library_site_condition_id
            )

        return await self._execute_statement(
            statement=statement,
            order_by=order_by,
            model=LibraryHazard,
            allow_archived=allow_archived,
        )

    def _apply_hazard_task_filter(
        self,
        statement: SelectOfScalar[LibraryHazard],
        library_task_id: uuid.UUID | None,
    ) -> SelectOfScalar[LibraryHazard]:
        if library_task_id:
            return statement.join(
                LibraryTaskRecommendations,
                LibraryHazard.id == LibraryTaskRecommendations.library_hazard_id,
            ).where(LibraryTaskRecommendations.library_task_id == library_task_id)
        return statement.where(col(LibraryHazard.for_tasks).is_(True))

    def _apply_hazard_site_condition_filter(
        self,
        statement: SelectOfScalar[LibraryHazard],
        library_site_condition_id: uuid.UUID | None,
    ) -> SelectOfScalar[LibraryHazard]:
        if library_site_condition_id:
            return statement.join(
                LibrarySiteConditionRecommendations,
                LibraryHazard.id
                == LibrarySiteConditionRecommendations.library_hazard_id,
            ).where(
                LibrarySiteConditionRecommendations.library_site_condition_id
                == library_site_condition_id
            )
        return statement.where(col(LibraryHazard.for_site_conditions).is_(True))

    def _apply_tenant_filter(
        self, statement: SelectOfScalar[T], tenant_id: uuid.UUID, model: type[T]
    ) -> SelectOfScalar[T]:
        settings_model: Union[
            type[TenantLibraryHazardSettings], type[TenantLibraryControlSettings]
        ]
        if model == LibraryHazard:
            settings_model = TenantLibraryHazardSettings
            id_column = TenantLibraryHazardSettings.library_hazard_id
        elif model == LibraryControl:
            settings_model = TenantLibraryControlSettings
            id_column = TenantLibraryControlSettings.library_control_id
        else:
            raise ValueError(f"Unsupported model type: {model}")

        return statement.join(
            settings_model,
            id_column == model.id,
        ).where(settings_model.tenant_id == tenant_id)

    async def _execute_statement(
        self,
        statement: SelectOfScalar[T],
        order_by: list[OrderBy] | None,
        model: type[T],
        allow_archived: bool = False,
    ) -> list[T]:
        statement = statement.group_by(model.id)
        statement = set_order_by(model, statement, order_by=order_by)
        if not allow_archived:
            statement = statement.where(col(model.archived_at).is_(None))
        return (await self.session.exec(statement)).all()

    async def load_hazards(
        self,
        type_key: LibraryFilterType,
        library_type_ids: list[uuid.UUID],
        order_by: list[OrderBy] | None = None,
    ) -> list[list[LibraryHazard]]:
        type_column: Any
        table: (
            Type[LibraryTaskRecommendations] | Type[LibrarySiteConditionRecommendations]
        )
        if type_key == LibraryFilterType.TASK:
            table = LibraryTaskRecommendations
            type_column = LibraryTaskRecommendations.library_task_id
        elif type_key == LibraryFilterType.SITE_CONDITION:
            table = LibrarySiteConditionRecommendations
            type_column = LibrarySiteConditionRecommendations.library_site_condition_id
        else:
            raise NotImplementedError(f"Invalid filter type {type_key}")

        statement = (
            select(type_column, LibraryHazard)
            # FIXME: This needs to be reverted post UI changes for 1220
            .where(LibraryHazard.id == table.library_hazard_id)
            # .join(table, LibraryHazard.id == table.library_hazard_id)
            # .join(
            #     TenantLibraryHazardSettings,
            #     TenantLibraryHazardSettings.library_hazard_id == LibraryHazard.id,
            # )
            .where(col(type_column).in_(library_type_ids))
            # .where(TenantLibraryHazardSettings.tenant_id == tenant_id)
            .group_by(type_column, LibraryHazard.id)
        )
        statement = set_order_by(LibraryHazard, statement, order_by=order_by)

        final: dict[uuid.UUID, list[LibraryHazard]] = {i: [] for i in library_type_ids}
        for library_type_id, library_hazard in (
            await self.session.exec(statement)
        ).all():
            final[library_type_id].append(library_hazard)
        return list(final.values())

    async def load_hazards_v2(
        self,
        tenant_id: uuid.UUID,
        type_key: LibraryFilterType,
        library_type_ids: list[uuid.UUID],
        order_by: list[OrderBy] | None = None,
    ) -> list[list[LibraryHazard]]:
        type_column: Any
        table: (
            Type[LibraryTaskRecommendations] | Type[LibrarySiteConditionRecommendations]
        )
        if type_key == LibraryFilterType.TASK:
            table = LibraryTaskRecommendations
            type_column = LibraryTaskRecommendations.library_task_id
        elif type_key == LibraryFilterType.SITE_CONDITION:
            table = LibrarySiteConditionRecommendations
            type_column = LibrarySiteConditionRecommendations.library_site_condition_id
        else:
            raise NotImplementedError(f"Invalid filter type {type_key}")

        statement = (
            select(type_column, LibraryHazard)
            .join(table, LibraryHazard.id == table.library_hazard_id)
            .join(
                TenantLibraryHazardSettings,
                TenantLibraryHazardSettings.library_hazard_id == LibraryHazard.id,
            )
            .where(col(type_column).in_(library_type_ids))
            .where(TenantLibraryHazardSettings.tenant_id == tenant_id)
            .group_by(type_column, LibraryHazard.id)
        )
        statement = set_order_by(LibraryHazard, statement, order_by=order_by)

        final: dict[uuid.UUID, list[LibraryHazard]] = {i: [] for i in library_type_ids}
        for library_type_id, library_hazard in (
            await self.session.exec(statement)
        ).all():
            final[library_type_id].append(library_hazard)
        return list(final.values())

    async def get_controls(
        self,
        type_key: LibraryFilterType | None,
        id: uuid.UUID | None = None,
        library_hazard_id: uuid.UUID | None = None,
        library_task_id: uuid.UUID | None = None,
        library_site_condition_id: uuid.UUID | None = None,
        order_by: list[OrderBy] | None = None,
    ) -> list[LibraryControl]:
        """
        Retrieve library controls
        """

        statement = select(LibraryControl)
        if id:
            statement = statement.where(LibraryControl.id == id)

        if type_key == LibraryFilterType.TASK:
            if library_hazard_id or library_task_id:
                statement = statement.where(
                    LibraryControl.id == LibraryTaskRecommendations.library_control_id
                )
                if library_hazard_id:
                    statement = statement.where(
                        LibraryTaskRecommendations.library_hazard_id
                        == library_hazard_id
                    )
                if library_task_id:
                    statement = statement.where(
                        LibraryTaskRecommendations.library_task_id == library_task_id
                    )
            else:
                statement = statement.where(col(LibraryControl.for_tasks).is_(True))
        elif type_key == LibraryFilterType.SITE_CONDITION:
            if library_hazard_id or library_site_condition_id:
                statement = statement.where(
                    LibraryControl.id
                    == LibrarySiteConditionRecommendations.library_control_id
                )
                if library_hazard_id:
                    statement = statement.where(
                        LibrarySiteConditionRecommendations.library_hazard_id
                        == library_hazard_id
                    )
                if library_site_condition_id:
                    statement = statement.where(
                        LibrarySiteConditionRecommendations.library_site_condition_id
                        == library_site_condition_id
                    )
            else:
                statement = statement.where(
                    col(LibraryControl.for_site_conditions).is_(True)
                )
        elif library_hazard_id:
            statement = (
                statement.join(
                    LibraryTaskRecommendations,
                    LibraryTaskRecommendations.library_control_id == LibraryControl.id,
                    isouter=True,
                )
                .join(
                    LibrarySiteConditionRecommendations,
                    LibrarySiteConditionRecommendations.library_control_id
                    == LibraryControl.id,
                    isouter=True,
                )
                .where(
                    or_(
                        LibraryTaskRecommendations.library_hazard_id
                        == library_hazard_id,
                        LibrarySiteConditionRecommendations.library_hazard_id
                        == library_hazard_id,
                    )
                )
            )

        statement = statement.group_by(LibraryControl.id)
        statement = set_order_by(LibraryControl, statement, order_by=order_by)
        return (await self.session.exec(statement)).all()

    async def get_controls_v2(
        self,
        type_key: LibraryFilterType | None = None,
        tenant_id: uuid.UUID | None = None,
        id: uuid.UUID | None = None,
        library_hazard_id: uuid.UUID | None = None,
        library_task_id: uuid.UUID | None = None,
        library_site_condition_id: uuid.UUID | None = None,
        order_by: list[OrderBy] | None = None,
        allow_archived: bool = False,
    ) -> list[LibraryControl]:
        """
        Retrieve library controls
        """

        statement = select(LibraryControl)
        if id:
            return await self._execute_statement(
                statement=statement.where(LibraryControl.id == id),
                order_by=order_by,
                model=LibraryControl,
                allow_archived=allow_archived,
            )

        if not tenant_id:
            return []

        else:
            statement = self._apply_tenant_filter(
                statement=statement, tenant_id=tenant_id, model=LibraryControl
            )
            statement = self._apply_control_type_filter(
                statement=statement,
                type_key=type_key,
                library_hazard_id=library_hazard_id,
                library_task_id=library_task_id,
                library_site_condition_id=library_site_condition_id,
            )

        return await self._execute_statement(
            statement=statement,
            order_by=order_by,
            model=LibraryControl,
            allow_archived=allow_archived,
        )

    def _apply_control_type_filter(
        self,
        statement: SelectOfScalar[LibraryControl],
        type_key: LibraryFilterType | None,
        library_hazard_id: uuid.UUID | None,
        library_task_id: uuid.UUID | None,
        library_site_condition_id: uuid.UUID | None,
    ) -> SelectOfScalar[LibraryControl]:
        if type_key == LibraryFilterType.TASK:
            statement = self._apply_control_task_filter(
                statement, library_hazard_id, library_task_id
            )
        elif type_key == LibraryFilterType.SITE_CONDITION:
            statement = self._apply_control_site_condition_filter(
                statement, library_hazard_id, library_site_condition_id
            )
        elif library_hazard_id:
            statement = self._apply_control_hazard_filter(statement, library_hazard_id)

        return statement

    def _apply_control_task_filter(
        self,
        statement: SelectOfScalar[LibraryControl],
        library_hazard_id: uuid.UUID | None,
        library_task_id: uuid.UUID | None,
    ) -> SelectOfScalar[LibraryControl]:
        if library_hazard_id or library_task_id:
            conditions = [
                LibraryControl.id == LibraryTaskRecommendations.library_control_id
            ]
            if library_hazard_id:
                conditions.append(
                    LibraryTaskRecommendations.library_hazard_id == library_hazard_id
                )
            if library_task_id:
                conditions.append(
                    LibraryTaskRecommendations.library_task_id == library_task_id
                )
            return statement.where(and_(*conditions))
        return statement.where(col(LibraryControl.for_tasks).is_(True))

    def _apply_control_site_condition_filter(
        self,
        statement: SelectOfScalar[LibraryControl],
        library_hazard_id: uuid.UUID | None,
        library_site_condition_id: uuid.UUID | None,
    ) -> SelectOfScalar[LibraryControl]:
        if library_hazard_id or library_site_condition_id:
            conditions = [
                LibraryControl.id
                == LibrarySiteConditionRecommendations.library_control_id
            ]
            if library_hazard_id:
                conditions.append(
                    LibrarySiteConditionRecommendations.library_hazard_id
                    == library_hazard_id
                )
            if library_site_condition_id:
                conditions.append(
                    LibrarySiteConditionRecommendations.library_site_condition_id
                    == library_site_condition_id
                )
            return statement.where(and_(*conditions))
        return statement.where(col(LibraryControl.for_site_conditions).is_(True))

    def _apply_control_hazard_filter(
        self,
        statement: SelectOfScalar[LibraryControl],
        library_hazard_id: uuid.UUID,
    ) -> SelectOfScalar[LibraryControl]:
        return (
            statement.join(
                LibraryTaskRecommendations,
                LibraryTaskRecommendations.library_control_id == LibraryControl.id,
                isouter=True,
            )
            .join(
                LibrarySiteConditionRecommendations,
                LibrarySiteConditionRecommendations.library_control_id
                == LibraryControl.id,
                isouter=True,
            )
            .where(
                or_(
                    LibraryTaskRecommendations.library_hazard_id == library_hazard_id,
                    LibrarySiteConditionRecommendations.library_hazard_id
                    == library_hazard_id,
                )
            )
        )

    async def load_controls(
        self,
        type_key: LibraryFilterType,
        library_hazard_ids: list[tuple[uuid.UUID | None, uuid.UUID]],
        order_by: list[OrderBy] | None = None,
    ) -> list[list[LibraryControl]]:
        """`library_hazard_ids` with `(library_parent_id, library_hazard_id)`"""

        unique_library_hazard_ids = {i[1] for i in library_hazard_ids}

        type_column: Any
        table: (
            Type[LibraryTaskRecommendations] | Type[LibrarySiteConditionRecommendations]
        )
        if type_key == LibraryFilterType.TASK:
            table = LibraryTaskRecommendations
            type_column = LibraryTaskRecommendations.library_task_id
        elif type_key == LibraryFilterType.SITE_CONDITION:
            table = LibrarySiteConditionRecommendations
            type_column = LibrarySiteConditionRecommendations.library_site_condition_id
        else:
            raise NotImplementedError(f"Invalid control filter type {type_key}")

        statement = (
            select(type_column, table.library_hazard_id, LibraryControl)
            # FIXME: These changes are required to be reverted once UI integration takes place
            # NOTE: This is fixed via v2 functions
            .where(LibraryControl.id == table.library_control_id)
            # .join(table, LibraryControl.id == table.library_control_id)
            # .join(
            #     TenantLibraryControlSettings,
            #     TenantLibraryControlSettings.library_control_id == LibraryControl.id,
            # )
            .where(col(table.library_hazard_id).in_(unique_library_hazard_ids))
            # .where(TenantLibraryControlSettings.tenant_id == tenant_id)
            .group_by(type_column, table.library_hazard_id, LibraryControl.id)
        )
        statement = set_order_by(LibraryControl, statement, order_by=order_by)

        final: dict[
            tuple[uuid.UUID | None, uuid.UUID], dict[uuid.UUID, LibraryControl]
        ] = {i: {} for i in library_hazard_ids}
        for parent_id, library_hazard_id, library_control in (
            await self.session.exec(statement)
        ).all():
            key = (parent_id, library_hazard_id)
            if key in final:
                final[key][library_control.id] = library_control
            none_key = (None, library_hazard_id)
            if none_key in final:
                final[none_key][library_control.id] = library_control
        return [list(i.values()) for i in final.values()]

    async def load_controls_v2(
        self,
        tenant_id: uuid.UUID,
        type_key: LibraryFilterType,
        library_hazard_ids: list[tuple[uuid.UUID | None, uuid.UUID]],
        order_by: list[OrderBy] | None = None,
    ) -> list[list[LibraryControl]]:
        """`library_hazard_ids` with `(library_parent_id, library_hazard_id)`"""

        unique_library_hazard_ids = {i[1] for i in library_hazard_ids}

        type_column: Any
        table: (
            Type[LibraryTaskRecommendations] | Type[LibrarySiteConditionRecommendations]
        )
        if type_key == LibraryFilterType.TASK:
            table = LibraryTaskRecommendations
            type_column = LibraryTaskRecommendations.library_task_id
        elif type_key == LibraryFilterType.SITE_CONDITION:
            table = LibrarySiteConditionRecommendations
            type_column = LibrarySiteConditionRecommendations.library_site_condition_id
        else:
            raise NotImplementedError(f"Invalid control filter type {type_key}")

        statement = (
            select(type_column, table.library_hazard_id, LibraryControl)
            .join(table, LibraryControl.id == table.library_control_id)
            .join(
                TenantLibraryControlSettings,
                TenantLibraryControlSettings.library_control_id == LibraryControl.id,
            )
            .where(col(table.library_hazard_id).in_(unique_library_hazard_ids))
            .where(TenantLibraryControlSettings.tenant_id == tenant_id)
            .group_by(type_column, table.library_hazard_id, LibraryControl.id)
        )
        statement = set_order_by(LibraryControl, statement, order_by=order_by)

        final: dict[
            tuple[uuid.UUID | None, uuid.UUID], dict[uuid.UUID, LibraryControl]
        ] = {i: {} for i in library_hazard_ids}
        for parent_id, library_hazard_id, library_control in (
            await self.session.exec(statement)
        ).all():
            key = (parent_id, library_hazard_id)
            if key in final:
                final[key][library_control.id] = library_control
            none_key = (None, library_hazard_id)
            if none_key in final:
                final[none_key][library_control.id] = library_control
        return [list(i.values()) for i in final.values()]

    async def get_divisions(
        self,
        ids: list[uuid.UUID] | None = None,
        names: Collection[str] | None = None,
        order_by: list[OrderBy] | None = None,
        tenant_id: uuid.UUID | None = None,
    ) -> list[LibraryDivision]:
        if ids is not None and not ids:
            return []

        statement = select(LibraryDivision)
        if ids:
            statement = statement.where(col(LibraryDivision.id).in_(ids))
        if names:
            statement = statement.where(col(LibraryDivision.name).in_(names))
        if tenant_id:
            statement = statement.join(
                LibraryDivisionTenantLink,
                onclause=LibraryDivisionTenantLink.library_division_id
                == LibraryDivision.id,
            ).where(LibraryDivisionTenantLink.tenant_id == tenant_id)

        statement = set_order_by(LibraryDivision, statement, order_by=order_by)
        return (await self.session.exec(statement)).all()

    async def get_divisions_by_id(
        self, ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, LibraryDivision]:
        return {i.id: i for i in await self.get_divisions(ids=ids)}

    async def get_regions(
        self,
        ids: list[uuid.UUID] | None = None,
        order_by: list[OrderBy] | None = None,
        tenant_id: uuid.UUID | None = None,
    ) -> list[LibraryRegion]:
        if ids is not None and not ids:
            return []

        statement = select(LibraryRegion)

        if ids:
            statement = statement.where(col(LibraryRegion.id).in_(ids))
        if tenant_id:
            statement = statement.join(
                LibraryRegionTenantLink,
                onclause=LibraryRegionTenantLink.library_region_id == LibraryRegion.id,
            ).where(LibraryRegionTenantLink.tenant_id == tenant_id)

        statement = set_order_by(LibraryRegion, statement, order_by=order_by)
        return (await self.session.exec(statement)).all()

    async def get_regions_by_id(
        self, ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, LibraryRegion]:
        return {i.id: i for i in await self.get_regions(ids=ids)}

    async def get_project_types(
        self,
        ids: list[uuid.UUID] | None = None,
        order_by: list[OrderBy] | None = None,
    ) -> list[LibraryProjectType]:
        if ids is not None and not ids:
            return []

        statement = select(LibraryProjectType)
        if ids:
            statement = statement.where(col(LibraryProjectType.id).in_(ids))

        statement = set_order_by(LibraryProjectType, statement, order_by=order_by)
        return (await self.session.exec(statement)).all()

    async def get_project_types_by_id(
        self, ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, LibraryProjectType]:
        return {i.id: i for i in await self.get_project_types(ids=ids)}

    async def get_asset_types(
        self,
        ids: list[uuid.UUID] | None = None,
        order_by: list[OrderBy] | None = None,
    ) -> list[LibraryAssetType]:
        if ids is not None and not ids:
            return []

        statement = select(LibraryAssetType)
        if ids:
            statement = statement.where(col(LibraryAssetType.id).in_(ids))

        statement = set_order_by(LibraryAssetType, statement, order_by=order_by)
        return (await self.session.exec(statement)).all()

    async def get_asset_types_by_id(
        self, ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, LibraryAssetType]:
        return {i.id: i for i in await self.get_asset_types(ids=ids)}

    async def get_activity_types(
        self,
        ids: Collection[uuid.UUID] | None = None,
        names: Collection[str] | None = None,
        tenant_id: uuid.UUID | None = None,
        order_by: list[OrderBy] | None = None,
    ) -> list[LibraryActivityType]:
        if ids is not None and not ids:
            return []

        statement = select(LibraryActivityType)
        if ids:
            statement = statement.where(col(LibraryActivityType.id).in_(ids))
        if names:
            statement = statement.where(col(LibraryActivityType.name).in_(names))
        if tenant_id:
            statement = statement.join(
                LibraryActivityTypeTenantLink,
                onclause=(
                    LibraryActivityTypeTenantLink.library_activity_type_id
                    == LibraryActivityType.id
                ),
            ).where(LibraryActivityTypeTenantLink.tenant_id == tenant_id)

        statement = set_order_by(LibraryActivityType, statement, order_by=order_by)
        return (await self.session.exec(statement)).all()

    async def get_activity_types_by_id(
        self,
        ids: list[uuid.UUID],
        tenant_id: uuid.UUID | None = None,
    ) -> dict[uuid.UUID, LibraryActivityType]:
        return {
            i.id: i for i in await self.get_activity_types(ids=ids, tenant_id=tenant_id)
        }

    async def get_activity_groups_by_library_task(
        self,
        library_task_ids: list[uuid.UUID],
        work_type_ids: List[uuid.UUID] | None = None,
    ) -> dict[uuid.UUID, list[Optional[LibraryActivityGroup]]]:
        # TODO: add tests for this
        statement = select(
            LibraryTaskActivityGroup.library_task_id.label("library_task_id"),  # type: ignore
            LibraryActivityGroup,
        )
        statement = statement.where(
            col(LibraryTaskActivityGroup.library_task_id).in_(library_task_ids)
        ).join(
            LibraryActivityGroup,
            onclause=LibraryTaskActivityGroup.activity_group_id
            == LibraryActivityGroup.id,
        )
        if work_type_ids:
            statement = (
                statement.join(
                    ActivityWorkTypeSettings,
                    onclause=ActivityWorkTypeSettings.library_activity_group_id
                    == LibraryTaskActivityGroup.activity_group_id,
                )
                .where(col(ActivityWorkTypeSettings.work_type_id).in_(work_type_ids))
                .where(col(ActivityWorkTypeSettings.disabled_at).is_(None))
            )

        # Add GROUP BY to ensure unique combinations of library_task_id and activity_group
        statement = statement.group_by(
            LibraryTaskActivityGroup.library_task_id, LibraryActivityGroup.id
        )

        data = (await self.session.exec(statement)).all()
        result: dict[uuid.UUID, list[Optional[LibraryActivityGroup]]] = {}
        for datum in data:
            library_task_id = datum[0]
            activity_group = datum[1]
            row = result.setdefault(library_task_id, [])
            row.append(activity_group)

        return result

    async def get_activity_group_ids_by_library_task_ids(
        self, library_task_ids: list[uuid.UUID]
    ) -> list[uuid.UUID]:
        statement = select(LibraryActivityGroup.id)
        statement = statement.join(
            LibraryTaskActivityGroup,
            onclause=LibraryTaskActivityGroup.activity_group_id
            == LibraryActivityGroup.id,
        ).where(col(LibraryTaskActivityGroup.library_task_id).in_(library_task_ids))
        return (await self.session.exec(statement)).all()

    async def get_work_types_by_library_task(
        self, library_task_ids: list[uuid.UUID], tenant_id: uuid.UUID | None = None
    ) -> dict[uuid.UUID, list[Optional[WorkType]]]:
        # TODO: add tests for this
        statement = select(
            WorkTypeTaskLink.task_id.label("library_task_id"),  # type: ignore
            WorkType,
        )
        statement = statement.where(
            col(WorkTypeTaskLink.task_id).in_(library_task_ids)
        ).join(
            WorkType,
            onclause=WorkTypeTaskLink.work_type_id == WorkType.id,
        )

        if tenant_id:
            statement = statement.where(WorkType.tenant_id == tenant_id)

        data = (await self.session.exec(statement)).all()
        result: dict[uuid.UUID, list[Optional[WorkType]]] = {}
        for datum in data:
            library_task_id = datum[0]
            work_type = datum[1]
            row = result.setdefault(library_task_id, [])
            row.append(work_type)

        return result

    async def get_work_types_by_library_site_condition(
        self,
        library_site_condition_ids: list[uuid.UUID],
        tenant_id: uuid.UUID | None = None,
    ) -> dict[uuid.UUID, list[Optional[WorkType]]]:
        # TODO: add tests for this
        statement = select(
            WorkTypeLibrarySiteConditionLink.library_site_condition_id.label("library_site_condition_id"),  # type: ignore
            WorkType,
        )
        statement = statement.where(
            col(WorkTypeLibrarySiteConditionLink.library_site_condition_id).in_(
                library_site_condition_ids
            )
        ).join(
            WorkType,
            onclause=WorkTypeLibrarySiteConditionLink.work_type_id == WorkType.id,
        )

        if tenant_id:
            statement = statement.where(WorkType.tenant_id == tenant_id)

        data = (await self.session.exec(statement)).all()
        result: dict[uuid.UUID, list[Optional[WorkType]]] = {}
        for datum in data:
            library_site_condition_id = datum[0]
            work_type = datum[1]
            row = result.setdefault(library_site_condition_id, [])
            row.append(work_type)

        return result

    async def get_activity_groups(
        self,
        order_by: list[OrderBy] | None = None,
        tenant_id: uuid.UUID | None = None,
    ) -> list[LibraryActivityGroup]:
        statement = select(LibraryActivityGroup)
        if tenant_id:
            statement = (
                statement.where(
                    LibraryActivityGroup.id
                    == LibraryTaskActivityGroup.activity_group_id
                )
                .where(LibraryTaskActivityGroup.library_task_id == LibraryTask.id)
                .where(WorkTypeTaskLink.work_type_id == WorkType.id)
                .where(WorkType.tenant_id == tenant_id)
                .where(WorkTypeTaskLink.task_id == LibraryTask.id)
            )
        statement = statement.group_by(LibraryActivityGroup.id)
        statement = set_order_by(LibraryActivityGroup, statement, order_by=order_by)
        return (await self.session.exec(statement)).all()

    async def create_location_hazard_control_setting(
        self,
        location_hazard_control_settings: list[LocationHazardControlSettingsCreate],
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        location_hazard_control_settings_list: list[LocationHazardControlSettings] = []
        for location_hazard_control_setting in location_hazard_control_settings:
            location_hazard_control_setting_data = LocationHazardControlSettings(
                location_id=location_hazard_control_setting.location_id,
                library_hazard_id=location_hazard_control_setting.library_hazard_id,
                library_control_id=location_hazard_control_setting.library_control_id,
                tenant_id=tenant_id,
                user_id=user_id,
                disabled=True,
            )
            location_hazard_control_settings_list.append(
                location_hazard_control_setting_data
            )

        self.session.add_all(location_hazard_control_settings_list)
        await self.session.commit()

    async def delete_location_hazard_control_setting(
        self,
        tenant_id: uuid.UUID,
        ids: list[uuid.UUID],
    ) -> None:
        if len(ids) > 0:
            delete_statement = (
                delete(LocationHazardControlSettings)
                .where(col(LocationHazardControlSettings.id).in_(ids))
                .where(LocationHazardControlSettings.tenant_id == tenant_id)
            )

            await self.session.execute(delete_statement)
            await self.session.commit()

    async def get_location_hazard_control_settings(
        self, location_id: uuid.UUID
    ) -> list[LocationHazardControlSettings]:
        statement = select(LocationHazardControlSettings).where(
            LocationHazardControlSettings.location_id == location_id
        )

        return (await self.session.exec(statement)).all()

    async def get_task_applicability_levels(
        self, library_hazard_task_tuples: list[tuple[uuid.UUID, uuid.UUID | None]]
    ) -> list[LibraryTaskLibraryHazardLink]:
        conditions = []
        for hazard_id, task_id in library_hazard_task_tuples:
            # If both hazard_id and task_id are provided
            if hazard_id is not None and task_id is not None:
                conditions.append(
                    (LibraryTaskLibraryHazardLink.library_hazard_id == hazard_id)
                    & (LibraryTaskLibraryHazardLink.library_task_id == task_id)
                )
            # If only hazard_id is provided
            elif hazard_id is not None:
                conditions.append(
                    (LibraryTaskLibraryHazardLink.library_hazard_id == hazard_id)
                )
            # If only task_id is provided
            elif task_id is not None:
                conditions.append(
                    (LibraryTaskLibraryHazardLink.library_task_id == task_id)
                )

        statement = select(LibraryTaskLibraryHazardLink).where(or_(*conditions))

        result = await self.session.execute(statement)
        all_results = result.scalars().all()
        return all_results

    async def get_task_hazard_applicabilities(
        self,
        after: Optional[uuid.UUID] = None,
        limit: int | None = None,
        use_seek_pagination: bool | None = False,
        library_task_ids: Optional[list[uuid.UUID]] = None,
        library_hazard_ids: Optional[list[uuid.UUID]] = None,
    ) -> list[LibraryTaskLibraryHazardLink]:
        statement = select(LibraryTaskLibraryHazardLink)

        if library_task_ids:
            statement = statement.where(
                col(LibraryTaskLibraryHazardLink.library_task_id).in_(library_task_ids)
            )

        if library_hazard_ids:
            statement = statement.where(
                col(LibraryTaskLibraryHazardLink.library_hazard_id).in_(
                    library_hazard_ids
                )
            )

        if use_seek_pagination:
            if after is not None:
                statement = statement.where(
                    LibraryTaskLibraryHazardLink.library_task_id > after
                )
            if limit is not None:
                statement = statement.limit(limit)

        return (await self.session.exec(statement)).all()

    async def add_task_hazard_applicability(
        self, library_task_hazard_applicability: LibraryTaskLibraryHazardLink
    ) -> LibraryTaskLibraryHazardLink:
        try:
            self.session.add(library_task_hazard_applicability)
            await self.session.commit()
            await self.session.refresh(library_task_hazard_applicability)
            return library_task_hazard_applicability
        except Exception as ex:
            await self.session.rollback()
            match = re.search(ERROR_MSG_PATTERN, str(ex))
            if match:
                raise EntityAlreadyExistsException("library_task_id, library_hazard_id")
            else:
                raise ex

    async def update_task_hazard_applicability(
        self, library_task_hazard_applicability: LibraryTaskLibraryHazardLink
    ) -> None:
        stm = (
            update(LibraryTaskLibraryHazardLink)
            .where(
                LibraryTaskLibraryHazardLink.library_task_id
                == library_task_hazard_applicability.library_task_id
            )
            .where(
                LibraryTaskLibraryHazardLink.library_hazard_id
                == library_task_hazard_applicability.library_hazard_id
            )
            .values(
                applicability_level=library_task_hazard_applicability.applicability_level
            )
        )

        result = await self.session.execute(stm)

        rc: int | None = None
        async with self.session.begin_nested():
            result = await self.session.execute(stm)
            rc = getattr(result, "rowcount")

        if rc == 0:
            raise DataNotFoundException("library_task_id, library_hazard_id")
