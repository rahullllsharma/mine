import copy
import datetime
import uuid
from typing import Any, Optional

from fastapi.encoders import jsonable_encoder
from sqlmodel import col, select

from worker_safety_service import get_logger
from worker_safety_service.audit_trail import audit_reopen
from worker_safety_service.dal.crua_audit_manager import CRUAAuditableManager
from worker_safety_service.dal.exceptions.entity_not_found import (
    EntityNotFoundException,
)
from worker_safety_service.dal.utils import merge_non_none_fields
from worker_safety_service.gcloud.cache import CachedFileStorage
from worker_safety_service.models import (
    AsyncSession,
    AuditObjectType,
    EnergyBasedObservation,
    FormStatus,
    User,
)
from worker_safety_service.models.concepts import (
    Completion,
    EnergyBasedObservationLayout,
)

logger = get_logger(__name__)

EXPIRATION_DAYS = 7


class EnergyBasedObservationManager(CRUAAuditableManager[EnergyBasedObservation]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(
            session=session,
            entity_type=EnergyBasedObservation,
            audit_object_type=AuditObjectType.energy_based_observation,
        )

    async def save(
        self,
        ebo_id: uuid.UUID | None,
        data: EnergyBasedObservationLayout,
        actor: User,
        tenant_id: uuid.UUID,
        token: Optional[str] = None,
    ) -> EnergyBasedObservation:
        if ebo_id is None:
            date_for = data.details.observation_date  # type: ignore
            encoded_data = jsonable_encoder(data)
            new_ebo = EnergyBasedObservation(
                tenant_id=tenant_id,
                date_for=date_for,
                contents=encoded_data,
                created_by_id=actor.id,
            )
            return await self.create(entity=new_ebo, actor=actor, token=token)
        else:
            ebo = await self.get_by_id(
                ebo_id, allow_archived=False, tenant_id=tenant_id
            )
            old_ebo = copy.deepcopy(ebo)
            if ebo is None:
                raise EntityNotFoundException(ebo_id, self._entity_type)

            if data.details and data.details.observation_date:
                ebo.date_for = data.details.observation_date

            merged_contents = merge_non_none_fields(
                data, EnergyBasedObservationLayout.parse_obj(ebo.contents)
            )
            ebo.contents = jsonable_encoder(merged_contents)
            ebo.updated_at = datetime.datetime.now(datetime.timezone.utc)
            return await self.update(
                entity=ebo, actor=actor, old_entity=old_ebo, token=token
            )

    async def complete(
        self,
        ebo_id: uuid.UUID,
        data: EnergyBasedObservationLayout,
        actor: User,
        tenant_id: uuid.UUID,
        token: Optional[str] = None,
    ) -> EnergyBasedObservation:
        ebo = await self.get_by_id(ebo_id, allow_archived=False, tenant_id=tenant_id)
        if ebo is None:
            logger.info(f"Energy based observation with id {ebo_id} not found")
            raise EntityNotFoundException(ebo_id, self._entity_type)

        old_ebo = copy.deepcopy(ebo)

        ebo.status = FormStatus.COMPLETE
        merged_content = merge_non_none_fields(
            data, EnergyBasedObservationLayout.parse_obj(ebo.contents)
        )

        final_ebo_layout = await self.calculate_and_save_heca_score(merged_content)

        now = datetime.datetime.now(datetime.timezone.utc)
        completion = Completion(completed_by_id=actor.id, completed_at=now)

        if ebo.completed_at is None:
            ebo.completed_by_id = completion.completed_by_id
            ebo.completed_at = completion.completed_at

        final_ebo_layout.completions = (
            [] if final_ebo_layout.completions is None else final_ebo_layout.completions
        )
        final_ebo_layout.completions.append(completion)

        ebo.updated_at = now
        ebo.contents = jsonable_encoder(final_ebo_layout)

        return await self.update(
            entity=ebo, actor=actor, old_entity=old_ebo, token=token
        )

    @audit_reopen
    async def reopen(
        self,
        ebo_id: uuid.UUID,
        actor: User,
        tenant_id: uuid.UUID,
        token: Optional[str] = None,
    ) -> EnergyBasedObservation:
        ebo = await self.get_by_id(ebo_id, allow_archived=False, tenant_id=tenant_id)
        if ebo is None:
            logger.info(f"Energy based observation with id {ebo_id} not found")
            raise EntityNotFoundException(ebo_id, self._entity_type)
        if ebo.status != FormStatus.COMPLETE:
            raise ValueError("Energy Based Observation is not complete")
        ebo.status = FormStatus.IN_PROGRESS
        ebo.updated_at = datetime.datetime.now(datetime.timezone.utc)
        return await self.update(ebo, actor)

    # calculating heca score on the basis if direct control is implemented (100) or not implemented (0)
    # for each activity the value is 'Success' (100) or 'Success + Exposure' (0)
    # for each observation the average score of all the activities gives the final score
    @staticmethod
    async def calculate_and_save_heca_score(
        ebo: EnergyBasedObservationLayout,
    ) -> EnergyBasedObservationLayout:
        if ebo.high_energy_tasks is None:
            return ebo

        het = ebo.high_energy_tasks
        for task in het:
            success_heca_items = 0
            success_and_exposure_heca_items = 0
            for hazard in task.hazards:
                if hazard.observed is False:
                    continue
                if hazard.direct_controls_implemented:
                    success_heca_items += 1
                    hazard.heca_score_hazard = "Success"
                    hazard.heca_score_hazard_percentage = 100
                else:
                    success_and_exposure_heca_items += 1
                    hazard.heca_score_hazard = "Success + Exposure"
                    hazard.heca_score_hazard_percentage = 0
            task.heca_score_task_percentage = (
                100
                * success_heca_items
                / (success_heca_items + success_and_exposure_heca_items)
            )
            task.heca_score_task = (
                "Success"
                if success_and_exposure_heca_items == 0
                else "Success + Exposure"
            )

        return ebo

    async def get_work_locations_on_ebo_id(
        self, ebo_ids: list[uuid.UUID]
    ) -> list[tuple[uuid.UUID, str]]:
        statement = select(
            EnergyBasedObservation.id,
            EnergyBasedObservation.contents["details"]["work_location"],  # type: ignore
        ).where(col(EnergyBasedObservation.id).in_(ebo_ids))
        work_locations = (await self.session.exec(statement)).all()
        return work_locations

    async def get_all_with_refreshed_urls(
        self, cached_file_storage: CachedFileStorage, **kwargs: Any
    ) -> list[EnergyBasedObservation]:
        ebos: list[EnergyBasedObservation] = await super().get_all(**kwargs)
        _expiration_timedelta = datetime.timedelta(days=EXPIRATION_DAYS)
        for ebo in ebos:
            ebo_layout = EnergyBasedObservationLayout.parse_obj(ebo.contents)
            if ebo_layout.photos:
                for file in ebo_layout.photos:
                    if file.id:
                        _url = await cached_file_storage.get_cached_signed_url(
                            file.id, expiration=_expiration_timedelta
                        )
                        if not _url.endswith("""/%s"""):
                            file.signed_url = _url
                ebo.contents = jsonable_encoder(ebo_layout)

        return ebos
