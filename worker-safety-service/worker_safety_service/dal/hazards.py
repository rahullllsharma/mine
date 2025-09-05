import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Optional

from worker_safety_service.dal.library import LibraryFilterType, LibraryManager
from worker_safety_service.models import (
    AsyncSession,
    BaseControl,
    BaseHazard,
    BaseHazardCreate,
    BaseHazardEdit,
    User,
)


class HazardParentManager(ABC):
    filter_type: LibraryFilterType

    def __init__(
        self,
        session: AsyncSession,
        library_manager: LibraryManager,
    ) -> None:
        self.session = session
        self.library_manager = library_manager

    @abstractmethod
    async def get_recommendations(
        self, library_reference_id: uuid.UUID, tenant_id: uuid.UUID | None = None
    ) -> defaultdict[uuid.UUID, set[uuid.UUID]]:
        raise NotImplementedError()

    async def get_other_recommendations(
        self, tenant_id: uuid.UUID, library_hazard_ids: set[uuid.UUID]
    ) -> defaultdict[uuid.UUID, set[uuid.UUID]]:
        """This returns all controls recommended to an hazard
        For example, if we have the following recommendations:
        - library task 1 -> library hazard 1 -> library control 1 + library control 2
        - library task 2 -> library hazard 1 -> library control 3
        "hazard 1" returns all 3 controls

        This is allowed when a user is adding a hazard not recommended for a library task,
            all recommended controls to that hazard should be added as recommendations
        """

        items: defaultdict[uuid.UUID, set[uuid.UUID]] = defaultdict(set)
        if library_hazard_ids:
            filter_ids: list[tuple[uuid.UUID | None, uuid.UUID]] = [
                (None, i) for i in library_hazard_ids
            ]
            for (_, library_hazard_id), hazard_controls in zip(
                filter_ids,
                await self.library_manager.load_controls_v2(
                    tenant_id=tenant_id,
                    type_key=self.filter_type,
                    library_hazard_ids=filter_ids,
                ),
            ):
                items[library_hazard_id].update(i.id for i in hazard_controls)

        return items

    @abstractmethod
    def hazard_orm(
        self,
        reference_id: uuid.UUID,
        library_hazard_id: uuid.UUID,
        is_applicable: bool,
        user_id: Optional[uuid.UUID],
        position: int,
    ) -> BaseHazard:
        raise NotImplementedError()

    @abstractmethod
    def control_orm(
        self,
        hazard_id: uuid.UUID,
        library_control_id: uuid.UUID,
        is_applicable: bool,
        user_id: Optional[uuid.UUID],
        position: int,
    ) -> BaseControl:
        raise NotImplementedError()

    @abstractmethod
    async def get_hazards_and_controls(
        self, reference_id: uuid.UUID, tenant_id: uuid.UUID | None = None
    ) -> tuple[
        dict[uuid.UUID, BaseHazard],
        defaultdict[uuid.UUID, dict[uuid.UUID, BaseControl]],
    ]:
        """
        Retrieve hazards and controls for a given reference_id(site_condition_id), optionally filtered by tenant_id.
        """
        raise NotImplementedError()

    def validate_structure(self, hazards: list[Any]) -> None:
        defined_library_hazard_ids = set()
        for hazard in hazards:
            if hazard.library_hazard_id in defined_library_hazard_ids:
                raise ValueError(
                    f"Library hazard {hazard.library_hazard_id} already defined"
                )
            else:
                defined_library_hazard_ids.add(hazard.library_hazard_id)

            defined_library_control_ids = set()
            for control in hazard.controls:
                if control.library_control_id in defined_library_control_ids:
                    raise ValueError(
                        f"Library control {control.library_control_id} already defined in library hazard {hazard.library_hazard_id}"
                    )
                else:
                    defined_library_control_ids.add(control.library_control_id)

    async def create_hazards_from_recommendations(
        self,
        reference_id: uuid.UUID,
        library_reference_id: uuid.UUID,
        tenant_id: uuid.UUID | None = None,
    ) -> None:
        recommendations = await self.get_recommendations(
            library_reference_id, tenant_id
        )
        for position, hazard_id in enumerate(recommendations):
            new_hazard = self.hazard_orm(
                reference_id,
                library_hazard_id=hazard_id,
                is_applicable=True,
                user_id=None,
                position=position,
            )
            self.session.add(new_hazard)
            for position, control_id in enumerate(recommendations[hazard_id]):
                self.session.add(
                    self.control_orm(
                        new_hazard.id,
                        library_control_id=control_id,
                        is_applicable=True,
                        user_id=None,
                        position=position,
                    )
                )

    async def create_hazards(
        self,
        reference_id: uuid.UUID,
        library_reference_id: uuid.UUID,
        hazards: list[BaseHazardCreate],
        user: User | None = None,
    ) -> None:
        if not hazards:
            return await self.create_hazards_from_recommendations(
                reference_id, library_reference_id
            )
        if not user:
            raise ValueError("User required to create custom hazards")
        self.validate_structure(hazards)

        # If a hazard/control submitted when creating a task/site conditions and is not one recommended by
        # Urbint then we will be associating the user ID with it, so we need a list of
        # said recommended hazards and controls
        recommendations = await self.get_recommendations(
            library_reference_id, user.tenant_id
        )

        # Other recommendations means controls recommendations for a different library task/siteCondition type
        other_hazard_ids = {
            i.library_hazard_id
            for i in hazards
            if i.library_hazard_id not in recommendations
        }
        other_recommendations = await self.get_other_recommendations(
            tenant_id=user.tenant_id, library_hazard_ids=other_hazard_ids
        )

        to_add: list[BaseHazard | BaseControl] = []
        for hazard_position, hazard in enumerate(hazards):
            # user_id on hazards and controls will only be not None if the
            # hazard or control is not in the recommended hazards and controls
            if hazard.library_hazard_id in recommendations:
                hazard_user_id = None
                hazard_applicable = hazard.is_applicable
                recommended_controls = recommendations[hazard.library_hazard_id]
            else:
                hazard_user_id = user.id
                # If this is a user-created hazard then it automatically must be applicable
                hazard_applicable = True
                recommended_controls = other_recommendations[hazard.library_hazard_id]

            new_hazard = self.hazard_orm(
                reference_id,
                library_hazard_id=hazard.library_hazard_id,
                is_applicable=hazard_applicable,
                user_id=hazard_user_id,
                position=hazard_position,
            )
            to_add.append(new_hazard)

            for control_position, control in enumerate(hazard.controls):
                if control.library_control_id not in recommended_controls:
                    control_user_id = user.id
                    # If this is a user-created control then it automatically must be applicable
                    control_applicable = True
                else:
                    control_user_id = None
                    control_applicable = control.is_applicable

                to_add.append(
                    self.control_orm(
                        new_hazard.id,
                        library_control_id=control.library_control_id,
                        is_applicable=control_applicable,
                        user_id=control_user_id,
                        position=control_position,
                    )
                )

        if to_add:
            self.session.add_all(to_add)

    async def edit_hazards(
        self,
        reference_id: uuid.UUID,
        hazards: list[BaseHazardEdit],
        user: User,
    ) -> bool:
        self.validate_structure(hazards)

        updated = False
        db_hazards, db_hazards_controls = await self.get_hazards_and_controls(
            reference_id,
            tenant_id=user.tenant_id,
        )

        # Other recommendations means controls recommendations for a different library task/siteCondition type
        other_hazard_ids = {i.library_hazard_id for i in hazards if not i.id}
        other_recommendations = await self.get_other_recommendations(
            tenant_id=user.tenant_id, library_hazard_ids=other_hazard_ids
        )

        to_add: list[BaseHazard | BaseControl] = []
        for hazard_position, hazard in enumerate(hazards):
            if not hazard.id:
                db_hazard = None
            elif hazard.id not in db_hazards:
                raise ValueError(f"Hazard {hazard.id} not found")
            else:
                db_hazard = db_hazards.pop(hazard.id)

            if not db_hazard:
                recommended_controls = other_recommendations[hazard.library_hazard_id]
                db_hazard = self.hazard_orm(
                    reference_id,
                    library_hazard_id=hazard.library_hazard_id,
                    is_applicable=True,
                    user_id=user.id,
                    position=hazard_position,
                )
                to_add.append(db_hazard)
            else:
                recommended_controls = set()
                if (
                    not db_hazard.user_id
                    and db_hazard.is_applicable != hazard.is_applicable
                ):
                    db_hazard.is_applicable = hazard.is_applicable
                    updated = True
                if db_hazard.position != hazard_position:
                    db_hazard.position = hazard_position
                    updated = True

            db_hazard_controls = db_hazards_controls[db_hazard.id]
            for control_position, control in enumerate(hazard.controls):
                db_control: Optional[BaseControl] = None
                if control.id:
                    if control.id not in db_hazard_controls:
                        raise ValueError(
                            f"Control {control.id} not found in hazard {db_hazard.id}"
                        )
                    else:
                        db_control = db_hazard_controls.pop(control.id)

                if not db_control:
                    if control.library_control_id in recommended_controls:
                        control_applicable = control.is_applicable
                        control_user_id = None
                    else:
                        control_applicable = True
                        control_user_id = user.id

                    db_control = self.control_orm(
                        db_hazard.id,
                        library_control_id=control.library_control_id,
                        is_applicable=control_applicable,
                        user_id=control_user_id,
                        position=control_position,
                    )
                    to_add.append(db_control)
                else:
                    if (
                        not db_control.user_id
                        and db_control.is_applicable != control.is_applicable
                    ):
                        db_control.is_applicable = control.is_applicable
                        updated = True
                    if db_control.position != control_position:
                        db_control.position = control_position
                        updated = True

            # Don't allow to remove recommendations
            for db_control in list(db_hazard_controls.values()):
                if not db_control.user_id:
                    raise ValueError(
                        f"Not allowed to remove control {db_control.id} from hazard {db_hazard.id}"
                    )

        # Don't allow to remove recommendations
        for db_hazard in list(db_hazards.values()):
            if not db_hazard.user_id:
                raise ValueError(f"Not allowed to remove hazard {db_hazard.id}")

        if to_add:
            self.session.add_all(to_add)
            updated = True

        archived_at = datetime.now(timezone.utc)
        if db_hazards:
            for db_h in db_hazards.values():
                db_h.archived_at = archived_at
            updated = True

        for db_hazard_controls in db_hazards_controls.values():
            for db_c in db_hazard_controls.values():
                db_c.archived_at = archived_at
                updated = True

        return updated
