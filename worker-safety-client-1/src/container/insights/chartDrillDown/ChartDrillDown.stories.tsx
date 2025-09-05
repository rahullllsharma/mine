import type { ComponentMeta, ComponentStory } from "@storybook/react";

import type { ChartItem } from "./ChartDrillDown";
import ChartDrillDown from "./ChartDrillDown";

export default {
  title: "Container/Insights/ChartDrillDown",
  component: ChartDrillDown,
  decorators: [
    Story => (
      <div className="w-full h-[600px] py-4 overflow-auto">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof ChartDrillDown>;

const Template: ComponentStory<typeof ChartDrillDown> = args => (
  <ChartDrillDown {...args} />
);

const charts: ChartItem[] = [
  {
    title: "By location",
  },
  {
    title: "By hazard",
  },
  {
    title: "By task type",
  },
  {
    title: "By task",
  },
];

export const Playground = Template.bind({});
Playground.args = {
  type: "hazard",
  inputValue: "",
  charts,
};
