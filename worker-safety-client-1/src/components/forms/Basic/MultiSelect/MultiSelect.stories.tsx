import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { MultiSelect } from "./MultiSelect";

const options = [
  {
    label: "Option 1",
    value: "option1",
  },
  {
    label: "Option 2",
    value: "option2",
  },
  {
    label: "Option 3 with a big text in the label to see if truncates",
    value: "option3",
  },
];

export default {
  title: "JSB/MultiSelect",
  component: MultiSelect,
} as ComponentMeta<typeof MultiSelect>;

export const Playground: ComponentStory<typeof MultiSelect> = args => (
  <MultiSelect {...args} />
);
Playground.args = {
  selected: [],
  options,
  optionKey: key => `${key}`,
  renderLabel: label => `${label}`,
  onSelected: alert,
  onRemoved: alert,
};
