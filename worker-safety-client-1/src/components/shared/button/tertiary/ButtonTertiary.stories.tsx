import type { ComponentMeta, ComponentStory } from "@storybook/react";

import ButtonTertiary from "./ButtonTertiary";

export default {
  title: "Silica/Button/ButtonTertiary",
  component: ButtonTertiary,
  argTypes: {
    onClick: { action: "clicked" },
    controlStateClass: { control: false },
  },
} as ComponentMeta<typeof ButtonTertiary>;

const TemplateRiskBadge: ComponentStory<typeof ButtonTertiary> = args => (
  <ButtonTertiary {...args} />
);

export const Playground = TemplateRiskBadge.bind({});

Playground.args = {
  label: "Button label",
  loading: false,
};
