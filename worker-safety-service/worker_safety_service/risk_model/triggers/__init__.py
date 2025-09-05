import enum

import strawberry

from .activity_changed import ActivityChanged
from .activity_deleted import ActivityDeleted
from .contractor_changed_for_project import ContractorChangedForProject
from .contractor_data_changed import ContractorDataChanged
from .contractor_data_changed_for_tenant import ContractorDataChangedForTenant
from .crew_data_changed_for_tenant import CrewDataChangedForTenant
from .incident_changed import IncidentChanged
from .library_task_data_changed import LibraryTaskDataChanged
from .location_changed import LocationChanged
from .project_changed import ProjectChanged
from .project_location_siteconditions_changed import (
    ProjectLocationSiteConditionsChanged,
)
from .supervisor_changed_for_project import (
    SupervisorChangedForProjectLocation,
    SupervisorsChangedForProject,
)
from .supervisor_data_changed import SupervisorDataChanged
from .supervisor_data_changed_for_tenant import SupervisorDataChangedForTenant
from .task_changed import TaskChanged
from .task_deleted import TaskDeleted
from .update_task_risk import UpdateTaskRisk


@strawberry.enum
class Triggers(enum.Enum):
    ACTIVITY_CHANGED = ActivityChanged
    ACTIVITY_DELETED = ActivityDeleted
    CONTRACTOR_CHANGED_FOR_PROJECT = ContractorChangedForProject
    CONTRACTOR_DATA_CHANGED = ContractorDataChanged
    CONTRACTOR_DATA_CHANGED_FOR_TENANT = ContractorDataChangedForTenant
    CREW_DATA_CHANGED_FOR_TENANT = CrewDataChangedForTenant
    INCIDENT_CHANGED = IncidentChanged
    LIBRARY_TASK_DATA_CHANGED = LibraryTaskDataChanged
    PROJECT_CHANGED = ProjectChanged
    PROJECT_LOCATION_SITE_CONDITIONS_CHANGED = ProjectLocationSiteConditionsChanged
    SUPERVISOR_CHANGED_FOR_PROJECT_LOCATION = SupervisorChangedForProjectLocation
    SUPERVISORS_CHANGED_FOR_PROJECT = SupervisorsChangedForProject
    SUPERVISOR_DATA_CHANGED = SupervisorDataChanged
    SUPERVISOR_DATA_CHANGED_FOR_TENANT = SupervisorDataChangedForTenant
    TASK_CHANGED = TaskChanged
    TASK_DELETED = TaskDeleted
    UPDATE_TASK_RISK = UpdateTaskRisk


ARCHIVE_TRIGGERS = [
    ActivityDeleted,
    TaskDeleted,
]

__all__ = [
    "ARCHIVE_TRIGGERS",
    "Triggers",
    "ActivityChanged",
    "ActivityDeleted",
    "ContractorChangedForProject",
    "ContractorDataChanged",
    "ContractorDataChangedForTenant",
    "CrewDataChangedForTenant",
    "IncidentChanged",
    "LibraryTaskDataChanged",
    "LocationChanged",
    "ProjectChanged",
    "ProjectLocationSiteConditionsChanged",
    "SupervisorsChangedForProject",
    "SupervisorChangedForProjectLocation",
    "SupervisorDataChanged",
    "SupervisorDataChangedForTenant",
    "TaskChanged",
    "TaskDeleted",
    "UpdateTaskRisk",
]
