import { fireEvent, screen } from "@testing-library/react";

import {
  samplePortfolioFilters,
  sampleProjectFilters,
} from "@/container/insights/charts/__mocks__/sharedMockData";
import { renderInsightsChart } from "@/container/insights/charts/__mocks__/mockDataHelper";
import { mockTenantStore } from "@/utils/dev/jest";
import { getFormattedDate } from "@/utils/date/helper";
import PortfolioTaskRiskHeatmap from "./PortfolioTaskRiskHeatmap";
import ProjectTaskRiskHeatmap from "./ProjectTaskRiskHeatmap";
import { taskRiskMockData, mockDataNoResult } from "./__mocks__/mockData";

const renderChart = async (
  name: string,
  args = {},
  mocks = taskRiskMockData
) => {
  if (name == PortfolioTaskRiskHeatmap.name) {
    return renderInsightsChart(<PortfolioTaskRiskHeatmap {...args} />, mocks);
  } else if (name == ProjectTaskRiskHeatmap.name)
    return renderInsightsChart(<ProjectTaskRiskHeatmap {...args} />, mocks);
};

describe.each([
  {
    name: PortfolioTaskRiskHeatmap.name,
    filters: samplePortfolioFilters,
  },
  {
    name: ProjectTaskRiskHeatmap.name,
    filters: sampleProjectFilters,
  },
])(`$name`, ({ name, filters }) => {
  describe("when passed taskRisk data", () => {
    mockTenantStore();
    beforeEach(async () => {
      await renderChart(name, { filters });
    });

    it("renders a title", async () => {
      await screen.findByText(/Task risk by day/);
    });

    it("renders a task name column", async () => {
      await screen.findByText(/Task name/);
    });

    it("renders task names", async () => {
      await screen.findByText("Task 0");
      await screen.findByText("Task 5");
    });
  });

  describe("renders tooltips on hover", () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let container: any;
    beforeEach(async () => {
      container = await renderChart(name, { filters });
    });

    it("renders a tooltip (high)", async () => {
      const ariaLabel = `High risk on ${getFormattedDate(
        "2022-01-29",
        "long"
      )}`;
      const cell = container.querySelector(`div[aria-label="${ariaLabel}"]`);
      fireEvent.mouseOver(cell);
      // should be 1 - no legend on the TaskRiskHeatmap
      const highFound = await screen.findAllByText(/High risk/);
      expect(highFound.length).toBe(1);
    });

    it("renders a tooltip (low)", async () => {
      const ariaLabel = `Low risk on ${getFormattedDate("2022-02-01", "long")}`;
      const cell = container.querySelector(`div[aria-label="${ariaLabel}"]`);
      fireEvent.mouseOver(cell);
      // should be 1 - no legend
      const lowFound = await screen.findAllByText(/Low risk/);
      expect(lowFound.length).toBe(1);
    });
  });

  describe("handles an empty state", () => {
    beforeEach(async () => {
      await renderChart(name, { filters }, mockDataNoResult);
    });

    it("renders a nice message", async () => {
      await screen.findByText(
        "There is currently no data available for this chart"
      );
    });
  });
});
