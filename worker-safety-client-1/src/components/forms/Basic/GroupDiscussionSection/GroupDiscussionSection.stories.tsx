import type { ComponentMeta, ComponentStory } from "@storybook/react";

import { GroupDiscussionSection } from "./GroupDiscussionSection";

export default {
  title: "JSB/GroupDiscussionSection",
  component: GroupDiscussionSection,
} as ComponentMeta<typeof GroupDiscussionSection>;

export const Playground: ComponentStory<typeof GroupDiscussionSection> =
  args => <GroupDiscussionSection {...args} />;

Playground.args = {
  title: "Job Information",
  onClickEdit: alert,
  children: <p>Content Example</p>,
};
