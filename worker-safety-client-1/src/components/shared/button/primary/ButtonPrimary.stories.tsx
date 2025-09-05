import type { ComponentMeta, ComponentStory } from "@storybook/react";

import ButtonPrimary from "./ButtonPrimary";

export default {
  title: "Silica/Button/ButtonPrimary",
  component: ButtonPrimary,
  argTypes: {
    onClick: { action: "clicked" },
    controlStateClass: { control: false },
  },
} as ComponentMeta<typeof ButtonPrimary>;

const TemplateRiskBadge: ComponentStory<typeof ButtonPrimary> = args => (
  <ButtonPrimary {...args} />
);

export const Playground = TemplateRiskBadge.bind({});

Playground.args = {
  label: "Button label",
  loading: false,
};
