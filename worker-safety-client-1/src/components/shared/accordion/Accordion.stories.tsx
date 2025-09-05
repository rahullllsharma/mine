import type { ComponentMeta, ComponentStory } from "@storybook/react";

import Accordion from "./Accordion";

export default {
  title: "Silica/Accordion",
  component: Accordion,
  decorators: [
    Story => (
      <div className="w-40">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof Accordion>;

const header = <div>Accordion header</div>;

const Template: ComponentStory<typeof Accordion> = args => (
  <Accordion {...args} header={header}>
    Accordion Content
  </Accordion>
);

export const Playground = Template.bind({});
Playground.args = {};

export const WithPopAnimation = Template.bind({});
WithPopAnimation.args = {
  animation: "pop",
};
