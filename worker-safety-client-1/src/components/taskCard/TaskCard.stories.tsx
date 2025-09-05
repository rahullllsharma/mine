import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { TaskHazardAggregator } from "@/types/project/HazardAggregator";
import { TaskStatus } from "@/types/task/TaskStatus";
import { RiskLevel } from "../riskBadge/RiskLevel";

import TaskCard from "./TaskCard";

export default {
  title: "components/TaskCard",
  component: TaskCard,
} as ComponentMeta<typeof TaskCard>;

const task: TaskHazardAggregator = {
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
};

const Template: ComponentStory<typeof TaskCard> = args => (
  <TaskCard {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  projectId: "1",
  locationId: "1",
  task,
};
