import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Iterable, List, Optional, Tuple, cast

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import and_, any_, delete, or_, select
from sqlmodel.sql.expression import col

from worker_safety_service import get_logger
from worker_safety_service.dal.base_relationship_manager import BaseRelationshipManager
from worker_safety_service.dal.crua_manager import CRUAManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.models import (
    ActivityWorkTypeSettings,
    AsyncSession,
    CreateCoreWorkTypeInput,
    CreateTenantWorkTypeInput,
    UpdateCoreWorkTypeInput,
    UpdateTenantWorkTypeInput,
    WorkType,
    WorkTypeLibrarySiteConditionLink,
    WorkTypeTaskLink,
)
from worker_safety_service.models.library import WorkTypeTenantLink

logger = get_logger(__name__)


# The `WorkTypeManager` class in Python provides methods for managing work types, including creating,
# updating, archiving, and linking work types to tasks and site conditions.
class WorkTypeManager(CRUAManager[WorkType]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, WorkType)
        self._tenant_relationship_manager: BaseRelationshipManager[
            WorkTypeTenantLink
        ] = BaseRelationshipManager(session)
        self._site_condition_relationship_manager: BaseRelationshipManager[
            WorkTypeLibrarySiteConditionLink
        ] = BaseRelationshipManager(session)
        self._task_relationship_manager: BaseRelationshipManager[
            WorkTypeTaskLink
        ] = BaseRelationshipManager(session)

    async def get_work_types(
        self,
        ids: Iterable[uuid.UUID] | None = None,
        work_type_names: list[str] | None = None,
        tenant_ids: list[uuid.UUID] | None = None,
        library_task_ids: list[uuid.UUID] | None = None,
        after: uuid.UUID | None = None,
        limit: int | None = None,
    ) -> list[WorkType]:
        if (ids is not None and not ids) or (
            work_type_names is not None and not work_type_names
        ):
            return []

        statement = select(WorkType)
        if tenant_ids:
            statement = statement.where(col(WorkType.tenant_id).in_(tenant_ids))

        if library_task_ids:
            statement = statement.join(
                WorkTypeTaskLink,
                onclause=WorkTypeTaskLink.work_type_id == WorkType.id,
            ).where(col(WorkTypeTaskLink.task_id).in_(library_task_ids))

        if ids:
            statement = statement.where(col(WorkType.id).in_(ids))
        if work_type_names:
            statement = statement.where(col(WorkType.name).in_(work_type_names))
        if after:
            statement = statement.where(WorkType.id > after)
        if limit:
            statement = statement.limit(limit)

        statement = statement.order_by(WorkType.id)

        result = await self.session.execute(statement)
        return result.scalars().unique().all()

    async def create_work_type(
        self, input: CreateCoreWorkTypeInput | CreateTenantWorkTypeInput
    ) -> None:
        """
        The function creates a work type object and links default tasks and site conditions based on the
        input provided.

        :param input [CreateCoreWorkTypeInput | CreateTenantWorkTypeInput]: The `input` parameter in the `create_work_type` method can be either an instance
        of `CreateCoreWorkTypeInput` or `CreateTenantWorkTypeInput`. The method first checks the type of the input to determine the necessary actions to take based on the input type. If it's a
        `CreateTenantWorkTypeInput` then it also add default tasks and sc to the work type
        """
        if isinstance(input, CreateTenantWorkTypeInput):
            input.core_work_type_ids = list(set(input.core_work_type_ids))
            await self._verify_tenant_work_type_input(input.core_work_type_ids)
            to_create_wt = WorkType(**input.dict())
        else:
            to_create_wt = WorkType(**input.dict())

        work_type = await self.create(to_create_wt)
        if isinstance(input, CreateTenantWorkTypeInput):
            # by default link all the core work type tasks and site conditions to the tenant work type
            await self._add_default_tasks_and_sc_to_tenant_work_type(
                input.core_work_type_ids, work_type
            )

    async def update_work_type(
        self,
        work_type_id: uuid.UUID,
        input: dict[str, Any],
    ) -> WorkType:
        """
        The `update_work_type` function updates a work type with the provided input data, ensuring data
        integrity and refreshing the session.

        work_type_id [uuid.UUID]: The `work_type_id` parameter is the unique identifier of the work type that
        you want to update. It is of type `uuid.UUID`, which is a universally unique identifier data
        type often used to uniquely identify entities in a system.
        input [UpdateCoreWorkTypeInput | UpdateTenantWorkTypeInput]: The `input` parameter in the `update_work_type`
        is used to provide the data that needs to be updated for a specific work type identified by the `work_type_id`

        :return: The `update_work_type` method returns a `WorkType` object.
        """
        work_type = await self.get_by_id(work_type_id)
        if not work_type:
            raise RuntimeError(f"No work type found with id {work_type_id}")

        data: UpdateCoreWorkTypeInput | UpdateTenantWorkTypeInput
        if work_type.core_work_type_ids and work_type.tenant_id:
            data = UpdateTenantWorkTypeInput(**input)
        else:
            data = UpdateCoreWorkTypeInput(**input)

        if isinstance(data, UpdateTenantWorkTypeInput) and data.core_work_type_ids:
            data.core_work_type_ids = list(set(data.core_work_type_ids))
            await self._verify_tenant_work_type_input(data.core_work_type_ids)

        update_data = data.dict()
        if isinstance(data, UpdateTenantWorkTypeInput):
            if not work_type:
                raise RuntimeError(f"No work type found with id {work_type_id}")
            if not work_type.tenant_id:
                raise RuntimeError(f"Tenant id missing for work type id {work_type_id}")
            update_data[
                "tenant_id"
            ] = (
                work_type.tenant_id  # because while updating the `update` method is overriding the tenant_id value to None
            )

        await self.update(WorkType(id=work_type_id, **update_data))
        await self.session.refresh(work_type)
        if isinstance(data, UpdateTenantWorkTypeInput) and data.core_work_type_ids:
            # by default link all the core work type tasks and site conditions to the tenant work type
            await self._add_default_tasks_and_sc_to_tenant_work_type(
                data.core_work_type_ids, work_type
            )
        assert work_type
        return work_type

    async def archive_work_type(self, work_type_id: uuid.UUID) -> None:
        """
        This function archives a work type by first checking its existence, then
        determining whether to handle core or tenant work type deletion, and finally archiving the work
        type itself.

        :param work_type_id [uuid.UUID]: The `work_type_id` parameter represents a specific work type in the system.
        This identifier is used to retrieve the work type from the database and perform operations such as archiving or deleting the work type based on certain conditions
        """
        work_type = await self.get_by_id(work_type_id)
        if not work_type:
            raise ResourceReferenceException(
                f"No work type found with id {work_type_id}"
            )

        if not work_type.core_work_type_ids and not work_type.tenant_id:
            await self._handle_core_work_type_deletion(work_type_id)
        else:
            await self._handle_tenant_work_type_deletion(work_type_id)

        # Delete the work type itself
        await self.archive(work_type_id)
        await self.session.commit()

    async def get_work_types_for_tenant(self, tenant_id: uuid.UUID) -> list[WorkType]:
        return await self.get_work_types(tenant_ids=[tenant_id])

    async def get_work_types_by_name(
        self, work_type_names: list[str]
    ) -> list[WorkType]:
        return await self.get_work_types(work_type_names=work_type_names)

    async def get_work_type_by_code_and_tenant(
        self, code: str, tenant_id: uuid.UUID
    ) -> uuid.UUID | None:
        statement = select(WorkType.id).where(
            WorkType.tenant_id == tenant_id, WorkType.code == code
        )
        result = await self.session.exec(statement)
        return result.one_or_none()

    async def link_work_type_to_site_condition(
        self, work_type_id: uuid.UUID, library_site_condition_id: uuid.UUID
    ) -> None:
        """
        This function links a work type to a library site condition by calling another method with
        specific parameters.

        :work_type_id [uuid.UUID]: The `work_type_id` parameter represents the unique
        identifier of a specific work type. This identifier is used to link the work type to a library
        site condition in the `link_work_type_to_site_condition` method

        :library_site_condition_id [uuid.UUID]: The `library_site_condition_id` parameter
        represents the unique identifier of a library site condition entity. This identifier is used to
        link a specific work type to the corresponding library site condition in the system
        """
        await self._link_work_type_to_library_entity(
            entity_id=library_site_condition_id,
            work_type_ids=[work_type_id],
            entity_type=WorkTypeLibrarySiteConditionLink,
        )

    async def unlink_work_type_from_site_condition(
        self,
        work_type_id: uuid.UUID,
        library_site_condition_id: uuid.UUID,
    ) -> None:
        """
        This async function unlinks a work type from a library site condition.

        :param work_type_id [uuid.UUID]: The `work_type_id` parameter is a UUID that represents the unique
        identifier of a work type entity

        :param library_site_condition_id [uuid.UUID]: The `library_site_condition_id` parameter
        is used to identify the library site condition from which the work type needs to be unlinked
        """
        await self._unlink_work_type_from_library_entity(
            entity_id=library_site_condition_id,
            work_type_id=work_type_id,
            entity_type=WorkTypeLibrarySiteConditionLink,
        )

    async def link_work_types_to_task(
        self, task_id: uuid.UUID, work_type_ids: list[uuid.UUID]
    ) -> None:
        """
        This async function links work types to a task entity using the provided task ID and list
        of work type IDs.

        :param task_id: A unique identifier for the task to which work types will be linked
        :type task_id: uuid.UUID
        :param work_type_ids: The `work_type_ids` parameter is a list of UUIDs representing the unique
        identifiers of work types that are being linked to a task
        :type work_type_ids: list[uuid.UUID]
        """
        await self._link_work_type_to_library_entity(
            entity_id=task_id, work_type_ids=work_type_ids, entity_type=WorkTypeTaskLink
        )

    async def unlink_work_types_from_task(
        self, task_id: uuid.UUID, work_type_id: uuid.UUID
    ) -> None:
        """
        This async function unlinks a work type from a task by calling another method with specific
        parameters.

        :param task_id [uuid.UUID]: A unique identifier for the task that you want to unlink from a specific work type
        :param work_type_id [uuid.UUID]: The `work_type_id` parameter is a unique identifier (UUID) that represents
        a specific work type. In the context of the `unlink_work_types_from_task` method, it is used to
        identify the work type that needs to be unlinked from a task
        """
        await self._unlink_work_type_from_library_entity(
            entity_id=task_id, work_type_id=work_type_id, entity_type=WorkTypeTaskLink
        )

    async def _unlink_work_type_from_library_entity(
        self,
        entity_id: uuid.UUID,
        work_type_id: uuid.UUID,
        entity_type: type[WorkTypeTaskLink] | type[WorkTypeLibrarySiteConditionLink],
    ) -> None:
        """
        This function unlinks a work type from a library entity based on the entity type and specific
        IDs provided.

        :param entity_id: `entity_id` is a UUID that represents the ID of the entity for which you want
        to unlink a work type
        :type entity_id: uuid.UUID

        :param work_type_id: The `work_type_id` parameter in the `_unlink_work_type_from_library_entity`
        method is a unique identifier (UUID) for a specific work type. This method is responsible for
        unlinking a work type from a library entity based on the provided `entity_id`, `work_type_id`,
        and `
        :type work_type_id: uuid.UUID

        :param entity_type: The `entity_type` parameter in the `_unlink_work_type_from_library_entity`
        method is used to specify the type of entity that needs to be unlinked from the work type. It
        can be either `WorkTypeTaskLink` or `WorkTypeLibrarySiteConditionLink`, which are two different
        types
        :type entity_type: type[WorkTypeTaskLink] | type[WorkTypeLibrarySiteConditionLink]
        """
        core_and_tenant_work_type_map = (
            await self._get_tenant_work_types_for_all_core_work_types()
        )

        work_type_entity_link_ids = [work_type_id] + list(
            core_and_tenant_work_type_map.get(work_type_id, [])
        )

        # Perform batch delete
        if entity_type is WorkTypeTaskLink:
            await self.session.execute(
                delete(WorkTypeTaskLink).where(
                    WorkTypeTaskLink.task_id == entity_id,
                    col(WorkTypeTaskLink.work_type_id).in_(work_type_entity_link_ids),
                )
            )
        elif entity_type is WorkTypeLibrarySiteConditionLink:
            await self.session.execute(
                delete(WorkTypeLibrarySiteConditionLink).where(
                    WorkTypeLibrarySiteConditionLink.library_site_condition_id
                    == entity_id,
                    col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                        work_type_entity_link_ids
                    ),
                )
            )
        else:
            raise RuntimeError("Invalid Library Entity Type.")
        await self.session.commit()

    async def _get_tenant_work_types_for_all_core_work_types(
        self,
    ) -> dict[uuid.UUID, set[uuid.UUID]]:
        """
        This async function retrieves tenant work types for all core work types and returns a dictionary
        mapping core work type IDs to sets of corresponding tenant work type IDs.

        :return: The function `_get_tenant_work_types_for_all_core_work_types` returns a dictionary
        where the keys are UUIDs representing core work types, and the values are sets of UUIDs
        representing tenant work types associated with each core work type.
        """
        tenant_work_types = await self.get_all(
            additional_where_clause=[
                col(WorkType.tenant_id).is_not(None),
                col(WorkType.core_work_type_ids).is_not(None),
                col(WorkType.archived_at).is_(None),
            ]
        )

        core_and_tenant_work_type_map: dict[uuid.UUID, set[uuid.UUID]] = defaultdict(
            set
        )
        for tenant_work_type in tenant_work_types:
            for core_id in tenant_work_type.core_work_type_ids:
                core_and_tenant_work_type_map[core_id].add(tenant_work_type.id)

        return dict(core_and_tenant_work_type_map)

    async def _add_default_tasks_and_sc_to_tenant_work_type(
        self, core_work_type_ids: list[uuid.UUID], tenant_work_type: WorkType
    ) -> None:
        """
        This function adds default tasks and site conditions to a specific tenant work type based on
        core work type IDs.

        :param core_work_type_ids: The `core_work_type_ids` parameter is a list of UUIDs representing
        the core work type IDs whose tasks and site conditions you want to associate with the tenant_work_type.
        These IDs are used in the query to fetch task and site condition links related to the core work types
        :type core_work_type_ids: list[uuid.UUID]

        :param tenant_work_type: `tenant_work_type` is an instance of the `WorkType` class that
        represents a specific type of work associated with a tenant. The function
        `_add_default_tasks_and_sc_to_tenant_work_type` adds default tasks and site conditions to this
        `tenant_work_type` based on the provided `core
        :type tenant_work_type: WorkType
        """
        try:
            query = (
                select(
                    WorkTypeTaskLink.task_id,
                    WorkTypeLibrarySiteConditionLink.library_site_condition_id,
                )
                .select_from(WorkTypeTaskLink)
                .outerjoin(
                    WorkTypeLibrarySiteConditionLink,
                    WorkTypeTaskLink.work_type_id
                    == WorkTypeLibrarySiteConditionLink.work_type_id,
                    full=True,
                )
                .where(
                    or_(
                        col(WorkTypeTaskLink.work_type_id).in_(core_work_type_ids),
                        col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                            core_work_type_ids
                        ),
                    )
                )
            )

            result = await self.session.execute(query)
            rows = result.fetchall()

            task_links = [
                {"work_type_id": tenant_work_type.id, "task_id": row.task_id}
                for row in rows
                if row.task_id is not None
            ]

            site_condition_links = [
                {
                    "work_type_id": tenant_work_type.id,
                    "library_site_condition_id": row.library_site_condition_id,
                }
                for row in rows
                if row.library_site_condition_id is not None
            ]

            # Insert task links
            if task_links:
                task_stmt = insert(WorkTypeTaskLink).values(task_links)
                task_stmt = task_stmt.on_conflict_do_nothing(
                    index_elements=["work_type_id", "task_id"]
                )
                task_result = await self.session.execute(task_stmt)
                task_inserted = task_result.rowcount  # type:ignore
                task_conflicts = len(task_links) - task_inserted

                logger.info(f"Attempted to insert {len(task_links)} task links.")
                logger.info(f"Successfully inserted {task_inserted} new task links.")
                logger.info(f"Encountered {task_conflicts} conflicts in task links.")

            # Insert site condition links
            if site_condition_links:
                sc_stmt = insert(WorkTypeLibrarySiteConditionLink).values(
                    site_condition_links
                )
                sc_stmt = sc_stmt.on_conflict_do_nothing(
                    index_elements=["work_type_id", "library_site_condition_id"]
                )
                sc_result = await self.session.execute(sc_stmt)
                sc_inserted = sc_result.rowcount  # type:ignore
                sc_conflicts = len(site_condition_links) - sc_inserted
                logger.info(
                    f"Attempted to insert {len(site_condition_links)} site condition links."
                )
                logger.info(
                    f"Successfully inserted {sc_inserted} new site condition links."
                )
                logger.info(
                    f"Encountered {sc_conflicts} conflicts in site condition links."
                )

            total_inserted = (task_inserted if task_links else 0) + (
                sc_inserted if site_condition_links else 0
            )
            total_conflicts = (task_conflicts if task_links else 0) + (
                sc_conflicts if site_condition_links else 0
            )

            logger.info(f"Total links added: {total_inserted}")
            logger.info(f"Total conflicts encountered: {total_conflicts}")

            await self.session.commit()
        except SQLAlchemyError as e:
            logger.error(
                f"An error occurred while adding default tasks and site conditions: {str(e)}"
            )
            await self.session.rollback()
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            await self.session.rollback()
            raise

    async def _link_work_type_to_library_entity(
        self,
        entity_id: uuid.UUID,
        work_type_ids: list[uuid.UUID],
        entity_type: type[WorkTypeTaskLink] | type[WorkTypeLibrarySiteConditionLink],
    ) -> None:
        """
        The function links work types to a library entity(tasks and site conditions) based on
        the provided entity ID, work type IDs, and entity type.

        :param entity_id: `entity_id` is a UUID that represents the ID of an entity (either a task or a
        library site condition) to which work types will be linked
        :type entity_id: uuid.UUID

        :param work_type_ids: The `work_type_ids` parameter is a list of UUIDs representing the IDs of
        work types that you want to link to a library entity
        :type work_type_ids: list[uuid.UUID]

        :param entity_type: The `entity_type` parameter in the `_link_work_type_to_library_entity`
        method is used to specify the type of entity that will be linked to the work types. It can be
        either `WorkTypeTaskLink` or `WorkTypeLibrarySiteConditionLink`. This parameter determines how
        the work type
        :type entity_type: type[WorkTypeTaskLink] | type[WorkTypeLibrarySiteConditionLink]
        """
        try:
            core_and_tenant_work_type_map = (
                await self._get_tenant_work_types_for_all_core_work_types()
            )
            work_type_entity_links = []
            for work_type_id in work_type_ids:
                if entity_type is WorkTypeTaskLink:
                    link = {"work_type_id": work_type_id, "task_id": entity_id}
                elif entity_type is WorkTypeLibrarySiteConditionLink:
                    link = {
                        "work_type_id": work_type_id,
                        "library_site_condition_id": entity_id,
                    }
                else:
                    raise RuntimeError("Invalid Library Entity Type.")
                work_type_entity_links.append(link)

                if core_and_tenant_work_type_map.get(work_type_id):
                    for twt_id in core_and_tenant_work_type_map[work_type_id]:
                        if entity_type is WorkTypeTaskLink:
                            link = {"work_type_id": twt_id, "task_id": entity_id}
                        elif entity_type is WorkTypeLibrarySiteConditionLink:
                            link = {
                                "work_type_id": twt_id,
                                "library_site_condition_id": entity_id,
                            }
                        else:
                            raise RuntimeError("Invalid Library Entity Type.")
                        work_type_entity_links.append(link)

            if entity_type is WorkTypeTaskLink:
                stmt = insert(WorkTypeTaskLink).values(work_type_entity_links)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=["work_type_id", "task_id"]
                )
            elif entity_type is WorkTypeLibrarySiteConditionLink:
                stmt = insert(WorkTypeLibrarySiteConditionLink).values(
                    work_type_entity_links
                )
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=["work_type_id", "library_site_condition_id"]
                )
            else:
                raise RuntimeError("Invalid Library Entity Type.")

            result = await self.session.execute(stmt)
            total_links = len(work_type_entity_links)
            inserted_count = result.rowcount  # type:ignore
            conflict_count = total_links - inserted_count

            logger.info(f"Attempted to insert {total_links} work type links.")
            logger.info(f"Successfully inserted {inserted_count} new links.")
            logger.info(
                f"Encountered {conflict_count} conflicts (already existing links)."
            )

            await self.session.commit()
        except SQLAlchemyError as e:
            logger.error(
                f"An error occurred while linking work type to library entity: {str(e)}"
            )
            await self.session.rollback()
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            await self.session.rollback()
            raise

    async def _verify_tenant_work_type_input(
        self, core_work_type_ids: list[uuid.UUID]
    ) -> None:
        """
        The function checks and validates core work type IDs to ensure
        they are valid core work types and not tenant work types.

        :param core_work_type_ids: The `core_work_type_ids` parameter is a list of UUIDs representing
        core work type IDs that need to be verified. The function `_verify_tenant_work_type_input`
        checks if these core work type IDs exist and if they are valid core work types or tenant work
        types. It raises ValueError with
        :type core_work_type_ids: list[uuid.UUID]
        """
        work_types = await self.get_work_types(core_work_type_ids)

        if not work_types:
            raise ValueError(f"No core work_types exist with ids: {core_work_type_ids}")
        # checks if the core work type's exists or not.
        if len(work_types) != len(core_work_type_ids):
            missing_ids = set(core_work_type_ids) - {wt.id for wt in work_types}
            raise ValueError(f"No core work_types exist with ids: {missing_ids}")

        # check if it really a core work type and not a tenant WT by checking if core_type_id and tenant_id exists or not,
        # If it exists then the "work_type" is a tenant_work_type and not a core_work_type and
        # we cannot add id of another tenant_work_type as core_work_type_id
        tenant_work_types = [
            wt for wt in work_types if wt.core_work_type_ids and wt.tenant_id
        ]
        if tenant_work_types:
            invalid_ids = [wt.id for wt in tenant_work_types]
            raise ValueError(
                f"IDs {invalid_ids} already exist as tenant_work_types. Please provide Core IDs."
            )

    async def _handle_core_work_type_deletion(
        self, core_work_type_id: uuid.UUID
    ) -> None:
        """
        This function handles the deletion of task and site condition from a core work type by
        removing associated links, and also removing task and site condition linked to tenant work types
        associated with the core work type.

        :param core_work_type_id: The `core_work_type_id` parameter is a unique identifier (UUID) that
        represents a specific core work type. This identifier is used to perform various operations
        related to the deletion of the core work type and its associated tasks, site conditions, and
        links to tenant work types
        :type core_work_type_id: uuid.UUID
        """
        (
            core_task_ids,
            core_site_condition_ids,
        ) = await self._get_core_task_and_site_condition_ids(core_work_type_id)

        await self._remove_task_and_site_condition_links(core_work_type_id)

        tenant_work_types = await self._get_tenant_work_types_linked_to_core(
            core_work_type_id
        )

        for tenant_work_type in tenant_work_types:
            tenant_work_type.core_work_type_ids = [
                cwt
                for cwt in tenant_work_type.core_work_type_ids
                if cwt != core_work_type_id
            ]

            await self._remove_links_from_tenant_work_type(
                tenant_work_type.id, core_task_ids, core_site_condition_ids
            )

        self.session.add_all(tenant_work_types)

    async def _handle_tenant_work_type_deletion(self, work_type_id: uuid.UUID) -> None:
        """
        This async function handles the deletion of a work type by removing task and site condition
        links associated with it.

        :param work_type_id: The `work_type_id` parameter is a UUID (Universally Unique Identifier) that
        represents the unique identifier of a work type that needs to be handled for deletion in the
        `_handle_tenant_work_type_deletion` method
        :type work_type_id: uuid.UUID
        """
        await self._remove_task_and_site_condition_links(work_type_id)

    async def _get_core_task_and_site_condition_ids(
        self, core_work_type_id: uuid.UUID
    ) -> Tuple[list[uuid.UUID], list[uuid.UUID]]:
        """
        The function  retrieves task and site condition IDs associated with a given core work type ID.

        :param core_work_type_id: The `core_work_type_id` parameter is a UUID that represents the unique
        identifier of a core work type. This identifier is used to query and retrieve associated task
        IDs and site condition IDs related to the core work type
        :type core_work_type_id: uuid.UUID

        :return: The `_get_core_task_and_site_condition_ids` method returns a tuple containing two lists
        of UUIDs. The first list contains core task IDs, and the second list contains core site
        condition IDs.
        """
        core_task_ids = (
            (
                await self.session.execute(
                    select(WorkTypeTaskLink.task_id).where(
                        WorkTypeTaskLink.work_type_id == core_work_type_id
                    )
                )
            )
            .scalars()
            .all()
        )

        core_site_condition_ids = (
            (
                await self.session.execute(
                    select(
                        WorkTypeLibrarySiteConditionLink.library_site_condition_id
                    ).where(
                        WorkTypeLibrarySiteConditionLink.work_type_id
                        == core_work_type_id
                    )
                )
            )
            .scalars()
            .all()
        )

        return core_task_ids, core_site_condition_ids

    async def _remove_task_and_site_condition_links(
        self, work_type_id: uuid.UUID
    ) -> None:
        """
        This async function removes task and site condition links associated with a specific work type
        ID.

        :param work_type_id: The `work_type_id` parameter is a UUID (Universally Unique Identifier) that
        identifies a specific work type. In the provided code snippet, this parameter is used to delete
        records from two different tables (`WorkTypeTaskLink` and `WorkTypeLibrarySiteConditionLink`)
        based on the `work

        :type work_type_id: uuid.UUID
        """
        await self.session.execute(
            delete(WorkTypeTaskLink).where(
                WorkTypeTaskLink.work_type_id == work_type_id
            )
        )
        await self.session.execute(
            delete(WorkTypeLibrarySiteConditionLink).where(
                WorkTypeLibrarySiteConditionLink.work_type_id == work_type_id
            )
        )

    async def _get_tenant_work_types_linked_to_core(
        self, work_type_id: uuid.UUID
    ) -> list:
        """
        This async function retrieves a list of tenant work types linked to a specific core work type.

        :param work_type_id: The `work_type_id` parameter is a UUID (Universally Unique Identifier) that
        represents the unique identifier of a specific work type. This identifier is used to retrieve a
        list of tenant work types linked to a core work type with the specified `work_type_id`
        :type work_type_id: uuid.UUID

        :return: The function `_get_tenant_work_types_linked_to_core` returns a list of `WorkType`
        objects that are linked to a specific core work type identified by the `work_type_id` parameter.
        If there are no work types linked to the specified core work type, an empty list is returned.
        """
        tenant_work_types = await self.get_all(
            additional_where_clause=[
                col(WorkType.tenant_id).is_not(None),
                col(WorkType.core_work_type_ids).is_not(None),
            ]
        )

        core_and_tenant_work_type_map: dict[uuid.UUID, list[WorkType]] = defaultdict(
            list
        )
        for tenant_work_type in tenant_work_types:
            for core_id in tenant_work_type.core_work_type_ids:
                core_and_tenant_work_type_map[core_id].append(tenant_work_type)

        return core_and_tenant_work_type_map.get(work_type_id, [])

    async def _remove_links_from_tenant_work_type(
        self,
        tenant_work_type_id: uuid.UUID,
        core_task_ids: list,
        core_site_condition_ids: list,
    ) -> None:
        """
        This async function removes links between a tenant work type and tasks and site conditions.

        :param tenant_work_type_id: The `tenant_work_type_id` parameter is a UUID that represents the
        unique identifier of a specific tenant work type. It is used to identify the work type for which
        you want to remove links to certain tasks and site conditions
        :type tenant_work_type_id: uuid.UUID

        :param core_task_ids: The `core_task_ids` parameter is a list containing the IDs of tasks
        that need to be removed from the `WorkTypeTaskLink` table associated with a specific
        `tenant_work_type id`. These IDs are used to identify the specific tasks that should no longer
        be linked to the given work type
        :type core_task_ids: list

        :param core_site_condition_ids: The `core_site_condition_ids` parameter in the
        `_remove_links_from_tenant_work_type` method is a list containing the IDs of core site
        conditions that need to be removed from the specified tenant work type. These IDs are used to
        identify the specific site conditions that should no longer be linked to the
        :type core_site_condition_ids: list
        """
        await self.session.execute(
            delete(WorkTypeTaskLink).where(
                and_(
                    WorkTypeTaskLink.work_type_id == tenant_work_type_id,
                    col(WorkTypeTaskLink.task_id).in_(core_task_ids),
                )
            )
        )
        await self.session.execute(
            delete(WorkTypeLibrarySiteConditionLink).where(
                and_(
                    WorkTypeLibrarySiteConditionLink.work_type_id
                    == tenant_work_type_id,
                    col(WorkTypeLibrarySiteConditionLink.library_site_condition_id).in_(
                        core_site_condition_ids
                    ),
                )
            )
        )

    async def get_tenant_ids_for_work_types(
        self, work_type_ids: list[uuid.UUID]
    ) -> list[uuid.UUID]:
        """
        Get distinct tenant IDs associated with given work type IDs, including tenant IDs
        of tenant work types associated with any core work types in the input.

        :param session: AsyncSession for database operations

        :param work_type_ids: List of work type IDs (can include both core and tenant work types)

        :return: List of distinct tenant IDs
        """

        work_types = await self.get_all(
            additional_where_clause=[
                col(WorkType.id).in_(work_type_ids),
            ]
        )

        tenant_ids = set()
        core_work_type_ids = set()

        for work_type in work_types:
            if work_type.tenant_id and work_type.core_work_type_ids:
                tenant_ids.add(work_type.tenant_id)
            else:
                core_work_type_ids.add(work_type.id)

        # If we found any core work types, query for their associated tenant work types
        if core_work_type_ids:
            core_query = (
                select(WorkType.tenant_id)
                .where(
                    *[
                        any_(WorkType.core_work_type_ids) == core_work_type_id
                        for core_work_type_id in core_work_type_ids
                    ]
                )
                .distinct()
            )

            core_result = await self.session.execute(core_query)
            core_tenant_ids = core_result.scalars().all()
            tenant_ids.update(core_tenant_ids)

        return list(tenant_ids)

    async def link_work_types_to_tenant(
        self, tenant_id: uuid.UUID, work_type_ids: list[uuid.UUID]
    ) -> None:
        for work_type_id in work_type_ids:
            link = WorkTypeTenantLink(work_type_id=work_type_id, tenant_id=tenant_id)
            await self._tenant_relationship_manager.create(link)

    async def unlink_work_types_from_tenant(
        self, tenant_id: uuid.UUID, work_type_ids: list[uuid.UUID]
    ) -> None:
        for work_type_id in work_type_ids:
            link = WorkTypeTenantLink(work_type_id=work_type_id, tenant_id=tenant_id)
            await self._tenant_relationship_manager.delete(link)

    async def get_task_ids_linked_to_work_type(
        self, work_type_id: uuid.UUID
    ) -> List[uuid.UUID]:
        statement = select(WorkTypeTaskLink.task_id).where(
            WorkTypeTaskLink.work_type_id == work_type_id
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create_activity_task_work_type_settings(
        self,
        work_type_id: uuid.UUID,
        library_activity_group_id: uuid.UUID,
        library_task_id: uuid.UUID,
        alias: Optional[str] = None,
        disabled_at: Optional[datetime] = None,
    ) -> ActivityWorkTypeSettings:
        """
        Create new Activity Task Work Type Settings.
        """
        try:
            # Verify that the work type exists
            work_type = await self.get_by_id(work_type_id)
            if not work_type:
                raise ResourceReferenceException(
                    f"No work type found with id {work_type_id}"
                )

            # Create new settings
            settings = ActivityWorkTypeSettings(
                work_type_id=work_type_id,
                library_activity_group_id=library_activity_group_id,
                library_task_id=library_task_id,
                alias=alias,
                disabled_at=disabled_at,
            )
            self.session.add(settings)
            await self.session.commit()
            await self.session.refresh(settings)
            return settings

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ValueError(
                f"Error creating activity task work type settings: {str(e)}"
            )

    async def get_activity_task_work_type_settings(
        self,
        work_type_id: uuid.UUID,
        library_activity_group_id: Optional[uuid.UUID] = None,
        alias: Optional[str] = None,
        include_disabled: bool = False,
    ) -> list[ActivityWorkTypeSettings]:
        """
        Get Activity Task Work Type Settings for a work type.
        """
        try:
            # Verify that the work type exists
            work_type = await self.get_by_id(work_type_id)
            if not work_type:
                raise ResourceReferenceException(
                    f"No work type found with id {work_type_id}"
                )

            # Build the query
            statement = select(ActivityWorkTypeSettings).where(
                ActivityWorkTypeSettings.work_type_id == work_type_id
            )

            if library_activity_group_id:
                statement = statement.where(
                    ActivityWorkTypeSettings.library_activity_group_id
                    == library_activity_group_id
                )

            if alias:
                statement = statement.where(ActivityWorkTypeSettings.alias == alias)

            if not include_disabled:
                statement = statement.where(
                    ActivityWorkTypeSettings.disabled_at.is_(None)  # type: ignore
                )

            result = await self.session.execute(statement)
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise ValueError(
                f"Error getting activity task work type settings: {str(e)}"
            )

    async def update_activity_task_work_type_settings(
        self,
        work_type_id: uuid.UUID,
        library_activity_group_id: uuid.UUID,
        library_task_id: uuid.UUID,
        alias: Optional[str] = None,
        disabled_at: Optional[datetime] = None,
    ) -> ActivityWorkTypeSettings:
        """
        Update Activity Task Work Type Settings.
        If the settings don't exist, create them.
        """
        try:
            # Verify that the work type exists
            work_type = await self.get_by_id(work_type_id)
            if not work_type:
                raise ResourceReferenceException(
                    f"No work type found with id {work_type_id}"
                )

            # Create the insert statement with ON CONFLICT DO UPDATE
            stmt = (
                insert(ActivityWorkTypeSettings)
                .values(
                    work_type_id=work_type_id,
                    library_activity_group_id=library_activity_group_id,
                    library_task_id=library_task_id,
                    alias=alias,
                    disabled_at=disabled_at,
                )
                .on_conflict_do_update(
                    constraint="unique_activity_task_worktype",
                    set_=dict(
                        alias=alias,
                        disabled_at=disabled_at,
                    ),
                )
                .returning(ActivityWorkTypeSettings)
            )

            result = await self.session.execute(stmt)
            await self.session.commit()
            settings = result.scalar_one()
            return cast(ActivityWorkTypeSettings, settings)

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ValueError(
                f"Error updating activity task work type settings: {str(e)}"
            )

    async def disable_activity_task_work_type_settings(
        self,
        settings_id: uuid.UUID,
        work_type_id: uuid.UUID,
    ) -> None:
        """
        Disable Activity Task Work Type Settings by setting disabled_at to current UTC time.
        """
        try:
            # Verify that the work type exists
            work_type = await self.get_by_id(work_type_id)
            if not work_type:
                raise ResourceReferenceException(
                    f"No work type found with id {work_type_id}"
                )

            # Get the existing settings
            statement = select(ActivityWorkTypeSettings).where(
                ActivityWorkTypeSettings.id == settings_id,
                ActivityWorkTypeSettings.work_type_id == work_type_id,
            )
            result = await self.session.execute(statement)
            settings = result.scalar_one_or_none()

            if not settings:
                raise ResourceReferenceException(
                    f"No activity task work type settings found with id {settings_id} for work type {work_type_id}"
                )

            # Set disabled_at to current UTC time
            settings.disabled_at = datetime.now(timezone.utc)

            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ValueError(
                f"Error disabling activity task work type settings: {str(e)}"
            )
