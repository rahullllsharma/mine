import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import ClusterDetails from "./ClusterDetails";

export default {
  title: "Components/Map/Cluster/ClusterDetails",
  component: ClusterDetails,
} as ComponentMeta<typeof ClusterDetails>;

const Template: ComponentStory<typeof ClusterDetails> = args => (
  <ClusterDetails {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  totalTitle: "Cluster has 23 locations",
  totals: {
    HIGH: 7,
    MEDIUM: 5,
    LOW: 7,
    UNKNOWN: 4,
  },
};

export const WithProjectDetails = Template.bind({});
WithProjectDetails.args = {
  riskLevel: RiskLevel.MEDIUM,
  projectName: "48th Street Access Point",
  supervisorName: "Roland Lemay",
  totalTitle: "Today’s tasks",
  totals: {
    HIGH: 1,
    MEDIUM: 3,
    LOW: 2,
  },
};
