import type { JobHazardAnalysisSectionInputs } from "@/types/report/DailyReportInputs";

import { jobHazardAnalysisFormInputPrefix } from "@/components/report/jobReport/JobReportCard";

type BaseFormData<T = Record<string, unknown>> = {
  [key: string]: {
    performed?: boolean;
    notes?: string;
    isApplicable?: boolean;
    notApplicableReason?: {
      id: string;
      name: string;
    };
    hazards: {
      [key: string]: {
        isApplicable: boolean;
        notApplicableReason?: {
          id: string;
          name: string;
        };
        controls: {
          [key: string]: {
            implemented: boolean;
            notImplementedReason?: {
              id: string;
              name: string;
            };
            furtherExplanation?: string;
          };
        };
      };
    };
  } & T;
};

type TasksFormData = BaseFormData;

type SiteConditionsFormData = BaseFormData;

export type JobHazardAnalysisGraphQLPayloadParams = {
  [jobHazardAnalysisFormInputPrefix]: {
    tasks: TasksFormData;
    siteConditions: SiteConditionsFormData;
  };
};

export type ReturnedJobHazardAnalysisGraphQLPayload = {
  [jobHazardAnalysisFormInputPrefix]: NonNullable<JobHazardAnalysisSectionInputs>;
};

type JobHazardAnalysisSectionName =
  keyof JobHazardAnalysisGraphQLPayloadParams["jobHazardAnalysis"];

const controlsDefaultValue = false;

/**
 * Parse the form raw data into a valid schema for either tasks or site conditions
 * @param {SiteConditionsFormData|TasksFormData} data
 * @todo
 *  TODO: This should use a generic to infer the return value based on the TValues used
 */
const transformToGraphqlSchema = (
  type: JobHazardAnalysisSectionName,
  data: JobHazardAnalysisGraphQLPayloadParams["jobHazardAnalysis"],
  withDefaultControlValue: boolean
) =>
  Object.entries(data?.[type] || {}).map(
    ([id, { hazards = {}, ...values }]) => ({
      id,
      // SiteConditionAnalysisInputs
      ...(type === "siteConditions" && {
        isApplicable: values.isApplicable ?? true,
      }),
      // TaskAnalysisInputs
      ...(type === "tasks" && {
        performed: values.performed ?? true,
        notApplicableReason: values.notApplicableReason?.name ?? "",
        notes: values.notes ?? "",
      }),
      hazards: Object.entries(hazards).map(
        ([hazardId, { isApplicable = true, controls = {} }]) => ({
          id: hazardId,
          isApplicable,
          controls: Object.entries(controls).map(
            ([
              controlsId,
              { implemented, notImplementedReason, furtherExplanation },
            ]) => ({
              id: controlsId,
              implemented: withDefaultControlValue
                ? implemented ?? controlsDefaultValue
                : implemented,
              notImplementedReason: notImplementedReason?.name ?? "",
              furtherExplanation: furtherExplanation ?? "",
            })
          ),
        })
      ),
    })
  );

/**
 * From a RHF form shape, convert its contents to a payload that is consumable by the mutation.
 * It will set default values if needed.
 *
 * @param {JobHazardAnalysisFormParams} formData
 * @returns {JobHazardAnalysisGraphQLPayload}
 */
function graphQLPayload(
  formData: JobHazardAnalysisGraphQLPayloadParams,
  { withDefaultControlValue } = { withDefaultControlValue: true }
): ReturnedJobHazardAnalysisGraphQLPayload {
  const { [jobHazardAnalysisFormInputPrefix]: jobHazardAnalysis } =
    formData || {};
  return {
    [jobHazardAnalysisFormInputPrefix]: {
      tasks: transformToGraphqlSchema(
        "tasks",
        jobHazardAnalysis,
        withDefaultControlValue
      ) as ReturnedJobHazardAnalysisGraphQLPayload["jobHazardAnalysis"]["tasks"],
      siteConditions: transformToGraphqlSchema(
        "siteConditions",
        jobHazardAnalysis,
        withDefaultControlValue
      ) as ReturnedJobHazardAnalysisGraphQLPayload["jobHazardAnalysis"]["siteConditions"],
    },
  };
}

export default graphQLPayload;
