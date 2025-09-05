import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { RiskLevelByDate, ProjectRiskLevelByDate } from "./types";
import { range, random } from "lodash";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";

import { getDate, getDayRange } from "@/utils/date/helper";
import DailyRiskHeatmap from "./DailyRiskHeatmap";

export default {
  title: "Components/Charts/DailyRiskHeatmap",
  component: DailyRiskHeatmap,
  argTypes: {
    data: { table: { disable: true } },
    onPreviousDateClick: { action: "clicked" },
    onNextDateClick: { action: "clicked" },
  },
} as ComponentMeta<typeof DailyRiskHeatmap>;

const Template: ComponentStory<typeof DailyRiskHeatmap> = args => (
  <DailyRiskHeatmap {...args} />
);

const startDate = "2022-01-29";
const dateRange = 14;
const endDate = getDate(startDate, dateRange - 1);
const buildRiskLevelByDate: (riskLevels: RiskLevel[]) => RiskLevelByDate[] =
  riskLevels =>
    getDayRange(startDate, 0, dateRange - 1).map(date => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const datum: any = {
        date,
        riskLevel: riskLevels[random(riskLevels.length - 1)],
      };
      return datum;
    });

function entityRiskLevelByDate(
  num: number,
  riskLevels = [
    RiskLevel.HIGH,
    RiskLevel.MEDIUM,
    RiskLevel.LOW,
    RiskLevel.UNKNOWN,
    RiskLevel.RECALCULATING,
  ]
): ProjectRiskLevelByDate[] {
  return range(num).map(i => ({
    projectName: `Entity ${i}`,
    riskLevelByDate: buildRiskLevelByDate(riskLevels),
  }));
}

const entityCol1 = {
  id: "name",
  Header: "Entity name",
  value: (entityRisk: ProjectRiskLevelByDate) => entityRisk.projectName,
};
const entityCol2 = {
  id: "another_col",
  Header: "Task name",
  value: (entityRisk: ProjectRiskLevelByDate) =>
    `long column value ${entityRisk.projectName} with a long long name`,
};
const entityColumns = [entityCol1, entityCol2];

export const Playground = Template.bind({});
Playground.args = {
  data: entityRiskLevelByDate(10),
  columns: [entityCol1],
  startDate: startDate,
  endDate: endDate,
};

export const TwoColumn = Template.bind({});
TwoColumn.args = {
  data: entityRiskLevelByDate(10),
  columns: entityColumns,
  startDate: startDate,
  endDate: endDate,
};

export const FiltersWhenMissingRiskLevels = Template.bind({});
FiltersWhenMissingRiskLevels.args = {
  data: [
    ...entityRiskLevelByDate(2, [RiskLevel.HIGH]),
    ...entityRiskLevelByDate(5, [RiskLevel.UNKNOWN, RiskLevel.RECALCULATING]),
    ...entityRiskLevelByDate(2, [RiskLevel.LOW]),
  ],
  columns: entityColumns,
  startDate: startDate,
  endDate: endDate,
  showLegend: true,
};

export const WithLegend = Template.bind({});
WithLegend.args = {
  data: entityRiskLevelByDate(10),
  columns: [entityCol1],
  startDate: startDate,
  endDate: endDate,
  showLegend: true,
};

export const ManyEntries = Template.bind({});
ManyEntries.args = {
  data: entityRiskLevelByDate(500),
  columns: [entityCol1],
  startDate: startDate,
  endDate: endDate,
};

export const TheWorks = Template.bind({});
TheWorks.args = {
  data: entityRiskLevelByDate(60),
  columns: entityColumns,
  startDate: startDate,
  endDate: endDate,
  showLegend: true,
};

export const EmptyState = Template.bind({});
EmptyState.args = {
  data: [],
  columns: entityColumns,
  startDate: startDate,
  endDate: endDate,
};
