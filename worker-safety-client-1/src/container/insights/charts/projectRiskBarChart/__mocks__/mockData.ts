import type { BarDatum } from "@nivo/bar";
import type { MockedResponse } from "@apollo/client/testing";

import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import PortfolioPlanningProjectRiskCountQuery from "@/graphql/queries/insights/portfolioPlanningProjectRiskCount.gql";
import PortfolioLearningsProjectRiskCountQuery from "@/graphql/queries/insights/portfolioLearningsProjectRiskCount.gql";

import { samplePortfolioFilters } from "@/container/insights/charts/__mocks__/sharedMockData";

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
    query: PortfolioPlanningProjectRiskCountQuery,
    variables: {
      filters: samplePortfolioFilters,
    },
  },
  result: {
    data: {
      portfolioPlanning: {
        projectRiskLevelOverTime: data,
      },
    },
  },
});

const learningsRequest = (data: BarDatum[]): MockedResponse => ({
  request: {
    query: PortfolioLearningsProjectRiskCountQuery,
    variables: {
      filters: samplePortfolioFilters,
    },
  },
  result: {
    data: {
      portfolioLearnings: { projectRiskLevelOverTime: data },
    },
  },
});

export const projectRiskMockData: MockedResponse[] = [
  planningRequest(sampleRiskCountData),
  learningsRequest(sampleRiskCountData),
];

export const mockDataNoResult: MockedResponse[] = [
  planningRequest([]),
  learningsRequest([]),
];
