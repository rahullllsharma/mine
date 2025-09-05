import copy
import datetime
import uuid
from collections import defaultdict
from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import desc
from sqlalchemy.orm import selectinload
from sqlmodel import col, select

from worker_safety_service.audit_trail import audit_reopen
from worker_safety_service.dal.crua_audit_manager import CRUAAuditableManager
from worker_safety_service.dal.exceptions.entity_not_found import (
    EntityNotFoundException,
)
from worker_safety_service.dal.utils import merge_non_none_fields
from worker_safety_service.models import (
    Activity,
    AsyncSession,
    FormStatus,
    GPSCoordinates,
    JobSafetyBriefing,
    JobSafetyBriefingLayout,
    LibraryRegion,
    Location,
    NatGridJobSafetyBriefingLayout,
    RecommendedTaskSelection,
    RiskLevel,
    User,
    WorkPackage,
)
from worker_safety_service.models.audit_events import AuditObjectType
from worker_safety_service.models.concepts import Completion, ControlSelection
from worker_safety_service.utils import assert_date


class JobSafetyBriefingManager(CRUAAuditableManager[JobSafetyBriefing]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(
            session=session,
            entity_type=JobSafetyBriefing,
            audit_object_type=AuditObjectType.job_safety_briefing,
        )

    def _normalize_save_control_assessment_selections(
        self, data: JobSafetyBriefingLayout
    ) -> None:
        """
        The legacy control_ids is going to be converted to the new format if provided.
        The control_selections is going to be converted to the legacy format if provided.
        In this case, the recommended and selected values will be set to their default value.
        If for some reason both are set an error is raised.
        """
        for control_assessment in data.control_assessment_selections or []:
            # if both are sent no need to normalize the data
            if (
                control_assessment.control_ids is not None
                and control_assessment.control_selections is not None
            ):
                return
            if control_assessment.control_ids is not None:
                control_assessment.control_selections = []
                for control_id in control_assessment.control_ids:
                    control_assessment.control_selections.append(
                        ControlSelection(id=control_id)
                    )
            elif control_assessment.control_selections is not None:
                control_assessment.control_ids = [
                    control_selection.id
                    for control_selection in control_assessment.control_selections
                ]

    async def _normalize_save_task_selections(
        self, data: JobSafetyBriefingLayout
    ) -> JobSafetyBriefingLayout:
        """
        Normalizes and updates task selections and recommended task selections.
        Handles scenarios with and without work_package_metadata.
        """
        # if recommended_task_selections is not None then return the data as is
        if data.recommended_task_selections:
            return data

        if data.work_package_metadata is None:
            return self._process_without_work_package(data)
        else:
            return await self._process_with_work_package(data)

    def _process_without_work_package(
        self, data: JobSafetyBriefingLayout
    ) -> JobSafetyBriefingLayout:
        """
        Handles scenarios when work_package_metadata is None.
        """
        return self._populate_recommended_task_selections_for_adhoc(data)

    async def _process_with_work_package(
        self, data: JobSafetyBriefingLayout
    ) -> JobSafetyBriefingLayout:
        """
        Handles scenarios when work_package_metadata is present.
        """
        if data.work_package_metadata:
            work_package_location_id = (
                data.work_package_metadata.work_package_location_id
            )
        else:
            return data
        location = await self.get_location_by_id(self.session, work_package_location_id)

        if location is None:
            raise ValueError(f"No location found for ID: {work_package_location_id}")

        briefing_date_time_date = get_briefing_date(data) or datetime.date.today()

        associated_activities = [
            activity
            for activity in location.activities
            if isinstance(activity, Activity)
            and activity.start_date <= briefing_date_time_date <= activity.end_date
        ]
        return self._populate_recommended_task_selections(data, associated_activities)

    def _populate_recommended_task_selections(
        self, data: JobSafetyBriefingLayout, activities: list[Activity] = []
    ) -> JobSafetyBriefingLayout:
        """
        Populates `recommended_task_selections` based on tasks in `activities` or `task_selections`.
        """
        if not data.task_selections:
            return data

        data.recommended_task_selections = []

        source_activities = activities

        existing_ids = set()
        task_selection_map = {task.id: task for task in data.task_selections or []}

        for activity in source_activities or []:
            for task in activity.tasks:
                if task.library_task_id in existing_ids:
                    continue

                selected_task = task_selection_map.get(task.id)
                recommended_task = RecommendedTaskSelection(
                    id=task.library_task_id,
                    name=(
                        selected_task.name if selected_task else None
                    ),  # Use name from task_selection if available
                    risk_level=(
                        selected_task.risk_level if selected_task else RiskLevel.UNKNOWN
                    ),
                    from_work_order=True,
                    selected=(
                        True
                        if task.library_task_id in task_selection_map.keys()
                        else False
                    ),  # Mark selected=True if task is in task_selections
                    recommended=True,
                )
                data.recommended_task_selections.append(recommended_task)
                existing_ids.add(task.library_task_id)
        return data

    def _populate_recommended_task_selections_for_adhoc(
        self, data: JobSafetyBriefingLayout
    ) -> JobSafetyBriefingLayout:
        """
        Populates `recommended_task_selections` based on tasks in `activities` or `task_selections`.
        """
        if not data.task_selections:
            return data

        data.recommended_task_selections = []

        source_activities = data.activities
        existing_ids = set()
        task_selection_map = {task.id: task for task in data.task_selections or []}

        for activity in source_activities or []:
            for task in activity.tasks:
                if task.id in existing_ids:
                    continue
                selected_task = task_selection_map.get(task.id)
                recommended_task = RecommendedTaskSelection(
                    id=task.id,
                    name=(
                        selected_task.name if selected_task else None
                    ),  # Use name from task_selection if available
                    risk_level=(
                        selected_task.risk_level if selected_task else RiskLevel.UNKNOWN
                    ),
                    recommended=True,
                    from_work_order=(
                        selected_task.from_work_order if selected_task else False
                    ),  # Use data from task_selection if available
                    selected=(
                        True if task.id in task_selection_map.keys() else False
                    ),  # Mark selected=True if task is in task_selections
                )
                data.recommended_task_selections.append(recommended_task)
                existing_ids.add(task.id)
        return data

    async def get_location_by_id(
        self, session: AsyncSession, location_id: uuid.UUID
    ) -> Location | None:
        """
        Retrieve a location by its ID using SQLAlchemy with asynchronous execution.
        """
        statement = (
            select(Location)
            .where(
                Location.id == location_id,
                col(Location.archived_at).is_(None),
            )
            .options(selectinload(Location.activities))
        )

        result = await session.execute(statement)
        return result.scalars().first()

    async def save(
        self,
        data: JobSafetyBriefingLayout,
        actor: User,
        tenant_id: uuid.UUID,
        token: Optional[str] = None,
    ) -> JobSafetyBriefing:
        self._normalize_save_control_assessment_selections(data)
        data = await self._normalize_save_task_selections(data)

        if data.jsb_id is None:
            date_for, project_location_id = extract_jsb_properties(data)

            if data.work_location and data.work_location.operating_hq is None:
                library_region = await get_library_region_from_project_location_id(
                    self.session, project_location_id, tenant_id
                )

                if data.work_location is None:
                    data.work_location = {}

                if library_region is not None:
                    data.work_location.operating_hq = library_region.name

            if date_for is None:
                date_for = datetime.date.today()

            encoded_data = jsonable_encoder(data)

            new_jsb = JobSafetyBriefing(
                tenant_id=tenant_id,
                date_for=date_for,
                project_location_id=project_location_id,
                contents=encoded_data,
                created_by_id=actor.id,
            )
            return await self.create(entity=new_jsb, actor=actor, token=token)
        else:
            jsb = await self.get_by_id(
                data.jsb_id, allow_archived=False, tenant_id=tenant_id
            )
            old_jsb = copy.deepcopy(jsb)

            if jsb is None:
                raise EntityNotFoundException(data.jsb_id, self._entity_type)

            """
                1. If conditions on nearest_medical_facilities and custom_nearest_medical_facilities
                are the quick fix for bugs WORK-3322 and WORK-3286.
                P.S as this is a quick fix and one of the field is mandatory ignored mypy issue.

                2. TODO: Proper fix involves:
                    a. Adding custom_nearest_medical_facility inside the nearest_medical_facility class in concepts.py.
                    b. Ensuring both variables are under the same field in JSB.
            """

            if data.custom_nearest_medical_facility is not None:
                jsb.contents["nearest_medical_facility"] = None  # type: ignore

            if data.nearest_medical_facility is not None:
                jsb.contents["custom_nearest_medical_facility"] = None  # type: ignore

            if data.work_location and data.work_location.operating_hq is None:
                library_region = await get_library_region_from_project_location_id(
                    self.session, jsb.project_location_id, tenant_id
                )

                if data.work_location is None:
                    data.work_location = {}

                if library_region is not None:
                    data.work_location.operating_hq = library_region.name

            jsb = set_jsb_properties(jsb, data)
            return await self.update(
                entity=jsb, actor=actor, old_entity=old_jsb, token=token
            )

    async def complete(
        self,
        data: JobSafetyBriefingLayout,
        actor: User,
        tenant_id: uuid.UUID,
        token: Optional[str] = None,
    ) -> JobSafetyBriefing:
        if data.jsb_id is None:
            raise ValueError("jsb_id is required")
        else:
            jsb = await self.get_by_id(
                data.jsb_id, allow_archived=False, tenant_id=tenant_id
            )
            old_jsb = copy.deepcopy(jsb)
            if jsb is None:
                raise EntityNotFoundException(data.jsb_id, self._entity_type)

            self._normalize_save_control_assessment_selections(data)

            now = datetime.datetime.now(datetime.timezone.utc)
            completion = Completion(completed_by_id=actor.id, completed_at=now)

            jsb = set_jsb_properties(jsb, data, completion)
            jsb.status = FormStatus.COMPLETE

            if jsb.completed_at is None:
                jsb.completed_by_id = completion.completed_by_id
                jsb.completed_at = completion.completed_at

            jsb.updated_at = now
            # TODO add validation
            return await self.update(
                entity=jsb, actor=actor, old_entity=old_jsb, token=token
            )

    @audit_reopen
    async def reopen(
        self, jsb_id: uuid.UUID, actor: User, token: Optional[str] = None
    ) -> JobSafetyBriefing:
        if jsb_id is None:
            raise ValueError("jsb_id is required")
        else:
            jsb = await self.get_by_id(
                jsb_id, allow_archived=False, tenant_id=actor.tenant_id
            )
            if jsb is None:
                raise EntityNotFoundException(jsb_id, self._entity_type)
            if jsb.status != FormStatus.COMPLETE:
                raise ValueError("Job Safety Briefing is not complete")
            jsb.status = FormStatus.IN_PROGRESS
            jsb.updated_at = datetime.datetime.now(datetime.timezone.utc)
            return await self.update(jsb, actor)

    async def get_job_safety_briefings_by_location(
        self,
        project_location_ids: list[uuid.UUID],
        date: datetime.date | None,
        tenant_id: uuid.UUID,
        filter_start_date: datetime.date | None = None,
        filter_end_date: datetime.date | None = None,
        allow_archived: bool = True,
    ) -> defaultdict[uuid.UUID, list[JobSafetyBriefing]]:
        stmt = (
            select(JobSafetyBriefing)
            .where(JobSafetyBriefing.tenant_id == tenant_id)
            .where(col(JobSafetyBriefing.project_location_id).in_(project_location_ids))
        )

        if allow_archived is False:
            stmt = stmt.where(col(JobSafetyBriefing.archived_at).is_(None))

        if date is not None:
            stmt = stmt.where(JobSafetyBriefing.date_for == date)
        if filter_start_date and filter_end_date:
            assert_date(filter_start_date)
            assert_date(filter_end_date)
            stmt = stmt.where(
                (JobSafetyBriefing.date_for >= filter_start_date)
                & (JobSafetyBriefing.date_for <= filter_end_date)
            )

        job_safety_briefings = (await self.session.exec(stmt)).all()
        items: defaultdict[uuid.UUID, list[JobSafetyBriefing]] = defaultdict(list)

        for jsb in job_safety_briefings:
            items[jsb.project_location_id].append(jsb)

        return items

    async def get_last_jsb_on_project_loc(
        self,
        tenant_id: uuid.UUID,
        project_location_id: uuid.UUID,
        allowed_archived: bool = False,
    ) -> JobSafetyBriefing | None:
        statement = (
            select(JobSafetyBriefing)
            .where(JobSafetyBriefing.tenant_id == tenant_id)
            .where(col(JobSafetyBriefing.completed_at).is_not(None))
            .where(JobSafetyBriefing.project_location_id == project_location_id)
            .order_by(desc(JobSafetyBriefing.completed_at))
        )

        if allowed_archived is True:
            statement.where(col(JobSafetyBriefing.archived_at).is_not(None))

        result = (await self.session.exec(statement)).first()

        if result is None:
            return None
        else:
            return result

    async def get_last_adhoc_jsb(
        self,
        tenant_id: uuid.UUID,
        actor: User,
        allowed_archived: bool = False,
    ) -> JobSafetyBriefing | None:
        statement = (
            select(JobSafetyBriefing)
            .where(JobSafetyBriefing.tenant_id == tenant_id)
            .where(col(JobSafetyBriefing.completed_at).is_not(None))
            .where(JobSafetyBriefing.created_by_id == actor.id)
            .where(col(JobSafetyBriefing.project_location_id).is_((None)))
            .order_by(desc(JobSafetyBriefing.completed_at))
        )

        if allowed_archived is True:
            statement.where(col(JobSafetyBriefing.archived_at).is_not(None))

        result = (await self.session.exec(statement)).first()

        return result

    async def get_last_jsb_on_user_id(
        self,
        tenant_id: uuid.UUID,
        actor: User,
        allowed_archived: bool = False,
    ) -> JobSafetyBriefing | None:
        statement = (
            select(JobSafetyBriefing)
            .where(JobSafetyBriefing.tenant_id == tenant_id)
            .where(col(JobSafetyBriefing.completed_at).is_not(None))
            .where(JobSafetyBriefing.created_by_id == actor.id)
            .order_by(desc(JobSafetyBriefing.completed_at))
        )

        if allowed_archived is True:
            statement.where(col(JobSafetyBriefing.archived_at).is_not(None))

        result = (await self.session.exec(statement)).first()

        if result is None:
            return None
        else:
            return result

    async def get_work_locations_on_jsb_id(
        self, jsb_ids: list[uuid.UUID]
    ) -> list[tuple[uuid.UUID, Optional[dict]]]:
        statement = select(
            JobSafetyBriefing.id,
            JobSafetyBriefing.contents["work_location"],  # type: ignore
        ).where(col(JobSafetyBriefing.id).in_(jsb_ids))
        work_locations = (await self.session.exec(statement)).all()
        return work_locations


def get_briefing_date(
    jsb: JobSafetyBriefingLayout | NatGridJobSafetyBriefingLayout,
) -> datetime.date | None:
    date_for = (
        jsb.jsb_metadata.briefing_date_time.date()
        if jsb.jsb_metadata is not None
        else None
    )
    return date_for


def extract_jsb_properties(
    jsb: JobSafetyBriefingLayout,
) -> tuple[datetime.date | None, uuid.UUID | None]:
    """
    Extracts the date_for and project_location_id from the JobSafetyBriefingLayout

    :param jsb: JobSafetyBriefingLayout
    :return: tuple of date_for and project_location_id
    """
    date_for = get_briefing_date(jsb)
    project_location_id = (
        jsb.work_package_metadata.work_package_location_id
        if jsb.work_package_metadata is not None
        else None
    )

    return date_for, project_location_id


def update_nearest_medical_facility(
    jsb_gps_coordinates: list[GPSCoordinates] | None,
    jsb_layout: JobSafetyBriefingLayout,
) -> JobSafetyBriefingLayout:
    if jsb_gps_coordinates != jsb_layout.gps_coordinates:
        jsb_layout.nearest_medical_facility = None

    return jsb_layout


def set_jsb_properties(
    jsb: JobSafetyBriefing,
    jsb_layout: JobSafetyBriefingLayout,
    completion: Completion | None = None,
) -> JobSafetyBriefing:
    """
    Sets the date_for and project_location_id on the JobSafetyBriefing from the JobSafetyBriefingLayout
    """
    current_jsb = JobSafetyBriefingLayout.parse_obj(jsb.contents)
    merged_jsb_layout = merge_non_none_fields(jsb_layout, current_jsb)
    date_for, project_location_id = extract_jsb_properties(merged_jsb_layout)
    jsb.date_for = date_for if date_for is not None else jsb.date_for
    jsb.project_location_id = (
        project_location_id
        if project_location_id is not None
        else jsb.project_location_id
    )
    jsb.updated_at = datetime.datetime.now(datetime.timezone.utc)
    merged_jsb_layout = update_nearest_medical_facility(
        current_jsb.gps_coordinates, merged_jsb_layout
    )
    if completion:
        merged_jsb_layout.completions = (
            []
            if merged_jsb_layout.completions is None
            else merged_jsb_layout.completions
        )
        merged_jsb_layout.completions.append(completion)
    jsb.contents = jsonable_encoder(merged_jsb_layout)
    return jsb


async def get_library_region_from_project_location_id(
    session: AsyncSession, project_location_id: uuid.UUID | None, tenant_id: uuid.UUID
) -> LibraryRegion | None:
    statement = (
        select(LibraryRegion)
        .join(WorkPackage)
        .join(Location)
        .where(
            Location.id == project_location_id,
            col(Location.archived_at).is_(None),
            Location.project_id == WorkPackage.id,
            WorkPackage.tenant_id == tenant_id,
            LibraryRegion.id == WorkPackage.region_id,
        )
    )

    return (await session.exec(statement)).first()
