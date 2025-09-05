import type { ComponentMeta, ComponentStory } from "@storybook/react";

import ChartCard from "./ChartCard";

export default {
  title: "Container/Insights/ChartDrillDown/Card",
  component: ChartCard,
} as ComponentMeta<typeof ChartCard>;

const Template: ComponentStory<typeof ChartCard> = args => (
  <ChartCard {...args} />
);

export const WithEmptyContent = Template.bind({});
WithEmptyContent.args = {
  title: "By location",
  type: "hazard",
};

export const WithChart = Template.bind({});
WithChart.args = {
  title: "By location",
  type: "hazard",
  chart: <div>Chart should be placed here</div>,
};
