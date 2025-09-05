from datetime import date
from uuid import UUID

from pydantic import BaseModel, field_serializer


class EnergyWheelSettings(BaseModel):
    is_energy_wheel_enabled: bool = True


class WorkTypeBase(BaseModel):
    """
    Work Type is a way to group Task Types that are applicable for utility company business units (Organization Units).
    Ex: {
        id: UUID("12345678-1234-5678-1234-567812345678"),
        name: "Gas Transmission Construction"
        }
        All the task types that are applicable for this work will be grouped under this work type.
    """

    id: UUID
    name: str

    @field_serializer("id", when_used="unless-none")
    def serialize_id(self, id: UUID) -> str:
        """
        Serializes the UUID to a string to avoid issues with JSON serialization.
        This is necessary because UUIDs are not JSON serializable by default.
        """
        return str(id)


class CopyRebriefSettings(BaseModel):
    is_copy_enabled: bool = False
    is_rebrief_enabled: bool = False
    is_allow_linked_form: bool = False


class Incident(BaseModel):
    """Incident data contains records of historical incidents (and sometimes observations) from customers.

    Includes details about each incident such as date, location, severity, free text describing
    the incident, and associated people.

    Attributes:
        id (UUID): Urbint unique identifier for each incident
        incident_id (str): Customer specific unique identifier for each incident
        incident_date (datetime): Date and time when the incident occurred
        incident_type (str): Classification of the incident (e.g., Good catch, process safety,
            injury, near miss, equipment failure, asset, environmental, MVI)
        task_type (str): Customer specific classification of the task being performed when the
            incident occurred (e.g. Loading, Excavation)
        task_type_id (str): Customer specific unique identifier for each task type
        severity (str): Severity rating based on established criteria (e.g., minor, moderate,
            major, catastrophic)
        description (str): Detailed description including events leading up to incident,
            injuries sustained, and immediate actions taken
    """

    id: UUID
    incident_date: date | None
    incident_type: str | None
    incident_id: str | None
    task_type_id: str | None
    severity_code: str | None
    description: str
    task_type: str | None
    archived_at: str | None
    severity: str | None


class HistoricalIncident(BaseModel):
    label: str
    incident: Incident | None = None
