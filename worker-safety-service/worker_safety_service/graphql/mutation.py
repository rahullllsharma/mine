import json
import uuid
from datetime import datetime, timezone
from typing import Optional

import strawberry
from fastapi.encoders import jsonable_encoder

from worker_safety_service import get_logger
from worker_safety_service.constants import GeneralConstants
from worker_safety_service.context import Info
from worker_safety_service.dal.jsb import get_briefing_date
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.graphql.common.types import (
    EntityConfigurationType,
    MyTenantType,
    UserPreferenceType,
)
from worker_safety_service.graphql.permissions import (
    CanAddPreferences,
    CanArchiveAllWorkPackages,
    CanConfigureTheApplication,
    CanCreateActivity,
    CanCreateProject,
    CanCreateSiteCondition,
    CanCreateTenant,
    CanDeleteNatGridJobSafetyBriefing,
    CanDeleteProject,
    CanDeleteReport,
    CanEditActivity,
    CanEditSiteCondition,
    CanEditTask,
    CanEditTenant,
    CanReopenEBO,
    CanSaveReport,
    CanUpdateProject,
)
from worker_safety_service.graphql.types import (
    ActivityType,
    AddActivityTasksInput,
    CreateActivityInput,
    CreateInsightInput,
    CreateProjectInput,
    CreateSiteConditionInput,
    CreateTenantInput,
    DailyReportType,
    EditActivityInput,
    EditProjectInput,
    EditSiteConditionInput,
    EditTaskInput,
    EditTenantInput,
    EnergyBasedObservationInput,
    EnergyBasedObservationType,
    EntityConfigurationInput,
    FormsNotificationsInput,
    FormStatus,
    FormStatusInput,
    GPSCoordinatesInput,
    IngestSubmitType,
    IngestType,
    InsightType,
    JobSafetyBriefingType,
    LocationHazardControlSettingsInput,
    LocationReturnType,
    NatGridJobSafetyBriefingInput,
    NatGridJobSafetyBriefingType,
    ProjectType,
    RecalculateInput,
    RemoveActivityTasksInput,
    SaveDailyReportInput,
    SaveJobSafetyBriefingInput,
    SignedPostPolicy,
    SiteConditionType,
    TaskType,
    UpdateInsightInput,
)
from worker_safety_service.models import (
    Activity,
    ActivityEdit,
    Location,
    LocationCreate,
    LocationEdit,
    LocationHazardControlSettingsCreate,
    SiteConditionCreate,
    UserPreferenceEntityType,
    WorkPackageCreate,
    WorkPackageEdit,
)
from worker_safety_service.types import Point

logger = get_logger(__name__)


@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[CanCreateProject])
    async def create_project(
        self, info: Info, project: CreateProjectInput
    ) -> ProjectType:
        project_create = WorkPackageCreate(
            name=project.name,
            start_date=project.start_date,
            end_date=project.end_date,
            status=project.status,
            external_key=project.external_key or project.number,
            description=project.description,
            region_id=project.library_region_id,
            division_id=project.library_division_id,
            # FIXME: To be deprecated
            work_type_id=project.library_project_type_id,
            work_type_ids=project.work_type_ids,
            manager_id=project.manager_id,
            primary_assigned_user_id=project.supervisor_id,
            additional_assigned_users_ids=project.additional_supervisors or [],
            contractor_id=project.contractor_id,
            engineer_name=project.engineer_name,
            zip_code=project.project_zip_code,
            contract_reference=project.contract_reference,
            contract_name=project.contract_name,
            asset_type_id=project.library_asset_type_id,
            tenant_id=info.context.user.tenant_id,
            location_creates=[
                LocationCreate(
                    name=location.name,
                    geom=Point(location.longitude, location.latitude),
                    supervisor_id=location.supervisor_id,
                    additional_supervisor_ids=location.additional_supervisors or [],
                    external_key=location.external_key or None,
                    tenant_id=info.context.user.tenant_id,
                )
                for location in project.locations or []
            ],
        )
        proj = await info.context.projects.create_work_packages(
            projects=[project_create],
            user=info.context.user,
        )

        return ProjectType.from_orm(proj[0])

    @strawberry.mutation(permission_classes=[CanUpdateProject])
    async def edit_project(self, info: Info, project: EditProjectInput) -> ProjectType:
        db_project = await info.context.projects.me.load(project.id)
        if not db_project:
            raise ValueError("Project ID not found")

        project_mutation = WorkPackageEdit(
            name=project.name,
            start_date=project.start_date,
            end_date=project.end_date,
            status=project.status,
            external_key=project.external_key or project.number,
            description=project.description,
            region_id=project.library_region_id,
            division_id=project.library_division_id,
            # FIXME: To be deprecated
            work_type_id=project.library_project_type_id,
            work_type_ids=project.work_type_ids,
            manager_id=project.manager_id,
            primary_assigned_user_id=project.supervisor_id,
            additional_assigned_users_ids=project.additional_supervisors or [],
            contractor_id=project.contractor_id,
            engineer_name=project.engineer_name,
            zip_code=project.project_zip_code,
            contract_reference=project.contract_reference,
            contract_name=project.contract_name,
            asset_type_id=project.library_asset_type_id,
        )
        project_location_edit = [
            LocationEdit(
                id=location.id,
                name=location.name,
                geom=Point(location.longitude, location.latitude),
                supervisor_id=location.supervisor_id,
                additional_supervisor_ids=location.additional_supervisors or [],
                external_key=location.external_key or None,
                tenant_id=info.context.user.tenant_id,
            )
            for location in project.locations or []
        ]

        await info.context.projects.edit_project_with_locations(
            db_project,
            project_mutation,
            project_location_edit,
            user=info.context.user,
        )

        return ProjectType.from_orm(db_project)

    @strawberry.mutation(permission_classes=[CanDeleteProject])
    async def delete_project(self, info: Info, id: uuid.UUID) -> bool:
        db_project = await info.context.projects.me.load(id)
        if not db_project:
            raise ValueError("Project ID not found")

        await info.context.projects.archive_project(
            db_project,
            user=info.context.user,
        )

        return True

    @strawberry.mutation(permission_classes=[CanArchiveAllWorkPackages])
    async def archive_all_projects(self, info: Info) -> int:
        num_of_projects_archived = (
            await info.context.projects.archive_all_tenant_projects(
                tenant_id=info.context.tenant_id, user=info.context.user
            )
        )

        return num_of_projects_archived

    @strawberry.mutation(permission_classes=[CanCreateActivity])
    async def create_activity(
        self, info: Info, activity_data: CreateActivityInput
    ) -> ActivityType:
        new_activity = activity_data.to_pydantic()
        if len(new_activity.tasks) <= 0:
            raise ValueError("Activity must be created with tasks")
        (
            db_activity,
            created_tasks,
        ) = await info.context.project_locations.create_activity(
            new_activity,
            user=info.context.user,
        )

        return ActivityType.from_orm(db_activity)

    @strawberry.mutation(permission_classes=[CanEditActivity])
    async def edit_activity(
        self, info: Info, activity_data: EditActivityInput
    ) -> Optional[ActivityType]:
        existing_activity: Optional[Activity] = await info.context.activities.me.load(
            activity_data.id
        )
        if not existing_activity:
            raise ResourceReferenceException("The activity is not found!")

        edited_activity_data = ActivityEdit(
            id=activity_data.id,
            name=activity_data.name or existing_activity.name,
            is_critical=activity_data.is_critical,
            critical_description=activity_data.critical_description,
            start_date=activity_data.start_date or existing_activity.start_date,
            end_date=activity_data.end_date or existing_activity.end_date,
            status=activity_data.status or existing_activity.status,
            crew_id=activity_data.crew_id,
            library_activity_type_id=activity_data.library_activity_type_id,
            # These fields cannot be edited
            location_id=existing_activity.location_id,
        )

        updated_activity, _ = await info.context.activities.edit_activity(
            existing_activity,
            edited_activity_data,
            user=info.context.user,
        )

        if updated_activity:
            return ActivityType.from_orm(updated_activity)

        return None

    @strawberry.mutation(permission_classes=[CanEditActivity])
    async def delete_activity(self, info: Info, id: uuid.UUID) -> bool:
        existing_activity: Optional[Activity] = await info.context.activities.me.load(
            id
        )

        if not existing_activity:
            raise ResourceReferenceException("The activity is not found!")

        if existing_activity.archived_at is not None:
            raise ValueError("Activity has already been archived!")

        archive_status = await info.context.activities.archive_activity(
            db_activity=existing_activity, user=info.context.user
        )

        return archive_status

    @strawberry.mutation(permission_classes=[CanEditActivity])
    async def add_supervisor_to_activity(
        self, info: Info, activity_id: uuid.UUID, supervisor_id: uuid.UUID
    ) -> bool:
        return await info.context.supervisors.add_supervisor_to_activity(
            activity_id, supervisor_id
        )

    @strawberry.mutation(permission_classes=[CanEditActivity])
    async def remove_supervisor_from_activity(
        self, info: Info, activity_id: uuid.UUID, supervisor_id: uuid.UUID
    ) -> bool:
        return await info.context.supervisors.remove_supervisor_from_activity(
            activity_id, supervisor_id
        )

    @strawberry.mutation(permission_classes=[CanEditTask])
    async def edit_task(self, info: Info, task_data: EditTaskInput) -> TaskType:
        task_info = await info.context.tasks.me.load(task_data.id)
        if not task_info:
            raise ValueError("Task ID not found.")

        _, db_task = task_info
        await info.context.project_locations.edit_task(
            db_task,
            [hazard.to_pydantic() for hazard in task_data.hazards],
            info.context.user,
        )

        return TaskType.from_orm(db_task)

    @strawberry.mutation(permission_classes=[CanEditTask])
    async def delete_task(self, info: Info, id: uuid.UUID) -> bool:
        task_info = await info.context.tasks.me.load(id)
        if not task_info:
            raise ValueError("Task ID not found.")

        _, db_task = task_info

        # For backwards compatibility, only perform this check for
        # tasks that are linked to an activity
        if db_task.activity_id:
            num_of_active_tasks_for_activity = (
                await info.context.activities.task_count.load(db_task.activity_id)
            )
            if num_of_active_tasks_for_activity <= 1:
                raise ValueError("Cannot delete this activity's only task!")

        await info.context.project_locations.archive_task(db_task, info.context.user)

        return True

    @strawberry.mutation(permission_classes=[CanCreateSiteCondition])
    async def create_site_condition(
        self, info: Info, data: CreateSiteConditionInput
    ) -> SiteConditionType:
        location = await info.context.project_locations.me.load(data.location_id)
        if not location:
            raise ValueError("Project Location ID not found.")

        new_site_condition = SiteConditionCreate(
            location_id=location.id,
            library_site_condition_id=data.library_site_condition_id,
            is_manually_added=True,
        )

        site_condition = await info.context.site_conditions.create_site_condition(
            new_site_condition,
            hazards=[hazard.to_pydantic() for hazard in data.hazards],
            user=info.context.user,
        )

        return SiteConditionType.from_orm(site_condition)

    @strawberry.mutation(permission_classes=[CanEditSiteCondition])
    async def edit_site_condition(
        self, info: Info, data: EditSiteConditionInput
    ) -> SiteConditionType:
        site_condition_info = await info.context.site_conditions.manually_added.load(
            data.id
        )
        if not site_condition_info:
            raise ValueError("Site condition ID not found.")

        _, site_condition = site_condition_info
        await info.context.project_locations.edit_site_condition(
            site_condition,
            [hazard.to_pydantic() for hazard in data.hazards],
            info.context.user,
        )

        # WS-882: Does not need to be changed since only the Hazards are edited.

        return SiteConditionType.from_orm(site_condition)

    @strawberry.mutation(permission_classes=[CanEditSiteCondition])
    async def delete_site_condition(self, info: Info, id: uuid.UUID) -> bool:
        try:
            await info.context.site_conditions.archive_site_condition(
                id, info.context.user
            )
            return True
        except ResourceReferenceException:
            raise ValueError("Site condition ID not found.")

    @strawberry.mutation(
        permission_classes=[CanSaveReport],
        description="Save partial submissions of the job safety briefing",
    )
    async def save_job_safety_briefing(
        self, info: Info, job_safety_briefing_input: SaveJobSafetyBriefingInput
    ) -> JobSafetyBriefingType:
        jsb_data = job_safety_briefing_input.to_pydantic()
        encoded_data = jsonable_encoder(jsb_data)
        if (
            encoded_data["work_package_metadata"] is None
            and encoded_data["gps_coordinates"]
        ):
            latitude = float(encoded_data["gps_coordinates"][0]["latitude"])
            longitude = float(encoded_data["gps_coordinates"][0]["longitude"])
            location_name = encoded_data["work_location"]["address"]
            geom = Point(
                longitude,
                latitude,
            )
            tenant_id = info.context.user.tenant_id
            location_data = Location(
                geom=geom,
                tenant_id=tenant_id,
                name=location_name,
                additional_supervisor_ids=[],
                clustering=[],
            )
            locations = await info.context.project_locations.create_locations(
                [location_data]
            )
            location = locations[0]
            date = get_briefing_date(jsb_data)
            if date is not None:
                logger.info(
                    "Evaluating location save_job_safety_briefing",
                    location_id=location.id,
                    date=date,
                )
                await (
                    info.context.background_site_condition_evaluator.evalulate_location(
                        location, date
                    )
                )

        jsb = await info.context.job_safety_briefings.save_job_safety_briefing(
            actor=info.context.user,
            data=jsb_data,
            token=info.context.token,
        )
        if jsb_data.jsb_id and jsb_data.crew_sign_off:
            await info.context.jsb_supervisors.update_supervisor_jsb_data(
                jsb_data.jsb_id, jsb_data.crew_sign_off
            )

        return JobSafetyBriefingType.from_orm(jsb)

    @strawberry.mutation(
        permission_classes=[CanSaveReport],
        description="Save submissions of the Natgrid job safety briefing",
    )
    async def save_natgrid_job_safety_briefing(
        self,
        info: Info,
        natgrid_job_safety_briefing: NatGridJobSafetyBriefingInput,
        form_status: Optional[FormStatusInput] = None,
        notification_input: Optional[FormsNotificationsInput] = None,
    ) -> NatGridJobSafetyBriefingType:
        jsb_data = natgrid_job_safety_briefing.to_pydantic()
        encoded_data = jsonable_encoder(jsb_data)
        notification_title = "Pending Sign Off"
        work_location_with_voltage_info = encoded_data.get(
            "work_location_with_voltage_info", []
        )
        if (
            encoded_data["work_package_metadata"] is None
            and work_location_with_voltage_info
        ):
            for work_location in work_location_with_voltage_info:
                latitude = float(work_location["gps_coordinates"].get("latitude"))
                longitude = float(work_location["gps_coordinates"].get("longitude"))
                location_name = work_location.get("address")
                if latitude and longitude and location_name:
                    tenant_id = info.context.user.tenant_id
                    geom = Point(longitude, latitude)
                    location_data = Location(
                        geom=geom,
                        tenant_id=tenant_id,
                        name=location_name,
                        additional_supervisor_ids=[],
                        clustering=[],
                    )
                    locations = await info.context.project_locations.create_locations(
                        [location_data]
                    )
                    location = locations[0]
                    notification_title = str(location_name)
                    date = get_briefing_date(jsb_data)
                    if date is not None:
                        logger.info(
                            "Evaluating location save_natgrid_job_safety_briefing",
                            location_id=location.id,
                            date=date,
                        )
                        await info.context.background_site_condition_evaluator.evalulate_location(
                            location, date
                        )
        form_status_value = None
        if form_status is not None:
            form_status_value = form_status.status

        ng_jsb_work_type_id = (
            await info.context.work_types.get_work_type_by_code_and_tenant(
                GeneralConstants.NATGRID_GENERIC_JSB_CODE, info.context.user.tenant_id
            )
        )
        jsb = await info.context.natgrid_job_safety_briefings.save_natgrid_job_safety_briefing(
            actor=info.context.user,
            data=jsb_data,
            form_status=form_status_value,
            work_type_id=ng_jsb_work_type_id,
        )

        if notification_input is not None:
            if form_status_value == "pending_sign_off":
                user = info.context.user
                crew_member_name = f"{user.first_name} {user.last_name}"
                created_at_utc = datetime.now(timezone.utc)
                work_location = None
                if jsb is not None and jsb.contents is not None:
                    work_location = jsb.contents["work_location"]

                if work_location and work_location["address"]:
                    notification_title = work_location["address"]

                if notification_input.created_at is not None:
                    created_at_utc = notification_input.created_at

                contents = {
                    "title": notification_title,
                    "message": f"Please sign off and complete Job Safety Briefing submitted by crew member {crew_member_name}",
                    "data": {
                        "created_at": created_at_utc.isoformat(),
                        "form_id": str(jsb.id),
                    },
                }
                str_content = json.dumps(contents)

                receiver_id = notification_input.receiver_ids[0].id
                form_type = notification_input.form_type
                notification_type = notification_input.notification_type

                await info.context.background_notifications_update.create_notifications(
                    contents=str_content,
                    form_type=form_type,
                    sender_id=user.id,
                    receiver_id=receiver_id,
                    notification_type=notification_type,
                    created_at=created_at_utc,
                )

        return NatGridJobSafetyBriefingType.from_orm(jsb)

    @strawberry.mutation(
        permission_classes=[CanDeleteNatGridJobSafetyBriefing],
        description="Mark the Natgrid job safety briefing as deleted",
    )
    async def delete_natgrid_job_safety_briefing(
        self, info: Info, id: uuid.UUID
    ) -> bool:
        await info.context.natgrid_job_safety_briefings.archive_natgrid_job_safety_briefing(
            jsb_id=id, user=info.context.user
        )
        return True

    @strawberry.mutation(
        permission_classes=[CanSaveReport],
        description="Mark the natgrid job safety briefing as reopened",
    )
    async def reopen_natgrid_job_safety_briefing(
        self, info: Info, id: uuid.UUID
    ) -> NatGridJobSafetyBriefingType:
        jsb = await info.context.natgrid_job_safety_briefings.reopen_natgrid_job_safety_briefing(
            jsb_id=id,
            user=info.context.user,
        )
        return NatGridJobSafetyBriefingType.from_orm(jsb)

    @strawberry.mutation(
        permission_classes=[CanSaveReport],
        description="Validate and save the job safety briefing and mark it complete",
    )
    async def complete_job_safety_briefing(
        self, info: Info, job_safety_briefing_input: SaveJobSafetyBriefingInput
    ) -> JobSafetyBriefingType:
        jsb_data = job_safety_briefing_input.to_pydantic()

        jsb = await info.context.job_safety_briefings.complete_job_safety_briefing(
            actor=info.context.user,
            data=jsb_data,
            token=info.context.token,
        )
        if jsb_data.jsb_id and jsb_data.crew_sign_off:
            await info.context.jsb_supervisors.update_supervisor_jsb_data(
                jsb_data.jsb_id, jsb_data.crew_sign_off
            )

        return JobSafetyBriefingType.from_orm(jsb)

    @strawberry.mutation(
        permission_classes=[CanDeleteReport],
        description="Mark the job safety briefing as deleted",
    )
    async def delete_job_safety_briefing(self, info: Info, id: uuid.UUID) -> bool:
        await info.context.job_safety_briefings.archive_job_safety_briefing(
            jsb_id=id, user=info.context.user, token=info.context.token
        )
        return True

    @strawberry.mutation(
        permission_classes=[CanSaveReport],
        description="Mark the job safety briefing as reopened",
    )
    async def reopen_job_safety_briefing(
        self, info: Info, id: uuid.UUID
    ) -> JobSafetyBriefingType:
        jsb = await info.context.job_safety_briefings.reopen_job_safety_briefing(
            jsb_id=id, user=info.context.user, token=info.context.token
        )
        return JobSafetyBriefingType.from_orm(jsb)

    @strawberry.mutation(permission_classes=[CanSaveReport])
    async def save_daily_report(
        self, info: Info, daily_report_input: SaveDailyReportInput
    ) -> DailyReportType:
        dailySourceInfo = None
        if daily_report_input.dailySourceInfo:
            dailySourceInfo = daily_report_input.dailySourceInfo.to_pydantic()
        work_schedule = None
        if daily_report_input.work_schedule:
            work_schedule = daily_report_input.work_schedule.to_pydantic()
        task_selection = None
        if daily_report_input.task_selection:
            task_selection = daily_report_input.task_selection.to_pydantic()
        job_hazard_analysis = None
        if daily_report_input.job_hazard_analysis:
            job_hazard_analysis = daily_report_input.job_hazard_analysis.to_pydantic()
        crew = None
        if daily_report_input.crew:
            crew = daily_report_input.crew.to_pydantic()
        additional_information = None
        if daily_report_input.additional_information:
            additional_information = (
                daily_report_input.additional_information.to_pydantic()
            )
        attachments = None
        if daily_report_input.attachments:
            attachments = daily_report_input.attachments.to_pydantic()

        daily_report = await info.context.daily_reports.save_daily_report(
            daily_report_id=daily_report_input.id,
            project_location_id=daily_report_input.project_location_id,
            date=daily_report_input.date,
            work_schedule=work_schedule,
            task_selection=task_selection,
            job_hazard_analysis=job_hazard_analysis,
            safety_and_compliance=daily_report_input.safety_and_compliance,
            crew=crew,
            attachments=attachments,
            additional_information=additional_information,
            created_by=info.context.user,
            dailySourceInfo=dailySourceInfo,
            token=info.context.token,
        )
        return DailyReportType.from_orm(daily_report)

    @strawberry.mutation(permission_classes=[CanSaveReport])
    async def update_daily_report_status(
        self, info: Info, id: uuid.UUID, status: FormStatus
    ) -> DailyReportType:
        daily_report = await info.context.daily_reports.get_daily_report(id)
        if not daily_report:
            raise ValueError("Daily Report ID not found.")

        await info.context.daily_reports.update_status(
            user=info.context.user,
            daily_report=daily_report,
            new_status=status,
            token=info.context.token,
        )
        return DailyReportType.from_orm(daily_report)

    @strawberry.mutation(permission_classes=[CanDeleteReport])
    async def delete_daily_report(self, info: Info, id: uuid.UUID) -> bool:
        daily_report = await info.context.daily_reports.get_daily_report(id)
        if not daily_report:
            raise ValueError("Daily Report ID not found.")

        await info.context.daily_reports.archive_daily_report(
            daily_report=daily_report,
            user=info.context.user,
            token=info.context.token,
        )
        return True

    @strawberry.mutation
    async def file_upload_policies(
        self, info: Info, count: int = 1
    ) -> list[SignedPostPolicy]:
        if count < 1:
            raise ValueError("count must be greater than zero")
        if count > 25:
            raise ValueError("count must be less than 25")

        policies = await info.context.files.get_upload_policies(count)
        return [SignedPostPolicy.from_policy(policy) for policy in policies]

    @strawberry.mutation(permission_classes=[CanConfigureTheApplication])
    async def configure_tenant(
        self,
        info: Info,
        entity_configuration: EntityConfigurationInput,
    ) -> EntityConfigurationType:
        configs = entity_configuration.to_pydantic()
        await info.context.configurations.update_section(configs)

        new_config = await info.context.configurations.get_section(configs.key)
        ret = EntityConfigurationType.from_pydantic(new_config)
        return ret

    @strawberry.mutation(permission_classes=[CanCreateTenant])
    async def create_tenant(
        self,
        info: Info,
        tenant_create: CreateTenantInput,
    ) -> MyTenantType | None:
        tenant = await info.context.tenants.create_tenant(tenant_create.to_pydantic())
        return MyTenantType.from_orm(tenant) if tenant else None

    @strawberry.mutation(permission_classes=[CanEditTenant])
    async def edit_tenant(
        self, info: Info, tenant_edit: EditTenantInput
    ) -> MyTenantType:
        tenant = await info.context.tenants.edit_tenant(tenant_edit.to_pydantic())
        return MyTenantType.from_orm(tenant)

    @strawberry.field(permission_classes=[CanConfigureTheApplication])
    async def ingest_csv(
        self, info: Info, key: IngestType, body: str, delimiter: str = ","
    ) -> IngestSubmitType:
        ingested = await info.context.ingest.ingest(key, body, delimiter=delimiter)
        return IngestSubmitType(
            key=key,
            added=jsonable_encoder(ingested.added),
            updated=jsonable_encoder(ingested.updated),
            deleted=jsonable_encoder(ingested.deleted),
        )

    @strawberry.field(permission_classes=[CanConfigureTheApplication])
    async def recalculate(
        self, info: Info, recalculate_input: RecalculateInput
    ) -> None:
        trigger = recalculate_input.trigger.value
        # could also use trigger_reactor & a background task
        await info.context.risk_model_reactor.add(trigger(recalculate_input.id))

    @strawberry.mutation(permission_classes=[CanCreateActivity])
    async def add_location_hazard_control_settings(
        self,
        info: Info,
        location_hazard_control_setting_inputs: list[
            LocationHazardControlSettingsInput
        ],
    ) -> None:
        location_hazard_control_setting_data: list[
            LocationHazardControlSettingsCreate
        ] = []
        for (
            location_hazard_control_setting_input
        ) in location_hazard_control_setting_inputs:
            location_hazard_control_setting_data.append(
                LocationHazardControlSettingsCreate(
                    location_id=location_hazard_control_setting_input.location_id,
                    library_hazard_id=location_hazard_control_setting_input.library_hazard_id,
                    library_control_id=location_hazard_control_setting_input.library_control_id,
                )
            )

        return await info.context.library.add_location_hazard_control_settings(
            location_hazard_control_setting_data,
            info.context.user.id,
        )

    @strawberry.mutation(permission_classes=[CanCreateActivity])
    async def remove_location_hazard_control_settings(
        self,
        info: Info,
        location_hazard_control_setting_ids: list[uuid.UUID] = [],
    ) -> None:
        return await info.context.library.remove_location_hazard_control_settings(
            location_hazard_control_setting_ids
        )

    @strawberry.mutation(permission_classes=[CanSaveReport])
    async def save_energy_based_observation(
        self,
        info: Info,
        energy_based_observation_input: EnergyBasedObservationInput,
        id: uuid.UUID | None = None,
    ) -> EnergyBasedObservationType:
        ebo_data = energy_based_observation_input.to_pydantic()

        ebo = (
            await info.context.energy_based_observations.save_energy_based_observation(
                id=id,
                actor=info.context.user,
                data=ebo_data,
                token=info.context.token,
            )
        )

        return EnergyBasedObservationType.from_orm(ebo)

    @strawberry.mutation(permission_classes=[CanSaveReport])
    async def complete_energy_based_observation(
        self,
        info: Info,
        id: uuid.UUID,
        energy_based_observation_input: EnergyBasedObservationInput,
    ) -> EnergyBasedObservationType:
        ebo_data = energy_based_observation_input.to_pydantic()

        ebo = await info.context.energy_based_observations.complete_energy_based_observation(
            ebo_id=id, actor=info.context.user, data=ebo_data, token=info.context.token
        )

        return EnergyBasedObservationType.from_orm(ebo)

    @strawberry.mutation(permission_classes=[CanDeleteReport])
    async def delete_energy_based_observation(self, info: Info, id: uuid.UUID) -> bool:
        await info.context.energy_based_observations.archive_energy_based_observation(
            ebo_id=id, user=info.context.user, token=info.context.token
        )

        return True

    @strawberry.mutation(permission_classes=[CanReopenEBO])
    async def reopen_energy_based_observation(
        self, info: Info, id: uuid.UUID
    ) -> EnergyBasedObservationType:
        ebo = await info.context.energy_based_observations.reopen_energy_based_observation(
            ebo_id=id, user=info.context.user, token=info.context.token
        )
        return EnergyBasedObservationType.from_orm(ebo)

    @strawberry.mutation(permission_classes=[CanConfigureTheApplication])
    async def create_insight(
        self, info: Info, create_input: CreateInsightInput
    ) -> InsightType:
        db_insight = await info.context.insight.create_insight(
            create_input=create_input.to_pydantic()
        )
        return InsightType.from_orm(db_insight)

    @strawberry.mutation(permission_classes=[CanConfigureTheApplication])
    async def update_insight(
        self, info: Info, id: uuid.UUID, update_input: UpdateInsightInput
    ) -> InsightType:
        db_insight = await info.context.insight.update_insight(
            id=id, update_input=update_input.to_pydantic()
        )
        return InsightType.from_orm(db_insight)

    @strawberry.mutation(permission_classes=[CanConfigureTheApplication])
    async def archive_insight(self, info: Info, id: uuid.UUID) -> bool:
        return await info.context.insight.archive_insight(id=id)

    @strawberry.mutation(permission_classes=[CanConfigureTheApplication])
    async def reorder_insights(
        self, info: Info, ordered_ids: list[uuid.UUID], limit: Optional[int] = None
    ) -> list[InsightType]:
        reordered_insights = await info.context.insight.reorder_insights(
            ordered_ids=ordered_ids, limit=limit
        )
        return [InsightType.from_orm(insight) for insight in reordered_insights]

    @strawberry.mutation(permission_classes=[CanAddPreferences])
    async def save_user_preferences(
        self,
        info: Info,
        data: str,
        entity_type: UserPreferenceEntityType,
        user_id: uuid.UUID,
    ) -> UserPreferenceType:
        contents = json.loads(data)
        result = await info.context.user_preference.save(contents, entity_type, user_id)
        return UserPreferenceType.from_orm(result)

    @strawberry.mutation(permission_classes=[CanEditActivity])
    async def add_tasks_to_activity(
        self, info: Info, id: uuid.UUID, new_tasks: AddActivityTasksInput
    ) -> ActivityType:
        existing_activity: Optional[Activity] = await info.context.activities.me.load(
            key=id
        )
        if not existing_activity:
            raise ResourceReferenceException("The activity is not found!")

        updated_activity = (
            await info.context.activities.add_new_tasks_to_existing_activity(
                db_activity=existing_activity,
                new_tasks=new_tasks.to_pydantic(),
                user=info.context.user,
            )
        )

        return ActivityType.from_orm(updated_activity)

    @strawberry.mutation(permission_classes=[CanEditActivity])
    async def remove_tasks_from_activity(
        self,
        info: Info,
        id: uuid.UUID,
        task_ids_to_be_removed: RemoveActivityTasksInput,
    ) -> Optional[ActivityType]:
        existing_activity: Optional[Activity] = await info.context.activities.me.load(
            key=id
        )
        if not existing_activity:
            raise ResourceReferenceException("The activity is not found!")

        updated_activity = (
            await info.context.activities.remove_tasks_from_existing_activity(
                db_activity=existing_activity,
                task_ids_to_be_removed=task_ids_to_be_removed.to_pydantic(),
                user=info.context.user,
            )
        )

        return ActivityType.from_orm(updated_activity)

    @strawberry.mutation(permission_classes=[CanSaveReport])
    async def create_location_from_lat_lon(
        self,
        info: Info,
        gps_coordinates: GPSCoordinatesInput,
        name: Optional[str] = None,
        date: Optional[datetime] = None,
    ) -> LocationReturnType:
        gps_coordinates_data = gps_coordinates.to_pydantic()
        tenant_id = info.context.user.tenant_id
        geom = Point(gps_coordinates_data.longitude, gps_coordinates_data.latitude)
        location_data = Location(
            geom=geom,
            tenant_id=tenant_id,
            name=name,
            additional_supervisor_ids=[],
            clustering=[],
        )
        locations = await info.context.project_locations.create_locations(
            [location_data]
        )
        location = locations[0]
        if date is not None:
            logger.info(
                "Evaluating location for template form",
                location_id=location.id,
                date=date,
            )
            await info.context.background_site_condition_evaluator.evalulate_location(
                location, date
            )
        return LocationReturnType(id=locations[0].id)
