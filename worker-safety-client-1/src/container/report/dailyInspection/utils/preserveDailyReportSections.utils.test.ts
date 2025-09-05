import type { DailyReport } from "@/types/report/DailyReport";
import { jobHazardAnalysisFormInputPrefix } from "@/components/report/jobReport/JobReportCard";
import { taskFormInputPrefix } from "../../tasks/Tasks";
import { workScheduleFormInputPrefix } from "../../workSchedule/WorkSchedule";
import {
  defaultSectionIsValidPropBySections,
  preserveDailyReportSections,
  revalidateSectionsBySection,
} from "./preserveDailyReportSections.utils";

const sections = {
  [workScheduleFormInputPrefix]: {
    startDatetime: "2022-02-08T10:10:00.000Z",
    endDatetime: "2022-02-25T20:20:00.000Z",
  },
  [taskFormInputPrefix]: {
    selectedTasks: [
      {
        id: "6420a636-baa0-4cc4-9115-2472e285c9e7",
        name: "Confined space entry",
        riskLevel: "unknown",
      },
    ],
  },
  [jobHazardAnalysisFormInputPrefix]: {
    foo: "bar",
  },
  safetyAndCompliance: {
    foo: "bar",
  },
  additionalInformation: {
    field1: "name",
    field2: "another name",
  },
};

const dailyReport = {
  sections,
} as unknown as DailyReport;

describe(preserveDailyReportSections.name, () => {
  it("should not remove any section when selected section doesnt affect other sections", () => {
    const { additionalInformation: _, ...expected } = sections;
    expect(
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      preserveDailyReportSections("additionalInformation", dailyReport)
    ).toEqual(expected);
  });

  describe(`for ${workScheduleFormInputPrefix} section`, () => {
    const removeableSections =
      revalidateSectionsBySection[workScheduleFormInputPrefix].join(", ");
    const result = preserveDailyReportSections(
      workScheduleFormInputPrefix,
      dailyReport
    );

    it(`should exclude the current selection`, () => {
      expect(result).not.toHaveProperty(workScheduleFormInputPrefix);
    });

    it(`should reset the following sections ${removeableSections}`, () => {
      const { additionalInformation } = sections;
      expect(result).toEqual({
        additionalInformation,
        safetyAndCompliance: sections.safetyAndCompliance,
      });
    });
  });

  describe(`for ${taskFormInputPrefix}`, () => {
    const removeableSections =
      revalidateSectionsBySection[taskFormInputPrefix].join(", ");
    const result = preserveDailyReportSections(
      taskFormInputPrefix,
      dailyReport
    );

    it(`should exclude the current selection`, () => {
      expect(result).not.toHaveProperty(taskFormInputPrefix);
    });

    it(`should reset the following sections ${removeableSections}`, () => {
      const { jobHazardAnalysis: _, taskSelection: __, ...expected } = sections;
      expect(result).toEqual(expected);
    });
  });
});

describe(defaultSectionIsValidPropBySections.name, () => {
  it("should include the `sectionIsValid` prop as null when the section does not have it set", () => {
    expect(
      defaultSectionIsValidPropBySections({
        [workScheduleFormInputPrefix]: sections[workScheduleFormInputPrefix],
      })
    ).toHaveProperty(`${workScheduleFormInputPrefix}.sectionIsValid`, null);
  });

  it("should skip if the section already includes the `sectionIsValid` property", () => {
    expect(
      defaultSectionIsValidPropBySections({
        [workScheduleFormInputPrefix]: {
          ...sections[workScheduleFormInputPrefix],
          sectionIsValid: false,
        },
      })
    ).toHaveProperty(`${workScheduleFormInputPrefix}.sectionIsValid`, false);
  });

  it("should skip if the section is null", () => {
    expect(
      defaultSectionIsValidPropBySections({
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        [workScheduleFormInputPrefix]: null,
      })
    ).not.toHaveProperty(`${workScheduleFormInputPrefix}.sectionIsValid`, null);
  });

  it("should only affect sections that don't have `sectionIsValid` set", () => {
    const payload = {
      ...sections,
      safetyAndCompliance: {
        plans: {
          comprehensivePHAConducted: "1",
        },

        systemOperatingProcedures: {
          sopId: "123",
          sopType: "4123",
          sopStepsCalledIn: "444",
        },
      },
      crew: {
        foremanName: "jose",
        contractor: "AccuWeld Technologies Inc",
        sectionIsValid: true,
      },
      attachments: null,
    } as unknown as Required<Pick<DailyReport, "sections">>["sections"];

    const result = defaultSectionIsValidPropBySections(payload);

    // include the property as null
    expect(result).toHaveProperty(
      `${workScheduleFormInputPrefix}.sectionIsValid`,
      null
    );
    expect(result).toHaveProperty(
      `${taskFormInputPrefix}.sectionIsValid`,
      null
    );
    expect(result).toHaveProperty("safetyAndCompliance.sectionIsValid", null);
    // skip if it exists
    expect(result).toHaveProperty("crew.sectionIsValid", true);

    expect(result).not.toHaveProperty("attachments.sectionIsValid", true);
  });
});
