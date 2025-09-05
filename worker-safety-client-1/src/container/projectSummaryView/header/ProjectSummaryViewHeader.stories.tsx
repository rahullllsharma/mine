import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { useProjects } from "@/hooks/useProjects";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { ProjectSummaryViewHeader } from "./ProjectSummaryViewHeader";

export default {
  title: "Container/SummaryView/Header",
  component: ProjectSummaryViewHeader,
  argTypes: {
    onAddContent: { action: "onAddContent" },
    onLocationSelected: { action: "onLocationSelected" },
  },
  decorators: [
    Story => (
      <div className="py-4 flex items-start md:items-center justify-between">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof ProjectSummaryViewHeader>;

useAuthStore.setState(state => ({
  ...state,
  me: {
    ...state.me,
    role: "administrator",
    permissions: [
      "ADD_ACTIVITIES",
      "ADD_TASKS",
      "ADD_SITE_CONDITIONS",
      "ADD_REPORTS",
    ],
  },
}));

const Template: ComponentStory<typeof ProjectSummaryViewHeader> = args => {
  const [project] = useProjects();

  return (
    <ProjectSummaryViewHeader
      {...args}
      locations={project.locations}
      selectedLocation={project.locations[0]}
    />
  );
};

export const Playground = Template.bind({});
