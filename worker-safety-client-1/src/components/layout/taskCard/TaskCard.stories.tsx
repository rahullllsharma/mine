import type { ComponentMeta, ComponentStory } from "@storybook/react";

import { noop } from "lodash-es";
import { RiskLevel } from "../../riskBadge/RiskLevel";
import TaskCard from "./TaskCard";
import TaskContent from "./content/TaskContent";
import TaskHeader from "./header/TaskHeader";

export default {
  title: "Layout/TaskCard/TaskCard",
  component: TaskCard,
  argTypes: {
    taskContent: { control: false },
  },
} as ComponentMeta<typeof TaskCard>;

const TemplateCardItem: ComponentStory<typeof TaskCard> = args => (
  <TaskCard {...args}></TaskCard>
);

export const Default = TemplateCardItem.bind({});
Default.args = {
  className: "border-risk-high",
  taskHeader: (
    <TaskHeader
      headerText="Above Ground Welding"
      riskLevel={RiskLevel.HIGH}
      onClick={noop}
    />
  ),
};

export const withSummary = TemplateCardItem.bind({});
withSummary.args = {
  className: "border-risk-high",
  taskHeader: (
    <TaskHeader
      icon="chevron_big_right"
      headerText="Above Ground Welding"
      riskLevel={RiskLevel.HIGH}
      onClick={noop}
      showSummaryCount={true}
      totalControls={3}
      totalHazards={4}
    />
  ),
};

export const collapsed = TemplateCardItem.bind({});

collapsed.args = {
  className: "border-risk-high",
  taskHeader: (
    <TaskHeader
      icon="chevron_big_right"
      headerText="Above Ground Welding"
      riskLevel={RiskLevel.HIGH}
      onClick={noop}
      showSummaryCount={true}
      totalControls={3}
      totalHazards={4}
    />
  ),
};

export const expanded = TemplateCardItem.bind({});

const task = {
  id: "1",
  name: "Task 1",
  riskLevel: RiskLevel.MEDIUM,
  hazards: [
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
  ],
};

expanded.args = {
  taskHeader: (
    <TaskHeader
      icon="chevron_big_down"
      headerText="Above Ground Welding"
      riskLevel={RiskLevel.HIGH}
      onClick={noop}
    />
  ),
  children: <TaskContent hazards={task.hazards}></TaskContent>,
};
