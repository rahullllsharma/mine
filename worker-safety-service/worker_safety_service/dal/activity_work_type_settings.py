import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import col, select, update

from worker_safety_service import get_logger
from worker_safety_service.dal.crua_manager import CRUAManager
from worker_safety_service.dal.work_types import WorkTypeManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.models import (
    ActivityWorkTypeSettings,
    AsyncSession,
    WorkType,
)

logger = get_logger(__name__)


class ActivityWorkTypeSettingsManager(CRUAManager[ActivityWorkTypeSettings]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ActivityWorkTypeSettings)
        self._work_type_manager: Optional[WorkTypeManager] = None

    def set_work_type_manager(self, work_type_manager: WorkTypeManager) -> None:
        """Set the work type manager for dependency injection."""
        self._work_type_manager = work_type_manager

    async def get_activity_aliases(
        self, id: uuid.UUID, work_type_ids: List[uuid.UUID]
    ) -> List[Optional[str]]:
        statement = (
            select(ActivityWorkTypeSettings.alias)
            .where(ActivityWorkTypeSettings.library_activity_group_id == id)
            .where(col(ActivityWorkTypeSettings.work_type_id).in_(work_type_ids))
            .where(col(ActivityWorkTypeSettings.disabled_at).is_(None))
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create_bulk_settings(
        self,
        settings_list: List[Dict[str, Any]],
    ) -> List[ActivityWorkTypeSettings]:
        """
        Bulk create Activity Work Type Settings.
        Will skip any settings that already exist (same work_type_id and library_activity_group_id combination).

        Args:
            settings_list: List of dictionaries containing:
                - work_type_id: UUID
                - library_activity_group_id: UUID
                - alias: Optional[str]
                - disabled_at: Optional[datetime]

        Returns:
            List of created ActivityWorkTypeSettings objects
        """
        if not self._work_type_manager:
            raise RuntimeError("Work type manager not set")

        try:
            # Verify all work types exist
            work_type_ids = {settings["work_type_id"] for settings in settings_list}
            for work_type_id in work_type_ids:
                work_type = await self._work_type_manager.get_by_id(work_type_id)
                if not work_type:
                    raise ResourceReferenceException(
                        f"No work type found with id {work_type_id}"
                    )

            # Create the insert statement with ON CONFLICT DO NOTHING
            stmt = (
                insert(ActivityWorkTypeSettings)
                .values(settings_list)
                .on_conflict_do_nothing(constraint="unique_activity_worktype")
                .returning(ActivityWorkTypeSettings)
            )

            result = await self.session.execute(stmt)
            await self.session.commit()
            created_settings = list(result.scalars().all())

            if not created_settings:
                logger.warning(
                    "No new activity work type settings were created - all already existed"
                )

            return created_settings

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ValueError(
                f"Error creating bulk activity work type settings: {str(e)}"
            )

    async def create_settings(
        self,
        work_type_id: uuid.UUID,
        library_activity_group_id: uuid.UUID,
        alias: Optional[str] = None,
        disabled_at: Optional[datetime] = None,
    ) -> ActivityWorkTypeSettings:
        """
        Create new Activity Work Type Settings.
        Will fail if a setting with the same combination already exists.
        """
        if not self._work_type_manager:
            raise RuntimeError("Work type manager not set")

        try:
            # Verify that the work type exists
            work_type = await self._work_type_manager.get_by_id(work_type_id)
            if not work_type:
                raise ResourceReferenceException(
                    f"No work type found with id {work_type_id}"
                )

            # Create the insert statement with ON CONFLICT DO NOTHING
            stmt = (
                insert(ActivityWorkTypeSettings)
                .values(
                    work_type_id=work_type_id,
                    library_activity_group_id=library_activity_group_id,
                    alias=alias,
                    disabled_at=disabled_at,
                )
                .on_conflict_do_nothing(constraint="unique_activity_worktype")
                .returning(
                    ActivityWorkTypeSettings.id,
                    ActivityWorkTypeSettings.work_type_id,
                    ActivityWorkTypeSettings.library_activity_group_id,
                    ActivityWorkTypeSettings.alias,
                    ActivityWorkTypeSettings.disabled_at,
                )
            )

            result = await self.session.execute(stmt)
            await self.session.commit()
            settings = result.fetchone()
            if not settings:
                raise ValueError("Activity Worktype Settings already exist!")
            return ActivityWorkTypeSettings(
                id=settings[0],
                work_type_id=settings[1],
                library_activity_group_id=settings[2],
                alias=settings[3],
                disabled_at=settings[4],
            )

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ValueError(f"Error creating activity work type settings: {str(e)}")

    async def update_settings(
        self,
        work_type_id: uuid.UUID,
        library_activity_group_id: uuid.UUID,
        alias: Optional[str] = None,
        disabled_at: Optional[datetime] = None,
    ) -> ActivityWorkTypeSettings:
        """
        Update Activity Work Type Settings.
        If the settings don't exist, create them.
        Uses PostgreSQL's ON CONFLICT DO UPDATE for upserting.
        """
        if not self._work_type_manager:
            raise RuntimeError("Work type manager not set")

        try:
            # Verify that the work type exists
            work_type = await self._work_type_manager.get_by_id(work_type_id)
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
                    alias=alias,
                    disabled_at=disabled_at,
                )
                .on_conflict_do_update(
                    constraint="unique_activity_worktype",
                    set_=dict(
                        alias=alias,
                        disabled_at=disabled_at,
                    ),
                )
                .returning(
                    ActivityWorkTypeSettings.id,
                    ActivityWorkTypeSettings.work_type_id,
                    ActivityWorkTypeSettings.library_activity_group_id,
                    ActivityWorkTypeSettings.alias,
                    ActivityWorkTypeSettings.disabled_at,
                )
            )

            result = await self.session.execute(stmt)
            await self.session.commit()
            settings = result.fetchone()
            if not settings:
                raise ValueError("Failed to update settings")
            return ActivityWorkTypeSettings(
                id=settings[0],
                work_type_id=settings[1],
                library_activity_group_id=settings[2],
                alias=settings[3],
                disabled_at=settings[4],
            )

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ValueError(f"Error updating activity work type settings: {str(e)}")

    async def get_settings(
        self,
        work_type_id: uuid.UUID,
        library_activity_group_id: Optional[uuid.UUID] = None,
        alias: Optional[str] = None,
        include_disabled: bool = False,
    ) -> list[ActivityWorkTypeSettings]:
        """
        Get Activity Work Type Settings for a work type.
        """
        if not self._work_type_manager:
            raise RuntimeError("Work type manager not set")

        try:
            # Verify that the work type exists
            work_type = await self._work_type_manager.get_by_id(work_type_id)
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
                    ActivityWorkTypeSettings.disabled_at == None  # noqa: E711
                )

            result = await self.session.execute(statement)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise ValueError(f"Error getting activity work type settings: {str(e)}")

    async def disable_settings(
        self,
        work_type_id: uuid.UUID,
        library_activity_group_id: uuid.UUID,
    ) -> ActivityWorkTypeSettings:
        """
        Disable Activity Work Type Settings by setting disabled_at to current UTC time.
        The settings are identified by the combination of work_type_id and activity_group_id.
        """
        if not self._work_type_manager:
            raise RuntimeError("Work type manager not set")

        try:
            # Verify that the work type exists
            work_type = await self._work_type_manager.get_by_id(work_type_id)
            if not work_type:
                raise ValueError(f"No work type found with id {work_type_id}")

            # Update the settings using an update query
            current_time = datetime.now(timezone.utc)
            update_stmt = (
                update(ActivityWorkTypeSettings)
                .where(
                    ActivityWorkTypeSettings.work_type_id == work_type_id,
                    ActivityWorkTypeSettings.library_activity_group_id
                    == library_activity_group_id,
                    col(ActivityWorkTypeSettings.disabled_at).is_(None),
                )
                .values(disabled_at=current_time, updated_at=current_time)
                .returning(
                    ActivityWorkTypeSettings.id,
                    ActivityWorkTypeSettings.work_type_id,
                    ActivityWorkTypeSettings.library_activity_group_id,
                    ActivityWorkTypeSettings.alias,
                    ActivityWorkTypeSettings.disabled_at,
                )
            )
            result = await self.session.execute(update_stmt)
            await self.session.commit()
            settings = result.fetchone()

            if not settings:
                raise ValueError("No settings found or settings already disabled")

            # Create a partial ActivityWorkTypeSettings object with the returned fields
            return ActivityWorkTypeSettings(
                id=settings[0],
                work_type_id=settings[1],
                library_activity_group_id=settings[2],
                alias=settings[3],
                disabled_at=settings[4],
            )

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ValueError(f"Error disabling activity work type settings: {str(e)}")

    async def get_work_types_and_aliases_by_work_types(
        self,
        work_type_ids: list[uuid.UUID],
        library_activity_group_id: uuid.UUID,
        tenant_id: uuid.UUID | None = None,
    ) -> dict[uuid.UUID, list[tuple[WorkType, Optional[str]]]]:
        """
        For each work_type_id, return a list of (WorkType, alias) tuples.
        Alias is from ActivityWorkTypeSettings for the given group and not disabled.
        """

        statement = (
            select(
                WorkType.id,
                WorkType,
                ActivityWorkTypeSettings.alias,
            )
            .join(
                ActivityWorkTypeSettings,
                (ActivityWorkTypeSettings.work_type_id == WorkType.id)
                & (
                    ActivityWorkTypeSettings.library_activity_group_id
                    == library_activity_group_id
                ),
            )
            .where(col(ActivityWorkTypeSettings.disabled_at).is_(None))
            .where(col(WorkType.id).in_(work_type_ids))
        )

        if tenant_id:
            statement = statement.where(WorkType.tenant_id == tenant_id)

        data = (await self.session.exec(statement)).all()

        result: dict[uuid.UUID, list[tuple[WorkType, Optional[str]]]] = {}
        for work_type_id, work_type, alias in data:
            result.setdefault(work_type_id, []).append((work_type, alias))
        return result
