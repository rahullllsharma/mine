import type { ComponentMeta, ComponentStory } from "@storybook/react";

import PageFooter from "./PageFooter";

export default {
  title: "Layout/PageFooter",
  component: PageFooter,
  argTypes: { onPrimaryClick: { action: "clicked" } },
} as ComponentMeta<typeof PageFooter>;

const TemplateRiskBadge: ComponentStory<typeof PageFooter> = args => (
  <PageFooter {...args} />
);

export const Playground = TemplateRiskBadge.bind({});

Playground.args = {
  primaryActionLabel: "Button label",
};
