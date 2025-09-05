import type { MockedResponse } from "@apollo/client/testing";

import type {
  RiskLevelByDate,
  TaskRiskLevelByDate,
} from "@/components/charts/dailyRiskHeatmap/types";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";

import PortfolioPlanningTaskRiskLevelByDateQuery from "@/graphql/queries/insights/portfolioPlanningTaskRiskLevelByDate.gql";
import ProjectPlanningTaskRiskLevelByDateQuery from "@/graphql/queries/insights/projectPlanningTaskRiskLevelByDate.gql";
import {
  orderByLocationName,
  orderByName,
  orderByProjectName,
} from "@/graphql/utils";

import {
  sampleDates,
  sampleProjectFilters,
  samplePortfolioFilters,
} from "@/container/insights/charts/__mocks__/sharedMockData";

import { getDayRangeBetween } from "@/utils/date/helper";

const sampleRiskLevelByDate: RiskLevelByDate[] = [
  {
    date: "2022-01-29",
    riskLevel: RiskLevel.HIGH,
  },
  {
    date: "2022-01-30",
    riskLevel: RiskLevel.MEDIUM,
  },
  {
    date: "2022-01-31",
    riskLevel: RiskLevel.UNKNOWN,
  },
  {
    date: "2022-02-01",
    riskLevel: RiskLevel.LOW,
  },
  {
    date: "2022-02-02",
    riskLevel: RiskLevel.RECALCULATING,
  },
  {
    date: "2022-02-03",
    riskLevel: RiskLevel.UNKNOWN,
  },
];
const sampleHeatmapData: TaskRiskLevelByDate[] = getDayRangeBetween(
  sampleDates.startDate,
  sampleDates.endDate
).map((_date, i) => ({
  locationName: `Location ${i}`,
  taskName: `Task ${i}`,
  projectName: `Project ${i}`,
  riskLevelByDate: sampleRiskLevelByDate,
}));

const portfolioPlanningRequest = (
  data: TaskRiskLevelByDate[]
): MockedResponse => ({
  request: {
    query: PortfolioPlanningTaskRiskLevelByDateQuery,
    variables: {
      filters: samplePortfolioFilters,
      taskOrderBy: [orderByProjectName, orderByName],
    },
  },
  result: {
    data: {
      portfolioPlanning: {
        taskRiskLevelByDate: data,
      },
    },
  },
});

const projectPlanningRequest = (
  data: TaskRiskLevelByDate[]
): MockedResponse => ({
  request: {
    query: ProjectPlanningTaskRiskLevelByDateQuery,
    variables: {
      filters: sampleProjectFilters,
      taskOrderBy: [orderByLocationName, orderByName],
    },
  },
  result: {
    data: {
      projectPlanning: {
        taskRiskLevelByDate: data,
      },
    },
  },
});

export const taskRiskMockData: MockedResponse[] = [
  portfolioPlanningRequest(sampleHeatmapData),
  projectPlanningRequest(sampleHeatmapData),
];

export const mockDataNoResult: MockedResponse[] = [
  portfolioPlanningRequest([]),
  projectPlanningRequest([]),
];
