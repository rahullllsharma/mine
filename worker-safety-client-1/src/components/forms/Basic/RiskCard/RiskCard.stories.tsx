import type { ComponentMeta, ComponentStory } from "@storybook/react";

import { RiskCard } from "./RiskCard";

export default {
  title: "JSB/RiskCard",
  component: RiskCard,
} as ComponentMeta<typeof RiskCard>;

export const Playground: ComponentStory<typeof RiskCard> = args => (
  <RiskCard {...args} />
);

Playground.args = {
  risk: "ArcFlash",
};
