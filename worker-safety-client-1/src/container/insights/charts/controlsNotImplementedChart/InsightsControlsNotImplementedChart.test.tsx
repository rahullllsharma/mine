import type { FiltersPayload } from "@/container/insights/charts/types";
import type { InsightsControlsNotImplementedChartProps } from "./InsightsControlsNotImplementedChart";
import type { FiltersDescriptionsReturn } from "../hooks/useFiltersDescriptions";
import { screen } from "@testing-library/react";
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
  controlsNotImpledMocks,
  sampleControlsNotImplementedData,
  mockDataNoResult,
} from "./__mocks__/mockData";
import InsightsControlsNotImplementedChart from "./InsightsControlsNotImplementedChart";

const renderChart = async (
  props: InsightsControlsNotImplementedChartProps,
  mocks = controlsNotImpledMocks
) => {
  return renderInsightsChart(
    <InsightsControlsNotImplementedChart {...props} />,
    mocks
  );
};

describe.each([
  {
    tab: InsightsTab.PORTFOLIO,
    filters: samplePortfolioFilters,
    filtersDescriptions: samplePortfolioFiltersDesc,
    subCharts: ["By Project", "By Hazard", "By Task", "By Task Type"],
  },
  {
    tab: InsightsTab.PROJECT,
    filters: sampleProjectFilters,
    filtersDescriptions: sampleProjectFiltersDesc,
    subCharts: ["By Location", "By Hazard", "By Task", "By Task Type"],
  },
])(
  `${InsightsControlsNotImplementedChart.name} in tab: $tab`,
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
        await screen.findByText(/Controls Not Implemented/);
      });

      it("renders the x-axis tick values", async () => {
        await screen.findByText(/Library Control 0/);
        await screen.findByText(/Library Control 1/);
        await screen.findByText(/Library Control 2/);
      });

      it("renders the y-axis label", async () => {
        await screen.findByText(/% of controls not implemented/);
      });

      it.each(subCharts)(`renders $name sub-charts`, async name => {
        await screen.findByText(name);
      });
    });

    describe("renders data", () => {
      let container: Element;
      beforeEach(async () => {
        container = await renderChart({ tab, filters, filtersDescriptions });
      });
      it.each(sampleControlsNotImplementedData)(
        `renders $libraryControl as $percent`,
        async ({ percent, libraryControl }) => {
          const ariaLabel = `percent: ${percent * 100} for: ${
            libraryControl.name
          }`;
          const bar = container.querySelector(
            `rect[aria-label="${ariaLabel}"]`
          );
          expect(bar).toBeTruthy();
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
