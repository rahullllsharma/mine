import type { ComponentMeta, ComponentStory } from "@storybook/react";

import TabsLight from "./TabsLight";

export default {
  title: "Silica/Tabs/Light",
  component: TabsLight,
  argTypes: { onSelect: { action: "onSelect" } },
} as ComponentMeta<typeof TabsLight>;

const Template: ComponentStory<typeof TabsLight> = args => (
  <TabsLight {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  options: ["Active", "Pending", "Completed"],
};
