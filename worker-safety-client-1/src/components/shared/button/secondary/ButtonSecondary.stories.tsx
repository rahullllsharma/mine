import type { ComponentMeta, ComponentStory } from "@storybook/react";

import ButtonSecondary from "./ButtonSecondary";

export default {
  title: "Silica/Button/ButtonSecondary",
  component: ButtonSecondary,
  argTypes: {
    onClick: { action: "clicked" },
    controlStateClass: { control: false },
  },
} as ComponentMeta<typeof ButtonSecondary>;

const TemplateRiskBadge: ComponentStory<typeof ButtonSecondary> = args => (
  <ButtonSecondary {...args} />
);

export const Playground = TemplateRiskBadge.bind({});

Playground.args = {
  label: "Button label",
  loading: false,
};
