import type { ComponentMeta, ComponentStory } from "@storybook/react";

import RiskBadge from "./RiskBadge";
import { RiskLevel } from "./RiskLevel";

export default {
  title: "Components/Badge/RiskBadge",
  component: RiskBadge,
  argTypes: {
    riskColor: { table: { disable: true } },
  },
} as ComponentMeta<typeof RiskBadge>;

const TemplateRiskBadge: ComponentStory<typeof RiskBadge> = ({
  risk,
  label,
}) => <RiskBadge risk={risk} label={label} />;

export const Playground = TemplateRiskBadge.bind({});

Playground.args = {
  risk: RiskLevel.HIGH,
  label: "Risk Label",
};
