import type { ComponentMeta, ComponentStory } from "@storybook/react";

import AdminAvatar from "./AdminAvatar";

export default {
  title: "Silica/Avatar/AdminAvatar",
  component: AdminAvatar,
} as ComponentMeta<typeof AdminAvatar>;

const Template: ComponentStory<typeof AdminAvatar> = args => (
  <AdminAvatar {...args} />
);

export const Playground = Template.bind({});
