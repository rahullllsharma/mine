import type { ComponentMeta, ComponentStory } from "@storybook/react";

import ButtonIcon from "./ButtonIcon";

export default {
  title: "Silica/Button/ButtonIcon",
  component: ButtonIcon,
  argTypes: {
    onClick: { action: "clicked" },
  },
} as ComponentMeta<typeof ButtonIcon>;

const TemplateRiskBadge: ComponentStory<typeof ButtonIcon> = args => (
  <ButtonIcon {...args} />
);

export const Playground = TemplateRiskBadge.bind({});

Playground.args = {
  iconName: "settings_filled",
  disabled: false,
  loading: false,
};
