import uuid

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.energy_based_observations import (
    EnergyBasedObservationManager,
)
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.models import (
    EnergyBasedObservation,
    EnergyBasedObservationLayout,
    User,
)


class TenantEnergyBasedObservationLoader:
    def __init__(
        self,
        manager: EnergyBasedObservationManager,
        tenant_id: uuid.UUID,
    ):
        self.tenant_id = tenant_id
        self.__manager = manager
        self.with_work_location = DataLoader(load_fn=self.get_work_location_on_ebo_id)

    async def get_energy_based_observations(
        self, ebo_id: uuid.UUID, allow_archived: bool | None = True
    ) -> EnergyBasedObservation:
        assert allow_archived is not None
        ebo = await self.__manager.get_by_id(
            ebo_id, allow_archived=allow_archived, tenant_id=self.tenant_id
        )
        if ebo is None:
            raise ResourceReferenceException("Energy Based Observation not found")
        return ebo

    async def save_energy_based_observation(
        self,
        id: uuid.UUID | None,
        actor: User,
        data: EnergyBasedObservationLayout,
        token: str | None = None,
    ) -> EnergyBasedObservation:
        return await self.__manager.save(id, data, actor, self.tenant_id, token)

    async def complete_energy_based_observation(
        self,
        ebo_id: uuid.UUID,
        actor: User,
        data: EnergyBasedObservationLayout,
        token: str | None = None,
    ) -> EnergyBasedObservation:
        return await self.__manager.complete(
            ebo_id=ebo_id,
            data=data,
            actor=actor,
            tenant_id=self.tenant_id,
            token=token,
        )

    async def archive_energy_based_observation(
        self,
        ebo_id: uuid.UUID,
        user: User,
        token: str | None = None,
    ) -> None:
        await self.__manager.archive(
            ebo_id,
            user,
            tenant_id=self.tenant_id,
            token=token,
        )

    async def reopen_energy_based_observation(
        self, ebo_id: uuid.UUID, user: User, token: str | None = None
    ) -> EnergyBasedObservation:
        return await self.__manager.reopen(
            ebo_id, actor=user, tenant_id=self.tenant_id, token=token
        )

    async def get_work_location_on_ebo_id(
        self, ebo_ids: list[uuid.UUID]
    ) -> list[str | None]:
        ebos = await self.__manager.get_work_locations_on_ebo_id(ebo_ids=ebo_ids)
        items: dict[uuid.UUID, str] = {i[0]: i[1] for i in ebos}

        return [items.get(i) for i in ebo_ids]
