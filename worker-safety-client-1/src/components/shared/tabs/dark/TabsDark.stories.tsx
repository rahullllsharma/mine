import type { ComponentMeta, ComponentStory } from "@storybook/react";

import TabsDark from "./TabsDark";

export default {
  title: "Silica/Tabs/Dark",
  component: TabsDark,
  argTypes: { onSelect: { action: "onSelect" } },
  decorators: [
    Story => (
      <div className="bg-brand-urbint-60 px-2 py-1">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof TabsDark>;

const Template: ComponentStory<typeof TabsDark> = args => (
  <TabsDark {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  options: ["Active", "Pending", "Completed"],
};
