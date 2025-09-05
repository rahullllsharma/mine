import type { MockedResponse } from "@apollo/client/testing";
import type { ControlData } from "../ControlsNotImplementedChart";
import type { APIControlsDrillDownData } from "../mapControlsDrillDownData";
import cloneDeep from "lodash/cloneDeep";

import PortfolioLearningsControlsNotImplementedQuery from "@/graphql/queries/insights/portfolioLearningsControlsNotImplemented.gql";
import ProjectLearningsControlsNotImplementedQuery from "@/graphql/queries/insights/projectLearningsControlsNotImplemented.gql";
import ProjectLearningsControlsDrillDownQuery from "@/graphql/queries/insights/projectLearningsControlsDrillDown.gql";
import PortfolioLearningsControlsDrillDownQuery from "@/graphql/queries/insights/portfolioLearningsControlsDrillDown.gql";

import {
  samplePortfolioFilters,
  sampleProjectFilters,
} from "@/container/insights/charts/__mocks__/sharedMockData";

// ControlsNotImplemented Data /////////////////////////////////////////////////

const libraryControlId = "id";

const percentages = [0.5, 0.33, 0.2];
export const sampleControlsNotImplementedData = cloneDeep(percentages).map(
  (percent, i) => ({
    percent,
    libraryControl: {
      id: libraryControlId,
      name: `Library Control ${i}`,
    },
  })
);

const sampleControlsByProjectData = cloneDeep(percentages).map(
  (percent, i) => ({
    percent,
    project: {
      id: i,
      name: `Project ${i}`,
    },
  })
);

const sampleControlsByLocationData = cloneDeep(percentages).map(
  (percent, i) => ({
    percent,
    location: {
      id: i,
      name: `Location ${i}`,
    },
  })
);

const sampleControlsByHazardData = cloneDeep(percentages).map((percent, i) => ({
  percent,
  libraryHazard: {
    id: i,
    name: `Library Hazard ${i}`,
  },
}));

const sampleControlsByTaskData = cloneDeep(percentages).map((percent, i) => ({
  percent,
  libraryTask: {
    id: i,
    name: `Library Task Name ${i}`,
    category: `Library Task Category ${i}`,
  },
}));

const sampleControlsDrillDownData: APIControlsDrillDownData = {
  notImplementedControlsByProject: sampleControlsByProjectData,
  notImplementedControlsByLocation: sampleControlsByLocationData,
  notImplementedControlsByHazard: sampleControlsByHazardData,
  notImplementedControlsByTask: sampleControlsByTaskData,
  notImplementedControlsByTaskType: sampleControlsByTaskData,
};

const portfolioLearningsRequest = (data: ControlData[]): MockedResponse => ({
  request: {
    query: PortfolioLearningsControlsNotImplementedQuery,
    variables: {
      filters: samplePortfolioFilters,
    },
  },
  result: {
    data: {
      portfolioLearnings: {
        notImplementedControls: data,
      },
    },
  },
});

const projectLearningsRequest = (data: ControlData[]): MockedResponse => ({
  request: {
    query: ProjectLearningsControlsNotImplementedQuery,
    variables: {
      filters: sampleProjectFilters,
    },
  },
  result: {
    data: {
      projectLearnings: {
        notImplementedControls: data,
      },
    },
  },
});

const portfolioLearningsDrillDownRequest = (
  data: APIControlsDrillDownData
): MockedResponse => ({
  request: {
    query: PortfolioLearningsControlsDrillDownQuery,
    variables: {
      filters: samplePortfolioFilters,
      libraryControlId,
    },
  },
  result: {
    data: {
      portfolioLearnings: {
        ...data,
      },
    },
  },
});

const projectLearningsDrillDownRequest = (
  data: APIControlsDrillDownData
): MockedResponse => ({
  request: {
    query: ProjectLearningsControlsDrillDownQuery,
    variables: {
      filters: sampleProjectFilters,
      libraryControlId,
    },
  },
  result: {
    data: {
      projectLearnings: {
        ...data,
      },
    },
  },
});

export const controlsNotImpledMocks: MockedResponse[] = [
  portfolioLearningsRequest(sampleControlsNotImplementedData),
  projectLearningsRequest(sampleControlsNotImplementedData),
  portfolioLearningsDrillDownRequest(sampleControlsDrillDownData),
  projectLearningsDrillDownRequest(sampleControlsDrillDownData),
];

export const mockDataNoResult: MockedResponse[] = [
  portfolioLearningsRequest([]),
  projectLearningsRequest([]),
];
