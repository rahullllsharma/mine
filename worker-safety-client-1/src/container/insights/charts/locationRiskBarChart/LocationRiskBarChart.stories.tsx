/* eslint-disable @typescript-eslint/no-explicit-any */
import type { ComponentMeta, ComponentStory } from "@storybook/react";

import { InsightsMode } from "@/container/insights/charts/types";
import { sampleProjectFilters } from "@/container/insights/charts/__mocks__/sharedMockData";
import { InsightsMockedProvider } from "@/container/insights/charts/__mocks__/mockDataHelper";
import { locationRiskMockData, mockDataNoResult } from "./__mocks__/mockData";
import LocationRiskBarChart from "./LocationRiskBarChart";

export default {
  title: "Container/Insights/Charts/LocationRiskBarChart",
  component: LocationRiskBarChart,
} as ComponentMeta<typeof LocationRiskBarChart>;

const Template: ComponentStory<typeof LocationRiskBarChart> = args => {
  return <LocationRiskBarChart filters={sampleProjectFilters} {...args} />;
};

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

export const LearningsMode = Template.bind({});
LearningsMode.args = {
  mode: InsightsMode.LEARNINGS,
};
LearningsMode.decorators = mockDataDecorators;

export const PlanningMode = Template.bind({});
PlanningMode.args = {
  mode: InsightsMode.PLANNING,
};
PlanningMode.decorators = mockDataDecorators;

export const LearningsModeNoData = Template.bind({});
LearningsModeNoData.args = {
  mode: InsightsMode.LEARNINGS,
};
LearningsModeNoData.decorators = noDataDecorators;

export const PlanningModeNoData = Template.bind({});
PlanningModeNoData.args = {
  mode: InsightsMode.PLANNING,
};
PlanningModeNoData.decorators = noDataDecorators;
