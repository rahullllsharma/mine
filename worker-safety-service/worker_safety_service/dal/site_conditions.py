import asyncio
import datetime
import itertools
import uuid
from collections import defaultdict
from collections.abc import Collection, Iterable
from datetime import date as date_type
from decimal import Decimal
from typing import Any, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from sqlmodel import and_, col, null, or_, select, update
from sqlmodel.sql.expression import Select

from worker_safety_service.dal.audit_events import (
    AuditContext,
    AuditEventType,
    archive_and_register_diffs,
    create_audit_event,
    diffs_from_session,
)
from worker_safety_service.dal.hazards import HazardParentManager
from worker_safety_service.dal.library import LibraryFilterType, LibraryManager
from worker_safety_service.dal.library_site_conditions import (
    LibrarySiteConditionManager,
)
from worker_safety_service.models import (
    AsyncSession,
    BaseControl,
    BaseHazard,
    BaseHazardCreate,
    BaseHazardEdit,
    LibraryControl,
    LibraryHazard,
    LibrarySiteCondition,
    Location,
    SiteCondition,
    SiteConditionControl,
    SiteConditionCreate,
    SiteConditionHazard,
    User,
    WorkPackage,
    set_item_order_by,
    unique_order_by_fields,
)
from worker_safety_service.models.base import SITE_CONDITION_MANUALLY_KEY
from worker_safety_service.models.tenant_library_settings import (
    TenantLibraryControlSettings,
    TenantLibraryHazardSettings,
    TenantLibrarySiteConditionSettings,
)
from worker_safety_service.site_conditions.types import SiteConditionResult
from worker_safety_service.types import OrderBy, Point
from worker_safety_service.urbint_logging import get_logger
from worker_safety_service.utils import assert_date

logger = get_logger(__name__)


class SiteConditionManager(HazardParentManager):
    def __init__(
        self,
        session: AsyncSession,
        library_manager: LibraryManager,
        library_site_condition_manager: LibrarySiteConditionManager,
    ):
        self.session = session
        self.library_manager = library_manager
        self.library_site_condition_manager = library_site_condition_manager

    ################################################################################
    # Fetching Site Conditions
    ################################################################################

    async def get_site_conditions_by_id(
        self,
        ids: list[uuid.UUID],
        *,
        order_by: list[OrderBy] | None = None,
        tenant_id: Optional[uuid.UUID] = None,
        with_archived: bool = False,
    ) -> list[tuple[LibrarySiteCondition, SiteCondition]]:
        """
        Retrieve project location site conditions
        Just by ID, no manually added/evaluated condition is checked
        """
        statement = build_site_conditions_statement(
            ids=ids,
            order_by=order_by,
            tenant_id=tenant_id,
            with_archived=with_archived,
        )
        if statement is None:
            return []
        else:
            return (await self.session.exec(statement)).all()

    async def get_manually_added_site_conditions(
        self,
        *,
        ids: list[uuid.UUID] | None = None,
        location_ids: list[uuid.UUID] | None = None,
        order_by: list[OrderBy] | None = None,
        tenant_id: Optional[uuid.UUID] = None,
        with_archived: bool = False,
    ) -> list[tuple[LibrarySiteCondition, SiteCondition]]:
        """
        Retrieve project location site conditions manually added by users
        """

        statement = build_site_conditions_statement(
            ids=ids,
            location_ids=location_ids,
            order_by=order_by,
            tenant_id=tenant_id,
            with_archived=with_archived,
        )
        if statement is None:
            return []

        # Only manually added
        statement = statement.where(col(SiteCondition.is_manually_added).is_(True))
        return (await self.session.exec(statement)).all()

    # async def get_site_condition_by_id_rest
    async def get_site_conditions(
        self,
        ids: list[uuid.UUID] | None = None,
        location_ids: list[uuid.UUID] | None = None,
        *,
        date: date_type | None = None,
        filter_start_date: date_type | None = None,
        filter_end_date: date_type | None = None,
        order_by: list[OrderBy] | None = None,
        tenant_id: Optional[uuid.UUID] = None,
        filter_tenant_settings: Optional[bool] = False,
        with_archived: bool = False,
    ) -> list[tuple[LibrarySiteCondition, SiteCondition]]:
        """
        Retrieve all project location site conditions (manually added and evaluated)
        Because this method ignore manually added if a evaluated exists,
            to fetch site condition by ID, `get_site_conditions_by_id` should be used
        """

        statement = build_site_conditions_statement(
            ids=ids,
            location_ids=location_ids,
            order_by=order_by,
            tenant_id=tenant_id,
            filter_start_date=filter_start_date,
            filter_end_date=filter_end_date,
            filter_tenant_settings=filter_tenant_settings,
            with_archived=with_archived,
        )
        if statement is None:
            return []

        evaluated_filters: list[Any] = [
            col(SiteCondition.is_manually_added).is_(False),
            col(SiteCondition.alert).is_(True),
        ]
        if date:
            assert_date(date)
            evaluated_filters.append(SiteCondition.date == date)

        # If we have manually added and evaluated with same library id, we should return the evaluated
        statement = statement.filter(
            or_(
                # All manually added site conditions
                col(SiteCondition.is_manually_added).is_(True),
                # Requested evaluated site conditions
                and_(*evaluated_filters),
            )
        )
        records = (await self.session.exec(statement)).all()

        evaluated = {i.id for i, s in records if not s.is_manually_added}
        return [
            (library_site_condition, site_condition)
            for library_site_condition, site_condition in records
            if (
                not site_condition.is_manually_added
                or library_site_condition.id not in evaluated
            )
        ]

    async def get_adhoc_site_conditions(
        self,
        latitude: Decimal,
        longitude: Decimal,
        date: datetime.date,
        order_by: list[OrderBy] | None = None,
        with_archived: bool = False,
        tenant_id: uuid.UUID | None = None,
        filter_tenant_settings: bool | None = False,
    ) -> list[tuple[LibrarySiteCondition, SiteCondition, Location]]:
        statement = build_adhoc_site_conditions_statement(
            latitude=latitude,
            longitude=longitude,
            date=date,
            order_by=order_by,
            with_archived=with_archived,
            tenant_id=tenant_id,
            filter_tenant_settings=filter_tenant_settings,
        )
        if statement is None:
            return []
        records = (await self.session.exec(statement)).all()
        return [
            (library_site_condition, site_condition, site_condition_location)
            for library_site_condition, site_condition, site_condition_location in records
        ]

    ################################################################################
    # Fetching Hazards
    ################################################################################

    async def get_hazards(
        self,
        ids: list[uuid.UUID] | None = None,
        site_condition_ids: list[uuid.UUID] | None = None,
        is_applicable: Optional[bool] = None,
        order_by: list[OrderBy] | None = None,
        tenant_id: uuid.UUID | None = None,
        with_archived: bool = False,
        filter_tenant_settings: bool | None = False,
    ) -> list[tuple[LibraryHazard, SiteConditionHazard]]:
        """
        Retrieve hazards for a project location site condition
        """
        if site_condition_ids is not None and not site_condition_ids:
            return []
        elif ids is not None and not ids:
            return []

        statement = select(LibraryHazard, SiteConditionHazard).where(
            LibraryHazard.id == SiteConditionHazard.library_hazard_id
        )

        if not with_archived:
            statement = statement.where(col(SiteConditionHazard.archived_at).is_(None))
        if ids:
            statement = statement.where(col(SiteConditionHazard.id).in_(ids))
        if site_condition_ids:
            statement = statement.where(
                col(SiteConditionHazard.site_condition_id).in_(site_condition_ids)
            )
        if is_applicable is not None:
            statement = statement.where(
                col(SiteConditionHazard.is_applicable).is_(is_applicable)
            )
        if tenant_id:
            statement = (
                statement.where(
                    SiteConditionHazard.site_condition_id == SiteCondition.id
                )
                .where(SiteCondition.location_id == Location.id)
                .where(Location.project_id == WorkPackage.id)
                .where(WorkPackage.tenant_id == tenant_id)
            )

        if filter_tenant_settings:
            statement = statement.join(
                TenantLibraryHazardSettings,
                onclause=TenantLibraryHazardSettings.library_hazard_id
                == LibraryHazard.id,
            ).where(TenantLibraryHazardSettings.tenant_id == tenant_id)

        # Order by
        if order_by:
            for order_by_item in unique_order_by_fields(order_by):
                if order_by_item.field == "id":
                    statement = set_item_order_by(
                        statement, SiteConditionHazard, order_by_item
                    )
                else:
                    statement = set_item_order_by(
                        statement, LibraryHazard, order_by_item
                    )
        else:
            statement = statement.order_by(SiteConditionHazard.position)

        return (await self.session.exec(statement)).all()

    async def get_hazards_by_site_condition(
        self,
        site_condition_ids: list[uuid.UUID],
        is_applicable: bool | None = None,
        order_by: list[OrderBy] | None = None,
        tenant_id: uuid.UUID | None = None,
        filter_tenant_settings: bool | None = False,
    ) -> defaultdict[uuid.UUID, list[tuple[LibraryHazard, SiteConditionHazard]]]:
        items: defaultdict[
            uuid.UUID, list[tuple[LibraryHazard, SiteConditionHazard]]
        ] = defaultdict(list)
        for library_hazard, hazard in await self.get_hazards(
            site_condition_ids=site_condition_ids,
            is_applicable=is_applicable,
            order_by=order_by,
            tenant_id=tenant_id,
            filter_tenant_settings=filter_tenant_settings,
        ):
            items[hazard.site_condition_id].append((library_hazard, hazard))
        return items

    ################################################################################
    # Fetching Controls
    ################################################################################

    async def get_controls(
        self,
        ids: list[uuid.UUID] | None = None,
        site_condition_id: uuid.UUID | None = None,
        hazard_ids: list[uuid.UUID] | None = None,
        is_applicable: bool | None = None,
        order_by: list[OrderBy] | None = None,
        tenant_id: uuid.UUID | None = None,
        with_archived: bool = False,
        filter_tenant_settings: bool | None = False,
    ) -> list[tuple[LibraryControl, SiteConditionControl]]:
        """
        Retrieve controls for a project location site condition
        """
        if hazard_ids is not None and not hazard_ids:
            return []
        elif ids is not None and not ids:
            return []

        statement = select(LibraryControl, SiteConditionControl).where(
            LibraryControl.id == SiteConditionControl.library_control_id
        )
        if not with_archived:
            statement = statement.where(col(SiteConditionControl.archived_at).is_(None))

        if ids:
            statement = statement.where(col(SiteConditionControl.id).in_(ids))
        if site_condition_id or tenant_id:
            statement = statement.where(
                SiteConditionControl.site_condition_hazard_id == SiteConditionHazard.id
            )

        if is_applicable is not None:
            statement = statement.where(
                col(SiteConditionControl.is_applicable).is_(is_applicable)
            )
        if site_condition_id:
            statement = statement.where(
                SiteConditionHazard.site_condition_id == site_condition_id
            )
        if tenant_id:
            statement = (
                statement.where(
                    SiteConditionHazard.site_condition_id == SiteCondition.id
                )
                .where(SiteCondition.location_id == Location.id)
                .where(Location.project_id == WorkPackage.id)
                .where(WorkPackage.tenant_id == tenant_id)
            )
        if hazard_ids:
            statement = statement.where(
                col(SiteConditionControl.site_condition_hazard_id).in_(hazard_ids)
            )

        if filter_tenant_settings:
            statement = statement.join(
                TenantLibraryControlSettings,
                onclause=TenantLibraryControlSettings.library_control_id
                == LibraryControl.id,
            ).where(TenantLibraryControlSettings.tenant_id == tenant_id)

        if order_by:
            for order_by_item in unique_order_by_fields(order_by):
                if order_by_item.field == "id":
                    statement = set_item_order_by(
                        statement,
                        SiteConditionControl,
                        order_by_item,
                    )
                else:
                    statement = set_item_order_by(
                        statement, LibraryControl, order_by_item
                    )
        else:
            statement = statement.order_by(SiteConditionControl.position)

        return (await self.session.exec(statement)).all()

    async def get_controls_by_hazard(
        self,
        hazard_ids: list[uuid.UUID],
        is_applicable: bool | None = None,
        order_by: list[OrderBy] | None = None,
        tenant_id: uuid.UUID | None = None,
        filter_tenant_settings: bool | None = False,
    ) -> defaultdict[uuid.UUID, list[tuple[LibraryControl, SiteConditionControl]]]:
        items: defaultdict[
            uuid.UUID,
            list[tuple[LibraryControl, SiteConditionControl]],
        ] = defaultdict(list)
        for library_control, control in await self.get_controls(
            hazard_ids=hazard_ids,
            is_applicable=is_applicable,
            order_by=order_by,
            tenant_id=tenant_id,
            filter_tenant_settings=filter_tenant_settings,
        ):
            items[control.site_condition_hazard_id].append((library_control, control))
        return items

    ################################################################################
    # Fetching Hazards and Controls
    ################################################################################

    async def get_manually_added_hazards_and_controls(
        self,
        location_id: uuid.UUID,
        library_site_condition_ids: Collection[uuid.UUID],
    ) -> tuple[
        defaultdict[uuid.UUID, dict[uuid.UUID, SiteConditionHazard]],
        defaultdict[
            tuple[uuid.UUID, uuid.UUID],
            dict[uuid.UUID, SiteConditionControl],
        ],
    ]:
        statement = (
            select(
                SiteCondition,
                SiteConditionHazard,
                SiteConditionControl,
            )
            .outerjoin_from(
                SiteConditionHazard,
                SiteConditionControl,
                SiteConditionHazard.id == SiteConditionControl.site_condition_hazard_id,
            )
            .where(SiteCondition.id == SiteConditionHazard.site_condition_id)
            .where(SiteCondition.location_id == location_id)
            .where(
                col(SiteCondition.library_site_condition_id).in_(
                    library_site_condition_ids
                )
            )
        )

        hazards: defaultdict[
            uuid.UUID, dict[uuid.UUID, SiteConditionHazard]
        ] = defaultdict(dict)
        controls: defaultdict[
            tuple[uuid.UUID, uuid.UUID],
            dict[uuid.UUID, SiteConditionControl],
        ] = defaultdict(dict)
        for site_condition, hazard, control in (
            await self.session.exec(statement)
        ).all():
            hazards[site_condition.library_site_condition_id][
                hazard.library_hazard_id
            ] = hazard
            if control:
                controls[
                    (site_condition.library_site_condition_id, hazard.library_hazard_id)
                ][control.library_control_id] = control

        return hazards, controls

    ################################################################################
    # Creating Site Conditions
    ################################################################################

    async def create_site_condition(
        self,
        site_condition: SiteConditionCreate,
        hazards: list[BaseHazardCreate],
        user: User | None,
    ) -> SiteCondition:
        library_site_condition = await self.library_site_condition_manager.get_by_id(
            site_condition.library_site_condition_id
        )
        if library_site_condition is None:
            raise ValueError("Library site condition does not exist")

        db_project_location_site_condition: SiteCondition = SiteCondition.from_orm(
            site_condition, update={"user_id": user.id if user else None}
        )

        try:
            self.session.add(db_project_location_site_condition)
            diffs = diffs_from_session(self.session)
            await self.session.flush()
        except IntegrityError as error:
            await self.session.rollback()
            if any(SITE_CONDITION_MANUALLY_KEY in arg for arg in error.args):
                raise ValueError(
                    f"Library site condition {site_condition.library_site_condition_id} already defined "
                    f"for location {site_condition.location_id}"
                )
            else:
                raise

        with self.session.no_autoflush:
            await self.create_hazards(
                db_project_location_site_condition.id,
                db_project_location_site_condition.library_site_condition_id,
                hazards,
                user,
            )
        create_audit_event(
            self.session,
            AuditEventType.site_condition_created,
            user,
            extra_diffs=diffs,
        )
        await self.session.commit()
        logger.info(
            "Project location site condition created",
            location_id=str(db_project_location_site_condition.location_id),
            site_condition_id=str(db_project_location_site_condition.id),
            by_user_id=str(user.id) if user else None,
        )
        return db_project_location_site_condition

    ################################################################################
    # Updating Site Conditions
    ################################################################################

    async def edit_site_condition(
        self,
        db_site_condition: SiteCondition,
        hazards: list[BaseHazardEdit],
        user: User,
    ) -> None:
        with self.session.no_autoflush:
            updated = await self.edit_hazards(db_site_condition.id, hazards, user)
        if updated:
            create_audit_event(
                self.session,
                AuditEventType.site_condition_updated,
                user,
            )
            await self.session.commit()
            logger.info(
                "Project location site condition updated",
                location_id=str(db_site_condition.location_id),
                site_condition_id=str(db_site_condition.id),
                by_user_id=str(user.id),
            )

    async def set_evaluated_site_conditions(
        self,
        date: date_type,
        location: Location,
        site_conditions: list[tuple[LibrarySiteCondition, SiteConditionResult]],
    ) -> None:
        """Create or update evaluated project location site conditions"""
        if not site_conditions:
            return None

        reference = {i.id: c for i, c in site_conditions}
        statement = (
            select(SiteCondition)
            .where(SiteCondition.location_id == location.id)
            .where(SiteCondition.date == date)
            .where(col(SiteCondition.library_site_condition_id).in_(reference.keys()))
        )

        with AuditContext(self.session) as audit:
            for site_condition in await self.session.exec(statement):
                condition_result = reference.pop(
                    site_condition.library_site_condition_id
                )
                if site_condition.archived_at:
                    site_condition.archived_at = None
                if condition_result.alert != site_condition.alert:
                    site_condition.alert = condition_result.alert
                if condition_result.multiplier != site_condition.multiplier:
                    site_condition.multiplier = condition_result.multiplier
                details = jsonable_encoder(condition_result.condition_value)
                if details != site_condition.details:
                    site_condition.details = details

            # Site conditions we need to add
            if reference:
                site_conditions_to_add = [
                    SiteCondition(
                        location_id=location.id,
                        library_site_condition_id=library_site_condition_id,
                        date=date,
                        alert=condition_result.alert,
                        multiplier=condition_result.multiplier,
                        details=jsonable_encoder(condition_result.condition_value),
                        is_manually_added=False,
                    )
                    for library_site_condition_id, condition_result in reference.items()
                ]
                self.session.add_all(site_conditions_to_add)

                await self.set_evaluated_site_conditions_hazards_and_controls(
                    site_conditions_to_add, location.tenant_id
                )

            if audit.with_diffs():
                await audit.create_system_event(AuditEventType.site_condition_evaluated)
                await self.session.commit()

    async def set_evaluated_site_conditions_hazards_and_controls(
        self, site_conditions: list[SiteCondition], tenant_id: uuid.UUID
    ) -> None:
        location_ids = {i.location_id for i in site_conditions}
        if len(location_ids) != 1:
            site_conditions_ids = {i.id for i in site_conditions}
            raise ValueError(
                "Multiple locations found on site conditions."
                f"Locations:{location_ids} SiteConditions:{site_conditions_ids}"
            )

        location_id = list(location_ids)[0]
        library_site_condition_ids = {
            i.library_site_condition_id for i in site_conditions
        }

        hazards_to_add = []
        controls_to_add = []

        # We only check hazards/controls if it's a new site condition
        recommendations, (
            all_hazards_manually_added,
            all_controls_manually_added,
        ) = await asyncio.gather(
            self.library_manager.get_site_condition_recommendations(
                library_site_condition_ids, tenant_id
            ),
            self.get_manually_added_hazards_and_controls(
                location_id, library_site_condition_ids
            ),
        )
        for site_condition in site_conditions:
            hazard_position = itertools.count()
            hazards_manually_added = all_hazards_manually_added[
                site_condition.library_site_condition_id
            ]
            for library_hazard_id, hazard_controls in recommendations[
                site_condition.library_site_condition_id
            ].items():
                # If we have a hazard recommendation, we can ignore the manually added
                hazards_manually_added.pop(library_hazard_id, None)

                hazard_id = uuid.uuid4()
                hazards_to_add.append(
                    SiteConditionHazard(
                        id=hazard_id,
                        site_condition_id=site_condition.id,
                        library_hazard_id=library_hazard_id,
                        is_applicable=True,
                        position=next(hazard_position),
                    )
                )

                # Add controls, we need to check library recommendations and manually added
                control_position = itertools.count()
                controls_manually_added = all_controls_manually_added.pop(
                    (site_condition.library_site_condition_id, library_hazard_id), {}
                )
                for library_control_id in hazard_controls:
                    # If we have a control recommendation, we can ignore the manually added
                    controls_manually_added.pop(library_control_id, None)

                    controls_to_add.append(
                        SiteConditionControl(
                            site_condition_hazard_id=hazard_id,
                            library_control_id=library_control_id,
                            is_applicable=True,
                            position=next(control_position),
                        )
                    )

                # Add manually added controls, if not added by recommendation
                for (
                    library_control_id,
                    ma_control,
                ) in controls_manually_added.items():
                    controls_to_add.append(
                        SiteConditionControl(
                            site_condition_hazard_id=hazard_id,
                            library_control_id=library_control_id,
                            is_applicable=ma_control.is_applicable,
                            user_id=ma_control.user_id,
                            position=next(control_position),
                        )
                    )

            # Add manually added hazards, if not added by recommendation
            for library_hazard_id, ma_hazard in hazards_manually_added.items():
                hazard_id = uuid.uuid4()
                hazards_to_add.append(
                    SiteConditionHazard(
                        id=hazard_id,
                        site_condition_id=site_condition.id,
                        library_hazard_id=library_hazard_id,
                        is_applicable=ma_hazard.is_applicable,
                        user_id=ma_hazard.user_id,
                        position=next(hazard_position),
                    )
                )

                # Add manually added controls
                for index, (library_control_id, ma_control) in enumerate(
                    all_controls_manually_added[
                        (site_condition.library_site_condition_id, library_hazard_id)
                    ].items()
                ):
                    controls_to_add.append(
                        SiteConditionControl(
                            site_condition_hazard_id=hazard_id,
                            library_control_id=library_control_id,
                            is_applicable=ma_control.is_applicable,
                            user_id=ma_control.user_id,
                            position=index,
                        )
                    )

        if hazards_to_add:
            self.session.add_all(hazards_to_add)
        if controls_to_add:
            self.session.add_all(controls_to_add)

    ################################################################################
    # Archiving Site Conditions, Hazards, and Controls
    ################################################################################

    async def archive_site_condition(
        self, site_condition: SiteCondition, user: User | None = None
    ) -> None:
        with AuditContext(self.session) as audit:
            await self.archive_site_conditions(site_condition_ids=[site_condition.id])
            await audit.create(AuditEventType.site_condition_archived, user)
            await self.session.commit()

        logger.info(
            "Project location site condition archived",
            location_id=str(site_condition.location_id),
            site_condition_id=str(site_condition.id),
            by_user_id=str(user.id if user else None),
        )

    async def archive_site_conditions(
        self,
        *,
        site_condition_ids: list[uuid.UUID] | None = None,
        location_ids: list[uuid.UUID] | None = None,
        include_manual_site_conditions: bool = True,
    ) -> None:
        statement = update(SiteCondition)
        if not include_manual_site_conditions:
            statement = statement.where(col(SiteCondition.is_manually_added).is_(False))
        if site_condition_ids is not None:
            statement = statement.where(col(SiteCondition.id).in_(site_condition_ids))
        elif location_ids is not None:
            statement = statement.where(
                col(SiteCondition.location_id).in_(location_ids)
            )
        else:
            raise NotImplementedError()

        # Archive site conditions
        await archive_and_register_diffs(self.session, statement, SiteCondition)

        # Archive hazards and controls
        await self.archive_hazards(
            site_conditions_ids=site_condition_ids,
            location_ids=location_ids,
        )

    async def archive_hazards(
        self,
        *,
        hazard_ids: Optional[Iterable[uuid.UUID]] = None,
        site_conditions_ids: Optional[Iterable[uuid.UUID]] = None,
        location_ids: Optional[Iterable[uuid.UUID]] = None,
    ) -> None:
        statement = update(SiteConditionHazard)
        if hazard_ids is not None:
            statement = statement.where(col(SiteConditionHazard.id).in_(hazard_ids))
        elif site_conditions_ids is not None:
            statement = statement.where(
                col(SiteConditionHazard.site_condition_id).in_(site_conditions_ids)
            )
        elif location_ids is not None:
            statement = statement.where(
                SiteConditionHazard.site_condition_id == SiteCondition.id
            ).where(col(SiteCondition.location_id).in_(location_ids))
        else:
            raise NotImplementedError()

        # Archive hazards
        await archive_and_register_diffs(self.session, statement, SiteConditionHazard)

        # Archive controls
        await self.archive_controls(
            hazard_ids=hazard_ids,
            site_conditions_ids=site_conditions_ids,
            location_ids=location_ids,
        )

    async def archive_controls(
        self,
        *,
        control_ids: Optional[Iterable[uuid.UUID]] = None,
        hazard_ids: Optional[Iterable[uuid.UUID]] = None,
        site_conditions_ids: Optional[Iterable[uuid.UUID]] = None,
        location_ids: Optional[Iterable[uuid.UUID]] = None,
    ) -> None:
        statement = update(SiteConditionControl)
        if control_ids is not None:
            statement = statement.where(col(SiteConditionControl.id).in_(control_ids))
        elif hazard_ids is not None:
            statement = statement.where(
                col(SiteConditionControl.site_condition_hazard_id).in_(hazard_ids)
            )
        else:
            statement = statement.where(
                SiteConditionControl.site_condition_hazard_id == SiteConditionHazard.id
            )
            if site_conditions_ids is not None:
                statement = statement.where(
                    col(SiteConditionHazard.site_condition_id).in_(site_conditions_ids)
                )
            elif location_ids is not None:
                statement = statement.where(
                    SiteConditionHazard.site_condition_id == SiteCondition.id
                ).where(col(SiteCondition.location_id).in_(location_ids))
            else:
                raise NotImplementedError()

        # Archive controls
        await archive_and_register_diffs(self.session, statement, SiteConditionControl)

    ################################################################################
    # HazardParentManager impl
    ################################################################################

    filter_type = LibraryFilterType.SITE_CONDITION

    async def get_recommendations(
        self, library_reference_id: uuid.UUID, tenant_id: uuid.UUID | None = None
    ) -> defaultdict[uuid.UUID, set[uuid.UUID]]:
        recommendations = await self.library_manager.get_site_condition_recommendations(
            [library_reference_id], tenant_id
        )
        return recommendations[library_reference_id]

    def hazard_orm(
        self,
        reference_id: uuid.UUID,
        library_hazard_id: uuid.UUID,
        is_applicable: bool,
        user_id: Optional[uuid.UUID],
        position: int,
    ) -> BaseHazard:
        return SiteConditionHazard(
            site_condition_id=reference_id,
            library_hazard_id=library_hazard_id,
            is_applicable=is_applicable,
            user_id=user_id,
            position=position,
        )

    def control_orm(
        self,
        hazard_id: uuid.UUID,
        library_control_id: uuid.UUID,
        is_applicable: bool,
        user_id: Optional[uuid.UUID],
        position: int,
    ) -> BaseControl:
        return SiteConditionControl(
            site_condition_hazard_id=hazard_id,
            library_control_id=library_control_id,
            is_applicable=is_applicable,
            user_id=user_id,
            position=position,
        )

    async def get_hazards_and_controls(
        self, reference_id: uuid.UUID, tenant_id: uuid.UUID | None = None
    ) -> tuple[
        dict[uuid.UUID, BaseHazard],
        defaultdict[uuid.UUID, dict[uuid.UUID, BaseControl]],
    ]:
        """
        Retrieve hazards and controls for a given site condition id, optionally filtered by tenant_id.
        """
        filter_tenant_settings: bool = (
            True if tenant_id else False
        )  # Check if filtering by tenant settings is needed based on the existence of tenant_id
        db_hazards: dict[uuid.UUID, BaseHazard] = {
            h.id: h
            for _, h in await self.get_hazards(
                site_condition_ids=[reference_id],
                filter_tenant_settings=filter_tenant_settings,
                tenant_id=tenant_id,
            )
        }

        db_hazards_controls: defaultdict[
            uuid.UUID, dict[uuid.UUID, BaseControl]
        ] = defaultdict(dict)
        for _, db_hazard_control in await self.get_controls(
            site_condition_id=reference_id,
            filter_tenant_settings=filter_tenant_settings,
            tenant_id=tenant_id,
        ):
            db_hazards_controls[db_hazard_control.site_condition_hazard_id][
                db_hazard_control.id
            ] = db_hazard_control

        return db_hazards, db_hazards_controls


def build_site_conditions_statement(
    *,
    ids: list[uuid.UUID] | None = None,
    location_ids: list[uuid.UUID] | None = None,
    order_by: list[OrderBy] | None = None,
    tenant_id: Optional[uuid.UUID] = None,
    filter_start_date: datetime.date | None = None,
    filter_end_date: datetime.date | None = None,
    filter_tenant_settings: Optional[bool] = False,
    with_archived: bool = False,
) -> Select[tuple[LibrarySiteCondition, SiteCondition]] | None:
    if location_ids is not None and not location_ids:
        return None
    elif ids is not None and not ids:
        return None
    statement = select(LibrarySiteCondition, SiteCondition).where(
        LibrarySiteCondition.id == SiteCondition.library_site_condition_id
    )
    if not with_archived:
        statement = statement.where(col(SiteCondition.archived_at).is_(None))
    if tenant_id:
        statement = (
            statement.join(Location)
            .join(WorkPackage)
            .where(WorkPackage.tenant_id == tenant_id)
        )
    if filter_tenant_settings:
        statement = statement.join(
            TenantLibrarySiteConditionSettings,
            onclause=TenantLibrarySiteConditionSettings.library_site_condition_id
            == SiteCondition.library_site_condition_id,
        ).where(TenantLibrarySiteConditionSettings.tenant_id == tenant_id)
    if ids:
        statement = statement.where(col(SiteCondition.id).in_(ids))
    if location_ids:
        statement = statement.where(col(SiteCondition.location_id).in_(location_ids))

    if filter_start_date is not None and filter_end_date is not None:
        if SiteCondition.date is not None:
            assert_date(filter_start_date)
            assert_date(filter_end_date)
            statement = statement.where(
                or_(
                    SiteCondition.date == null(),
                    and_(
                        SiteCondition.date >= filter_start_date,
                        SiteCondition.date <= filter_end_date,
                    ),
                )
            )
    # Order by
    for order_by_item in unique_order_by_fields(order_by):
        if order_by_item.field == "id":
            statement = set_item_order_by(statement, SiteCondition, order_by_item)
        else:
            statement = set_item_order_by(
                statement, LibrarySiteCondition, order_by_item
            )

    return statement


def build_adhoc_site_conditions_statement(
    latitude: Decimal,
    longitude: Decimal,
    date: datetime.date,
    order_by: list[OrderBy] | None = None,
    with_archived: bool = False,
    tenant_id: uuid.UUID | None = None,
    filter_tenant_settings: bool | None = False,
) -> Select[tuple[LibrarySiteCondition, SiteCondition, Location]]:
    statement = select(LibrarySiteCondition, SiteCondition, Location).where(
        (LibrarySiteCondition.id == SiteCondition.library_site_condition_id)
        & (SiteCondition.location_id == Location.id)  # Join based on location_id
    )

    if filter_tenant_settings and tenant_id:
        statement = statement.join(
            TenantLibrarySiteConditionSettings,
            onclause=TenantLibrarySiteConditionSettings.library_site_condition_id
            == LibrarySiteCondition.id,
        ).where(TenantLibrarySiteConditionSettings.tenant_id == tenant_id)

    if not with_archived:
        statement = statement.where(col(SiteCondition.archived_at).is_(None))
    # Filter by date, latitude, and longitude
    point = Point(longitude, latitude)
    statement = statement.where((SiteCondition.date == date) & (Location.geom == point))
    statement = statement.distinct(LibrarySiteCondition.id)
    # Order by
    for order_by_item in unique_order_by_fields(order_by):
        if order_by_item.field == "id":
            statement = set_item_order_by(statement, SiteCondition, order_by_item)
        else:
            statement = set_item_order_by(
                statement, LibrarySiteCondition, order_by_item
            )
    return statement
