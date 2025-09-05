import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { useProjects } from "@/hooks/useProjects";

import { WrapperScroll } from "@/utils/dev/storybook";
import ProjectDailyPlan from "./ProjectDailyPlan";

export default {
  title: "Container/SummaryView/DailyPlan",
  component: ProjectDailyPlan,
  argTypes: {
    onDateSelect: { action: "onDateSelect" },
    onAddTask: { action: "onAddTask" },
    onAddSiteCondition: { action: "onAddSiteCondition" },
    onAddDailyReport: { action: "onAddDailyReport" },
  },

  decorators: [
    Story => (
      <WrapperScroll>
        <Story />
      </WrapperScroll>
    ),
  ],
} as ComponentMeta<typeof ProjectDailyPlan>;

const Template: ComponentStory<typeof ProjectDailyPlan> = args => {
  const [project] = useProjects();

  return (
    <ProjectDailyPlan
      {...args}
      project={project}
      location={project.locations[0]}
    />
  );
};

export const Playground = Template.bind({});
