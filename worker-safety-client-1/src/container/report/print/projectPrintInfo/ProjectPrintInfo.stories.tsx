import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { useProjects } from "@/hooks/useProjects";
import ProjectPrintInfo from "./ProjectPrintInfo";

export default {
  title: "Container/Report/Print/ProjectInformation",
  component: ProjectPrintInfo,
  decorators: [
    Story => (
      <div className="h-[600px] overflow-y-auto">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof ProjectPrintInfo>;

const Template: ComponentStory<typeof ProjectPrintInfo> = () => {
  const [project] = useProjects();
  return (
    <ProjectPrintInfo
      project={project}
      report={project.locations[0].dailyReports[0]}
    />
  );
};

export const Playground = Template.bind({});
