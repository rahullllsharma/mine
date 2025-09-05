import type { ComponentMeta, ComponentStory } from "@storybook/react";

import type { RadioGroupOption } from "./RadioGroup";
import RadioGroup from "./RadioGroup";

export default {
  title: "Silica/RadioGroup",
  component: RadioGroup,
  argTypes: { onSelect: { action: "selected" } },
} as ComponentMeta<typeof RadioGroup>;

const DUMMY_OPTIONS: RadioGroupOption[] = [
  { id: 1, value: "Yes" },
  { id: 2, value: "No" },
  { id: 3, value: "N/A" },
];

const Template: ComponentStory<typeof RadioGroup> = args => (
  <RadioGroup {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  direction: "row",
  hideLabels: false,
  isDisabled: false,
  hasError: false,
  options: DUMMY_OPTIONS,
  defaultOption: { id: 2, value: "No" },
};
