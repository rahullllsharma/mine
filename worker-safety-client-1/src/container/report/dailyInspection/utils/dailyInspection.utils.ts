import type { DailyInspectionReportForms } from "../types";
import type { DailyReport } from "@/types/report/DailyReport";
import type { DailyReportRecommendations } from "@/types/report/DailyReportRecommendations";
import { convertDateToString } from "@/utils/date/helper";
import { workScheduleFormInputPrefix } from "../../workSchedule/WorkSchedule";

// Types
type DailyReportResponse = Omit<DailyReport, "sections"> & {
  sections: Required<
    {
      [k in keyof Required<DailyReport>["sections"]]:
        | Required<DailyReport>["sections"][k]
        | null;
    }
  >;
};

type ApplyRecommendationsFn = (params: {
  recommendations: DailyReportRecommendations["dailyReport"] | null;
  dailyReport: DailyReportResponse | undefined;
}) => DailyReport | undefined;

type ApplyDefaultsToArrayFieldsFn = (
  params: DailyReport | undefined
) => DailyReport | undefined;

// Private functions

const getCrewSectionRecommendations = ({
  crew,
}: Pick<DailyReportRecommendations["dailyReport"], "crew">) =>
  crew === null
    ? null
    : {
        foremanName: crew.foremanName,
        contractor: crew.constructionCompany,
      };

const getSafetyAndComplianceSectionRecommendations = ({
  safetyAndCompliance,
}: Pick<DailyReportRecommendations["dailyReport"], "safetyAndCompliance">) =>
  safetyAndCompliance === null
    ? null
    : {
        plans: {
          comprehensivePHAConducted: safetyAndCompliance.phaCompletion,
        },
        systemOperatingProcedures: {
          sopId: safetyAndCompliance.sopNumber,
          sopType: safetyAndCompliance.sopType,
          sopStepsCalledIn: safetyAndCompliance.stepsCalledIn,
        },
      };

// Public functions

function getWorkScheduleStartDateTime(
  formData: DailyInspectionReportForms
): string {
  const startDateTime = formData?.[workScheduleFormInputPrefix]?.startDatetime;
  if (startDateTime) {
    return convertDateToString(startDateTime);
  }

  throw new Error(
    "Unable to get start date time from Work Schedule section in form"
  );
}

function getStartDateTimeFromSavedReport(dailyReport?: DailyReport): string {
  const startDateTime = dailyReport?.sections?.workSchedule?.startDatetime;
  if (startDateTime) {
    return convertDateToString(startDateTime);
  }

  throw new Error("Unable to get start date time from existing daily report");
}

/** Generate the daily report based on the recommendations */
const applyRecommendationsToSections: ApplyRecommendationsFn = ({
  recommendations,
  dailyReport,
}) => {
  if (!recommendations) {
    return dailyReport as DailyReport;
  }

  const { crew, safetyAndCompliance } = dailyReport?.sections || {};

  // All sections filled
  if (!!crew && !!safetyAndCompliance) {
    return dailyReport as DailyReport;
  }

  return {
    ...dailyReport,
    sections: {
      ...(dailyReport?.sections || {}),
      crew: crew || getCrewSectionRecommendations(recommendations),
      safetyAndCompliance:
        safetyAndCompliance ||
        getSafetyAndComplianceSectionRecommendations(recommendations),
    },
  } as DailyReport;
};

/** Apply an empty array for all attachment fields (documents and photos) for all sections */
const applyDefaultsToArrayFields: ApplyDefaultsToArrayFieldsFn =
  dailyReport => {
    if (!dailyReport || !dailyReport?.sections) {
      return dailyReport;
    }

    const modifiedDailyReport = {
      ...dailyReport,
      sections: {
        ...dailyReport.sections,
      },
    };

    // we could this recursively or use lodash but for now, we only have these scenarios.
    if (modifiedDailyReport.sections?.crew) {
      modifiedDailyReport.sections.crew.documents ??= [];
    }

    if (modifiedDailyReport.sections?.attachments) {
      modifiedDailyReport.sections.attachments.documents ??= [];
      modifiedDailyReport.sections.attachments.photos ??= [];
    }

    return modifiedDailyReport;
  };

export type { DailyReportResponse };

export {
  applyRecommendationsToSections,
  applyDefaultsToArrayFields,
  getWorkScheduleStartDateTime,
  getStartDateTimeFromSavedReport,
};
