import type { ProjectRiskBarChartProps } from "./ProjectRiskBarChart";
import { fireEvent, screen } from "@testing-library/react";
import { renderInsightsChart } from "@/container/insights/charts/__mocks__/mockDataHelper";
import { samplePortfolioFilters } from "@/container/insights/charts/__mocks__/sharedMockData";
import { InsightsMode } from "@/container/insights/charts/types";
import { mockTenantStore } from "@/utils/dev/jest";
import { projectRiskMockData, mockDataNoResult } from "./__mocks__/mockData";
import ProjectRiskBarChart from "./ProjectRiskBarChart";

const defaultProps = {
  filters: samplePortfolioFilters,
  mode: InsightsMode.LEARNINGS,
};

const renderChart = async (
  props: ProjectRiskBarChartProps,
  mocks = projectRiskMockData
) => {
  return renderInsightsChart(
    <ProjectRiskBarChart {...defaultProps} {...props} />,
    mocks
  );
};

mockTenantStore();

describe.each([InsightsMode.LEARNINGS, InsightsMode.PLANNING])(
  `${ProjectRiskBarChart.name} in mode: %s`,
  (mode: InsightsMode) => {
    describe("renders titles, labels, and axes", () => {
      beforeEach(async () => {
        await renderChart({ mode });
      });

      it("renders a title", async () => {
        await screen.findByText(/Project risk over time/);
      });

      it("renders a legend label", async () => {
        await screen.findByText(/Risk level/);
      });

      it("renders the legend keys", async () => {
        await screen.findByText(/Low/);
        await screen.findByText(/Medium/);
        await screen.findByText(/High/);
      });

      it("renders the x-axis label", async () => {
        await screen.findByText(/Time frame/);
      });

      it("renders the y-axis label", async () => {
        await screen.findByText(/# of Projects/);
      });

      it("renders all the dates", async () => {
        await screen.findByText("1/29/22");
        await screen.findByText("1/30/22");
        await screen.findByText("1/31/22");
        await screen.findByText("2/1/22");
        await screen.findByText("2/2/22");
        await screen.findByText("2/3/22");
      });
    });

    describe("renders data and tooltips", () => {
      mockTenantStore();
      let container: Element;
      beforeEach(async () => {
        container = await renderChart({ mode });
      });

      it("renders a tooltip", async () => {
        // indirectly testing that bars were rendered
        const ariaLabel = "Low: 30 for: 1/29/22";
        const bar = container.querySelector(`rect[aria-label="${ariaLabel}"]`);
        fireEvent.mouseOver(bar as Element);
        await screen.findByText(/30 low risk projects/);
      });

      it("renders a tooltip (singular, for count = 1)", async () => {
        const ariaLabel = "High: 1 for: 2/1/22";
        const bar = container.querySelector(`rect[aria-label="${ariaLabel}"]`);
        fireEvent.mouseOver(bar as Element);
        await screen.findByText(/1 high risk project/);
      });
    });

    describe("handles an empty state", () => {
      beforeEach(async () => {
        await renderChart({ mode }, mockDataNoResult);
      });

      it("renders a nice message", async () => {
        await screen.findByText(
          "There is currently no data available for this chart"
        );
      });
    });
  }
);
