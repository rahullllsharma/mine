import type { ComponentMeta, ComponentStory } from "@storybook/react";
import ProjectAudit from "./ProjectAudit";

export default {
  title: "Container/ProjectAudit",
  component: ProjectAudit,
} as ComponentMeta<typeof ProjectAudit>;

const Template: ComponentStory<typeof ProjectAudit> = args => (
  <ProjectAudit {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  projectId: "01",
};
