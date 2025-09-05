import type { ComponentMeta, ComponentStory } from "@storybook/react";

import { none } from "fp-ts/lib/Option";
import { Select } from "./Select";

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
  title: "JSB/Select",
  component: Select,
} as ComponentMeta<typeof Select>;

export const Playground: ComponentStory<typeof Select> = args => (
  <Select {...args} />
);
Playground.args = {
  selected: none,
  options,
  optionKey: key => `${key}`,
  renderLabel: label => <>`${label}`</>,
  onSelected: alert,
};
