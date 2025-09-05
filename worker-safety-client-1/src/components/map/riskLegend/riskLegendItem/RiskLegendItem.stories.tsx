import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import RiskLegendItem from "./RiskLegendItem";

export default {
  title: "Components/Map/RiskLegend/RiskLegendItem",
  component: RiskLegendItem,
} as ComponentMeta<typeof RiskLegendItem>;

const TemplateRiskLegendItem: ComponentStory<typeof RiskLegendItem> = args => (
  <RiskLegendItem {...args} />
);

export const Playground = TemplateRiskLegendItem.bind({});
Playground.args = {
  riskLevel: RiskLevel.HIGH,
  legend: "legend",
};
