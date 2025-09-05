import type { DailyReport as DailyInspectionReportType } from "@/types/report/DailyReport";
import type { DailyInspectionReportMultiStep } from "../types";
import { cloneDeep } from "lodash-es";
import { getDailyReportMetadataWithCompletedSections } from "./markDailyReportSectionsCompletedFromReport.utils";

const metadata = [
  {
    id: "workSchedule",
    name: "workSchedule",
    path: "#workSchedule",
  },
  {
    id: "safetyAndCompliance",
    name: "Safety And Compliance",
    path: "#safety-and-compliance",
  },
  {
    id: "crew",
    name: "Crew",
    path: "#crew",
  },
  {
    id: "additionalInformation",
    name: "Additional Information",
    path: "#additional-information",
  },
  {
    id: "attachments",
    name: "Attachments",
    path: "#attachments",
  },
] as DailyInspectionReportMultiStep[];

describe(getDailyReportMetadataWithCompletedSections.name, () => {
  it("should not affect metadata if no daily report is found", () => {
    expect(getDailyReportMetadataWithCompletedSections(metadata)).toBe(
      metadata
    );
  });

  describe("when DOES NOT include the sectionIsValid propery", () => {
    let result: DailyInspectionReportMultiStep[];
    const completedSection = "attachments";

    beforeEach(() => {
      const storedDailyReport = {
        sections: {
          [completedSection]: {
            lessons: "hello",
            another: null,
          },
        },
      } as unknown as DailyInspectionReportType;

      result = getDailyReportMetadataWithCompletedSections(
        metadata,
        storedDailyReport
      );
    });

    it("should mark a section as completed if has data stored", () => {
      expect(
        result.find(section => section.id === completedSection)?.status
      ).toBe("completed");
    });

    it("should NOT mark sections as completed if the section is null", () => {
      result
        .filter(section => section.id !== completedSection)
        .forEach(section => {
          expect(section?.status).toBeUndefined();
        });
    });
  });

  describe("when includes the sectionIsValid property", () => {
    it("should mark a section as default when the section is marked as null", () => {
      const storedDailyReport = {
        sections: {
          workSchedule: {
            sectionIsValid: null,
            startDatetime: "2022-02-25T00:00",
            endDatetime: null,
          },
        },
      } as unknown as DailyInspectionReportType;

      const result = getDailyReportMetadataWithCompletedSections(
        metadata,
        storedDailyReport
      );

      expect(result.find(r => r.id === "workSchedule")?.status).toBeUndefined();
    });

    it("should mark a section as completed if it was saved in a daily inspection report", () => {
      const storedDailyReport = {
        sections: {
          crew: {
            sectionIsValid: null,
          },
          attachments: {
            sectionIsValid: false,
          },
          additionalInformation: {
            sectionIsValid: true,
            lessons: "dummy",
          },
        },
      } as unknown as DailyInspectionReportType;

      const result = getDailyReportMetadataWithCompletedSections(
        metadata,
        storedDailyReport
      );

      expect(
        result.find(r => r.id === "additionalInformation")?.status
      ).toEqual("completed");

      result
        .filter(r => r.id !== "additionalInformation")
        .forEach(section => {
          expect(section?.status).toBeUndefined();
        });
    });

    it("should mark a section as completed if it was saved in a daily inspection report", () => {
      const storedDailyReport = {
        sections: {
          additionalInformation: {
            sectionIsValid: true,
            lessons: "dummy",
          },
        },
      } as unknown as DailyInspectionReportType;

      const result = getDailyReportMetadataWithCompletedSections(
        metadata,
        storedDailyReport
      );
      expect(
        result.find(r => r.id === "additionalInformation")?.status
      ).toEqual("completed");
    });

    describe("when the daily inspection report has several sections filled", () => {
      let result: DailyInspectionReportMultiStep[];
      beforeAll(() => {
        const storedDailyReport = {
          sections: {
            safetyAndCompliance: null,
            additionalInformation: {
              sectionIsValid: true,
              lessons: "dummy",
            },
            attachments: {
              sectionIsValid: true,
              files: [],
            },
          },
        } as unknown as DailyInspectionReportType;

        result = getDailyReportMetadataWithCompletedSections(
          metadata,
          storedDailyReport
        );
      });

      it("should mark the stored sections as completed", () => {
        expect(
          result.find(r => r.id === "additionalInformation")?.status
        ).toEqual("completed");
        expect(result.find(r => r.id === "attachments")?.status).toEqual(
          "completed"
        );
      });

      it("should leave the other sections as default", () => {
        expect(
          result.find(r => r.id === "safetyAndCompliance")?.status
        ).toBeUndefined();
        expect(result.find(r => r.id === "crew")?.status).toBeUndefined();
      });
    });

    describe("between daily reports", () => {
      it("should NOT affect the original metadata between calls", () => {
        const originalMetadata = cloneDeep(metadata);

        const storedDailyReport = {
          sections: {
            workSchedule: {
              sectionIsValid: true,
              startDate: "2022-01-01",
            },
            crew: {
              sectionIsValid: true,
              contractor: null,
            },
            safetyAndCompliance: {
              sectionIsValid: true,
              dummy: 1,
            },
            additionalInformation: {
              sectionIsValid: true,
              lessons: "dummy",
            },
            attachments: {
              sectionIsValid: true,
              files: [],
            },
          },
        } as unknown as DailyInspectionReportType;

        expect(
          getDailyReportMetadataWithCompletedSections(
            metadata,
            storedDailyReport
          ).every(item => item.status === "completed")
        ).toBe(true);

        expect(getDailyReportMetadataWithCompletedSections(metadata)).toEqual(
          originalMetadata
        );
      });
    });
  });
});
