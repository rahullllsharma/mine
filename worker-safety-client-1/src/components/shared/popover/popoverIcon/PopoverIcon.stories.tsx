import type { ComponentMeta, ComponentStory } from "@storybook/react";

import PopoverIcon from "./PopoverIcon";

export default {
  title: "Silica/Popover/Icon",
  component: PopoverIcon,
} as ComponentMeta<typeof PopoverIcon>;

const Template: ComponentStory<typeof PopoverIcon> = args => (
  <PopoverIcon {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  iconName: "chevron_big_down",
  className: "w-72 h-44",
  children: <div className="p-2 bg-white h-full">Popover content</div>,
};
