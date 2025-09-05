import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import LocationRiskIcon from "./LocationRiskIcon";

export default {
  title: "Components/Map/LocationRiskIcon",
  component: LocationRiskIcon,
} as ComponentMeta<typeof LocationRiskIcon>;

const TemplateMarker: ComponentStory<typeof LocationRiskIcon> = args => (
  <LocationRiskIcon {...args} />
);

export const Playground = TemplateMarker.bind({});
Playground.args = {
  riskLevel: RiskLevel.HIGH,
};
