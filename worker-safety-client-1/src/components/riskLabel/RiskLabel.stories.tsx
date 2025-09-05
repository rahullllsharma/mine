import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import RiskLabel from "./RiskLabel";

export default {
  title: "Components/Badge/RiskLabel",
  component: RiskLabel,
} as ComponentMeta<typeof RiskLabel>;

const Template: ComponentStory<typeof RiskLabel> = args => (
  <RiskLabel {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  label: "Some label",
  risk: RiskLevel.LOW,
};
