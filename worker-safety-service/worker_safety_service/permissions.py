# Permissions
#
# This file contains a number of utility functions to work with permissions
# and roles.
#
# Note: Permissions are used outside of this repo. Hence some permissions might
# appear to not be in use, though they are

# ------------------------------- Role / Permission Mapping

import enum
from typing import Optional


@enum.unique
class Permission(enum.Enum):
    VIEW_PROJECT = "VIEW_PROJECT"
    VIEW_TASKS = "VIEW_TASKS"
    VIEW_ACTIVITIES = "VIEW_ACTIVITIES"
    VIEW_SITE_CONDITIONS = "VIEW_SITE_CONDITIONS"
    VIEW_HAZARDS = "VIEW_HAZARDS"
    VIEW_CONTROLS = "VIEW_CONTROLS"
    VIEW_INSPECTIONS = "VIEW_INSPECTIONS"
    VIEW_INSIGHT_REPORTS = "VIEW_INSIGHT_REPORTS"
    VIEW_MEDICAL_FACILITIES = "VIEW_MEDICAL_FACILITIES"
    VIEW_MANAGERS = "VIEW_MANAGERS"
    VIEW_CREW = "VIEW_CREW"
    VIEW_COMPANIES = "VIEW_COMPANIES"
    ASSIGN_USERS_TO_PROJECTS = "ASSIGN_USERS_TO_PROJECTS"
    ASSIGN_CONTROLS = "ASSIGN_CONTROLS"
    ADD_ACTIVITIES = "ADD_ACTIVITIES"
    ADD_HAZARDS = "ADD_HAZARDS"
    ADD_CONTROLS = "ADD_CONTROLS"
    ADD_SITE_CONDITIONS = "ADD_SITE_CONDITIONS"
    ADD_TENANTS = "ADD_TENANTS"
    ADD_REPORTS = "ADD_REPORTS"
    EDIT_ACTIVITIES = "EDIT_ACTIVITIES"
    EDIT_HAZARDS = "EDIT_HAZARDS"
    EDIT_CONTROLS = "EDIT_CONTROLS"
    EDIT_TASKS = "EDIT_TASKS"
    EDIT_TENANTS = "EDIT_TENANTS"
    EDIT_SITE_CONDITIONS = "EDIT_SITE_CONDITIONS"
    EDIT_PROJECTS = "EDIT_PROJECTS"
    EDIT_OWN_REPORTS = "EDIT_OWN_REPORTS"
    EDIT_REPORTS = "EDIT_REPORTS"
    REOPEN_REPORTS = "REOPEN_REPORTS"
    ADD_PROJECTS = "ADD_PROJECTS"
    REOPEN_PROJECT = "REOPEN_PROJECT"
    CONFIGURE_APPLICATION = "CONFIGURE_APPLICATION"
    DELETE_OWN_REPORTS = "DELETE_OWN_REPORTS"
    DELETE_REPORTS = "DELETE_REPORTS"
    DELETE_PROJECTS = "DELETE_PROJECTS"
    VIEW_PROJECT_AUDITS = "VIEW_PROJECT_AUDITS"
    GET_FEATURE_FLAG_DETAILS = "GET_FEATURE_FLAG_DETAILS"
    ADD_OPCO_AND_DEPARTMENT = "ADD_OPCO_AND_DEPARTMENT"
    VIEW_CREW_LEADERS = "VIEW_CREW_LEADERS"
    GET_REPORTS_TOKEN = "GET_REPORTS_TOKEN"
    ADD_PREFERENCES = "ADD_PREFERENCES"
    REOPEN_OWN_REPORT = "REOPEN_OWN_REPORT"
    VIEW_NOTIFICATIONS = "VIEW_NOTIFICATIONS"
    VIEW_SUPERVISOR_SIGN_OFF = "VIEW_SUPERVISOR_SIGN_OFF"
    EDIT_SUPERVISOR_SIGN_OFF = "EDIT_SUPERVISOR_SIGN_OFF"
    # CWF permissions
    VIEW_ALL_CWF = "VIEW_ALL_CWF"
    CREATE_CWF = "CREATE_CWF"
    EDIT_DELETE_OWN_CWF = "EDIT_DELETE_OWN_CWF"
    EDIT_DELETE_ALL_CWF = "EDIT_DELETE_ALL_CWF"
    REOPEN_OWN_CWF = "REOPEN_OWN_CWF"
    REOPEN_ALL_CWF = "REOPEN_ALL_CWF"
    CONFIGURE_CUSTOM_TEMPLATES = "CONFIGURE_CUSTOM_TEMPLATES"
    ALLOW_EDITS_AFTER_EDIT_PERIOD = "ALLOW_EDITS_AFTER_EDIT_PERIOD"


# As we want to have each role fully defined, they need to refer to other
# roles. Hence we can not put them into a map
permissions_viewer = [
    Permission.VIEW_PROJECT,
    Permission.VIEW_TASKS,
    Permission.VIEW_ACTIVITIES,
    Permission.VIEW_SITE_CONDITIONS,
    Permission.VIEW_HAZARDS,
    Permission.VIEW_CONTROLS,
    Permission.VIEW_INSPECTIONS,
    Permission.VIEW_INSIGHT_REPORTS,
    Permission.VIEW_MANAGERS,
    Permission.VIEW_CREW,
    Permission.VIEW_COMPANIES,
    Permission.GET_FEATURE_FLAG_DETAILS,
    Permission.ADD_OPCO_AND_DEPARTMENT,
    Permission.VIEW_CREW_LEADERS,
    Permission.ADD_PREFERENCES,
    Permission.VIEW_NOTIFICATIONS,
    # CWF permissions
    Permission.VIEW_ALL_CWF,
]
permissions_supervisor = permissions_viewer + [
    Permission.ASSIGN_USERS_TO_PROJECTS,
    Permission.ASSIGN_CONTROLS,
    Permission.ADD_ACTIVITIES,
    Permission.EDIT_ACTIVITIES,
    Permission.ADD_HAZARDS,
    Permission.ADD_CONTROLS,
    Permission.ADD_SITE_CONDITIONS,
    Permission.ADD_REPORTS,
    Permission.EDIT_HAZARDS,
    Permission.EDIT_CONTROLS,
    Permission.EDIT_TASKS,
    Permission.EDIT_SITE_CONDITIONS,
    Permission.EDIT_PROJECTS,
    Permission.EDIT_OWN_REPORTS,
    Permission.DELETE_OWN_REPORTS,
    Permission.VIEW_PROJECT_AUDITS,
    Permission.REOPEN_OWN_REPORT,
    # CWF permissions
    Permission.CREATE_CWF,
    Permission.EDIT_DELETE_OWN_CWF,
    Permission.REOPEN_OWN_CWF,
]
permissions_manager = permissions_supervisor + [
    Permission.ADD_PROJECTS,
    Permission.DELETE_REPORTS,
    Permission.EDIT_REPORTS,
    Permission.REOPEN_REPORTS,
    Permission.GET_REPORTS_TOKEN,
    Permission.VIEW_SUPERVISOR_SIGN_OFF,
    Permission.EDIT_SUPERVISOR_SIGN_OFF,
    # CWF permissions
    Permission.EDIT_DELETE_ALL_CWF,
    Permission.REOPEN_ALL_CWF,
]
permissions_administrator = permissions_manager + [
    Permission.ADD_TENANTS,
    Permission.EDIT_TENANTS,
    Permission.DELETE_PROJECTS,
    Permission.REOPEN_PROJECT,
    Permission.CONFIGURE_APPLICATION,
    Permission.CONFIGURE_CUSTOM_TEMPLATES,
    Permission.ALLOW_EDITS_AFTER_EDIT_PERIOD,
]


role_to_permissions_map = {
    "viewer": permissions_viewer,
    "supervisor": permissions_supervisor,
    "manager": permissions_manager,
    "administrator": permissions_administrator,
}

# ------------------------------- Role Lattice

# Important: Order _really_ matters
roles_lattice = ["administrator", "manager", "supervisor", "viewer"]

# ------------------------------- Utils


def permissions_for_role(r: Optional[str]) -> list[Permission]:
    if not r:
        return []
    elif r in role_to_permissions_map:
        return role_to_permissions_map[r]
    raise Exception(f"Role could not be recognized {r}")


def role_has_permission(role: str, permission: Permission) -> bool:
    try:
        return permission in permissions_for_role(role)
    except Exception:
        return False


def role_is_at_least(r1: str, r2: str) -> bool:
    """
    Returns whether r1 is at least an r2

    eg.
    * viewer is at last an administrator returns False
    * administrator is at least a viewer returns True

    """
    return roles_lattice.index(r1) <= roles_lattice.index(r2)
