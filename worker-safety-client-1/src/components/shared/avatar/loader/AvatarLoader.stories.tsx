import type { ComponentMeta, ComponentStory } from "@storybook/react";

import { AvatarLoader } from "./AvatarLoader";

export default {
  title: "Silica/Avatar",
  component: AvatarLoader,
} as ComponentMeta<typeof AvatarLoader>;

const Template: ComponentStory<typeof AvatarLoader> = () => <AvatarLoader />;

export const avatarLoader = Template.bind({});
