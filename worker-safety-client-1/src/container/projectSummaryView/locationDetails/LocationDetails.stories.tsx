import type { ComponentMeta, ComponentStory } from "@storybook/react";

import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { DailyReportStatus } from "@/types/report/DailyReportStatus";
import { TaskStatus } from "@/types/task/TaskStatus";
import { LocationDetails } from "./LocationDetails";

export default {
  title: "Container/SummaryView/LocationDetails",
  component: LocationDetails,
} as ComponentMeta<typeof LocationDetails>;

const TemplateProjectSummaryView: ComponentStory<typeof LocationDetails> =
  args => <LocationDetails {...args} />;

const siteConditions = [
  {
    id: "1",
    name: "High Heat Index",
    riskLevel: RiskLevel.MEDIUM,
    startDate: "2021-10-10",
    endDate: "2021-10-11",
    supervisor: {
      id: "1",
      name: "El",
    },
    riskCalculation: {
      totalTaskRiskLevel: RiskLevel.UNKNOWN,
      isSupervisorAtRisk: false,
      isContractorAtRisk: false,
    },
    status: TaskStatus.NOT_STARTED,
    isManuallyAdded: false,
    hazards: [
      {
        id: "1",
        name: "Dehydration",
        isApplicable: true,
        controls: [
          {
            id: "1",
            name: "Replenish Water Supply",
            isApplicable: true,
          },
        ],
      },
    ],
    incidents: [],
  },
];

const tasks = [
  {
    id: "1",
    name: "Pipe Face Alignment",
    riskLevel: RiskLevel.MEDIUM,
    startDate: "2021-10-10",
    endDate: "2021-10-11",
    status: TaskStatus.NOT_STARTED,
    hazards: [
      {
        id: "1",
        name: "Pinch Point",
        isApplicable: true,
        controls: [
          {
            id: "1",
            name: "Gloves",
            isApplicable: true,
          },
          {
            id: "2",
            name: "Situational Jobsite Awareness",
            isApplicable: true,
          },
        ],
      },
    ],
    incidents: [],
  },
];

const dailyReports = [
  {
    id: "6162b039-40ad-486f-b6f7-2efb3822c437",
    createdBy: {
      id: "bab6fc84-63c3-4fe5-b7a6-137e26189ad9",
      name: "Test User",
    },
    createdAt: "2022-02-02T09:32:20.464954",
    status: DailyReportStatus.IN_PROGRESS,
  },
  {
    id: "6162b039-40ad-486f-b6f7-2efb3822c438",
    createdBy: {
      id: "bab6fc84-63c3-4fe5-b7a6-137e26189ad9",
      name: "Test User",
    },
    createdAt: "2022-02-02T09:32:20.464954",
    completedBy: {
      id: "bab6fc84-63c3-4fe5-b7a6-137e26189ad9",
      name: "Test User",
    },
    completedAt: "2022-02-02T09:32:20.464954",
    status: DailyReportStatus.COMPLETE,
  },
];

export const Location = TemplateProjectSummaryView.bind({});

Location.args = {
  location: {
    id: "1",
    name: "Location name",
    latitude: 34.054913,
    longitude: -62.136754,
    supervisor: {
      id: "1",
      name: "El",
    },
    riskLevel: RiskLevel.MEDIUM,
    riskCalculation: {
      totalTaskRiskLevel: RiskLevel.UNKNOWN,
      isSupervisorAtRisk: false,
      isContractorAtRisk: false,
      isCrewAtRisk: false,
    },
    siteConditions,
    tasks,
    activities: [],
    jobSafetyBriefings: [],
    dailyReports,
  },
};

export const LocationWithoutSiteConditions = TemplateProjectSummaryView.bind(
  {}
);

LocationWithoutSiteConditions.args = {
  location: {
    id: "1",
    name: "Location name",
    latitude: 34.054913,
    longitude: -62.136754,
    supervisor: {
      id: "1",
      name: "El",
    },
    additionalSupervisors: [
      { id: "235", name: "Sirius Goldberg" },
      { id: "236", name: "Hailey Quinn" },
    ],
    riskLevel: RiskLevel.MEDIUM,
    riskCalculation: {
      totalTaskRiskLevel: RiskLevel.UNKNOWN,
      isSupervisorAtRisk: false,
      isContractorAtRisk: false,
      isCrewAtRisk: false,
    },
    siteConditions: [],
    tasks,
    activities: [],
    jobSafetyBriefings: [],
    dailyReports,
  },
};
export const LocationWithoutTasks = TemplateProjectSummaryView.bind({});

LocationWithoutTasks.args = {
  location: {
    id: "1",
    name: "Location name",
    latitude: 34.054913,
    longitude: -62.136754,
    supervisor: {
      id: "1",
      name: "El",
    },
    additionalSupervisors: [
      { id: "235", name: "Sirius Goldberg" },
      { id: "236", name: "Hailey Quinn" },
    ],
    riskLevel: RiskLevel.MEDIUM,
    riskCalculation: {
      totalTaskRiskLevel: RiskLevel.UNKNOWN,
      isSupervisorAtRisk: false,
      isContractorAtRisk: false,
      isCrewAtRisk: false,
    },
    siteConditions,
    tasks: [],
    activities: [],
    jobSafetyBriefings: [],
    dailyReports,
  },
};

export const LocationWithoutReports = TemplateProjectSummaryView.bind({});

LocationWithoutReports.args = {
  location: {
    id: "1",
    name: "Location name",
    latitude: 34.054913,
    longitude: -62.136754,
    supervisor: {
      id: "1",
      name: "El",
    },
    riskLevel: RiskLevel.MEDIUM,
    riskCalculation: {
      totalTaskRiskLevel: RiskLevel.UNKNOWN,
      isSupervisorAtRisk: false,
      isContractorAtRisk: false,
      isCrewAtRisk: false,
    },
    siteConditions,
    tasks,
    activities: [],
    dailyReports: [],
    jobSafetyBriefings: [],
  },
};
