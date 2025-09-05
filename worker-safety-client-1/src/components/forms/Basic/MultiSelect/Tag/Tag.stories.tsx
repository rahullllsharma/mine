import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { Tag } from "./Tag";

export default {
  title: "JSB/MultiSelect/Tag",
  component: Tag,
} as ComponentMeta<typeof Tag>;

export const Playground: ComponentStory<typeof Tag> = args => <Tag {...args} />;
Playground.args = {
  label: "Option 1",
  onDeleteClick: alert,
};
