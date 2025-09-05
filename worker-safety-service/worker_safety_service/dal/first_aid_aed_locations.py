from datetime import datetime, timezone
from logging import getLogger
from typing import Optional
from uuid import UUID

from sqlalchemy import asc
from sqlalchemy.orm.attributes import set_attribute
from sqlmodel import col, select

from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.models import (
    AsyncSession,
    CreateFirstAidAEDLocationsInput,
    FirstAidAedLocations,
    LocationType,
    UpdateFirstAidAEDLocationsInput,
    set_column_order_by,
    unique_order_by_fields,
)
from worker_safety_service.types import OrderBy

logger = getLogger(__name__)


class FirstAIDAEDLocationsManager:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_first_aid_and_aed_location(
        self, input: CreateFirstAidAEDLocationsInput, tenant_id: UUID
    ) -> FirstAidAedLocations:
        # create the new location
        location_instance = FirstAidAedLocations(**input.dict(), tenant_id=tenant_id)

        return await self.add_and_commit(location_instance)

    async def get_first_aid_aed_location_by_id(
        self, location_id: UUID
    ) -> Optional[FirstAidAedLocations]:
        query = select(FirstAidAedLocations).where(
            FirstAidAedLocations.id == location_id,
            col(FirstAidAedLocations.archived_at).is_(None),
        )
        location = (await self.session.exec(query)).first()

        if not location:
            raise ResourceReferenceException(
                f"Could not find requested location with id {location_id}"
            )

        return location

    async def update_first_aid_and_aed_location(
        self,
        location_id: UUID,
        update_input: UpdateFirstAidAEDLocationsInput,
    ) -> Optional[FirstAidAedLocations]:
        location = await self.get_first_aid_aed_location_by_id(location_id)
        self.check_location_id_exists(location)
        assert location
        data_dict = update_input.dict(exclude_none=True, exclude_unset=True)
        for column_name, updated_value in data_dict.items():
            set_attribute(location, column_name, updated_value)

        return await self.add_and_commit(location)

    async def archive_first_aid_and_aed_location(
        self, location_id: UUID, tenant_id: UUID
    ) -> bool:
        location_to_be_archived = await self.get_first_aid_aed_location_by_id(
            location_id
        )
        if (
            not location_to_be_archived
            or location_to_be_archived.tenant_id != tenant_id
        ):
            raise ResourceReferenceException(
                f"Could not find requested first aid and aed location with id {id} for tenant {tenant_id}"
            )
        location_to_be_archived.archived_at = datetime.now(timezone.utc)
        _ = await self.add_and_commit(location_to_be_archived)

        return True

    async def get_first_aid_aed_location_from_location_type(
        self,
        location_type: Optional[LocationType] = None,
        order_by: list[OrderBy] | None = None,
    ) -> list[FirstAidAedLocations]:
        statement = select(FirstAidAedLocations).where(
            col(FirstAidAedLocations.archived_at).is_(None),
        )
        statement = statement.order_by(asc(FirstAidAedLocations.location_name))

        if location_type is not None:
            statement = statement.where(
                FirstAidAedLocations.location_type == location_type
            )
        if order_by is not None:
            for order_by_item in unique_order_by_fields(order_by):
                statement = set_column_order_by(
                    statement,
                    FirstAidAedLocations.location_name,
                    order_by_item.direction,
                )

        return (await self.session.exec(statement)).all()

    async def add_and_commit(
        self, first_aid_or_aed_location: FirstAidAedLocations
    ) -> FirstAidAedLocations:
        try:
            self.session.add(first_aid_or_aed_location)
            await self.session.commit()
            await self.session.refresh(first_aid_or_aed_location)
            return first_aid_or_aed_location
        except Exception as e:
            await self.session.rollback()
            logger.exception(
                "Some error occurred while committing to first_aid_or_aed_location"
            )
            raise e

    def check_location_id_exists(
        self, first_aid_aed_location: Optional[FirstAidAedLocations]
    ) -> None:
        if not first_aid_aed_location:
            raise ResourceReferenceException(
                "Could not find requested first aid and aed location."
            )
        else:
            return
