import type { ComponentMeta, ComponentStory } from "@storybook/react";

import Input from "./Input";

export default {
  title: "Silica/Input",
  component: Input,
  argTypes: {
    type: {
      name: "type",
      type: { name: "string", required: true },
      defaultValue: "text",
      description: "native HTML input type",
      table: {
        defaultValue: { summary: "text" },
      },
      options: ["text", "password", "date", "datetime-local", "time"],
      control: { type: "select" },
    },
  },
} as ComponentMeta<typeof Input>;

const Template: ComponentStory<typeof Input> = args => <Input {...args} />;

export const Playground = Template.bind({});
Playground.args = {
  placeholder: "Placeholder for the input",
};

export const WithIcon = Template.bind({});
WithIcon.args = {
  id: "date",
  type: "date",
  placeholder: "YYYY/MM/DD", // doesnt work with type date
  icon: "dashboard",
};
