import type { ComponentMeta, ComponentStory } from "@storybook/react";

import { InsightsTab } from "@/container/insights/charts/types";
import {
  samplePortfolioFilters,
  sampleProjectFilters,
} from "@/container/insights/charts/__mocks__/sharedMockData";
import { InsightsMockedProvider } from "@/container/insights/charts/__mocks__/mockDataHelper";
import {
  reasonsNotImpledMockData,
  mockDataNoResult,
  mockDataPartialResult,
} from "./__mocks__/mockData";
import ReasonsNotImplementedBarChart from "./ReasonsNotImplementedBarChart";

export default {
  title: "Container/Insights/Charts/ReasonsNotImplementedBarChart",
  component: ReasonsNotImplementedBarChart,
} as ComponentMeta<typeof ReasonsNotImplementedBarChart>;

const Template: ComponentStory<typeof ReasonsNotImplementedBarChart> = args => (
  <ReasonsNotImplementedBarChart {...args} />
);

export const PortfolioTab = Template.bind({});
PortfolioTab.args = {
  tab: InsightsTab.PORTFOLIO,
  filters: samplePortfolioFilters,
};
PortfolioTab.decorators = [
  Story => (
    <InsightsMockedProvider mocks={reasonsNotImpledMockData}>
      <Story />
    </InsightsMockedProvider>
  ),
];

export const ProjectTab = Template.bind({});
ProjectTab.args = {
  tab: InsightsTab.PROJECT,
  filters: sampleProjectFilters,
};
ProjectTab.decorators = [
  Story => (
    <InsightsMockedProvider mocks={reasonsNotImpledMockData}>
      <Story />
    </InsightsMockedProvider>
  ),
];

export const PortfolioTabNoData = Template.bind({});
PortfolioTabNoData.args = {
  tab: InsightsTab.PORTFOLIO,
  filters: samplePortfolioFilters,
};
PortfolioTabNoData.decorators = [
  Story => (
    <InsightsMockedProvider mocks={mockDataNoResult}>
      <Story />
    </InsightsMockedProvider>
  ),
];

export const ProjectTabNoData = Template.bind({});
ProjectTabNoData.args = {
  tab: InsightsTab.PROJECT,
  filters: sampleProjectFilters,
};
ProjectTabNoData.decorators = [
  Story => (
    <InsightsMockedProvider mocks={mockDataNoResult}>
      <Story />
    </InsightsMockedProvider>
  ),
];

export const PortfolioTabPartialData = Template.bind({});
PortfolioTabPartialData.args = {
  tab: InsightsTab.PORTFOLIO,
  filters: samplePortfolioFilters,
};
PortfolioTabPartialData.decorators = [
  Story => (
    <InsightsMockedProvider mocks={mockDataPartialResult}>
      <Story />
    </InsightsMockedProvider>
  ),
];

export const ProjectTabPartialData = Template.bind({});
ProjectTabPartialData.args = {
  tab: InsightsTab.PROJECT,
  filters: sampleProjectFilters,
};
ProjectTabPartialData.decorators = [
  Story => (
    <InsightsMockedProvider mocks={mockDataPartialResult}>
      <Story />
    </InsightsMockedProvider>
  ),
];
