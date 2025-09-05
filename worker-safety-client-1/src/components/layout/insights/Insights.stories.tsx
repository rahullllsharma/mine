import type { ComponentMeta, ComponentStory } from "@storybook/react";

import InsightsLayout from "./Insights";

export default {
  title: "Layout/Insights",
  component: InsightsLayout,
} as ComponentMeta<typeof InsightsLayout>;

const Template: ComponentStory<typeof InsightsLayout> = args => (
  <InsightsLayout {...args} />
);

export const Playground = Template.bind({});

Playground.args = {};
