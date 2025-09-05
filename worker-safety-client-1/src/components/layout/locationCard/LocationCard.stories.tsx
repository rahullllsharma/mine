import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import LocationCard from "./LocationCard";

const slots = ["Montgomery Burns", "Distribution"];

export default {
  title: "Layout/LocationCard",
  component: LocationCard,
} as ComponentMeta<typeof LocationCard>;

const Template: ComponentStory<typeof LocationCard> = args => (
  <LocationCard {...args} />
);

const TemplateWithIdentifier: ComponentStory<typeof LocationCard> = args => (
  <LocationCard {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  risk: RiskLevel.HIGH,
  title: "310, Main Street",
  slots,
  description: "Some Project",
};

export const WithChildren = TemplateWithIdentifier.bind({});

WithChildren.args = {
  risk: RiskLevel.HIGH,
  title: "310, Main Street",
  slots,
  description: "Some Project",
  identifier: <div>Identifier text</div>,
};
