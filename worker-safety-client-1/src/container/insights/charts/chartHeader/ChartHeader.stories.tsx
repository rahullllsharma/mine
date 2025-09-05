import type { ComponentMeta, ComponentStory } from "@storybook/react";

import ChartHeader from "./ChartHeader";

export default {
  title: "Container/Insights/Charts/ChartHeader",
  component: ChartHeader,
} as ComponentMeta<typeof ChartHeader>;

const Template: ComponentStory<typeof ChartHeader> = args => {
  return <ChartHeader {...args} />;
};

export const Playground = Template.bind({});
Playground.args = {
  title: "Example",
  chartData: [["workbook", [{ column: "value " }]]],
};
