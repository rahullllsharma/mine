import type { ComponentMeta, ComponentStory } from "@storybook/react";

import Paragraph from "./Paragraph";

export default {
  title: "Components/Paragraph",
  component: Paragraph,
} as ComponentMeta<typeof Paragraph>;

const Template: ComponentStory<typeof Paragraph> = args => (
  <Paragraph {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  text: "Lorem Ipsum",
};
