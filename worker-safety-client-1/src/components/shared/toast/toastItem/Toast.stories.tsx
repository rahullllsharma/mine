import type { ComponentMeta, ComponentStory } from "@storybook/react";

import Toast from "./Toast";

export default {
  title: "Silica/Toast/Item",
  component: Toast,
  argTypes: { onDismiss: { action: "onDismiss" } },
} as ComponentMeta<typeof Toast>;

const Template: ComponentStory<typeof Toast> = args => <Toast {...args} />;

export const WithIcon = Template.bind({});
WithIcon.args = {
  type: "error",
  message: "There was an error deleting the task",
};

export const WithoutIcon = Template.bind({});
WithoutIcon.args = {
  message: "There was an error deleting the task",
};
