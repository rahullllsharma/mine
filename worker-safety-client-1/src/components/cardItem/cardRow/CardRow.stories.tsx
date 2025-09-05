import type { ComponentMeta, ComponentStory } from "@storybook/react";
import CardRow from "./CardRow";

export default {
  title: "components/CardItem/CardRow",
  component: CardRow,
} as ComponentMeta<typeof CardRow>;

const Template: ComponentStory<typeof CardRow> = args => <CardRow {...args} />;

export const Playground = Template.bind({});
Playground.args = {
  label: "Region",
  children: "Ne (New England)",
};
