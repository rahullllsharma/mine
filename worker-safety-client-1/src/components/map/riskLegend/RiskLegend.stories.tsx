import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import RiskLegend from "./RiskLegend";
import RiskLegendItem from "./riskLegendItem/RiskLegendItem";

export default {
  title: "Components/Map/RiskLegend",
  component: RiskLegend,
} as ComponentMeta<typeof RiskLegend>;

const TemplateRiskLegend: ComponentStory<typeof RiskLegend> = args => (
  <RiskLegend {...args}>
    <RiskLegendItem riskLevel={RiskLevel.HIGH} legend="High Risk" />
    <RiskLegendItem riskLevel={RiskLevel.MEDIUM} legend="Medium Risk" />
    <RiskLegendItem riskLevel={RiskLevel.LOW} legend="Low Risk" />
  </RiskLegend>
);

export const Playground = TemplateRiskLegend.bind({});
Playground.args = {
  label: "Location risk",
};
