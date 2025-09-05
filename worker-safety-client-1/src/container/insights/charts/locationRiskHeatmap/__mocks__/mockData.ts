import type { MockedResponse } from "@apollo/client/testing";

import type {
  RiskLevelByDate,
  LocationRiskLevelByDate,
} from "@/components/charts/dailyRiskHeatmap/types";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import ProjectPlanningLocationRiskLevelByDateQuery from "@/graphql/queries/insights/projectPlanningLocationRiskLevelByDate.gql";

import {
  sampleDates,
  sampleProjectFilters,
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
const sampleHeatmapData: LocationRiskLevelByDate[] = getDayRangeBetween(
  sampleDates.startDate,
  sampleDates.endDate
).map((_date, i) => ({
  locationName: `Location ${i}`,
  taskName: `Task ${i}`,
  riskLevelByDate: sampleRiskLevelByDate,
}));

const planningRequest = (data: LocationRiskLevelByDate[]): MockedResponse => ({
  request: {
    query: ProjectPlanningLocationRiskLevelByDateQuery,
    variables: {
      filters: sampleProjectFilters,
    },
  },
  result: {
    data: {
      projectPlanning: {
        locationRiskLevelByDate: data,
      },
    },
  },
});

export const locationRiskMockData: MockedResponse[] = [
  planningRequest(sampleHeatmapData),
];

export const mockDataNoResult: MockedResponse[] = [planningRequest([])];
