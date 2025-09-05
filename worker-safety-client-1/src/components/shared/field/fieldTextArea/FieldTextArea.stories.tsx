import type { ComponentMeta, ComponentStory } from "@storybook/react";

import FieldTextArea from "./FieldTextArea";

export default {
  title: "Silica/Field/FieldTextArea",
  component: FieldTextArea,
  argTypes: { onChange: { actions: "onChange" } },
} as ComponentMeta<typeof FieldTextArea>;

const Template: ComponentStory<typeof FieldTextArea> = args => (
  <FieldTextArea {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  className: "w-102",
  label: "Lorem ipsum dolor sit amet.",
  initialValue: "",
  caption: "",
  required: false,
  error: "",
};

export const WithLongText = Template.bind({});
WithLongText.args = {
  className: "w-102",
  label: "Lorem ipsum dolor sit amet.",
  name: "some-name",
  initialValue:
    "Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. ",
  caption: "",
  required: false,
  error: "",
};

export const Readonly = Template.bind({});
Readonly.args = {
  className: "w-102",
  label: "Description",
  name: "some-name",
  initialValue:
    "Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet.",
  caption: "",
  required: false,
  error: "",
  readOnly: true,
};
