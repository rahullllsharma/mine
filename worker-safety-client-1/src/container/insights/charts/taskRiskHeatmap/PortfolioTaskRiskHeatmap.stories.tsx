/* eslint-disable @typescript-eslint/no-explicit-any */
import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { samplePortfolioFilters } from "@/container/insights/charts/__mocks__/sharedMockData";
import { InsightsMockedProvider } from "@/container/insights/charts/__mocks__/mockDataHelper";
import PortfolioTaskRiskHeatmap from "./PortfolioTaskRiskHeatmap";
import { taskRiskMockData, mockDataNoResult } from "./__mocks__/mockData";

export default {
  title: "Container/Insights/Charts/PortfolioTaskRiskHeatmap",
  component: PortfolioTaskRiskHeatmap,
} as ComponentMeta<typeof PortfolioTaskRiskHeatmap>;

const Template: ComponentStory<typeof PortfolioTaskRiskHeatmap> = args => (
  <PortfolioTaskRiskHeatmap filters={samplePortfolioFilters} {...args} />
);

const mockDataDecorators: any = [
  (Story: any) => (
    <InsightsMockedProvider mocks={taskRiskMockData}>
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

export const Playground = Template.bind({});
Playground.args = {};
Playground.decorators = mockDataDecorators;

export const NoData = Template.bind({});
NoData.args = {};
NoData.decorators = noDataDecorators;
