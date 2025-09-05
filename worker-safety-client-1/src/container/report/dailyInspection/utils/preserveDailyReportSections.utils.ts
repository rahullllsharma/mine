import type { DailyReport } from "@/types/report/DailyReport";

import { jobHazardAnalysisFormInputPrefix } from "@/components/report/jobReport/JobReportCard";
import { taskFormInputPrefix } from "../../tasks/Tasks";
import { workScheduleFormInputPrefix } from "../../workSchedule/WorkSchedule";

type DailyReportSectionsKeys = keyof NonNullable<DailyReport["sections"]>;

type DailyInspectionReportResettableSections = Extract<
  DailyReportSectionsKeys,
  typeof workScheduleFormInputPrefix | typeof taskFormInputPrefix
>;

const revalidateSectionsBySection: {
  [k in DailyInspectionReportResettableSections]: Array<
    Partial<DailyReportSectionsKeys>
  >;
} = {
  [workScheduleFormInputPrefix]: [
    taskFormInputPrefix,
    jobHazardAnalysisFormInputPrefix,
  ],
  [taskFormInputPrefix]: [jobHazardAnalysisFormInputPrefix],
};

function preserveDailyReportSections(
  currentSection: DailyInspectionReportResettableSections,
  dailyReport?: DailyReport
): Partial<NonNullable<DailyReport["sections"]>> {
  const staledSectionsBasedOnCurrentSection =
    revalidateSectionsBySection[currentSection] || [];

  const {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    sections: { [currentSection]: _, ...remaining } = {},
  } = dailyReport || {};

  return Object.fromEntries(
    Object.entries(remaining).filter(
      ([section]: Array<DailyReportSectionsKeys>) =>
        !staledSectionsBasedOnCurrentSection.includes(section)
    )
  );
}

function defaultSectionIsValidPropBySections(
  dailyReportPayload: Required<Pick<DailyReport, "sections">>["sections"]
) {
  return Object.fromEntries(
    Object.entries(dailyReportPayload).map(([key, value]) => [
      key,
      value === null
        ? null
        : {
            ...value,
            ...{ sectionIsValid: value?.sectionIsValid ?? null },
          },
    ])
  );
}

// export types
export type { DailyInspectionReportResettableSections };

// exports
export {
  revalidateSectionsBySection,
  preserveDailyReportSections,
  defaultSectionIsValidPropBySections,
};
