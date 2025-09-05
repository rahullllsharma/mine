import type { BarDatum } from "@nivo/bar";
import type { MockedResponse } from "@apollo/client/testing";

import ProjectPlanningLocationRiskCountQuery from "@/graphql/queries/insights/projectPlanningLocationRiskCount.gql";
import ProjectLearningsLocationRiskCountQuery from "@/graphql/queries/insights/projectLearningsLocationRiskCount.gql";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";

import { sampleProjectFilters } from "@/container/insights/charts/__mocks__/sharedMockData";

// RiskBarChart data ///////////////////////////////////////////////////////////

const sampleRiskCountData = [
  {
    date: "2022-01-29",
    riskLevel: RiskLevel.HIGH,
    count: 10,
  },
  {
    date: "2022-01-29",
    riskLevel: RiskLevel.MEDIUM,
    count: 20,
  },
  {
    date: "2022-01-29",
    riskLevel: RiskLevel.LOW,
    count: 30,
  },
  {
    date: "2022-01-30",
    riskLevel: RiskLevel.HIGH,
    count: 5,
  },
  {
    date: "2022-01-30",
    riskLevel: RiskLevel.MEDIUM,
    count: 10,
  },
  {
    date: "2022-01-30",
    riskLevel: RiskLevel.LOW,
    count: 20,
  },
  {
    date: "2022-02-01",
    riskLevel: RiskLevel.HIGH,
    count: 1,
  },
  // skipping medium
  {
    date: "2022-02-01",
    riskLevel: RiskLevel.LOW,
    // set Low to zero
    count: 0,
  },
];

const planningRequest = (data: BarDatum[]): MockedResponse => ({
  request: {
    query: ProjectPlanningLocationRiskCountQuery,
    variables: {
      filters: sampleProjectFilters,
    },
  },
  result: {
    data: {
      projectPlanning: {
        locationRiskLevelOverTime: data,
      },
    },
  },
});

const learningsRequest = (data: BarDatum[]): MockedResponse => ({
  request: {
    query: ProjectLearningsLocationRiskCountQuery,
    variables: {
      filters: sampleProjectFilters,
    },
  },
  result: {
    data: {
      projectLearnings: { locationRiskLevelOverTime: data },
    },
  },
});

export const locationRiskMockData: MockedResponse[] = [
  planningRequest(sampleRiskCountData),
  learningsRequest(sampleRiskCountData),
];

export const mockDataNoResult: MockedResponse[] = [
  planningRequest([]),
  learningsRequest([]),
];
