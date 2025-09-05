import type { ComponentMeta, ComponentStory } from "@storybook/react";

import NavItem from "./NavItem";

export default {
  title: "Components/Navigation/NavItem",
  component: NavItem,
} as ComponentMeta<typeof NavItem>;

const Template: ComponentStory<typeof NavItem> = args => <NavItem {...args} />;

export const Playground = Template.bind({});
Playground.args = {
  name: "Locations",
  icon: "location",
  as: "div",
  isSelected: false,
  status: "default",
  markerType: "full",
};
