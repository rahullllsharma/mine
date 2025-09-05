import type { ComponentMeta, ComponentStory } from "@storybook/react";

import PopoverPrimary from "./PopoverPrimary";

export default {
  title: "Silica/Popover/Primary",
  component: PopoverPrimary,
} as ComponentMeta<typeof PopoverPrimary>;

const Template: ComponentStory<typeof PopoverPrimary> = args => (
  <PopoverPrimary {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  label: "Open me",
  iconEnd: "chevron_big_down",
  className: "w-72 h-44 mt-2",
  children: <div className="p-2 bg-white h-full">Popover content</div>,
};
