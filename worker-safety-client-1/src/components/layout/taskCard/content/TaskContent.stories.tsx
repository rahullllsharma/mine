import type { ComponentMeta } from "@storybook/react";

import TaskContent from "./TaskContent";

export default {
  title: "Layout/TaskCard/Content/TaskContent",
  component: TaskContent,
} as ComponentMeta<typeof TaskContent>;

const hazards = [
  {
    id: "1",
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
    ],
  },
  {
    id: "2",
    name: "Radiation Sickness",
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
        name: "Radiation Monitoring Device",
        isApplicable: true,
      },
      {
        id: "3",
        name: "Isotopes Stored and Handled Properly",
        isApplicable: true,
      },
    ],
  },
  {
    id: "3",
    name: "hazard 3",
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
        name: "Radiation Monitoring Device",
        isApplicable: true,
      },
      {
        id: "3",
        name: "Isotopes Stored and Handled Properly",
        isApplicable: true,
      },
    ],
  },
  {
    id: "4",
    name: "hazard 4",
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
        name: "Radiation Monitoring Device",
        isApplicable: true,
      },
      {
        id: "3",
        name: "Isotopes Stored and Handled Properly",
        isApplicable: true,
      },
    ],
  },
];

export const taskContent = (): JSX.Element => (
  <TaskContent hazards={hazards}></TaskContent>
);
