export type JobSafetyBriefing = {
  jsbId: string;
  activities: Activity[];
  completions: Completion[];
  jsbMetadata: {
    briefingDateTime: string;
  };
  voltageInfo: VoltageInfo;
  crewSignOff: CrewSignOff;
  workLocation: WorkLocation;
  workLocationWithVoltageInfo: WorkLocationWithVoltageInfo[];
  postJobBrief: PostJobBrief;
  gpsCoordinates: GPSCoordinate[];
  hazardsControl: HazardsControl;
  groupDiscussion: GroupDiscussion;
  attachmentSection: AttachmentSection;
  onUpdate: () => void;
  taskHistoricIncidents: Array<{
    historicIncidents: string[];
    id: string;
    name: string;
  }>;
  medicalInformation: MedicalInformationType;
  energySourceControl: EnergySourceControl;
  standardOperatingProcedure: StandardOperatingProcedures;
  siteConditions: {
    siteConditionSelections: SiteConditionSelections[];
    additionalComments: string;
    digSafe: string;
  };
  criticalTasksSelections: {
    specialPrecautionsNotes: string;
    jobDescription: string;
    taskSelections: Array<{
      id: string;
      name: string;
    }>;
  };
  generalReferenceMaterials: {
    id: string;
    link: string;
    name: string;
  }[];
};

export const orderByManager = [
  {
    field: "NAME",
    direction: "ASC",
  },
];

export type SiteConditionSelections = {
  name: string;
  id: string;
  highEnergyHazard: HighEnergyHazard[];
  lowEnergyHazard: LowEnergyHazard[];
};

export type EnergySourceControl = {
  controls: { id: string | number; name: string; controlInfoValues: string }[];
  energized: boolean;
  deEnergized: boolean;
  clearanceTypes: {
    id: string | number;
    clearanceTypes: string;
  } | null;
  clearanceNumber: string | null;
  controlsDescription: string | null;
  pointsOfProtection: { id: string; name: string; details: string }[];
};

export type Activity = {
  name: string;
  tasks: Task[];
};

export type Task = {
  id: string;
  name: string;
  riskLevel: string;
  fromWorkOrder: boolean;
};

export type HistoricIncidentType = {
  historicIncidents: string[] | null;
  id: string;
  name: string;
};

export type HistoricIncidents = {
  id: string;
  description: string;
  incidentDate: string;
  incidentType: string;
  severity: string;
};

export type Completion = {
  completedAt: string;
  completedById: string;
};

export type VoltageInfo = {
  circuit: string;
  voltages: string;
};

export type CreatorSign = {
  discussionConducted: boolean;
  otherCrewDetails: string;
  crewDetails: CrewDetails;
  signature: Signature;
};

export type CrewSignOff = {
  creatorSign: CreatorSign;
  crewSign: CrewSign[];
  multipleCrews: MultipleCrews;
};

export type CrewSign = {
  signature: Signature;
  otherCrewDetails: string;
  crewDetails: CrewDetails;
  discussionConducted: boolean;
};

export type Signature = {
  id: string;
  md5: string | null;
  url: string;
  date: string;
  name: string;
  size: string;
  time: string;
  crc32c: string | null;
  category: string | null;
  mimetype: string | null;
  signedUrl: string;
  displayName: string;
};

export type CrewDetails = {
  id: string;
  name: string;
  email: string;
};

export type MultipleCrews = {
  crewDiscussion: boolean;
  personIncharge: PersonInCharge[];
  multipleCrewInvolved: boolean;
};

export type PersonInCharge = {
  id: string;
  name: string;
  email: string;
};

export type WorkLocation = {
  state: string | null;
  address: string;
  landmark: string | null;
  operatingHq: string | null;
  vehicleNumber: string[];
  minimumApproachDistance: string;
};

export type Voltage = {
  id: string;
  value: string;
  other: boolean;
};

export type MinimumApproachDistance = {
  phaseToPhase: string;
  phaseToGround: string;
};

export type VoltageInformation = {
  voltage: Voltage;
  minimumApproachDistance: MinimumApproachDistance;
};

export type WorkLocationWithVoltageInfo = {
  createdAt: string | null;
  state: string | null;
  city: string | null;
  address: string | null;
  landmark: string | null;
  circuit: string | null;
  gpsCoordinates: GPSCoordinate;
  voltageInformation: VoltageInformation;
};

export type PostJobBrief = {
  discussionItems: DiscussionItems;
  postJobDiscussionNotes: string;
  supervisorApprovalSignOff: SupervisorApprovalSignOff;
};

export type DiscussionItems = {
  changesInProcedureWork: boolean;
  changesInProcedureWorkDescription: string;
  crewMemebersAdequateTrainingProvided: boolean;
  crewMemebersAdequateTrainingProvidedDescription: string;
  jobBriefAdequateCommunication: boolean;
  jobBriefAdequateCommunicationDescription: string;
  jobWentAsPlanned: boolean;
  jobWentAsPlannedDescription: boolean;
  nearMissOccuredDescription: string;
  nearMissOccuredDuringActivities: boolean;
  otherLessonLearnt: boolean;
  otherLessonLearntDescription: string;
  safetyConcernsIdentifiedDuringWork: boolean;
  safetyConcernsIdentifiedDuringWorkDescription: string;
};

export type SupervisorApprovalSignOff = {
  id: string;
  name: string;
  email: string;
};

export type GPSCoordinate = {
  latitude: string;
  longitude: string;
};

export type HazardsControl = {
  tasks: HazardTask[];
  energyTypes: string[];
  siteConditions: SiteCondition[];
  manuallyAddedHazards: ManuallyAddedHazards;
  additionalComments?: string;
  customHazards?: any;
};

export interface EnergyWheelColour {
  id: number;
  name: string;
  color: string;
}

export interface UiConfigData {
  uiConfig: {
    contents: {
      energy_wheel_color: EnergyWheelColour[];
    };
  };
}

export type HazardTask = {
  id: string;
  name: string;
  lowEnergyHazards: HighEnergyHazard[] | null;
  highEnergyHazards: HighEnergyHazard[];
};

export type HighEnergyHazard = {
  siteConditionData?: siteConditionData;
  customControls?: CustomControls;
  id: string;
  name: string;
  controls: Controls;
  energyTypes: string;
};

export type siteConditionData = {
  id: string;
  name: string;
  selected: string;
  HighEnergyHazard?: HighEnergyHazard[];
  additionalComments?: string;
};

export type Controls = {
  directControls: Control[] | null;
  alternativeControls: Control[] | null;
  directControlDescription: string | null;
  alternativeControlDescription: string | null;
};

export type Control = {
  id: string;
  name: string;
};
export type CustomControls = {
  controls: Control[];
  id: string;
  name: string;
};

export type EnergyType =
  | "pressure"
  | "gravity"
  | "temperature"
  | "electrical"
  | "mechanical"
  | "chemical"
  | "radiation"
  | string;

export type barnLocation = {
  id: string;
  name: string;
};

export type Hazard = {
  controls?: Control;
  id: string;
  name: string;
  energyTypes: EnergyType;
  controlsImplemented: boolean;
  customControls: CustomControls;
};

export type HazardList = Array<HighEnergyHazard | LowEnergyHazard | Hazard>;

export type SiteCondition = {
  id: string;
  name: string;
  lowEnergyHazards: LowEnergyHazard[] | null;
  highEnergyHazards: string[];
};

export type ManuallyAddedHazards = {
  lowEnergyHazards: LowEnergyHazard[] | null;
  highEnergyHazards: HighEnergyHazard[] | null;
};

export type LowEnergyHazard = {
  id: string;
  name: string;
  controls: Controls | null;
  energyTypes: string;
};

export type GroupDiscussion = {
  viewed: boolean;
  groupDiscussionNotes: string;
};

export type AttachmentSection = {
  photos: Attachment[];
  documents: Attachment[];
  documentsProvided: DocumentProvided[];
  descriptionDocumentProvided: string | null;
};

export type Attachment = {
  id: string;
  md5: string | null;
  url: string;
  date: string;
  name: string;
  size: string;
  time: string;
  crc32c: string | null;
  category: string | null;
  mimetype: string | null;
  signedUrl: string;
  displayName: string;
};

export type DocumentProvided = {
  id: number;
  name: string;
};

type SOP = {
  id: string;
  link: string;
  name: string;
};

type StandardOperatingProcedure = {
  id: string;
  name: string;
  sops: SOP[];
};

export type StandardOperatingProcedures = StandardOperatingProcedure[];

export type NearestHospitalType = {
  description?: string;
  distanceFromJob?: number;
  phoneNumber?: string;
  address: string;
  city?: string;
  state?: string;
  zip?: number;
};
export type TaskLib = {
  id: string;
  name: string;
  riskLevel: string;
};

export type MedicalInformationType = {
  aedInformation: AEDInformation;
  nearestHospital: NearestHospitalType | null;
  burnKitLocation: BurnKitLocation;
  customAedLocation: string | null;
  firstAidKitLocation: FirstAidKitLocation;
  customBurnKitLocation: CustomLocation;
  customFirstAidKitLocation: CustomLocation;
  customMedicalNearestHospital: CustomLocation;
  vehicleNumber: string[] | null;
  primaryFireSupressionLocation: PrimaryFireSupressionLocation;
  customPrimaryFireSupressionLocation: CustomLocation;
};

export type AEDInformation = {
  id: string;
  aedLocationName: string;
};

export type BurnKitLocation = {
  id: string;
  burnKitLocationName: string;
};

export type PrimaryFireSupressionLocation = {
  id: string;
  primaryFireSupressionLocationName: string;
};

type FirstAidKitLocation = {
  id: string;
  firstAidLocationName: string;
};

type CustomLocation = {
  address: string;
};

export interface SketchPadDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (blob: Blob, policy: any) => void;
  name?: string;
}

export type FileInputs = {
  id?: string;
  name: string | undefined;
  displayName: string | undefined;
  size?: string;
  url?: string;
  signedUrl?: string;
};

export interface FileInputsCWF {
  id: string;
  url?: string;
  signedUrl: string;
  name: string | undefined;
  displayName: string | undefined;
  size: string;
  date?: string;
  time?: string;
  category?: string;
  mimetype?: string;
  md5?: string;
  crc32c?: string;
}

export interface SupervisorSignOffType {
  dateTime: string;
  supervisor: {
    supervisorInfo: {
      id: string;
      name: string;
      email: string;
    };
    signatures: {
      id: string;
      signedUrl: string;
      exists: boolean;
      url: string;
      name: string;
      displayName: string;
      size: string;
      date: string;
      time: string;
    };
  };
}

export interface Manager {
  name: string;
  id: string;
}

type postSignatureInfo = {
  id: string;
  name: string;
  email: string;
};

export interface SuperSignOffProps {
  isReadOnly?: boolean;
  onSignatureSave?: ((signature: FileInputs) => void) | undefined;
  supervisorSignOff?: SupervisorSignOffType;
  supervisorSignOffName?: string;
  formStatus?: Status;
  supervisorSignOffSignature?: any;
  postSignatureName?: postSignatureInfo;
  jsbId?: string;
  postJobBriefData?: PostJobBrief;
}

export enum Status {
  IN_PROGRESS = "IN_PROGRESS",
  COMPLETE = "COMPLETE",
  PENDING_SIGN_OFF = "PENDING_SIGN_OFF",
  PENDING_POST_JOB_BRIEF = "PENDING_POST_JOB_BRIEF",
  NOT_EXISTS = "NOT_EXISTS",
}
