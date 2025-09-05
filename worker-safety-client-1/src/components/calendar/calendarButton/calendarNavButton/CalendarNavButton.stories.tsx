import type { ComponentMeta, ComponentStory } from "@storybook/react";

import CalendarNavButton from "./CalendarNavButton";

export default {
  title: "Components/Calendar/Button",
  component: CalendarNavButton,
  argTypes: {
    onClick: { action: "onClick" },
    isToday: { control: false },
    isActive: { control: false },
  },
} as ComponentMeta<typeof CalendarNavButton>;

const Template: ComponentStory<typeof CalendarNavButton> = args => (
  <CalendarNavButton {...args} />
);

export const NavButton = Template.bind({});
NavButton.args = {
  icon: "chevron_big_left",
  isDisabled: false,
};
