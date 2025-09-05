import type { ComponentMeta, ComponentStory } from "@storybook/react";

import { Checkbox } from "./Checkbox";

export default {
  title: "JSB/Checkbox",
  component: Checkbox,
} as ComponentMeta<typeof Checkbox>;

export const Playground: ComponentStory<typeof Checkbox> = args => (
  <Checkbox {...args}>Test</Checkbox>
);

Playground.args = {
  className: "mr-2",
};
