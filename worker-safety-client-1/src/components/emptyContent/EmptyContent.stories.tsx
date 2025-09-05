import type { ComponentMeta, ComponentStory } from "@storybook/react";

import EmptyContent from "./EmptyContent";

export default {
  title: "Components/EmptyContent",
  component: EmptyContent,
  decorators: [
    Story => (
      <div className="w-full mt-12">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof EmptyContent>;

const Template: ComponentStory<typeof EmptyContent> = args => (
  <EmptyContent {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  title: "You currently have no active projects",
  description:
    "If you believe this is an error, please contact your customer success manager to help troubleshoot the issues",
};
