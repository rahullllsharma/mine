import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { RiskLevel } from "../riskBadge/RiskLevel";

import LocationRisk from "./LocationRisk";

export default {
  title: "Components/LocationRisk",
  component: LocationRisk,
  decorators: [
    Story => (
      <div className="shadow-10">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof LocationRisk>;

const Template: ComponentStory<typeof LocationRisk> = args => (
  <LocationRisk {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  risk: RiskLevel.MEDIUM,
  supervisorRisk: true,
  contractorRisk: true,
  crewRisk: true,
};
