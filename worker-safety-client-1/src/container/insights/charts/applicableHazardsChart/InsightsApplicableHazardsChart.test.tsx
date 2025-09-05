import type { FiltersPayload } from "@/container/insights/charts/types";
import type { InsightsApplicableHazardsChartProps } from "./InsightsApplicableHazardsChart";
import type { FiltersDescriptionsReturn } from "../hooks/useFiltersDescriptions";
import { fireEvent, screen } from "@testing-library/react";
import { renderInsightsChart } from "@/container/insights/charts/__mocks__/mockDataHelper";
import {
  samplePortfolioFilters,
  samplePortfolioFiltersDesc,
  sampleProjectFilters,
  sampleProjectFiltersDesc,
} from "@/container/insights/charts/__mocks__/sharedMockData";
import { InsightsTab } from "@/container/insights/charts/types";
import { mockTenantStore } from "@/utils/dev/jest";
import {
  sampleApplicableHazardsData,
  applicableHazardsMocks,
  mockDataNoResult,
} from "./__mocks__/mockData";
import InsightsApplicableHazardsChart from "./InsightsApplicableHazardsChart";

const renderChart = async (
  props: InsightsApplicableHazardsChartProps,
  mocks = applicableHazardsMocks
) => {
  return renderInsightsChart(
    <InsightsApplicableHazardsChart {...props} />,
    mocks
  );
};

describe.each([
  {
    tab: InsightsTab.PORTFOLIO,
    filters: samplePortfolioFilters,
    filtersDescriptions: samplePortfolioFiltersDesc,
    subCharts: ["By Project", "By Site Condition", "By Task", "By Task Type"],
  },
  {
    tab: InsightsTab.PROJECT,
    filters: sampleProjectFilters,
    filtersDescriptions: sampleProjectFiltersDesc,
    subCharts: ["By Location", "By Site Condition", "By Task", "By Task Type"],
  },
])(
  `${InsightsApplicableHazardsChart.name} in tab: $tab`,
  ({
    tab,
    filters,
    filtersDescriptions,
    subCharts,
  }: {
    tab: InsightsTab;
    filters: FiltersPayload;
    filtersDescriptions: FiltersDescriptionsReturn;
    subCharts: string[];
  }) => {
    describe("renders titles, labels, and axes", () => {
      mockTenantStore();
      beforeEach(async () => {
        await renderChart({ tab, filters, filtersDescriptions });
      });

      it("renders a title", async () => {
        await screen.findByText(/Applicable Hazards/);
      });

      it("renders the x-axis tick values", async () => {
        await screen.findByText(/Library Hazard 0/);
        await screen.findByText(/Library Hazard 1/);
        await screen.findByText(/Library Hazard 2/);
      });

      it("renders the y-axis label", async () => {
        await screen.findByText(/# of times hazard was applicable/);
      });

      it.each(subCharts)(`renders %s sub-charts`, async name => {
        await screen.findByText(name);
      });
    });

    describe("renders data", () => {
      let container: Element;
      beforeEach(async () => {
        container = await renderChart({ tab, filters, filtersDescriptions });
      });
      it.each(sampleApplicableHazardsData)(
        `renders $libraryHazard as $count, with tooltip`,
        async ({ count, libraryHazard }) => {
          const ariaLabel = `count: ${count} for: ${libraryHazard.name}`;
          const bar = container.querySelector(
            `rect[aria-label="${ariaLabel}"]`
          );
          expect(bar).toBeTruthy();

          fireEvent.mouseOver(bar as Element);
          await screen.findByText(
            `${libraryHazard.name} was applicable ${count} ${
              count === 1 ? "time" : "times"
            }`
          );
        }
      );
    });

    describe("handles an empty state", () => {
      beforeEach(async () => {
        await renderChart(
          { tab, filters, filtersDescriptions },
          mockDataNoResult
        );
      });

      it("renders a nice message", async () => {
        await screen.findByText(
          "There is currently no data available for this chart"
        );
      });
    });
  }
);
