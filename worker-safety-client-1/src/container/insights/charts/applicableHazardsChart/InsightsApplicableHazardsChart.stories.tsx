/* eslint-disable @typescript-eslint/no-explicit-any */
import type { ComponentMeta, ComponentStory } from "@storybook/react";

import { InsightsTab } from "@/container/insights/charts/types";
import {
  sampleProjectFilters,
  samplePortfolioFilters,
} from "@/container/insights/charts/__mocks__/sharedMockData";
import { InsightsMockedProvider } from "@/container/insights/charts/__mocks__/mockDataHelper";
import { applicableHazardsMocks, mockDataNoResult } from "./__mocks__/mockData";
import InsightsApplicableHazardsChart from "./InsightsApplicableHazardsChart";

export default {
  title: "Container/Insights/Charts/ApplicableHazardsChart",
  component: InsightsApplicableHazardsChart,
} as ComponentMeta<typeof InsightsApplicableHazardsChart>;

const Template: ComponentStory<typeof InsightsApplicableHazardsChart> =
  args => <InsightsApplicableHazardsChart {...args} />;

const mockDataDecorators: any = [
  (Story: any) => (
    <div style={{ height: "100vh", overflow: "auto" }}>
      <InsightsMockedProvider mocks={applicableHazardsMocks}>
        <Story />
      </InsightsMockedProvider>
    </div>
  ),
];

const noDataDecorators: any = [
  (Story: any) => (
    <div style={{ height: "100vh", overflow: "auto" }}>
      <InsightsMockedProvider mocks={mockDataNoResult}>
        <Story />
      </InsightsMockedProvider>
    </div>
  ),
];

export const PortfolioTab = Template.bind({});
PortfolioTab.args = {
  tab: InsightsTab.PORTFOLIO,
  filters: samplePortfolioFilters,
};
PortfolioTab.decorators = mockDataDecorators;

export const ProjectTab = Template.bind({});
ProjectTab.args = {
  tab: InsightsTab.PROJECT,
  filters: sampleProjectFilters,
};
ProjectTab.decorators = mockDataDecorators;

export const PortfolioTabNoData = Template.bind({});
PortfolioTabNoData.args = {
  tab: InsightsTab.PORTFOLIO,
  filters: samplePortfolioFilters,
};
PortfolioTabNoData.decorators = noDataDecorators;

export const ProjectTabNoData = Template.bind({});
ProjectTabNoData.args = {
  tab: InsightsTab.PROJECT,
  filters: sampleProjectFilters,
};
ProjectTabNoData.decorators = noDataDecorators;
