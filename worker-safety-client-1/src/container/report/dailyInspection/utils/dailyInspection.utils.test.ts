import type { DailyReportResponse } from "./dailyInspection.utils";
import type { DailyReport } from "@/types/report/DailyReport";
import { DailyReportStatus } from "@/types/report/DailyReportStatus";
import {
  getStartDateTimeFromSavedReport,
  getWorkScheduleStartDateTime,
  applyRecommendationsToSections,
  applyDefaultsToArrayFields,
} from "./dailyInspection.utils";

const crewRecommendation = {
  constructionCompany: "ACME inc.",
  foremanName: "John Doe",
};

const safetyAndComplianceRecommendation = {
  phaCompletion: "1",
  sopNumber: "123",
  sopType: "4123",
  stepsCalledIn: "444",
};

const dailyReport = {
  sections: {
    workSchedule: {
      startDatetime: "2022-07-10T23:00:00+00:00",
      endDatetime: "2022-07-11T23:00:00+00:00",
      sectionIsValid: true,
    },
    additionalInformation: {
      progress: "some comment",
      lessons: "another comment",
      sectionIsValid: true,
    },
    crew: {
      sectionIsValid: false,
      contractor: "Urbint",
      foremanName: "Jane Doe",
      nWelders: 0,
      nSafetyProf: 0,
      nOperators: 0,
      nFlaggers: 0,
      nLaborers: 0,
      nOtherCrew: 0,
      documents: null,
    },
    safetyAndCompliance: {
      sectionIsValid: true,
      plans: {},
      jobBrief: {
        jobBriefConductAfterWork: "0",
        comprehensiveJobBriefConduct: "1",
      },
      workMethods: { contractorAccess: "1" },
      digSafeMarkOuts: {
        markOutsVerified: "1",
        digSafeMarkOutsLocation: "something",
        facilitiesLocatedAndExposed: "1",
      },
      operatorQualifications: { qualificationsVerified: "1" },
      spottersSafetyObserver: {},
      systemOperatingProcedures: {
        sopId: "spa",
        sopType: "types",
        onSiteAndCurrent: "0",
        sopStepsCalledIn: "1",
        gasControlsNotified: "1",
      },
      privateProtectionEquipment: { wearingPPE: "1" },
    },
  },
} as unknown as DailyReportResponse;

const date = "2022-07-09";

describe("src/container/report/dailyInspection/utils/dailyInspection.utils", () => {
  describe(getWorkScheduleStartDateTime.name, () => {
    describe("when the work schedule data is passed", () => {
      it("should return the start date", () => {
        const formData = {
          workSchedule: {
            startDatetime: `${date}T00:00`,
            endDatetime: `${date}T00:00`,
            dateLimits: {
              projectStartDate: "2022-07-07T00:00",
              projectEndDate: "2022-07-10T00:00",
            },
          },
          additionalInformation: null,
        };

        expect(getWorkScheduleStartDateTime(formData)).toBe(date);
      });
    });

    describe("when we don't have work schedule data", () => {
      it("should throw an exception", () => {
        expect(getWorkScheduleStartDateTime).toThrow(
          "Unable to get start date time from Work Schedule section in form"
        );
      });
    });
  });

  describe(getStartDateTimeFromSavedReport.name, () => {
    describe("when we have an existing daily report", () => {
      it("should return the start date from work schedule section", () => {
        const partialDailyReport = {
          createdAt: "2022-07-11T08:18:45.312787+00:00",
          createdBy: {
            id: "7f5975ac-6cfc-4b9a-848d-b1ceb52b7ec7",
            name: "Super User",
          },
          id: "3f83f66e-85dd-4cbe-a85b-cf26f4ed5231",
          sections: {
            workSchedule: {
              endDatetime: `${date}T23:00:00+00:00`,
              sectionIsValid: true,
              startDatetime: `${date}T23:00:00+00:00`,
            },
          },
          status: DailyReportStatus.IN_PROGRESS,
        };

        expect(getStartDateTimeFromSavedReport(partialDailyReport)).toBe(date);
      });
    });

    describe("when we don't have work schedule data", () => {
      it("should throw an exception", () => {
        expect(getStartDateTimeFromSavedReport).toThrow(
          "Unable to get start date time from existing daily report"
        );
      });
    });
  });

  describe(applyRecommendationsToSections.name, () => {
    it.each([undefined, null])(
      "should skip recommendations if the recommendations are not set",
      recommendations => {
        const recommendedDailyReport = undefined;
        expect(
          applyRecommendationsToSections({
            dailyReport: recommendedDailyReport,
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            recommendations,
          })
        ).toBe(recommendedDailyReport);
      }
    );

    it.each([
      {},
      { crew: null },
      { crew: undefined },
      { crew: {} },
      { crew: { foremanName: undefined } },
      { safetyAndCompliance: null },
      { safetyAndCompliance: undefined },
      { safetyAndCompliance: {} },
      { safetyAndCompliance: { phaCompletion: undefined } },
    ])(
      "should skip recommendations when not filled properly",
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      ({ recommendation }) => {
        const draftDailyReport = {
          ...dailyReport,
          sections: {
            ...dailyReport.sections,
            crew: null,
            safetyAndCompliance: null,
          },
        };

        const result = applyRecommendationsToSections({
          dailyReport: draftDailyReport,
          recommendations: recommendation,
        });

        expect(result).toBe(draftDailyReport);
      }
    );

    it("should skip recommendations if the crew and control assessment are filled", () => {
      const recommendations = {
        crew: crewRecommendation,
        safetyAndCompliance: safetyAndComplianceRecommendation,
      };

      const result = applyRecommendationsToSections({
        dailyReport,
        recommendations,
      }) as DailyReport;

      expect(result?.sections?.crew?.foremanName).not.toEqual(
        recommendations.crew.foremanName
      );
      expect(result).toBe(dailyReport);
    });

    it.each([
      {
        sections: {},
        recommended: {},
      },
      {
        sections: {
          crew: null,
        },
        recommended: {
          crew: {
            contractor: crewRecommendation.constructionCompany,
            foremanName: crewRecommendation.foremanName,
          },
        },
      },
      {
        sections: {
          safetyAndCompliance: null,
        },
        recommended: {
          safetyAndCompliance: {
            plans: {
              comprehensivePHAConducted:
                safetyAndComplianceRecommendation.phaCompletion,
            },
            systemOperatingProcedures: {
              sopId: safetyAndComplianceRecommendation.sopNumber,
              sopType: safetyAndComplianceRecommendation.sopType,
              sopStepsCalledIn: safetyAndComplianceRecommendation.stepsCalledIn,
            },
          },
        },
      },
    ])(
      "should only add recommendations to sections that are null",
      ({ sections, recommended }) => {
        const recommendations = {
          crew: crewRecommendation,
          safetyAndCompliance: safetyAndComplianceRecommendation,
        };

        const result = applyRecommendationsToSections({
          dailyReport: {
            ...dailyReport,
            sections: {
              ...dailyReport.sections,
              ...sections,
            },
          },
          recommendations,
        });

        for (const key of Object.keys(recommendations) as Array<
          keyof typeof recommendations
        >) {
          const affected = result?.sections?.[key];
          const expected =
            key in sections && !sections[key]
              ? recommended[key]
              : dailyReport.sections[key];

          // assert that the section was not modified, not recommendation was applied.
          expect(affected).toEqual(expected);
        }
      }
    );

    it("should skip recommendations when the recommendations are not set", () => {
      const recommendations = {
        crew: null,
        safetyAndCompliance: null,
      };

      const modifiedDailyReport = {
        ...dailyReport,
        sections: {
          ...dailyReport.sections,
          crew: null,
          safetyAndCompliance: null,
        },
      };

      const result = applyRecommendationsToSections({
        dailyReport: modifiedDailyReport,
        recommendations,
      }) as DailyReport;

      expect(result).toStrictEqual(modifiedDailyReport);
    });

    it("should apply both recommendations if the crew and control assessment are null", () => {
      const recommendations = {
        crew: crewRecommendation,
        safetyAndCompliance: safetyAndComplianceRecommendation,
      };

      const result = applyRecommendationsToSections({
        dailyReport: {
          ...dailyReport,
          sections: {
            ...dailyReport.sections,
            crew: null,
            safetyAndCompliance: null,
          },
        },
        recommendations,
      }) as DailyReport;

      expect(result?.sections?.crew).toEqual({
        contractor: crewRecommendation.constructionCompany,
        foremanName: crewRecommendation.foremanName,
      });
      expect(result?.sections?.safetyAndCompliance).toEqual({
        plans: {
          comprehensivePHAConducted:
            safetyAndComplianceRecommendation.phaCompletion,
        },
        systemOperatingProcedures: {
          sopId: safetyAndComplianceRecommendation.sopNumber,
          sopType: safetyAndComplianceRecommendation.sopType,
          sopStepsCalledIn: safetyAndComplianceRecommendation.stepsCalledIn,
        },
      });
    });

    it("should apply the recommendations if the daily report is new", () => {
      const recommendations = {
        crew: crewRecommendation,
        safetyAndCompliance: safetyAndComplianceRecommendation,
      };

      const result = applyRecommendationsToSections({
        dailyReport: undefined,
        recommendations,
      }) as DailyReport;

      expect(result?.sections?.crew).toEqual({
        contractor: crewRecommendation.constructionCompany,
        foremanName: crewRecommendation.foremanName,
      });

      expect(result?.sections?.safetyAndCompliance).toEqual({
        plans: {
          comprehensivePHAConducted:
            safetyAndComplianceRecommendation.phaCompletion,
        },
        systemOperatingProcedures: {
          sopId: safetyAndComplianceRecommendation.sopNumber,
          sopType: safetyAndComplianceRecommendation.sopType,
          sopStepsCalledIn: safetyAndComplianceRecommendation.stepsCalledIn,
        },
      });
    });
  });

  describe(applyDefaultsToArrayFields.name, () => {
    it("should return undefined if no daily report is passed", () => {
      const modifiedDailyReport = undefined;
      expect(applyDefaultsToArrayFields(modifiedDailyReport)).toBeUndefined();
    });

    it.each([
      {
        key: "crew",
        values: {
          ...dailyReport.sections.crew,
          documents: ["ab"],
        },
      },
      {
        key: "attachments",
        values: {
          photos: ["photo", "another"],
        },
      },
      {
        key: "attachments",
        values: {
          documents: ["doc", "another"],
        },
      },
      {
        key: "attachments",
        values: {
          photos: ["photo", "another"],
          documents: ["doc", "another"],
        },
      },
    ])("should NOT affect the section", ({ key, values }) => {
      const modifiedDailyReport = {
        ...dailyReport,
        sections: {
          ...dailyReport.sections,
          [key]: values,
        },
      };

      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      expect(applyDefaultsToArrayFields(modifiedDailyReport)).toStrictEqual(
        modifiedDailyReport
      );
    });

    it.each([
      {
        key: "crew",
        values: {
          ...dailyReport.sections.crew,
          documents: null,
        },
      },
      {
        key: "attachments",
        values: {
          photos: null,
        },
      },
      {
        key: "attachments",
        values: {
          documents: null,
        },
      },
      {
        key: "attachments",
        values: {
          photos: null,
          documents: null,
        },
      },
    ] as const)(
      "should affect the section and set empty array as the default value",
      ({ key, values }) => {
        const result = applyDefaultsToArrayFields({
          ...dailyReport,
          // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore
          sections: {
            ...dailyReport.sections,
            [key]: values,
          },
        });

        // only documents or photos are valid
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        Object.entries(result.sections?.[key])
          .filter(([k]) => ["documents", "photos"].includes(k))
          .forEach(([, value]) => {
            expect(value).toBeInstanceOf(Array);
            expect(value).toHaveLength(0);
          });
      }
    );
  });
});
