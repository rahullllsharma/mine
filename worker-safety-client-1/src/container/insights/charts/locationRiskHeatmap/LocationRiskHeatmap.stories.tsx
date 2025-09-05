/* eslint-disable @typescript-eslint/no-explicit-any */
import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { sampleProjectFilters } from "@/container/insights/charts/__mocks__/sharedMockData";
import { InsightsMockedProvider } from "@/container/insights/charts/__mocks__/mockDataHelper";
import LocationRiskHeatmap from "./LocationRiskHeatmap";
import { locationRiskMockData, mockDataNoResult } from "./__mocks__/mockData";

export default {
  title: "Container/Insights/Charts/LocationRiskHeatmap",
  component: LocationRiskHeatmap,
} as ComponentMeta<typeof LocationRiskHeatmap>;

const Template: ComponentStory<typeof LocationRiskHeatmap> = args => (
  <LocationRiskHeatmap filters={sampleProjectFilters} {...args} />
);

const mockDataDecorators: any = [
  (Story: any) => (
    <InsightsMockedProvider mocks={locationRiskMockData}>
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
