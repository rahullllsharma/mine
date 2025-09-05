import type { ComponentMeta, ComponentStory } from "@storybook/react";

import FieldRadioGroup from "./FieldRadioGroup";

export default {
  title: "Silica/Field/FieldRadioGroup",
  component: FieldRadioGroup,
  argTypes: { onSelect: { action: "clicked" }, hasError: { control: false } },
} as ComponentMeta<typeof FieldRadioGroup>;

const TemplateFieldRadioGroup: ComponentStory<typeof FieldRadioGroup> =
  args => <FieldRadioGroup {...args} />;

export const Playground = TemplateFieldRadioGroup.bind({});
Playground.args = {
  className: "w-72",
  label: "Lorem ipsum dolor sit amet.",
  caption: "",
  required: false,
  error: "",
  options: [
    { id: 1, value: "One" },
    { id: 2, value: "Two" },
    { id: 3, value: "Three" },
  ],
  defaultOption: { id: 3, value: "Three" },
};

export const Readonly = TemplateFieldRadioGroup.bind({});
Readonly.args = {
  className: "w-72",
  label: "Lorem ipsum dolor sit amet.",
  caption: "",
  required: false,
  error: "",
  options: [
    { id: 1, value: "One" },
    { id: 2, value: "Two" },
    { id: 3, value: "Three" },
  ],
  defaultOption: { id: 3, value: "Three" },
  readOnly: true,
};
