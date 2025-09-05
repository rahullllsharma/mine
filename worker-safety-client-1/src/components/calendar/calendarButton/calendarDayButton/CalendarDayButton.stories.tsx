import type { ComponentMeta, ComponentStory } from "@storybook/react";

import CalendarDayButton from "./CalendarDayButton";

export default {
  title: "Components/Calendar/Button",
  component: CalendarDayButton,
  argTypes: {
    onClick: { action: "onClick" },
    isToday: { control: false },
  },
} as ComponentMeta<typeof CalendarDayButton>;

const Template: ComponentStory<typeof CalendarDayButton> = args => (
  <CalendarDayButton {...args} />
);

export const DayButton = Template.bind({});
DayButton.args = {
  date: new Date().toString(),
  isDisabled: false,
  isActive: false,
};
