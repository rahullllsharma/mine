import { fireEvent, screen } from "@testing-library/react";
import { renderInsightsChart } from "@/container/insights/charts/__mocks__/mockDataHelper";
import {
  samplePortfolioFilters,
  samplePortfolioFiltersDesc,
} from "@/container/insights/charts/__mocks__/sharedMockData";
import { mockTenantStore } from "@/utils/dev/jest";
import { getFormattedDate } from "@/utils/date/helper";
import { InsightsTab } from "../types";
import ProjectRiskHeatmap from "./ProjectRiskHeatmap";
import { projectRiskMockData, mockDataNoResult } from "./__mocks__/mockData";

const renderChart = async (mocks = projectRiskMockData) => {
  return renderInsightsChart(
    <ProjectRiskHeatmap
      tab={InsightsTab.PROJECT}
      filters={samplePortfolioFilters}
      filtersDescriptions={samplePortfolioFiltersDesc}
    />,
    mocks
  );
};

describe(ProjectRiskHeatmap.name, () => {
  mockTenantStore();
  describe("when passed projectRisk data", () => {
    beforeEach(async () => {
      await renderChart();
    });

    it("renders a title", async () => {
      await screen.findByText(/Project risk by day/);
    });

    it("renders a legend", async () => {
      await screen.findByText(/Risk level/);
      await screen.findByText(/Low risk/);
      await screen.findByText(/Medium risk/);
      await screen.findByText(/High risk/);
    });

    it("renders a project name column", async () => {
      await screen.findByText(/Project name/i);
    });

    it("renders project names", async () => {
      await screen.findByText("Project 0");
      await screen.findByText("Project 5");
    });
  });

  describe("renders tooltips on hover", () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let container: any;
    beforeEach(async () => {
      container = await renderChart();
    });

    it("renders a tooltip (high)", async () => {
      const ariaLabel = `High risk on ${getFormattedDate(
        "2022-01-29",
        "long"
      )}`;
      const cell = container.querySelector(`div[aria-label="${ariaLabel}"]`);
      fireEvent.mouseOver(cell);

      // should be 2 including the legend
      const highFound = await screen.findAllByText(/High risk/);
      expect(highFound.length).toBe(2);

      // sanity check
      const lowFound = await screen.findAllByText(/Low risk/);
      expect(lowFound.length).toBe(1);
    });

    it("renders a tooltip (low)", async () => {
      const ariaLabel = `Low risk on ${getFormattedDate("2022-02-01", "long")}`;
      const cell = container.querySelector(`div[aria-label="${ariaLabel}"]`);
      fireEvent.mouseOver(cell);

      // sanity check
      const highFound = await screen.findAllByText(/High risk/);
      expect(highFound.length).toBe(1);

      // should be 2 including the legend
      const lowFound = await screen.findAllByText(/Low risk/);
      expect(lowFound.length).toBe(2);
    });
  });

  describe("handles an empty state", () => {
    beforeEach(async () => {
      await renderChart(mockDataNoResult);
    });

    it("renders a nice message", async () => {
      await screen.findByText(
        "There is currently no data available for this chart"
      );
    });
  });
});
