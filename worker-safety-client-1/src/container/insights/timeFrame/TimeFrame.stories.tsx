import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { pastTimeFrameData } from "../utils";

import TimeFrame from "./TimeFrame";

export default {
  title: "Container/Insights/TimeFrame",
  component: TimeFrame,
  argTypes: { onChange: { control: "onChange" } },
  decorators: [
    Story => (
      <div className="w-80">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof TimeFrame>;

const Template: ComponentStory<typeof TimeFrame> = args => (
  <TimeFrame {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  options: pastTimeFrameData,
};
