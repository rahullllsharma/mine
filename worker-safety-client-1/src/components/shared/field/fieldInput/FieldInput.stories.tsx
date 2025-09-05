import type { ComponentMeta, ComponentStory } from "@storybook/react";

import FieldInput from "./FieldInput";

export default {
  title: "Silica/Field/FieldInput",
  component: FieldInput,
  argTypes: { hasError: { control: false } },
} as ComponentMeta<typeof FieldInput>;

const Template: ComponentStory<typeof FieldInput> = args => (
  <FieldInput {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  className: "w-72",
  label: "Lorem ipsum dolor sit amet.",
  caption: "",
  error: "",
  required: false,
};

export const Readonly = Template.bind({});
Readonly.args = {
  className: "w-72",
  label: "Lorem ipsum dolor sit amet.",
  caption: "",
  error: "",
  defaultValue: "12345",
  required: false,
  readOnly: true,
};
