import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { noop } from "lodash-es";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import TaskHeader from "./TaskHeader";

export default {
  title: "Layout/TaskCard/TaskHeader",
  component: TaskHeader,
} as ComponentMeta<typeof TaskHeader>;

const TemplateCardItem: ComponentStory<typeof TaskHeader> = args => (
  <TaskHeader {...args}></TaskHeader>
);

export const taskExpanded = TemplateCardItem.bind({});

taskExpanded.args = {
  icon: "chevron_big_down",
  headerText: "Above Ground Welding",
  riskLevel: RiskLevel.MEDIUM,
};

export const taskCollapsed = TemplateCardItem.bind({});

taskCollapsed.args = {
  icon: "chevron_big_right",
  headerText: "Above Ground Welding",
  riskLevel: RiskLevel.MEDIUM,
  showSummaryCount: true,
  totalHazards: 3,
  totalControls: 4,
};

export const reportInProgress = TemplateCardItem.bind({});

reportInProgress.args = {
  icon: "pie_chart_25",
  headerText: "Daily Inspection Report",
  subHeaderText: "Completed 10/5/2021 at 5:00PM by Roland Lemay",
};

export const withMenuAction = TemplateCardItem.bind({});

withMenuAction.args = {
  icon: "chevron_big_right",
  headerText: "Above Ground Welding",
  riskLevel: RiskLevel.MEDIUM,
  showSummaryCount: true,
  totalHazards: 3,
  totalControls: 4,
  menuIcon: "edit",
  onMenuClicked: noop,
};

export const taskWithNoEditPermissions = TemplateCardItem.bind({});

taskWithNoEditPermissions.args = {
  icon: "chevron_big_right",
  headerText: "Above Ground Welding",
  riskLevel: RiskLevel.MEDIUM,
  showSummaryCount: true,
  totalHazards: 3,
  totalControls: 4,
  menuIcon: "show",
  hasInfoIcon: true,
  infoIconTooltipText: "Text to display on hover",
  onMenuClicked: noop,
};

export const withDropdownOptions = TemplateCardItem.bind({});

withDropdownOptions.args = {
  icon: "chevron_big_right",
  headerText: "Above Ground Welding",
  riskLevel: RiskLevel.MEDIUM,
  showSummaryCount: true,
  totalHazards: 3,
  totalControls: 4,
  menuIcon: "edit",
  onMenuClicked: noop,
  hasDropdown: true,
  dropdownOptions: [
    [
      {
        label: "option 1",
        onClick: noop,
      },
    ],
    [
      {
        label: "option 2",
        onClick: noop,
      },
    ],
  ],
};
