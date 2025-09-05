import type { Project } from "@/types/project/Project";
import type { Location } from "@/types/project/Location";
import type { DailyReport as DailyInspectionReportType } from "@/types/report/DailyReport";
import type { MultiStepFormStep } from "../multiStepForm/state/reducer";
import type { JobHazardAnalysisGraphQLPayloadParams as JobHazardAnalysisFields } from "../jobHazardAnalysis/transformers/graphQLPayload";

import type { jobHazardAnalysisFormInputPrefix } from "@/components/report/jobReport/JobReportCard";
import type { taskFormInputPrefix } from "../tasks/Tasks";
import type {
  workScheduleFormInputPrefix,
  WorkScheduleProps as WorkScheduleFields,
} from "../workSchedule/WorkSchedule";
import type { DailyReportRecommendations } from "@/types/report/DailyReportRecommendations";
import type { FormViewTabStates } from "@/components/forms/Utils";

type DailyInspectionReport = {
  project: Project;
  location: Location;
  dailyReport?: DailyInspectionReportType;
  projectSummaryViewDate?: string;
  recommendations: DailyReportRecommendations["dailyReport"] | null;
  selectedTeb?: FormViewTabStates;
  setSelectedTab?: (tab: string) => void;
};

export type CriticalActivityType = {
  date: string;
  isCritical: boolean;
};
type DailyInspectionReportStepProps = Omit<
  DailyInspectionReport,
  "projectSummaryViewDate"
> & {
  defaults: Required<Pick<DailyInspectionReport, "projectSummaryViewDate">>;
};

type DailyInspectionReportMultiStep = MultiStepFormStep<{
  transformFormDataToSchema?: (
    formData: any,
    options: Pick<DailyInspectionReport, "location">
  ) => any;
}>;

type DailyInspectionReportForms = {
  [workScheduleFormInputPrefix]?: WorkScheduleFields;
  [taskFormInputPrefix]?: Record<string, true>;
  [jobHazardAnalysisFormInputPrefix]?: JobHazardAnalysisFields["jobHazardAnalysis"];
  safetyAndCompliance?: Record<string, never>;
  crew?: Record<string, never> | null;
  additionalInformation: Record<string, never> | null;
};

type DailyInspectionReportSectionKeys = keyof NonNullable<
  DailyInspectionReportType["sections"]
>;

export type {
  DailyInspectionReport,
  DailyInspectionReportStepProps,
  DailyInspectionReportMultiStep,
  DailyInspectionReportForms,
  DailyInspectionReportSectionKeys,
};
