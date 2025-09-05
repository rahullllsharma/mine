import datetime
import enum
import uuid
from decimal import Decimal
from typing import Optional, Union

from pydantic import BaseModel, ConstrainedStr, root_validator

from worker_safety_service.models.base import RiskLevel
from worker_safety_service.models.google_cloud_storage import File
from worker_safety_service.models.library import EnergyType


@enum.unique
class FormStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    PENDING_POST_JOB_BRIEF = "pending_post_job_brief"
    PENDING_SIGN_OFF = "pending_sign_off"
    COMPLETE = "complete"


@enum.unique
class SourceAppInformation(str, enum.Enum):
    ANDROID = "ANDROID"
    IOS = "IOS"
    WEB_PORTAL = "WEB"


class JSBMetadata(BaseModel):
    briefing_date_time: datetime.datetime


class WorkPackageMetadata(BaseModel):
    work_package_location_id: uuid.UUID


class GPSCoordinates(BaseModel):
    latitude: Decimal
    longitude: Decimal


class WorkLocation(BaseModel):
    description: str
    address: str
    city: str
    state: str
    operating_hq: str | None


# Following is an example but is a phone number regex
# Needs to be made more robust
phone_regex_str = "^[0-9]{3}[0-9]{3}[0-9]{4}$"


class PhoneNumber(ConstrainedStr):
    min_length = 10
    max_length = 10
    regex = phone_regex_str


class EmergencyContact(BaseModel):
    name: str
    phone_number: PhoneNumber
    primary: bool


class MedicalFacility(BaseModel):
    description: str
    distance_from_job: float | None
    phone_number: str | None
    address: str | None
    city: str | None
    state: str | None
    zip: int | None


class AEDInformation(BaseModel):
    location: str


class TaskSelectionConcept(BaseModel):
    id: uuid.UUID
    name: str | None
    risk_level: RiskLevel
    from_work_order: bool


class RecommendedTaskSelection(TaskSelectionConcept):
    recommended: bool | None = None
    selected: bool | None = None


class CriticalRiskArea(BaseModel):
    name: str


class VoltageType(enum.Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TRANSMISSION = "transmission"


class CrewInformationTypes(enum.Enum):
    PERSONNEL = "Personnel"
    OTHER = "Other"


class Voltage(BaseModel):
    value: Optional[float] = None
    unit: str
    type: VoltageType
    value_str: Optional[str] = None

    @root_validator(pre=True)
    def set_value_str(cls, values: dict) -> dict:
        value = values.get("value")
        value_str = values.get("value_str")
        if value_str is None and value is not None:
            values["value_str"] = str(value)
        return values


class EWPMetadata(BaseModel):
    remote: bool
    issued: datetime.datetime
    completed: datetime.datetime | None
    procedure: str
    issued_by: str
    received_by: str


class EWPEquipmentInformation(BaseModel):
    circuit_breaker: str
    switch: str
    transformer: str


class EWP(BaseModel):
    id: str
    metadata: EWPMetadata
    reference_points: list[str]
    equipment_information: list[EWPEquipmentInformation]


class EnergySourceControl(BaseModel):
    arc_flash_category: int | None
    clearance_points: str | None
    transfer_of_control: bool
    voltages: list[Voltage]
    ewp: list[EWP]


class SiteConditionSelection(BaseModel):
    id: uuid.UUID
    recommended: bool
    selected: bool
    name: Optional[str] | None


class ControlSelection(BaseModel):
    id: str
    name: Optional[str] | None
    recommended: bool | None = None
    selected: bool | None = None


class ControlAssessment(BaseModel):
    hazard_id: str
    name: Optional[str] | None
    control_ids: list[str] | None
    control_selections: list[ControlSelection] | None


class WorkProcedureSelection(BaseModel):
    id: str
    values: list[str]
    name: Optional[str] | None


class CrewInformation(BaseModel):
    name: Optional[str]
    signature: File | None
    type: Optional[CrewInformationTypes] | None
    external_id: Optional[str]
    employee_number: Optional[str]
    display_name: Optional[str]
    email: Optional[str]
    job_title: Optional[str]
    department: Optional[str]
    company_name: Optional[str]
    manager_id: Optional[str]
    manager_name: Optional[str]
    manager_email: Optional[str]
    primary: Optional[bool]


class ActivityConcept(BaseModel):
    name: str
    tasks: list[TaskSelectionConcept]


class GroupDiscussion(BaseModel):
    viewed: bool


class CustomMedicalFacility(BaseModel):
    address: str


class Completion(BaseModel):
    completed_by_id: uuid.UUID | None
    completed_at: datetime.datetime | None


class DailySourceInformationConcepts(BaseModel):
    app_version: str | None
    source_information: SourceAppInformation | None
    section_is_valid: bool | None


# @strawberry.type
class SourceInformationConcepts(BaseModel):
    app_version: str | None
    source_information: SourceAppInformation | None


class JobSafetyBriefingLayout(BaseModel):
    jsb_id: uuid.UUID | None
    jsb_metadata: JSBMetadata | None
    work_package_metadata: WorkPackageMetadata | None
    gps_coordinates: list[GPSCoordinates] | None
    work_location: WorkLocation | None
    emergency_contacts: list[EmergencyContact] | None
    nearest_medical_facility: MedicalFacility | None
    custom_nearest_medical_facility: CustomMedicalFacility | None
    aed_information: AEDInformation | None
    task_selections: list[TaskSelectionConcept] | None
    recommended_task_selections: list[RecommendedTaskSelection] | None
    activities: list[ActivityConcept] | None
    critical_risk_area_selections: list[CriticalRiskArea] | None
    energy_source_control: EnergySourceControl | None
    work_procedure_selections: list[WorkProcedureSelection] | None
    other_work_procedures: str | None
    distribution_bulletin_selections: list[str] | None
    minimum_approach_distance: str | None
    site_condition_selections: list[SiteConditionSelection] | None
    control_assessment_selections: list[ControlAssessment] | None
    additional_ppe: list[str] | None
    hazards_and_controls_notes: str | None
    crew_sign_off: list[CrewInformation] | None
    photos: list[File] | None
    group_discussion: GroupDiscussion | None
    documents: list[File] | None
    completions: list[Completion] | None
    source_info: SourceInformationConcepts | None


class EmptyLayout(BaseModel):
    pass


class ControlsConcept(BaseModel):
    id: str
    name: str | None


class HazardObservationConcept(BaseModel):
    id: str
    name: str | None
    description: str | None
    observed: bool
    direct_controls_implemented: bool | None
    reason: str | None
    indirect_controls: list[ControlsConcept] | None
    limited_controls: list[ControlsConcept] | None
    direct_controls: list[ControlsConcept] | None
    direct_control_description: str | None
    limited_control_description: str | None
    heca_score_hazard: str | None
    heca_score_hazard_percentage: float | None
    energy_level: str | None


class HighEnergyTaskConcept(BaseModel):
    id: str
    name: str | None
    hazards: list[HazardObservationConcept]
    activity_id: str | None
    activity_name: str | None
    heca_score_task: str | None
    heca_score_task_percentage: float | None


class PersonnelConcept(BaseModel):
    id: uuid.UUID | None
    name: str
    role: str | None  # enum?


class WorkTypeConcept(BaseModel):
    id: uuid.UUID
    name: str


class DepartmentObservedConcept(BaseModel):
    id: uuid.UUID | None
    name: str


class OpCoObservedConcept(BaseModel):
    id: uuid.UUID
    name: str
    full_name: Optional[str]


class ObservationDetailsConcept(BaseModel):
    work_order_number: str | None
    work_location: str | None
    department_observed: DepartmentObservedConcept
    work_type: list[WorkTypeConcept] | None
    observation_date: datetime.date
    observation_time: datetime.time
    opco_observed: OpCoObservedConcept | None
    subopco_observed: OpCoObservedConcept | None


class EBOControlsConcept(ControlsConcept):
    hazard_control_connector_id: Optional[str] = None


class EBOHazardObservationConcept(HazardObservationConcept):
    task_hazard_connector_id: Optional[str] = None
    hazard_control_connector_id: Optional[str] = None
    indirect_controls: list[EBOControlsConcept] | None  # type:ignore
    limited_controls: list[EBOControlsConcept] | None  # type:ignore
    direct_controls: list[EBOControlsConcept] | None  # type:ignore


class EBOHighEnergyTaskConcept(HighEnergyTaskConcept):
    instance_id: int = 1
    task_hazard_connector_id: Optional[str] = None
    hazards: list[EBOHazardObservationConcept] = []  # type:ignore


class EBOTaskSelectionConcept(TaskSelectionConcept):
    instance_id: int = 1
    task_hazard_connector_id: Optional[str] = None
    hazards: list[EBOHazardObservationConcept] = []


class EBOActivityConcept(ActivityConcept):
    id: Optional[uuid.UUID] = None
    tasks: list[EBOTaskSelectionConcept]  # type:ignore


class EBOSummary(BaseModel):
    viewed: bool


class EnergyBasedObservationLayout(BaseModel):
    details: ObservationDetailsConcept | None
    gps_coordinates: list[GPSCoordinates] | None
    activities: list[EBOActivityConcept] | None
    high_energy_tasks: list[EBOHighEnergyTaskConcept] | None
    historic_incidents: list[str] | None
    additional_information: str | None
    photos: list[File] | None
    summary: EBOSummary | None
    personnel: list[PersonnelConcept] | None
    completions: list[Completion] | None
    source_info: SourceInformationConcepts | None


class EnergyControlInfo(BaseModel):
    id: int
    name: str
    control_info_values: str | None


class PointsOfProtection(BaseModel):
    id: int
    name: str
    details: str


class DocumentsProvided(BaseModel):
    id: int
    name: str


class VoltageInformationFromConfig(BaseModel):
    id: uuid.UUID
    value: str
    other: bool


class MininimumApproachDistance(BaseModel):
    phase_to_phase: str | None
    phase_to_ground: str | None


class VoltageInformationV2(BaseModel):
    voltage: VoltageInformationFromConfig | None
    minimum_approach_distance: MininimumApproachDistance | None


class LocationInformation(BaseModel):
    address: str | None
    landmark: str | None
    city: str | None
    state: str | None
    vehicle_number: list[str] | None
    minimum_approach_distance: str
    operating_hq: str | None


class BarnLocation(BaseModel):
    id: uuid.UUID
    name: str


class VoltageInformation(BaseModel):
    circuit: str
    voltages: str


class LocationInformationV2(BaseModel):
    created_at: datetime.datetime
    address: str | None
    landmark: str | None
    city: str | None
    state: str | None
    gps_coordinates: GPSCoordinates | None
    circuit: str | None
    voltage_information: VoltageInformationV2 | None


class FirstAidLocation(BaseModel):
    id: uuid.UUID
    first_aid_location_name: str


class Attachments(BaseModel):
    photos: list[File] | None
    documents: list[File] | None
    documents_provided: list[DocumentsProvided] | None
    description_document_provided: str | None


class ClearanceTypes(BaseModel):
    id: int
    clearance_types: str


class NatGridEnergySourceControl(BaseModel):
    energized: bool = False
    de_energized: bool = False
    controls: list[EnergyControlInfo]
    clearance_types: ClearanceTypes
    clearance_number: str | None
    controls_description: str | None
    points_of_protection: list[PointsOfProtection] = []


class CriticalTasksSelection(BaseModel):
    task_selections: list[TaskSelectionConcept]
    job_description: str
    special_precautions_notes: str | None


class UserInfo(BaseModel):
    id: uuid.UUID
    name: str
    email: str


class MultipleCrews(BaseModel):
    multiple_crew_involved: bool
    crew_discussion: bool | None
    person_incharge: list[UserInfo] | None


class CrewInfo(BaseModel):
    crew_details: UserInfo | None
    other_crew_details: str | None
    discussion_conducted: bool
    signature: File | None


class CrewSignOff(BaseModel):
    multiple_crews: MultipleCrews
    crew_sign: list[CrewInfo] | None
    creator_sign: Optional[CrewInfo]


class AEDInformationData(BaseModel):
    id: uuid.UUID
    aed_location_name: str


class BurnKitLocation(BaseModel):
    id: uuid.UUID
    burn_kit_location_name: str


class PrimaryFireSupressionLocation(BaseModel):
    id: uuid.UUID
    primary_fire_supression_location_name: str


class MedicalInformation(BaseModel):
    nearest_hospital: MedicalFacility | None
    custom_medical_nearest_hospital: CustomMedicalFacility | None
    first_aid_kit_location: FirstAidLocation | None
    custom_first_aid_kit_location: CustomMedicalFacility | None
    burn_kit_location: BurnKitLocation | None
    custom_burn_kit_location: CustomMedicalFacility | None
    primary_fire_supression_location: PrimaryFireSupressionLocation | None
    custom_primary_fire_supression_location: CustomMedicalFacility | None
    aed_information: AEDInformationData | None
    custom_aed_location: CustomMedicalFacility | None
    vehicle_number: list[str] | None


class PostJobBriefDiscussion(BaseModel):
    near_miss_occured_during_activities: bool
    near_miss_occured_description: str | None
    job_brief_adequate_communication: bool
    job_brief_adequate_communication_description: str | None
    safety_concerns_identified_during_work: bool
    safety_concerns_identified_during_work_description: str | None
    changes_in_procedure_work: bool
    changes_in_procedure_work_description: str | None
    crew_memebers_adequate_training_provided: bool
    crew_memebers_adequate_training_provided_description: str | None
    other_lesson_learnt: bool
    other_lesson_learnt_description: str | None
    job_went_as_planned: bool
    job_went_as_planned_description: str | None


class PostJobBrief(BaseModel):
    discussion_items: PostJobBriefDiscussion
    post_job_discussion_notes: str | None
    supervisor_approval_sign_off: UserInfo | None


class CrewInformationData(BaseModel):
    supervisor_info: UserInfo
    signature: File | None


class SupervisorSignOff(BaseModel):
    supervisor: CrewInformationData
    date_time: datetime.datetime


class GroupDiscussionInformation(BaseModel):
    # Remove this field after some time of release
    group_discussion_notes: str | None
    viewed: bool


class OperatingProcedure(BaseModel):
    id: uuid.UUID
    name: str | None
    link: str | None


class TaskStandardOperatingProcedure(BaseModel):
    id: uuid.UUID
    name: str | None
    sops: list[OperatingProcedure] | None


class GeneralReferenceMaterial(BaseModel):
    id: int
    name: str
    link: str
    category: str | None


class EnergyControls(BaseModel):
    controls: list[ControlsConcept] | None


class EnergyHazards(BaseModel):
    id: uuid.UUID
    name: str | None
    energy_types: str | None
    controls: EnergyControls | None
    custom_controls: EnergyControls | None
    controls_implemented: bool = False


class HighLowEnergyHazards(BaseModel):
    high_energy_hazards: list[EnergyHazards] | None
    low_energy_hazards: list[EnergyHazards] | None


class CustomHazards(BaseModel):
    low_energy_hazards: list[EnergyHazards] | None


class TaskSiteConditonEnergyHazards(HighLowEnergyHazards):
    id: uuid.UUID
    name: str | None


class HazardsControls(BaseModel):
    energy_types: list[str]
    tasks: list[TaskSiteConditonEnergyHazards] | None
    site_conditions: list[TaskSiteConditonEnergyHazards] | None
    manually_added_hazards: HighLowEnergyHazards | None
    custom_hazards: CustomHazards | None
    additional_comments: str | None


class NatGridTaskHistoricIncident(BaseModel):
    id: uuid.UUID
    name: str | None
    historic_incidents: list[str] | None


class NatGridSiteCondition(BaseModel):
    site_condition_selections: list[SiteConditionSelection] | None
    additional_comments: str | None
    dig_safe: str | None


class NatGridJobSafetyBriefingLayout(BaseModel):
    jsb_id: uuid.UUID | None
    jsb_metadata: JSBMetadata | None
    work_package_metadata: WorkPackageMetadata | None
    gps_coordinates: list[GPSCoordinates] | None
    work_location: LocationInformation | None
    barn_location: BarnLocation | None
    work_location_with_voltage_info: list[LocationInformationV2] | None
    voltage_info: VoltageInformation | None
    medical_information: MedicalInformation | None
    activities: list[ActivityConcept] | None
    critical_tasks_selections: CriticalTasksSelection | None
    hazards_control: HazardsControls | None
    energy_source_control: NatGridEnergySourceControl | None
    attachment_section: Attachments | None
    task_historic_incidents: list[NatGridTaskHistoricIncident] | None
    standard_operating_procedure: list[TaskStandardOperatingProcedure] | None
    general_reference_materials: list[GeneralReferenceMaterial] | None
    group_discussion: GroupDiscussionInformation | None
    crew_sign_off: CrewSignOff | None
    post_job_brief: PostJobBrief | None
    supervisor_sign_off: SupervisorSignOff | None
    completions: list[Completion] | None
    site_conditions: NatGridSiteCondition | None
    source_info: SourceInformationConcepts | None


class UIConfigClearanceTypes(BaseModel):
    id: int
    name: str


class UIConfigStatusWorkflow(BaseModel):
    color_code: str
    new_status: str
    action_button: str
    current_status: str


class UIConfigPointsOfProtection(BaseModel):
    id: int
    name: str
    description_allowed: bool


class UIConfigEnergySourceControl(BaseModel):
    id: int
    name: str
    description_allowed: bool


class UIConfigNotificationSettings(BaseModel):
    configurable: bool
    notification_duration_days: str | int


class UIConfigMinimumApproachDistances(BaseModel):
    id: uuid.UUID
    location: str
    voltages: str
    phase_to_phase: str
    phase_to_ground: str


class UIConfigMinimumApproachDistancesLinks(BaseModel):
    id: uuid.UUID
    url: str
    description: str


class ExtendedEnergyType(str, enum.Enum):
    DEFAULT = "Default"
    UNSPECIFIED = "Unspecified"


class UIConfigEnergyWheelColors(BaseModel):
    id: int
    name: Union[ExtendedEnergyType, EnergyType]
    color: str


Layout = (
    JobSafetyBriefingLayout
    | EmptyLayout
    | EnergyBasedObservationLayout
    | NatGridJobSafetyBriefingLayout
)
