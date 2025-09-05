import type { ComponentMeta, ComponentStory } from "@storybook/react";

import type { TaskHazardAggregator } from "@/types/project/HazardAggregator";
import { WrapperScroll } from "@/utils/dev/storybook";
import { TaskStatus } from "@/types/task/TaskStatus";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import ProjectTasks from "./ProjectTasks";

export default {
  title: "Container/SummaryView/ProjectTasks",
  component: ProjectTasks,
  argTypes: { tasks: { control: "false" } },
  decorators: [
    Story => (
      <WrapperScroll>
        <Story />
      </WrapperScroll>
    ),
  ],
} as ComponentMeta<typeof ProjectTasks>;

const tasks: TaskHazardAggregator[] = [
  {
    id: "task1",
    name: "Above-ground welding - Above ground weld",
    hazards: [],
    incidents: [],
    activity: {
      id: "activity1",
      name: "activity1",
      status: TaskStatus.NOT_STARTED,
      startDate: "2022-05-01",
      endDate: "2022-05-31",
      taskCount: 1,
      tasks: [],
    },
    riskLevel: RiskLevel.UNKNOWN,
    libraryTask: {
      id: "8658c5d4-9d51-41ef-9729-6ca0680fc4c4",
      name: "Above-ground welding - Above ground weld",
      category: "Welding / joining",
      hazards: [],
      activitiesGroups: [
        {
          id: "aa",
          name: "Welding",
        },
      ],
    },
  },
  {
    id: "task2",
    name: "Excavation of soil using hydro-vac",
    hazards: [],
    incidents: [],
    activity: {
      id: "activity2",
      name: "activity2",
      status: TaskStatus.IN_PROGRESS,
      startDate: "2022-05-05",
      endDate: "2022-05-25",
      taskCount: 1,
      tasks: [],
    },
    riskLevel: RiskLevel.UNKNOWN,
    libraryTask: {
      id: "8658c5d4-9d51-41ef-9729-6ca0680fc4c4",
      name: "Excavation of soil using hydro-vac",
      category: "Trenching / excavating",
      hazards: [],
      activitiesGroups: [
        {
          id: "bba",
          name: "Excavation",
        },
      ],
    },
  },
  {
    id: "task3",
    name: "Heater installation",
    hazards: [],
    incidents: [],
    activity: {
      id: "activity3",
      name: "activity3",
      status: TaskStatus.NOT_COMPLETED,
      startDate: "2022-05-01",
      endDate: "2022-05-25",
      taskCount: 1,
      tasks: [],
    },
    riskLevel: RiskLevel.UNKNOWN,
    libraryTask: {
      id: "8658c5d4-9d51-41ef-9729-6ca0680fc4c4",
      name: "Heater installation",
      category: "Regulator / gate station installation",
      hazards: [],
      activitiesGroups: [
        {
          id: "cca",
          name: "Installation",
        },
      ],
    },
  },
  {
    id: "task4",
    name: "Electrical testing",
    hazards: [],
    incidents: [],
    activity: {
      id: "activity4",
      name: "activity4",
      status: TaskStatus.COMPLETE,
      startDate: "2022-05-10",
      endDate: "2022-05-23",
      taskCount: 1,
      tasks: [],
    },
    riskLevel: RiskLevel.UNKNOWN,
    libraryTask: {
      id: "8658c5d4-9d51-41ef-9729-6ca0680fc4c4",
      name: "Electrical testing",
      category: "Electrical work",
      hazards: [],
      activitiesGroups: [
        {
          id: "dda",
          name: "Electrical work",
        },
      ],
    },
  },
];

const Template: ComponentStory<typeof ProjectTasks> = args => (
  <ProjectTasks {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  projectId: "1",
  locationId: "1",
  tasks,
};

export const WithoutTasks = Template.bind({});
