import type { ComponentMeta, ComponentStory } from "@storybook/react";

import InitialsAvatar from "./InitialsAvatar";

export default {
  title: "Silica/Avatar/InitialsAvatar",
  component: InitialsAvatar,
} as ComponentMeta<typeof InitialsAvatar>;

const Template: ComponentStory<typeof InitialsAvatar> = args => (
  <InitialsAvatar {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  name: "Test",
};
