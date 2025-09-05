from typing import Any, Callable

from strawberry.permission import BasePermission
from strawberry.types import Info

from worker_safety_service.context import Context
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.graphql.exceptions import NoRoleOnUserException
from worker_safety_service.models import FormStatus, ProjectStatus
from worker_safety_service.permissions import Permission, role_has_permission

# ------------------------------- Permission Classes


class SimplePermissionClass(BasePermission):
    """
    Extend this class to define new permission classes that depend on only one permission
    """

    message = "User is not authorized to access this resource"
    allowed_permission: Permission | None = None

    async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
        if self.allowed_permission is None:
            return False
        r = user_role(info)
        return role_has_permission(r, self.allowed_permission)


class CanCreateProject(SimplePermissionClass):
    message = "User is not authorized to create projects"
    allowed_permission = Permission.ADD_PROJECTS


class CanCreateTenant(SimplePermissionClass):
    message = "User is not authorized to create tenants"
    allowed_permission = Permission.ADD_TENANTS


class CanEditTenant(SimplePermissionClass):
    message = "User is not authorized to edit tenants"
    allowed_permission = Permission.EDIT_TENANTS


class CanDeleteProject(SimplePermissionClass):
    message = "User is not authorized to delete projects"
    allowed_permission = Permission.DELETE_PROJECTS


class CanReadSiteConditions(SimplePermissionClass):
    message = "User is not authorized to view site conditions"
    allowed_permission = Permission.VIEW_SITE_CONDITIONS


class CanReadTasks(SimplePermissionClass):
    message = "User is not authorized to view tasks"
    allowed_permission = Permission.VIEW_TASKS


class CanReadHazards(SimplePermissionClass):
    message = "User is not authorized to view hazards"
    allowed_permission = Permission.VIEW_HAZARDS


class CanReadControls(SimplePermissionClass):
    message = "User is not authorized to view controls"
    allowed_permission = Permission.VIEW_CONTROLS


class CanReadProject(SimplePermissionClass):
    message = "User is not authorized to read projects"
    allowed_permission = Permission.VIEW_PROJECT


class CanReadReports(SimplePermissionClass):
    message = "User is not authorized to read reports"
    allowed_permission = Permission.VIEW_INSIGHT_REPORTS


class CanEditProjects(SimplePermissionClass):
    message = "User is not authorized to edit projects"
    allowed_permission = Permission.EDIT_PROJECTS


class CanReadActivity(SimplePermissionClass):
    message = "User is not authorized to read activities"
    allowed_permission = Permission.VIEW_ACTIVITIES


class CanCreateActivity(SimplePermissionClass):
    message = "User is not authorized to create activities"
    allowed_permission = Permission.ADD_ACTIVITIES


class CanEditActivity(SimplePermissionClass):
    message = "User is not authorized to edit activities"
    allowed_permission = Permission.EDIT_ACTIVITIES


class CanEditTask(SimplePermissionClass):
    message = "User is not authorized to update tasks"
    allowed_permission = Permission.EDIT_TASKS


class CanCreateSiteCondition(SimplePermissionClass):
    message = "User is not authorized to create site conditions"
    allowed_permission = Permission.ADD_SITE_CONDITIONS


class CanEditSiteCondition(SimplePermissionClass):
    message = "User is not authorized to update site conditions"
    allowed_permission = Permission.EDIT_SITE_CONDITIONS


class CanReadProjectAudits(SimplePermissionClass):
    message = "User is not authorized to read project audits"
    allowed_permission = Permission.VIEW_PROJECT_AUDITS


class CanViewManagers(SimplePermissionClass):
    message = "User is not authorized to fetch managers"
    allowed_permission = Permission.VIEW_MANAGERS


class CanViewCrew(SimplePermissionClass):
    message = "User is not authorized to fetch supervisors"
    allowed_permission = Permission.VIEW_CREW


class CanViewCompanies(SimplePermissionClass):
    message = "User is not authorized to fetch contractors"
    allowed_permission = Permission.VIEW_COMPANIES


class CanConfigureTheApplication(SimplePermissionClass):
    message = "User is not authorized to configure the application"
    allowed_permission = Permission.CONFIGURE_APPLICATION


class CanConfigureOpcoAndDepartment(SimplePermissionClass):
    message = "User is not authorized to configure opcos and departments"
    allowed_permission = Permission.ADD_OPCO_AND_DEPARTMENT


class CanGetFeatureFlagDetails(SimplePermissionClass):
    message = "User is not authorized to configure the application"
    allowed_permission = Permission.GET_FEATURE_FLAG_DETAILS


class CanViewCrewLeaders(SimplePermissionClass):
    message = "User is not authorized to view crew leaders"
    allowed_permission = Permission.VIEW_CREW_LEADERS


class CanGenerateReportsAPIToken(SimplePermissionClass):
    message = "User is not authorized to generate token for reports API"
    allowed_permission = Permission.GET_REPORTS_TOKEN


class CanAddPreferences(SimplePermissionClass):
    message = "User is not authorized to Add Preferences"
    allowed_permission = Permission.ADD_PREFERENCES


class CanViewNotifications(SimplePermissionClass):
    message = "User is not authorized to view notifications"
    allowed_permission = Permission.VIEW_NOTIFICATIONS


class CanViewSupervisorSignOff(SimplePermissionClass):
    message = "User is not authorized to view supervisor sign-off"
    allowed_permission = Permission.VIEW_SUPERVISOR_SIGN_OFF


class CanEditSupervisorSignOff(SimplePermissionClass):
    message = "User is not authorized to edit supervisor sign-off"
    allowed_permission = Permission.EDIT_SUPERVISOR_SIGN_OFF


# ------------------------------- Complex permissions


class CanUpdateProject(BasePermission):
    message = "User is not authorized to update projects"

    async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
        r = user_role(info)
        project = kwargs["project"]

        if project is None:
            return False

        project_id = getattr(project, "id", None)
        if not project_id:
            return False

        context: Context = info.context
        prev_proj = await context.projects.me.load(project_id)

        if prev_proj is None:
            return False

        if prev_proj.status == ProjectStatus.COMPLETED and r.lower() != "administrator":
            # Extra access is needed, Ie. user must be administrator
            # Note, we fall through if we are not entirely sure
            return False

        return role_has_permission(r, Permission.EDIT_PROJECTS)


class CanDeleteReport(BasePermission):
    message = "User is not authorized to delete report"

    async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
        r = user_role(info)
        if role_has_permission(r, Permission.DELETE_REPORTS):
            return True

        report_id = kwargs.get("id")
        if report_id is None:
            self.message = "Report ID not found"
            return False

        context: Context = info.context
        daily_report = await context.daily_reports.get_daily_report(report_id)
        try:
            ebo = await context.energy_based_observations.get_energy_based_observations(
                report_id
            )
        except ResourceReferenceException:
            ebo = None

        # Check if either daily_report or ebo is present
        if not any((daily_report, ebo)):
            self.message = f"Report not found: {report_id}"
            return False

        # Check if the user created the report
        if daily_report and daily_report.created_by_id == context.user.id:
            return role_has_permission(r, Permission.DELETE_OWN_REPORTS)

        # Check if the user created the EBO
        if ebo and ebo.created_by_id == context.user.id:
            return role_has_permission(r, Permission.DELETE_OWN_REPORTS)

        return False


class CanDeleteNatGridJobSafetyBriefing(BasePermission):
    message = "User is not authorized to delete report"

    async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
        r = user_role(info)
        if role_has_permission(r, Permission.DELETE_REPORTS):
            return True

        report_id = kwargs.get("id")
        if report_id is None:
            self.message = "Report ID not found"
            return False

        context: Context = info.context
        try:
            ngjsb = await context.natgrid_job_safety_briefings.get_natgrid_job_safety_briefing(
                report_id
            )
        except ResourceReferenceException:
            ngjsb = None
        # Check if ngjsb is present
        if not ngjsb:
            self.message = f"Report not found: {report_id}"
            return False

        # Check if the user created the NGJSB
        if ngjsb and ngjsb.created_by_id == context.user.id:
            return role_has_permission(r, Permission.DELETE_OWN_REPORTS)

        return False


class CanSaveReport(BasePermission):
    async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
        r = user_role(info)
        report = kwargs.get("daily_report_input")
        report_id = getattr(report, "id", None)

        if report_id is None:
            self.message = "User is not authorized to create reports"
            return role_has_permission(r, Permission.ADD_REPORTS)

        if role_has_permission(r, Permission.EDIT_REPORTS):
            return True

        context: Context = info.context
        report = await context.daily_reports.get_daily_report(report_id)
        if report is None:
            self.message = "Daily Report ID not found"
            return False

        if report.status == FormStatus.COMPLETE:
            self.message = "User may not edit closed reports"
            return role_has_permission(r, Permission.REOPEN_REPORTS)

        self.message = "User is not authorized to edit this report"
        if report and report.created_by_id == context.user.id:
            return role_has_permission(r, Permission.EDIT_OWN_REPORTS)

        return False


class CanArchiveAllWorkPackages(BasePermission):
    config_property_name = "FEATURES.IS_ARCHIVE_ALL_WORK_PACKAGES_ENABLED"
    message = "User is not authorized to delete all projects!"

    async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
        r = user_role(info)
        if r.lower() != "administrator":
            return False

        if not role_has_permission(r, Permission.DELETE_PROJECTS):
            return False

        configurations_manager: ConfigurationsManager = (
            info.context.configurations_manager
        )
        raw_value = await configurations_manager.load(
            CanArchiveAllWorkPackages.config_property_name, info.context.tenant_id
        )
        return raw_value == "true"


class CanReopenEBO(BasePermission):
    async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
        role = user_role(info)

        if role_has_permission(role, Permission.REOPEN_REPORTS):
            return True

        report_id = kwargs.get("id")
        if report_id is None:
            self.message = "Report ID not found"
            return False

        context: Context = info.context
        try:
            ebo = await context.energy_based_observations.get_energy_based_observations(
                report_id
            )
        except ResourceReferenceException:
            ebo = None

        if ebo and ebo.created_by_id == context.user.id:
            return role_has_permission(role, Permission.REOPEN_OWN_REPORT)

        self.message = "User is not authorized to reopen ebo"
        return False


# ------------------------------- Dependent permissions


class ComposedPermissionClass(BasePermission):
    """
    Extend this class to define new permission classes that depend on multiple permissions

    - operator property needs to be set to change the logic of the allowed_permission validator
      - any = "OR"
      - all = "AND"
    """

    message = "User is not authorized to access this resource"
    allowed_permissions: tuple[Permission, ...] = ()
    operator: Callable[..., bool] | None = None

    async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
        if self.operator is None:
            return False

        if self.allowed_permissions == []:
            return False

        r = user_role(info)
        return self.operator(
            role_has_permission(r, p) for p in self.allowed_permissions
        )


# ------------------------------- Utils


def user_role(info: Info) -> str:
    context: Context = info.context
    if context.user.role is None:
        raise NoRoleOnUserException
    return str(context.user.role)
