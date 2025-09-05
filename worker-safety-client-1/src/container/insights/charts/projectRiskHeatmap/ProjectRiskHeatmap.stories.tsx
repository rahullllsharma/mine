/* eslint-disable @typescript-eslint/no-explicit-any */
import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { samplePortfolioFilters } from "@/container/insights/charts/__mocks__/sharedMockData";
import { InsightsMockedProvider } from "@/container/insights/charts/__mocks__/mockDataHelper";
import ProjectRiskHeatmap from "./ProjectRiskHeatmap";
import { projectRiskMockData, mockDataNoResult } from "./__mocks__/mockData";

export default {
  title: "Container/Insights/Charts/ProjectRiskHeatmap",
  component: ProjectRiskHeatmap,
  argTypes: {
    data: { table: { disable: true } },
  },
  decorators: [
    Story => (
      <InsightsMockedProvider>
        <Story />
      </InsightsMockedProvider>
    ),
  ],
} as ComponentMeta<typeof ProjectRiskHeatmap>;

const Template: ComponentStory<typeof ProjectRiskHeatmap> = args => (
  <ProjectRiskHeatmap filters={samplePortfolioFilters} {...args} />
);

const mockDataDecorators: any = [
  (Story: any) => (
    <InsightsMockedProvider mocks={projectRiskMockData}>
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
