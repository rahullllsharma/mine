import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { useForm } from "react-hook-form";

import { WrapperForm } from "@/utils/dev/storybook";
import TaskContentEdit from "./TaskContentEdit";

export default {
  title: "Layout/TaskCard/Content/TaskContentEdit",
  component: TaskContentEdit,
} as ComponentMeta<typeof TaskContentEdit>;

const TemplateCardItem: ComponentStory<typeof TaskContentEdit> = args => {
  const methods = useForm();

  return (
    <div className="h-screen pb-8 overflow-auto">
      <WrapperForm {...methods}>
        <TaskContentEdit {...args}></TaskContentEdit>
      </WrapperForm>
    </div>
  );
};

export const Playground = TemplateCardItem.bind({});

Playground.args = {
  controlsLibrary: [
    {
      id: "custom-control-1",
      name: "Control 1",
      isApplicable: true,
    },
    {
      id: "custom-control-2",
      name: "Control 2",
      isApplicable: true,
    },
    {
      id: "custom-control-3",
      name: "Control 3",
      isApplicable: true,
    },
    {
      id: "custom-control-4",
      name: "Control 4",
      isApplicable: true,
    },
  ],
  hazards: [
    {
      id: "1",
      key: "1",
      name: "Bodily Injury",
      isApplicable: true,
      controls: [
        {
          id: "1",
          name: "Situational Jobsite Awareness",
          isApplicable: true,
        },
        {
          id: "2",
          name: "Trained and Qualified",
          isApplicable: true,
        },
        {
          id: "3",
          name: "Erection of Proper Barricades and Warning Signs",
          isApplicable: true,
        },
        {
          id: "custom-control-2",
          name: "Control 2",
          isApplicable: true,
          createdBy: {
            id: "0",
            name: "User",
          },
          libraryControl: {
            id: "custom-control-2",
          },
        },
        {
          id: "custom-control-4",
          name: "Control 4",
          isApplicable: true,
          createdBy: {
            id: "0",
            name: "User",
          },
          libraryControl: {
            id: "custom-control-4",
          },
        },
      ],
    },
    {
      id: "2",
      key: "2",
      name: "Radiation Sickness",
      isApplicable: true,
      controls: [
        {
          id: "11",
          name: "Situational Jobsite Awareness",
          isApplicable: true,
        },
        {
          id: "21",
          name: "Trained and Qualified",
          isApplicable: true,
        },
        {
          id: "31",
          name: "Radiation Monitoring Device",
          isApplicable: true,
        },
        {
          id: "41",
          name: "Isotopes Stored and Handled Properly",
          isApplicable: true,
        },
      ],
    },
  ],
};
