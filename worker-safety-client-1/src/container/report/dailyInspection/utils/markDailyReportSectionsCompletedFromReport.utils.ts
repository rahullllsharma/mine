import type { DailyReport as DailyInspectionReportType } from "@/types/report/DailyReport";
import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import type { DailyInspectionReportMultiStep } from "../types";

type DailyReportInputsKeys = keyof NonNullable<DailyReportInputs>;

/**
 * Checks if the current section is completed or not.
 * It should work for both new (with sectionIsValid) and old sections (without the flag)
 * For new reports, `sectionIsValid` can assume 3 values (true | false | null)
 *
 * When sectionIsValid = NULL, it should fallback to the old way of checking
 * if a section is valid or not, which is basically checking if the section has values.
 */
const isSectionCompleted = (
  section:
    | NonNullable<DailyInspectionReportType["sections"]>[DailyReportInputsKeys]
    | null
    | undefined = {}
) => {
  if (
    section !== null &&
    Object.prototype.hasOwnProperty.call(section, "sectionIsValid")
  ) {
    return section?.sectionIsValid;
  }

  return Object.values(section || {}).length !== 0;
};

function getDailyReportMetadataWithCompletedSections(
  metadata: DailyInspectionReportMultiStep[],
  savedDailyReport?: DailyInspectionReportType
): DailyInspectionReportMultiStep[] {
  if (!savedDailyReport?.sections) {
    return metadata;
  }

  return metadata.map(item => {
    const hasSectionCompleted = isSectionCompleted(
      savedDailyReport.sections?.[item.id as DailyReportInputsKeys]
    );

    return {
      ...item,
      status: hasSectionCompleted ? "completed" : item?.status,
    };
  });
}

export { getDailyReportMetadataWithCompletedSections };
