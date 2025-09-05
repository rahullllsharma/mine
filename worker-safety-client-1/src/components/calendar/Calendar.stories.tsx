import type { ComponentMeta, ComponentStory } from "@storybook/react";

import Calendar from "./Calendar";

export default {
  title: "Components/Calendar",
  component: Calendar,
  argTypes: { onDateSelect: { action: "onDateSelect" } },
} as ComponentMeta<typeof Calendar>;

const Template: ComponentStory<typeof Calendar> = args => (
  <Calendar {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  startDate: "2022-01-15",
  endDate: "2022-01-25",
};
