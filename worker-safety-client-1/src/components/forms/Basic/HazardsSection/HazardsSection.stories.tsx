import type { ComponentMeta, ComponentStory } from "@storybook/react";

import { HazardsSection } from "./HazardsSection";

export default {
  title: "JSB/HazardsSection",
  component: HazardsSection,
} as ComponentMeta<typeof HazardsSection>;

export const Playground: ComponentStory<typeof HazardsSection> = args => (
  <HazardsSection {...args} />
);

Playground.args = {
  onClickEdit: alert,
  hazards: [
    "Stuck by equipment",
    "Electrical contact with source",
    "Biological hazards - Insects, animals, poisonous plants",
  ],
};
