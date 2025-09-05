import type { MockedResponse } from "@apollo/client/testing";
import type { ReasonNotImplementedCount } from "@/container/insights/charts/reasonsNotImplementedBarChart/ReasonsNotImplementedBarChart";
import cloneDeep from "lodash/cloneDeep";

import { getControlNotPerformedOptions } from "@/container/report/jobHazardAnalysis/constants";

import PortfolioLearningsReasonsNotImplementedCountQuery from "@/graphql/queries/insights/portfolioLearningsReasonsNotImplementedCount.gql";
import ProjectLearningsReasonsNotImplementedCountQuery from "@/graphql/queries/insights/projectLearningsReasonsNotImplementedCount.gql";

import {
  samplePortfolioFilters,
  sampleProjectFilters,
} from "@/container/insights/charts/__mocks__/sharedMockData";
import { mockTenantStore } from "@/utils/dev/jest";

const vals = [50, 150, 80, 280];
mockTenantStore();
export const sampleReasonsNotImplementedData = cloneDeep(
  getControlNotPerformedOptions()
).map(({ name }, i) => ({
  reason: name,
  count: vals[i],
}));

export const partialReasonsNotImplementedData = cloneDeep(
  getControlNotPerformedOptions().slice(0, 1)
).map(({ name }, i) => ({
  reason: name,
  count: vals[i],
}));

const portfolioRequest = (
  reasonData: ReasonNotImplementedCount[]
): MockedResponse => ({
  request: {
    query: PortfolioLearningsReasonsNotImplementedCountQuery,
    variables: {
      filters: samplePortfolioFilters,
    },
  },
  result: {
    data: {
      portfolioLearnings: {
        reasonsControlsNotImplemented: reasonData,
      },
    },
  },
});

const projectRequest = (
  reasonData: ReasonNotImplementedCount[]
): MockedResponse => ({
  request: {
    query: ProjectLearningsReasonsNotImplementedCountQuery,
    variables: {
      filters: sampleProjectFilters,
    },
  },
  result: {
    data: {
      projectLearnings: {
        reasonsControlsNotImplemented: reasonData,
      },
    },
  },
});

export const reasonsNotImpledMockData: MockedResponse[] = [
  portfolioRequest(sampleReasonsNotImplementedData),
  projectRequest(sampleReasonsNotImplementedData),
];

export const mockDataNoResult: MockedResponse[] = [
  portfolioRequest([]),
  projectRequest([]),
];

export const mockDataPartialResult: MockedResponse[] = [
  portfolioRequest(partialReasonsNotImplementedData),
  projectRequest(partialReasonsNotImplementedData),
];
