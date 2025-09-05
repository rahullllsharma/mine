import type { FiltersPayload } from "@/container/insights/charts/types";
import type { ReasonsNotImplementedBarChartProps } from "./ReasonsNotImplementedBarChart";
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
import { getControlNotPerformedOptions } from "@/container/report/jobHazardAnalysis/constants";

import {
  sampleReasonsNotImplementedData,
  reasonsNotImpledMockData,
  mockDataNoResult,
  mockDataPartialResult,
} from "@/container/insights/charts/reasonsNotImplementedBarChart/__mocks__/mockData";
import ReasonsNotImplementedBarChart from "./ReasonsNotImplementedBarChart";

const defaultProps = {
  filters: samplePortfolioFilters,
  tab: InsightsTab.PORTFOLIO,
};

const renderChart = async (
  props: ReasonsNotImplementedBarChartProps,
  mocks = reasonsNotImpledMockData
) => {
  return renderInsightsChart(
    <ReasonsNotImplementedBarChart {...defaultProps} {...props} />,
    mocks
  );
};

describe.each([
  {
    tab: InsightsTab.PORTFOLIO,
    filters: samplePortfolioFilters,
    filtersDescriptions: samplePortfolioFiltersDesc,
  },
  {
    tab: InsightsTab.PROJECT,
    filters: sampleProjectFilters,
    filtersDescriptions: sampleProjectFiltersDesc,
  },
])(
  `${ReasonsNotImplementedBarChart.name} in tab: $tab`,
  ({
    tab,
    filters,
    filtersDescriptions,
  }: {
    tab: InsightsTab;
    filters: FiltersPayload;
    filtersDescriptions: FiltersDescriptionsReturn;
  }) => {
    describe("renders titles, labels, and axes", () => {
      beforeEach(async () => {
        await renderChart({ tab, filters, filtersDescriptions });
      });

      it("renders a title", async () => {
        await screen.findByText(/Reasons for controls not implemented/);
      });

      it("renders the x-axis label", async () => {
        await screen.findByText(/# of times reason reported/);
      });
    });

    describe("renders data", () => {
      let container: Element;
      beforeEach(async () => {
        container = await renderChart({ tab, filters, filtersDescriptions });
      });

      it.each(sampleReasonsNotImplementedData)(
        "renders $reason as $count",
        async ({ reason, count }) => {
          const ariaLabel = `count: ${count} for: ${reason}`;
          const bar = container.querySelector(
            `rect[aria-label="${ariaLabel}"]`
          );
          expect(bar).toBeTruthy();
        }
      );
    });

    describe.each([
      { name: "all data", mocks: reasonsNotImpledMockData },
      { name: "partial data", mocks: mockDataPartialResult },
    ])("shows all y-axis labels given $name results", ({ mocks }) => {
      it.each(getControlNotPerformedOptions())(
        "renders the label: $name",
        async ({ name }) => {
          await renderChart({ tab, filters, filtersDescriptions }, mocks);
          await screen.findByText(name);
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
