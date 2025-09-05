import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { Hazard } from "@/types/project/Hazard";
import type { Control } from "@/types/project/Control";
import type { TaskInputs } from "@/types/task/TaskInputs";

import type { TaskDetailsProps } from "./TaskDetails";
import { action } from "@storybook/addon-actions";
import { useForm } from "react-hook-form";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { TaskStatus } from "@/types/task/TaskStatus";

import { WrapperForm } from "@/utils/dev/storybook";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import { TaskDetails } from "./TaskDetails";

const controlsLibrary: Control[] = [
  { id: "custom-control-1", name: "Control 1", isApplicable: true },
  { id: "custom-control-2", name: "Control 2", isApplicable: true },
  { id: "custom-control-3", name: "Control 3", isApplicable: true },
  { id: "custom-control-4", name: "Control 4", isApplicable: true },
];

// Information should be retrieved by using useQuery and fetched from BE
const hazardsLibrary: Hazard[] = [
  { id: "custom-hazard-1", name: "Hazard 1", isApplicable: true, controls: [] },
  { id: "custom-hazard-2", name: "Hazard 2", isApplicable: true, controls: [] },
  { id: "custom-hazard-3", name: "Hazard 3", isApplicable: true, controls: [] },
  { id: "custom-hazard-4", name: "Hazard 4", isApplicable: true, controls: [] },
];

const sharedArgs = {
  task: {
    id: "1",
    name: "Task 1",
    riskLevel: RiskLevel.MEDIUM,
    activity: {
      id: "1",
      startDate: "2021-10-10",
      endDate: "2021-10-10",
      status: TaskStatus.NOT_STARTED,
    },
    hazards: [
      {
        id: "1",
        name: "hazard 123",
        isApplicable: true,
        controls: [
          {
            id: "1",
            name: "control name",
            isApplicable: true,
          },
          {
            id: "2",
            name: "control name 2",
            isApplicable: true,
          },
        ],
      },
      {
        id: "2",
        name: "hazard 567",
        isApplicable: true,
        controls: [
          {
            id: "12",
            name: "control name",
            isApplicable: true,
          },
          {
            id: "22",
            name: "control name 2",
            isApplicable: true,
          },
        ],
      },
    ],
  },
  hazardsLibrary,
  controlsLibrary,
} as TaskDetailsProps;

export default {
  title: "Layout/TaskDetails/TaskDetails",
  component: TaskDetails,
} as ComponentMeta<typeof TaskDetails>;

const TemplateTaskDetails: ComponentStory<typeof TaskDetails> = ({
  task,
  ...tailProps
}) => {
  const form = useForm<TaskInputs>({
    defaultValues: {
      libraryTaskId: task.id,
    },
  });

  const { handleSubmit } = form;

  return (
    <div className="h-screen px-1 pb-8 overflow-auto">
      <WrapperForm methods={form}>
        <ButtonPrimary
          onClick={handleSubmit(action("onSubmit"))}
          label="Submit"
        />
        <TaskDetails task={task} {...tailProps} />
      </WrapperForm>
    </div>
  );
};

export const Task = TemplateTaskDetails.bind({});

Task.args = sharedArgs;

export const TaskWithManualHazardsAndControl = TemplateTaskDetails.bind({});

TaskWithManualHazardsAndControl.args = {
  task: {
    ...sharedArgs.task,
    hazards: [
      {
        id: "custom-hazard-2",
        name: "Hazard 2",
        isApplicable: true,
        createdBy: {
          id: "0",
          name: "User",
        },
        libraryHazard: {
          id: "custom-hazard-2",
        },
        controls: [],
      },
      {
        id: "custom-hazard-4",
        name: "Hazard 4",
        isApplicable: true,
        createdBy: {
          id: "0",
          name: "User",
        },
        libraryHazard: {
          id: "custom-hazard-4",
        },
        controls: [],
      },
      {
        id: "h-1",
        name: "Bodily Injury",
        isApplicable: true,
        controls: [
          {
            id: "c-1",
            name: "Situational Jobsite Awareness",
            isApplicable: false,
          },
          {
            id: "c-2",
            name: "Trained and Qualified",
            isApplicable: true,
          },
        ],
      },
      {
        id: "h-2",
        name: "Radiation Sickness",
        isApplicable: true,
        controls: [
          {
            id: "c-3",
            name: "Radiation Monitoring Device",
            isApplicable: true,
          },
          {
            id: "c-4",
            name: "Isotopes Stored and Handled Properly",
            isApplicable: true,
          },
        ],
      },
    ],
  },
  hazardsLibrary: sharedArgs.hazardsLibrary,
  controlsLibrary: sharedArgs.controlsLibrary,
} as TaskDetailsProps;

export const TaskWithHeader = TemplateTaskDetails.bind({});

TaskWithHeader.args = {
  ...sharedArgs,
  withTaskNameVisible: true,
} as TaskDetailsProps;
