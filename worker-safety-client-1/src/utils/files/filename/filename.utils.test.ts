import {
  generateExportedProjectFilename,
  generateExportedPortfolioFilename,
} from "./filename.utils";

jest.useFakeTimers();
jest.setSystemTime(new Date("2022-05-23T10:25:00.000Z"));

describe("filename", () => {
  describe(generateExportedProjectFilename.name, () => {
    it("should filename include the project id", () => {
      expect(
        generateExportedProjectFilename({
          project: {
            number: "project-abc",
            name: "project-name-abc",
          },
          title: "Project risk over time",
        })
      ).toEqual(expect.stringContaining("project-abc"));
    });

    it("should filename generate include the project name", () => {
      expect(
        generateExportedProjectFilename({
          project: {
            number: "project-abc",
            name: "project-name-abc",
          },
          title: "Location risk over time",
        })
      ).toEqual(expect.stringContaining("project-name-abc"));
    });

    it("should include todays date in the US format", () => {
      expect(
        generateExportedProjectFilename({
          project: {
            number: "project-abc",
            name: "project-name-abc",
          },
          title: "Location risk over time",
        })
      ).toEqual(expect.stringContaining("05/23/22"));
    });

    it("should output the filename with the tenant, chart information and todays date, separated by hifens without the extension", () => {
      jest.setSystemTime(new Date("2022-03-25T10:25:00.000Z"));
      expect(
        generateExportedProjectFilename({
          project: {
            number: "project-abc",
            name: "project-name-abc",
          },
          title: "Project risk over time",
        })
      ).toEqual(
        "[project-abc]-project-name-abc-Project risk over time-Urbint-03/25/22"
      );
    });
  });

  describe(generateExportedPortfolioFilename.name, () => {
    it("should generate include the tenant name", () => {
      expect(
        generateExportedPortfolioFilename({
          tenant: "Urbint Gas",
          title: "Project risk over time",
        })
      ).toEqual(expect.stringContaining("Urbint Gas"));
    });

    it("should generate include the chart name", () => {
      expect(
        generateExportedPortfolioFilename({
          tenant: "Urbint Gas",
          title: "Location risk over time",
        })
      ).toEqual(expect.stringContaining("Location risk over time"));
    });

    it("should include todays date in the US format", () => {
      expect(
        generateExportedPortfolioFilename({
          tenant: "Urbint Gas",
          title: "Location risk over time",
        })
      ).toEqual(expect.stringContaining("03/25/22"));
    });

    it("should output the filename with the tenant, chart information and todays date, separated by hifens without the extension", () => {
      jest.setSystemTime(new Date("2022-03-25T10:25:00.000Z"));
      expect(
        generateExportedPortfolioFilename({
          tenant: "National Grid",
          title: "Project risk over time",
        })
      ).toEqual("National Grid-Project risk over time-Urbint-03/25/22");
    });
  });
});
