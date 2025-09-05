import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { Icon } from "@urbint/silica";

import Tooltip from "./Tooltip";

export default {
  title: "Silica/Tooltip",
  component: Tooltip,
  argTypes: { position: { control: false } },
  decorators: [
    Story => (
      <div className="w-full h-screen flex items-center justify-center">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof Tooltip>;

const Template: ComponentStory<typeof Tooltip> = args => (
  <Tooltip {...args}>
    <Icon name="info_circle" className="text-xl" />
  </Tooltip>
);

const title = "This is a tooltip!";

export const Top = Template.bind({});
Top.args = {
  title,
};

export const Bottom = Template.bind({});
Bottom.args = {
  title,
  position: "bottom",
};

export const Left = Template.bind({});
Left.args = {
  title,
  position: "left",
};

export const Right = Template.bind({});
Right.args = {
  title,
  position: "right",
};
