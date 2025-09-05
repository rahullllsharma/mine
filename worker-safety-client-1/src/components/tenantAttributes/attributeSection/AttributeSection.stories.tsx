import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { AttributeSection } from "./AttributeSection";

export default {
  title: "Components/TenantAttributes/AttributeSection",
  component: AttributeSection,
  decorators: [Story => <Story />],
} as ComponentMeta<typeof AttributeSection>;

const Template: ComponentStory<typeof AttributeSection> = args => (
  <AttributeSection {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  label: "Activity",
  defaultLabel: "Activity",
};

export const WithChildren = Template.bind({});
WithChildren.args = {
  label: "Work package",
  defaultLabel: "Work package",
  children: <div>WIP</div>,
};

export const WithTooltip = Template.bind({});
WithTooltip.args = {
  label: "Project package",
  defaultLabel: "Work package",
};
