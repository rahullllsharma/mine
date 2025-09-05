import type { ComponentMeta, ComponentStory } from "@storybook/react";

import { TagCard } from "./TagCard";

export default {
  title: "JSB/TagCard",
  component: TagCard,
} as ComponentMeta<typeof TagCard>;

export const Playground: ComponentStory<typeof TagCard> = args => (
  <TagCard {...args} />
);

Playground.args = {
  children: <p>This is an example</p>,
};
