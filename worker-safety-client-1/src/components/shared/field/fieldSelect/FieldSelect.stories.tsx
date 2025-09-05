import type { ComponentMeta, ComponentStory } from "@storybook/react";

import { noop } from "lodash-es";
import FieldSelect from "./FieldSelect";

export default {
  title: "Silica/Field/FieldSelect",
  component: FieldSelect,
  argTypes: { hasError: { control: false } },
} as ComponentMeta<typeof FieldSelect>;

const Template: ComponentStory<typeof FieldSelect> = args => (
  <FieldSelect {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  className: "w-72",
  label: "Lorem ipsum dolor sit amet.",
  caption: "",
  required: false,
  error: "",
  onSelect: noop,
  options: [
    { id: 1, name: "One" },
    { id: 2, name: "Two" },
    { id: 3, name: "Three" },
    { id: 4, name: "Four" },
  ],
};

export const Readonly = Template.bind({});
Readonly.args = {
  className: "w-72",
  label: "Lorem ipsum dolor sit amet.",
  caption: "",
  required: false,
  error: "",
  onSelect: noop,
  options: [
    { id: 1, name: "One" },
    { id: 2, name: "Two" },
    { id: 3, name: "Three" },
    { id: 4, name: "Four" },
  ],
  readOnly: true,
  defaultOption: { id: 2, name: "Two" },
};
