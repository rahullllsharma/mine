import type { ComponentMeta, ComponentStory } from "@storybook/react";

import Button from "./Button";

export default {
  title: "Silica/Button/Button",
  component: Button,
  argTypes: { onClick: { action: "clicked" } },
} as ComponentMeta<typeof Button>;

const TemplateRiskBadge: ComponentStory<typeof Button> = args => (
  <Button {...args} />
);

export const Playground = TemplateRiskBadge.bind({});

Playground.args = {
  label: "Button label",
  loading: false,
};
