import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { PropsWithClassName } from "@/types/Generic";
import type { TaskHazardAggregator } from "@/types/project/HazardAggregator";
import { FormProvider, useForm } from "react-hook-form";
import { TaskStatus } from "@/types/task/TaskStatus";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import TaskReportCard from "./TaskReportCard";

export default {
  title: "Components/Report/TaskReportCard",
  component: TaskReportCard,
  decorators: [
    Story => (
      <Wrapper>
        <div className="max-w-lg h-screen overflow-auto p-1">
          <Story />
        </div>
      </Wrapper>
    ),
  ],
} as ComponentMeta<typeof TaskReportCard>;

const task: TaskHazardAggregator = {
  id: "1",
  name: "Pipe Face Alignment",
  activity: {
    id: "activity1",
    name: "activity1",
    status: TaskStatus.NOT_STARTED,
    startDate: "2021-10-10",
    endDate: "2021-10-10",
    taskCount: 1,
    tasks: [],
  },
  riskLevel: RiskLevel.MEDIUM,
  hazards: [
    {
      id: "1",
      name: "Pinch Point",
      isApplicable: true,
      controls: [
        { id: "1", name: "Gloves", isApplicable: true },
        { id: "2", name: "Situational Jobsite Awareness", isApplicable: false },
      ],
    },
    {
      id: "2",
      name: "Struck by Equipment and Material",
      isApplicable: true,
      controls: [
        { id: "3", name: "Gloves", isApplicable: true },
        { id: "4", name: "Situational Jobsite Awareness", isApplicable: false },
      ],
    },
  ],
  incidents: [],
};

function Wrapper({ children }: PropsWithClassName): JSX.Element {
  const methods = useForm();
  return <FormProvider {...methods}>{children}</FormProvider>;
}

const Template: ComponentStory<typeof TaskReportCard> = args => (
  <TaskReportCard {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  task,
};
