import type { ComponentMeta, ComponentStory } from "@storybook/react";

import { RiskToggleCard } from "./RiskToggleCard";

export default {
  title: "JSB/RiskToggleCard",
  component: RiskToggleCard,
} as ComponentMeta<typeof RiskToggleCard>;

export const Playground: ComponentStory<typeof RiskToggleCard> = args => (
  <RiskToggleCard {...args} />
);

Playground.args = {
  onClick: alert,
  risk: "ArcFlash",
  checked: false,
};
