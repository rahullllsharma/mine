import type { MockedResponse } from "@apollo/client/testing";
import type { HazardData } from "../ApplicableHazardsChart";
import type { APIHazardsDrillDownData } from "../mapHazardsDrillDownData";
import cloneDeep from "lodash/cloneDeep";

import PortfolioLearningsApplicableHazardsQuery from "@/graphql/queries/insights/portfolioLearningsApplicableHazards.gql";
import ProjectLearningsApplicableHazardsQuery from "@/graphql/queries/insights/projectLearningsApplicableHazards.gql";
import ProjectLearningsHazardsDrillDownQuery from "@/graphql/queries/insights/projectLearningsHazardsDrillDown.gql";
import PortfolioLearningsHazardsDrillDownQuery from "@/graphql/queries/insights/portfolioLearningsHazardsDrillDown.gql";

import {
  samplePortfolioFilters,
  sampleProjectFilters,
} from "@/container/insights/charts/__mocks__/sharedMockData";

// ApplicableHazards Data /////////////////////////////////////////////////

const libraryHazardId = "id";

const hazardsCounts = [50, 33, 20, 1];
export const sampleApplicableHazardsData = cloneDeep(hazardsCounts).map(
  (count, i) => ({
    count,
    libraryHazard: {
      id: libraryHazardId,
      name: `Library Hazard ${i}`,
    },
  })
);

export const sampleHazardsByProjectData = cloneDeep(hazardsCounts).map(
  (count, i) => ({
    count,
    project: {
      id: i,
      name: `Project ${i}`,
    },
  })
);

export const sampleHazardsByLocationData = cloneDeep(hazardsCounts).map(
  (count, i) => ({
    count,
    location: {
      id: i,
      name: `Location ${i}`,
    },
  })
);

export const sampleHazardsBySiteConditionData = cloneDeep(hazardsCounts).map(
  (count, i) => ({
    count,
    librarySiteCondition: {
      id: i,
      name: `Library Site Condition ${i}`,
    },
  })
);

export const sampleHazardsByTaskData = cloneDeep(hazardsCounts).map(
  (count, i) => ({
    count,
    libraryTask: {
      id: i,
      name: `Library Task Name ${i}`,
      category: `Library Task Category ${i}`,
    },
  })
);

const sampleHazardsDrillDownData: APIHazardsDrillDownData = {
  applicableHazardsByProject: sampleHazardsByProjectData,
  applicableHazardsByLocation: sampleHazardsByLocationData,
  applicableHazardsBySiteCondition: sampleHazardsBySiteConditionData,
  applicableHazardsByTask: sampleHazardsByTaskData,
  applicableHazardsByTaskType: sampleHazardsByTaskData,
};

const portfolioLearningsRequest = (data: HazardData[]): MockedResponse => ({
  request: {
    query: PortfolioLearningsApplicableHazardsQuery,
    variables: {
      filters: samplePortfolioFilters,
    },
  },
  result: {
    data: {
      portfolioLearnings: {
        applicableHazards: data,
      },
    },
  },
});

const projectLearningsRequest = (data: HazardData[]): MockedResponse => ({
  request: {
    query: ProjectLearningsApplicableHazardsQuery,
    variables: {
      filters: sampleProjectFilters,
    },
  },
  result: {
    data: {
      projectLearnings: {
        applicableHazards: data,
      },
    },
  },
});

const portfolioLearningsDrillDownRequest = (
  data: APIHazardsDrillDownData
): MockedResponse => ({
  request: {
    query: PortfolioLearningsHazardsDrillDownQuery,
    variables: {
      filters: samplePortfolioFilters,
      libraryHazardId,
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
  data: APIHazardsDrillDownData
): MockedResponse => ({
  request: {
    query: ProjectLearningsHazardsDrillDownQuery,
    variables: {
      filters: sampleProjectFilters,
      libraryHazardId,
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

export const applicableHazardsMocks: MockedResponse[] = [
  portfolioLearningsRequest(sampleApplicableHazardsData),
  projectLearningsRequest(sampleApplicableHazardsData),
  portfolioLearningsDrillDownRequest(sampleHazardsDrillDownData),
  projectLearningsDrillDownRequest(sampleHazardsDrillDownData),
];

export const mockDataNoResult: MockedResponse[] = [
  portfolioLearningsRequest([]),
  projectLearningsRequest([]),
];
