import type { UploadItem } from "@/components/upload/Upload";
import type { PlansInputs } from "@/components/report/jobReport/safetyAndCompliance/plans/Plans";
import type { JobBriefInputs } from "@/components/report/jobReport/safetyAndCompliance/jobBrief/JobBrief";
import type { WorkMethodsInputs } from "@/components/report/jobReport/safetyAndCompliance/workMethods/WorkMethods";
import type { DigSafeMarkOutsInputs } from "@/components/report/jobReport/safetyAndCompliance/digSafeMarkOuts/DigSafeMarkOuts";
import type { SystemOperatingProceduresInputs } from "@/components/report/jobReport/safetyAndCompliance/systemOperatingProcedures/SystemOperatingProcedures";
import type { SpottersSafetyObserverInputs } from "@/components/report/jobReport/safetyAndCompliance/spottersSafetyObserver/SpottersSafetyObserver";
import type { PrivateProtectionEquipmentInputs } from "@/components/report/jobReport/safetyAndCompliance/privateProtectionEquipment/PrivateProtectionEquipment";
import type { OperatorQualificationsInputs } from "@/components/report/jobReport/safetyAndCompliance/operatorQualifications/OperatorQualifications";
import type { RiskLevel } from "@/components/riskBadge/RiskLevel";
import type { AdditionalInformationInputs } from "@/container/report/additionalInformation/AdditionalInformation";
import type { DailySourceInformationConceptsInput } from "@/api/generated/types";

type DailyInspectionInputsPartialUpdateStatus<T> = T & {
  sectionIsValid?: boolean | null;
};

// Commented the other sections as it will throw type check errors for now
export type DailyReportInputs = {
  workSchedule?: DailyInspectionInputsPartialUpdateStatus<WorkScheduleInputs>;
  taskSelection?: DailyInspectionInputsPartialUpdateStatus<TaskSelectionSectionInputs>;
  jobHazardAnalysis?: DailyInspectionInputsPartialUpdateStatus<JobHazardAnalysisSectionInputs>;
  safetyAndCompliance?: DailyInspectionInputsPartialUpdateStatus<SafetyComplianceInputs>;
  crew?: DailyInspectionInputsPartialUpdateStatus<CrewInputs>;
  attachments?: DailyInspectionInputsPartialUpdateStatus<AttachmentsInputs>;
  additionalInformation?: DailyInspectionInputsPartialUpdateStatus<AdditionalInformationInputs>;
  dailySourceInfo?: DailyInspectionInputsPartialUpdateStatus<dailySourceInfoInput>;
};

export type dailySourceInfoInput = {
  dailySourceInfo: DailySourceInformationConceptsInput;
  appVersion: string;
};

export type CrewInputs = {
  contractor: string | null;
  foremanName: string | null;
  nWelders: number | "" | null;
  nSafetyProf: number | "" | null;
  nFlaggers: number | "" | null;
  nLaborers: number | "" | null;
  nOperators: number | "" | null;
  nOtherCrew: number | "" | null;
  documents: UploadItem[] | null;
};

export type AttachmentsInputs = {
  photos: UploadItem[] | null;
  documents: UploadItem[] | null;
};

export type SafetyComplianceInputs = {
  plans?: PlansInputs;
  jobBrief?: JobBriefInputs;
  workMethods?: WorkMethodsInputs;
  digSafeMarkOuts?: DigSafeMarkOutsInputs;
  systemOperatingProcedures?: SystemOperatingProceduresInputs;
  spottersSafetyObserver?: SpottersSafetyObserverInputs;
  privateProtectionEquipment?: PrivateProtectionEquipmentInputs;
  operatorQualifications?: OperatorQualificationsInputs;
};

export type WorkScheduleInputs = {
  startDatetime: string | null;
  endDatetime: string | null;
};

export type TaskSelectionInputs = {
  id: string;
  name: string;
  riskLevel: RiskLevel;
};

export type TaskSelectionSectionInputs = {
  selectedTasks: TaskSelectionInputs[];
};

export type SiteConditionAnalysisInputs = {
  id: string;
  isApplicable: boolean;
  notApplicableReason?: string;
  hazards: HazardAnalysisInput[];
};

export type ControlAnalysisInput = {
  id: string;
  implemented: boolean;
  notImplementedReason?: string;
  furtherExplanation?: string;
};

export type HazardAnalysisInput = {
  id: string;
  isApplicable: boolean;
  notApplicableReason?: string;
  controls: ControlAnalysisInput[];
};

export type TaskAnalysisInputs = {
  id: string;
  notes: string;
  performed: boolean;
  notApplicableReason?: string;
  hazards: HazardAnalysisInput[];
};

export type JobHazardAnalysisSectionInputs = {
  siteConditions: SiteConditionAnalysisInputs[];
  tasks: TaskAnalysisInputs[];
};
