import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import ProjectDetails from "./ProjectDetails";

export default {
  title: "Components/Map/Cluster/ClusterDetailsAddress/ProjectDetails",
  component: ProjectDetails,
} as ComponentMeta<typeof ProjectDetails>;

const Template: ComponentStory<typeof ProjectDetails> = args => (
  <ProjectDetails {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  riskLevel: RiskLevel.MEDIUM,
  projectName: "48th Street Access Point",
  supervisorName: "Roland Lemay",
};
