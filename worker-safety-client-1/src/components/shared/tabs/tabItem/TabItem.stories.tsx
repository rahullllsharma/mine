import type { ComponentMeta, ComponentStory } from "@storybook/react";

import TabItem from "./TabItem";

export default {
  title: "Silica/Tabs/Item",
  component: TabItem,
} as ComponentMeta<typeof TabItem>;

const Template: ComponentStory<typeof TabItem> = args => <TabItem {...args} />;

export const Playground = Template.bind({});
Playground.args = {
  value: "Projects",
};

export const WithIcon = Template.bind({});
WithIcon.args = {
  value: "Location(s)",
  icon: "location_outline",
};
