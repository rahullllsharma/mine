import type { ComponentMeta, ComponentStory } from "@storybook/react";

import Switch from "./Switch";

export default {
  title: "Components/Switch",
  component: Switch,
  argTypes: { onToggle: { action: "clicked" } },
} as ComponentMeta<typeof Switch>;

const Template: ComponentStory<typeof Switch> = args => <Switch {...args} />;

export const Playground = Template.bind({});
Playground.args = {
  stateOverride: true,
  isDisabled: false,
};
