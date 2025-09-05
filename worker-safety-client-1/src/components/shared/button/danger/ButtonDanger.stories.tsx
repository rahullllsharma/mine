import type { ComponentMeta, ComponentStory } from "@storybook/react";

import ButtonDanger from "./ButtonDanger";

export default {
  title: "Silica/Button/ButtonDanger",
  component: ButtonDanger,
  argTypes: {
    onClick: { action: "clicked" },
    controlStateClass: { control: false },
  },
} as ComponentMeta<typeof ButtonDanger>;

const TemplateButtonDanger: ComponentStory<typeof ButtonDanger> = args => (
  <ButtonDanger {...args} />
);

export const Playground = TemplateButtonDanger.bind({});

Playground.args = {
  label: "Button label",
  loading: false,
};
