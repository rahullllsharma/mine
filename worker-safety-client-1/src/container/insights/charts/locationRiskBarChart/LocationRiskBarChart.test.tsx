import type { LocationRiskBarChartProps } from "./LocationRiskBarChart";
import { fireEvent, screen } from "@testing-library/react";
import { renderInsightsChart } from "@/container/insights/charts/__mocks__/mockDataHelper";
import { sampleProjectFilters } from "@/container/insights/charts/__mocks__/sharedMockData";
import { InsightsMode } from "@/container/insights/charts/types";
import { mockTenantStore } from "@/utils/dev/jest";
import { insightsTenant } from "../__mocks__/tenant.mock";
import { locationRiskMockData, mockDataNoResult } from "./__mocks__/mockData";
import LocationRiskBarChart from "./LocationRiskBarChart";

const defaultProps = {
  filters: sampleProjectFilters,
  mode: InsightsMode.LEARNINGS,
};

const renderChart = async (
  props: LocationRiskBarChartProps,
  mocks = locationRiskMockData
) => {
  return renderInsightsChart(
    <LocationRiskBarChart {...defaultProps} {...props} />,
    mocks
  );
};

describe.each([InsightsMode.LEARNINGS, InsightsMode.PLANNING])(
  `${LocationRiskBarChart.name} in mode: %s`,
  (mode: InsightsMode) => {
    beforeAll(() => {
      mockTenantStore(insightsTenant);
    });

    describe("renders titles, labels, and axes", () => {
      beforeEach(async () => {
        await renderChart({ mode });
      });

      it("renders a title", async () => {
        await screen.findByRole("heading", {
          name: /^location risk over time$/gi,
        });
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
        await screen.findByText(/# of Locations/);
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
      let container: Element;
      beforeEach(async () => {
        container = await renderChart({ mode });
      });

      it("renders a tooltip", async () => {
        // indirectly testing that bars were rendered
        const ariaLabel = "Low: 30 for: 1/29/22";
        const bar = container.querySelector(`rect[aria-label="${ariaLabel}"]`);
        fireEvent.mouseOver(bar as Element);
        await screen.findByText(/30 low risk locations/);
      });

      it("renders a tooltip (singular, for count = 1)", async () => {
        const ariaLabel = "High: 1 for: 2/1/22";
        const bar = container.querySelector(`rect[aria-label="${ariaLabel}"]`);
        fireEvent.mouseOver(bar as Element);
        await screen.findByText(/1 high risk location/);
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
