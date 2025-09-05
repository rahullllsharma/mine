import datetime
import uuid
from typing import Any, Dict, List, Optional

from fastapi.encoders import jsonable_encoder
from sqlmodel import col, select

from worker_safety_service.dal.crua_audit_manager import CRUAAuditableManager
from worker_safety_service.dal.exceptions.entity_not_found import (
    EntityNotFoundException,
)
from worker_safety_service.dal.utils import merge_non_none_fields
from worker_safety_service.models import (
    AsyncSession,
    Completion,
    FormStatus,
    NatGridJobSafetyBriefing,
    NatGridJobSafetyBriefingLayout,
    User,
)
from worker_safety_service.models.audit_events import AuditObjectType


class NatGridJobSafetyBriefingManager(CRUAAuditableManager[NatGridJobSafetyBriefing]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(
            session=session,
            entity_type=NatGridJobSafetyBriefing,
            audit_object_type=AuditObjectType.natgrid_job_safety_briefing,
        )

    async def save(
        self,
        data: NatGridJobSafetyBriefingLayout,
        actor: User,
        tenant_id: uuid.UUID,
        form_status: FormStatus | None,
        work_type_id: uuid.UUID | None,
    ) -> NatGridJobSafetyBriefing:
        if data.jsb_id is None:
            date_for, project_location_id = extract_natgrid_jsb_properties(data)
            if date_for is None:
                date_for = datetime.date.today()
            encoded_data = jsonable_encoder(data)
            new_jsb = NatGridJobSafetyBriefing(
                tenant_id=tenant_id,
                date_for=date_for,
                project_location_id=project_location_id,
                contents=encoded_data,
                created_by_id=actor.id,
                status=(
                    form_status if form_status is not None else FormStatus.IN_PROGRESS
                ),
                work_type_id=work_type_id,
            )
            if data.work_location:
                new_jsb = set_backward_compatibility_for_natgrid_jsb_general_section(
                    new_jsb, data
                )
            return await self.create(new_jsb, actor)
        else:
            jsb = await self.get_by_id(
                data.jsb_id, allow_archived=False, tenant_id=tenant_id
            )
            if jsb is None:
                raise EntityNotFoundException(data.jsb_id, self._entity_type)

            jsb = set_natgrid_jsb_properties(jsb, data, form_status, actor)
            return await self.update(jsb, actor)

    async def get_work_locations_on_natgrid_jsb_id(
        self, jsb_ids: list[uuid.UUID]
    ) -> list[tuple[uuid.UUID, Optional[dict]]]:
        statement = select(
            NatGridJobSafetyBriefing.id,
            NatGridJobSafetyBriefing.contents["work_location"],  # type: ignore
        ).where(col(NatGridJobSafetyBriefing.id).in_(jsb_ids))
        work_locations = (await self.session.exec(statement)).all()
        return work_locations

    async def get_multiple_work_locations_on_natgrid_jsb_id(
        self, jsb_ids: list[uuid.UUID]
    ) -> list[tuple[uuid.UUID, Optional[dict]]]:
        statement = select(
            NatGridJobSafetyBriefing.id,
            NatGridJobSafetyBriefing.contents["work_location_with_voltage_info"],  # type: ignore
        ).where(col(NatGridJobSafetyBriefing.id).in_(jsb_ids))
        work_locations = (await self.session.exec(statement)).all()
        return work_locations

    async def get_barn_location_on_natgrid_jsb_id(
        self, jsb_ids: list[uuid.UUID]
    ) -> list[tuple[uuid.UUID, Any]]:
        statement = select(
            NatGridJobSafetyBriefing.id,
            NatGridJobSafetyBriefing.contents["barn_location"],  # type: ignore
        ).where(col(NatGridJobSafetyBriefing.id).in_(jsb_ids))
        barn_locations = (await self.session.exec(statement)).all()
        return barn_locations

    async def get_by_user_id(
        self,
        user_id: uuid.UUID,
        limit: Optional[int],
        allow_archived: bool = True,
        tenant_id: uuid.UUID | None = None,
    ) -> list[tuple[uuid.UUID, Optional[dict]]]:
        statement = select(
            NatGridJobSafetyBriefing.id,
            NatGridJobSafetyBriefing.contents["crew_sign_off"],  # type: ignore
        ).order_by(col(NatGridJobSafetyBriefing.created_at).desc())
        if tenant_id is not None:
            statement = statement.where(
                col(NatGridJobSafetyBriefing.tenant_id) == tenant_id
            )
        statement = statement.where(
            col(NatGridJobSafetyBriefing.created_by_id) == user_id
        )
        if not allow_archived:
            statement = statement.where(
                col(NatGridJobSafetyBriefing.archived_at) == None  # noqa
            )
        statement = statement.where(
            col(NatGridJobSafetyBriefing.status) != FormStatus.IN_PROGRESS
        )
        statement = statement.limit(limit if limit is not None else 5)
        result = (await self.session.exec(statement)).all()
        return result

    async def get_last_natgrid_jsb_by_user_id(
        self,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
        allow_archived: bool | None = True,
    ) -> NatGridJobSafetyBriefing | None:
        statement = (
            select(NatGridJobSafetyBriefing)
            .where(
                NatGridJobSafetyBriefing.created_by_id == user_id,
                NatGridJobSafetyBriefing.tenant_id == tenant_id,
            )
            .order_by(col(NatGridJobSafetyBriefing.created_at).desc())
        ).limit(1)
        if not allow_archived:
            statement = statement.where(
                col(NatGridJobSafetyBriefing.archived_at) == None  # noqa
            )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def reopen_natgrid_jsb(
        self, jsb_id: uuid.UUID, actor: User
    ) -> NatGridJobSafetyBriefing:
        if jsb_id is None:
            raise ValueError("NatGrid JSB Id is required")
        else:
            natgrid_jsb = await self.get_by_id(
                jsb_id, allow_archived=False, tenant_id=actor.tenant_id
            )
            if natgrid_jsb is None:
                raise EntityNotFoundException(jsb_id, self._entity_type)
            if natgrid_jsb.status != FormStatus.COMPLETE:
                raise ValueError("NatGrid Job Safety Briefing is not complete")
            natgrid_jsb.status = FormStatus.PENDING_SIGN_OFF
            contents = NatGridJobSafetyBriefingLayout.parse_obj(natgrid_jsb.contents)
            if contents.supervisor_sign_off is not None:
                contents.supervisor_sign_off = None
            natgrid_jsb.contents = jsonable_encoder(contents)
            natgrid_jsb.updated_at = datetime.datetime.now(datetime.timezone.utc)
            return await self.update(natgrid_jsb, actor)


def get_natgrid_briefing_date(
    jsb: NatGridJobSafetyBriefingLayout,
) -> datetime.date | None:
    date_for = (
        jsb.jsb_metadata.briefing_date_time.date()
        if jsb.jsb_metadata is not None
        else None
    )
    return date_for


def extract_natgrid_jsb_properties(
    jsb: NatGridJobSafetyBriefingLayout,
) -> tuple[datetime.date | None, uuid.UUID | None]:
    """
    Extracts the date_for and project_location_id from the NatGridJobSafetyBriefingLayout

    :param jsb: NatGridJobSafetyBriefingLayout
    :return: tuple of date_for and project_location_id
    """
    date_for = get_natgrid_briefing_date(jsb)
    project_location_id = (
        jsb.work_package_metadata.work_package_location_id
        if jsb.work_package_metadata is not None
        else None
    )

    return date_for, project_location_id


# For backward compatibility of this field for multi location
def set_backward_compatibility_for_natgrid_jsb_general_section(
    jsb: NatGridJobSafetyBriefing,
    jsb_layout: NatGridJobSafetyBriefingLayout,
) -> NatGridJobSafetyBriefing:
    # Safely handle work_location_with_voltage_info
    contents: Dict[str, Any] = jsb.contents or {}
    work_location_info: List[Dict[str, Any]] = contents.get(
        "work_location_with_voltage_info", [{}]
    )
    # Ensure first item exists and is a dictionary
    if not work_location_info:
        work_location_info = [{}]
    # Safely get or create the first work location entry
    new_work_location = work_location_info[0]
    # Handle created_at
    new_work_location["created_at"] = (
        new_work_location.get("created_at")
        or datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    # Safely add location details with null checks
    if jsb_layout.work_location:
        new_work_location["address"] = jsb_layout.work_location.address or ""
        new_work_location["city"] = jsb_layout.work_location.city or ""
        new_work_location["state"] = jsb_layout.work_location.state or ""
        new_work_location["landmark"] = jsb_layout.work_location.landmark or ""
        new_work_location["operating_hq"] = jsb_layout.work_location.operating_hq or ""
    # Handle medical information and vehicle number
    if jsb_layout.work_location and jsb_layout.work_location.vehicle_number:
        # Ensure medical_information exists
        contents["medical_information"] = contents.get("medical_information", {})
        contents["medical_information"][
            "vehicle_number"
        ] = jsb_layout.work_location.vehicle_number
    # Handle minimum approach distance
    if jsb_layout.work_location and jsb_layout.work_location.minimum_approach_distance:
        new_work_location.setdefault("voltage_information", {})
        new_work_location["voltage_information"].setdefault(
            "minimum_approach_distance", {}
        )
        min_approach = new_work_location["voltage_information"][
            "minimum_approach_distance"
        ]
        min_approach[
            "phase_to_phase"
        ] = jsb_layout.work_location.minimum_approach_distance
        min_approach["phase_to_ground"] = None
    # Handle GPS coordinates
    if jsb_layout.gps_coordinates:
        new_work_location.setdefault("gps_coordinates", {})
        gps_coords = jsb_layout.gps_coordinates[0]
        if gps_coords:
            new_work_location["gps_coordinates"]["latitude"] = float(
                gps_coords.latitude
            )
            new_work_location["gps_coordinates"]["longitude"] = float(
                gps_coords.longitude
            )
    # Handle voltage information
    if jsb_layout.voltage_info:
        new_work_location.setdefault("voltage_information", {})
        # Handle voltages
        if jsb_layout.voltage_info.voltages:
            new_work_location["voltage_information"].setdefault("voltage", {})
            voltage_info = new_work_location["voltage_information"]["voltage"]
            voltage_info["value"] = jsb_layout.voltage_info.voltages
            voltage_info["other"] = True
            voltage_info["id"] = str(uuid.uuid4())
        # Handle circuit
        if jsb_layout.voltage_info.circuit:
            new_work_location["circuit"] = jsb_layout.voltage_info.circuit
    # Update contents with modified work location
    contents["work_location_with_voltage_info"] = work_location_info
    jsb.contents = contents
    return jsb


def set_natgrid_jsb_properties(
    jsb: NatGridJobSafetyBriefing,
    jsb_layout: NatGridJobSafetyBriefingLayout,
    form_status: FormStatus | None,
    actor: User,
) -> NatGridJobSafetyBriefing:
    """
    Sets the date_for and project_location_id on the NatGridJobSafetyBriefing from the NatGridJobSafetyBriefingLayout
    """
    # For backward compatibility of this field
    if (
        jsb.contents is not None
        and jsb_layout.group_discussion
        and jsb_layout.group_discussion.group_discussion_notes
        and jsb.contents["critical_tasks_selections"]
    ):
        jsb.contents["critical_tasks_selections"][
            "special_precautions_notes"
        ] = jsb_layout.group_discussion.group_discussion_notes

    if jsb_layout.work_location:
        jsb = set_backward_compatibility_for_natgrid_jsb_general_section(
            jsb, jsb_layout
        )

    merged_jsb_layout = merge_non_none_fields(
        jsb_layout, NatGridJobSafetyBriefingLayout.parse_obj(jsb.contents)
    )
    date_for, project_location_id = extract_natgrid_jsb_properties(merged_jsb_layout)
    jsb.date_for = date_for if date_for is not None else jsb.date_for
    jsb.project_location_id = (
        project_location_id
        if project_location_id is not None
        else jsb.project_location_id
    )
    jsb.status = form_status if form_status is not None else FormStatus.IN_PROGRESS
    jsb.updated_at = datetime.datetime.now(datetime.timezone.utc)
    if (
        form_status == FormStatus.COMPLETE
        and merged_jsb_layout.crew_sign_off is not None
    ):
        now = datetime.datetime.now(datetime.timezone.utc)
        completion = Completion(
            completed_by_id=actor.id,
            completed_at=now,
        )
        merged_jsb_layout.completions = (
            []
            if merged_jsb_layout.completions is None
            else merged_jsb_layout.completions
        )
        merged_jsb_layout.completions.append(completion)
        if jsb.completed_at is None:
            jsb.completed_at = completion.completed_at
            jsb.completed_by_id = completion.completed_by_id
    jsb.contents = jsonable_encoder(merged_jsb_layout)

    return jsb
