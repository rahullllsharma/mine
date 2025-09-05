import type { ComponentMeta, ComponentStory } from "@storybook/react";

import EmptyChart from "./EmptyChart";

export default {
  title: "Components/EmptyChart",
  component: EmptyChart,
  decorators: [
    Story => (
      <div className="w-full mt-12">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof EmptyChart>;

const Template: ComponentStory<typeof EmptyChart> = args => (
  <EmptyChart {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  title: "Project Risk Over Time",
};

export const Small = Template.bind({});
Small.args = {
  title: "Small Placeholder in a drill down",
  small: true,
};
