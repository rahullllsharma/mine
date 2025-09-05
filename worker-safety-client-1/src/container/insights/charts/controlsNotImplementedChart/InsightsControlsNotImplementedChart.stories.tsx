/* eslint-disable @typescript-eslint/no-explicit-any */
import type { ComponentMeta, ComponentStory } from "@storybook/react";

import { InsightsTab } from "@/container/insights/charts/types";
import {
  samplePortfolioFilters,
  sampleProjectFilters,
} from "@/container/insights/charts/__mocks__/sharedMockData";
import { InsightsMockedProvider } from "@/container/insights/charts/__mocks__/mockDataHelper";
import { controlsNotImpledMocks, mockDataNoResult } from "./__mocks__/mockData";
import InsightsControlsNotImplementedChart from "./InsightsControlsNotImplementedChart";

export default {
  title: "Container/Insights/Charts/ControlsNotImplementedChart",
  component: InsightsControlsNotImplementedChart,
} as ComponentMeta<typeof InsightsControlsNotImplementedChart>;

const Template: ComponentStory<typeof InsightsControlsNotImplementedChart> =
  args => {
    return <InsightsControlsNotImplementedChart {...args} />;
  };

const mockDataDecorators: any = [
  (Story: any) => (
    <InsightsMockedProvider mocks={controlsNotImpledMocks}>
      <Story />
    </InsightsMockedProvider>
  ),
];

const noDataDecorators: any = [
  (Story: any) => (
    <InsightsMockedProvider mocks={mockDataNoResult}>
      <Story />
    </InsightsMockedProvider>
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
