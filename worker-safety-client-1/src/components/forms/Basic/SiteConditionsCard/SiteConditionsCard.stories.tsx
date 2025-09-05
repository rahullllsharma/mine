import type { ComponentMeta, ComponentStory } from "@storybook/react";

import { SiteConditionsCard } from "./SiteConditionsCard";

export default {
  title: "JSB/SiteConditionsCard",
  component: SiteConditionsCard,
} as ComponentMeta<typeof SiteConditionsCard>;

export const Playground: ComponentStory<typeof SiteConditionsCard> = args => (
  <SiteConditionsCard {...args} />
);

Playground.args = { title: "Traffic density" };
